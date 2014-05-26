#!/usr/bin/python

# standard modules
import collections
import os
import os.path
import random

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
        mt = self.dequeue_by_pct()
        self.queued.remove(mt)
        response = 'render ' + mt
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
        

    ### Dequeueing strategies

    def dequeue_by_pct(self):
        # Queues are weighted according to how many messages they have and the
        # likelihood of further updates invalidating the queue's tiles.  (At
        # zoom level 0, every update invalidates the tile.  At zoom 1, an update
        # has a one-in-four chance of invalidating the tile, and so on.  Thus,
        # the higher the zoom level, the more weight they're given, so low-zoom
        # tiles are not rendered as often as their queue length might otherwise
        # dictate.)
        # Rendering performance is based on how much time has been spent on each
        # queue.  We try to make the time-spent-rendering percentages match the
        # weighted queue percentages.
        weighted_queues = [ len(self.expire_queues[z]) * pow(4, z) / pow(NTILES[z], 2) for z in range(0, self.maxz + 1) ]
        if sum(weighted_queues) == 0:
            return None
        queue_pcts = [ float(t) / sum(weighted_queues) for t in weighted_queues ]
        chosen_pct = random.random()
        pct_sum = 0
        chosen_queue = -1
        for z in xrange(0, self.maxz + 1):
            pct_sum += queue_pcts[z]
            if chosen_pct < pct_sum and chosen_queue == -1:
                chosen_queue = z
        print 'q%: ' + ' '.join([ '%.2f' % (n * 100) for n in queue_pcts ])
        return self.expire_queues[chosen_queue].popleft()

    def dequeue_by_fixed_pct(self):
        # Considers only the total number of tiles at each zoom level, not the
        # number of tiles present.  (Exception: empty queues are not considered
        # at all.)  Good for clearing out high-zoom queues that the by_pct
        # strategy will neglect.
        queues = [ 4**z if len(self.expire_queues[z]) > 0 else 0 for z in range(0, self.maxz + 1) ]
        queue_pcts = [ float(t) / sum(weighted_queues) for t in weighted_queues ]
        chosen_pct = random.random()
        pct_sum = 0
        chosen_queue = -1
        for z in xrange(0, self.maxz + 1):
            pct_sum += queue_pcts[z]
            if chosen_pct < pct_sum and chosen_queue == -1:
                chosen_queue = z
        print 'q%: ' + ' '.join([ '%.2f' % (n * 100) for n in queue_pcts ])
        return self.expire_queues[chosen_queue].popleft()
    
if __name__ == "__main__":
    qm = Queuemaster(16)
    qm.run()
