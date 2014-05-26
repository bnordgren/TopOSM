#!/usr/bin/python

# standard modules
import collections
import os
import os.path

# addon modules
import pika
import xattr

import pprint

from toposm import *

REFERENCE_TILESET='composite_h'

class Queuemaster:

    def __init__(self, maxz):
        self.pp = pprint.PrettyPrinter()
        self.maxz = maxz
        self.expire_queues = [ collections.deque() for z in range(0, self.maxz + 1) ]
        self.queued = set()

    ### Startup sequence.
    
    def run(self):
        connection = pika.SelectConnection(
            pika.ConnectionParameters(host=DB_HOST), self.on_connection_open)
        connection.ioloop.start()
        
    def on_connection_open(self, conn):
        conn.channel(self.on_channel_open)

    def on_channel_open(self, chan):
        self.channel = chan
        chan.exchange_declare(
            self.on_exchange_declare, exchange="osm", type="direct",
            durable=True, auto_delete=False)

    def on_exchange_declare(self, frame):
        self.channel.queue_declare(self.on_expire_declare, queue='expire_toposm',
                                   durable=True, auto_delete=False)
            
    def on_expire_declare(self,frame):
        self.channel.queue_bind(
            self.on_expire_bind, queue='expire_toposm', exchange='osm',
            routing_key='expire')

    def on_expire_bind(self,frame):
        self.channel.basic_consume(self.on_expire, queue='expire_toposm',
                                   exclusive=True)
        self.load_expire_queue()
        self.channel.queue_declare(self.on_command_declare, exclusive=True)
    
    def on_command_declare(self, frame):
        self.command_queue = frame.method.queue
        self.channel.queue_bind(
            self.on_command_bind, queue=self.command_queue,
            exchange='osm', routing_key='toposm.queuemaster')

    def on_command_bind(self, frame):
        self.channel.basic_consume(self.on_request, queue=self.command_queue,
                                   exclusive=True)
        self.channel.basic_publish(exchange='osm',
                                   routing_key='command.toposm.render',
                                   body='queuemaster_online')

    ### AMQP commands.
    
    def on_expire(self, chan, method, props, body):
        self.expire_tile(body)
        chan.basic_ack(delivery_tag=method.delivery_tag)

    def on_request(self, chan, method, props, body):
        timestr = time.strftime('[%Y-%m-%d %H:%M:%S]')
        parts = body.split()
        if parts[0] != 'request':
            print timestr + ' bad command: ' + body
            return
        for z in xrange(self.maxz, -1, -1):
            try:
                mt = self.expire_queues[z].popleft()
                self.queued.remove(mt)
                response = 'render ' + mt
                break
            except IndexError:
                pass
        print '%s %s -> %s @ %s' % (timestr, body, response, props.reply_to)
        print 'queue size: %s' % ' '.join([ '%s:%s' % (z, len(self.expire_queues[z])) for z in xrange(0, self.maxz + 1) ])
        chan.basic_publish(exchange='',
                           routing_key=props.reply_to,
                           properties=pika.BasicProperties(
                               correlation_id=props.correlation_id),
                           body=response)
        chan.basic_ack(delivery_tag=method.delivery_tag)

    ### Queue management.

    def load_expire_queue(self):
        print '%s Initializing queue.' % time.strftime('[%Y-%m-%d %H:%M:%S]')
        for root, dirs, files in os.walk(os.path.join(BASE_TILE_DIR, REFERENCE_TILESET)):
            for file in files:
                if 'user.toposm_dirty' in xattr.listxattr(os.path.join(root, file)):
                    cs = root.split('/')
                    self.queue_tile(int(cs[-2]), int(cs[-1]), int(file.split('.')[0]))
        print '%s Queue initialized.' % time.strftime('[%Y-%m-%d %H:%M:%S]')

    def expire_tile(self, tile):
        (z, x, y) = [int(i) for i in tile.split('/') ]
        if z < self.maxz:
            x = x * 2**(maxz - z)
            y = y * 2**(maxz - z)
            z = maxz
        while z >= 0:
            tile_path = getTilePath(REFERENCE_TILESET, z, x, y)
            if path.isfile(tile_path):
                xattr.setxattr(tile_path, 'user.toposm_dirty', 'yes')
                tile_path = getTilePath(REFERENCE_TILESET, z, x/NTILES[z]*NTILES[z], y/NTILES[z]*NTILES[z])
                if path.isfile(tile_path):
                    xattr.setxattr(tile_path, 'user.toposm_dirty', 'yes')
                self.queue_tile(z, x, y)
            z -= 1
            x /= 2
            y /= 2

    def queue_tile(self, z, x, y):
        metatile = '%s/%s/%s' % (z, x/NTILES[z], y/NTILES[z])
        if not metatile in self.queued:
            self.queued.add(metatile)
            timestr = time.strftime('[%Y-%m-%d %H:%M:%S]')
            print '%s queue: %s' % (timestr, metatile)
            self.expire_queues[z].append(metatile)
        

if __name__ == "__main__":
    qm = Queuemaster(16)
    qm.run()
