#!/usr/bin/python

# standard modules
import collections
import json
import os
import os.path
import random
import threading

# addon modules
import pika
import xattr

import pprint

from toposm import *
import tileexpire


REFERENCE_TILESET = 'composite_h'
# How many seconds to wait after starting the queue filling thread to begin
# processing messages.
QUEUE_FILL_DELAY = 15
# How often the tile expiry thread should wake up and see if it should process
# the dequeued expirations.
EXPIRE_SLEEP_INTERVAL = 10


def queue_tile(z, x, y, queued_set, queues, queue_lock, queue_from=None):
    metatile = '%s/%s/%s' % (z, x/NTILES[z], y/NTILES[z])
    timestr = time.strftime('[%Y-%m-%d %H:%M:%S]')
    with queue_lock:
        if not metatile in queued_set:
            queued_set.add(metatile)
            queues[z].append(metatile)
            if queue_from:
                console.printMessage('%s queue from %s: %s' % (timestr, queue_from, metatile))
            else:
                console.printMessage('%s queue: %s' % (timestr, metatile))


class QueueFiller(threading.Thread):
    def __init__(self, queues, queued, lock):
        threading.Thread.__init__(self)
        self.queues = queues
        self.queued = queued
        self.lock = lock
        
    def run(self):
        console.printMessage('%s Initializing queue.' % time.strftime('[%Y-%m-%d %H:%M:%S]'))
        for root, dirs, files in os.walk(os.path.join(BASE_TILE_DIR, REFERENCE_TILESET)):
            for file in files:
                if 'user.toposm_dirty' in xattr.listxattr(os.path.join(root, file)):
                    cs = root.split('/')
                    queue_tile(int(cs[-2]), int(cs[-1]), int(file.split('.')[0]),
                               self.queued, self.queues, self.lock, 'init')
        console.printMessage('%s Queue initialized.' % time.strftime('[%Y-%m-%d %H:%M:%S]'))


class TileExpirer(threading.Thread):
    def __init__(self, maxz, queues, queued, lock):
        threading.Thread.__init__(self)
        self.maxz = maxz
        self.queues = queues
        self.queued = queued
        self.queue_lock = lock
        self.keep_running = True
        self.input_queue = collections.deque()

    def run(self):
        while self.keep_running:
            try:
                if len(self.input_queue) > 0:
                    console.printMessage('%s reading expiry input queue' % time.strftime('[%Y-%m-%d %H:%M:%S]'))
                    expire = tileexpire.OSMTileExpire()
                    while True:
                        (z, x, y) = self.input_queue.popleft()
                        expire.expire(z, x, y)
            except IndexError:
                console.printMessage('%s expiry input queue empty; expiring' % time.strftime('[%Y-%m-%d %H:%M:%S]'))
                self.process_expire(expire)
                console.printMessage('%s expiration pass finished' % time.strftime('[%Y-%m-%d %H:%M:%S]'))
            time.sleep(EXPIRE_SLEEP_INTERVAL)

    def process_expire(self, expire):
        for z in xrange(self.maxz, 2 - 1, -1):
            for (x, y) in expire.expiredAt(z):
                tile_path = getTilePath(REFERENCE_TILESET, z, x, y)
                if path.isfile(tile_path):
                    if 'user.toposm_dirty' not in xattr.listxattr(tile_path):
                        xattr.setxattr(tile_path, 'user.toposm_dirty', 'yes')
                    tile_path = getTilePath(REFERENCE_TILESET, z, x/NTILES[z]*NTILES[z], y/NTILES[z]*NTILES[z])
                    if path.isfile(tile_path) and 'user.toposm_dirty' not in xattr.listxattr(tile_path):
                        xattr.setxattr(tile_path, 'user.toposm_dirty', 'yes')
                    queue_tile(z, x, y, self.queued, self.queues, self.queue_lock, 'expire')

    def add_expired(self, tile):
        z, x, y = [ int(i) for i in tile.split('/') ]
        self.input_queue.append((z, x, y))

    def get_input_length(self):
        return len(self.input_queue)
    
        
class Queuemaster:

    def __init__(self, maxz):
        self.pp = pprint.PrettyPrinter()
        self.maxz = maxz
        self.expire_queues = [ collections.deque() for z in range(0, self.maxz + 1) ]
        self.queued = set()
        self.queue_lock = threading.Lock()
        self.expirer = TileExpirer(self.maxz, self.expire_queues, self.queued, self.queue_lock)
        self.expirer.start()

    ### Startup sequence.
    
    def run(self):
        self.connection = pika.SelectConnection(
            pika.ConnectionParameters(host=DB_HOST), self.on_connection_open)
        self.connection.ioloop.start()
        
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
        queue_filler = QueueFiller(self.expire_queues, self.queued, self.queue_lock)
        queue_filler.start()
        time.sleep(QUEUE_FILL_DELAY)
        self.channel.queue_declare(self.on_command_declare, exclusive=True)
    
    def on_command_declare(self, frame):
        self.command_queue = frame.method.queue
        self.channel.queue_bind(
            self.on_command_bind, queue=self.command_queue,
            exchange='osm', routing_key='toposm.queuemaster')

    def on_command_bind(self, frame):
        self.channel.basic_consume(self.on_command, queue=self.command_queue,
                                   exclusive=True)
        self.channel.basic_publish(exchange='osm',
                                   routing_key='command.toposm.render',
                                   body=json.dumps({'command': 'queuemaster online'}))


    ### AMQP commands.
    
    def on_expire(self, chan, method, props, body):
        self.expirer.add_expired(body)
        chan.basic_ack(delivery_tag=method.delivery_tag)

    def on_command(self, chan, method, props, body):
        timestr = time.strftime('[%Y-%m-%d %H:%M:%S]')
        try:
            message = json.loads(body)
            command = message['command']
            if command == 'dequeue':
                response = self.handle_request(message['strategy'])
            elif command == 'stats':
                response = self.get_stats()
            else:
                response = json.dumps({'result': 'error', 'error': 'unknown command: ' + body})
            if command != 'stats':
                console.printMessage('%s %s -> %s @ %s' % (timestr, body, response, props.reply_to))
            chan.basic_publish(
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(
                    correlation_id=props.correlation_id,
                    content_type='application/json'),
                body=response)
        except ValueError:
            console.printMessage('%s Non-JSON message: %s' % (timestr, body))
        chan.basic_ack(delivery_tag=method.delivery_tag)

    def handle_request(self, dequeue_strategy):
        if dequeue_strategy == 'by_pct':
            mt = self.dequeue_by_pct()
        elif dequeue_strategy == 'by_fixed_pct':
            mt = self.dequeue_by_fixed_pct()
        else:
            return json.dumps({'result': 'error',
                               'error': 'unknown dequeue strategy: ' + dequeue_strategy})
        with self.queue_lock:
            self.queued.remove(mt)
        return json.dumps({'result': 'ok', 'value': mt})

    def get_stats(self):
        return json.dumps({'queues': {z: len(self.expire_queues[z]) for z in xrange(0, self.maxz + 1)},
                           'expire': self.expirer.get_input_length()})


    ### Dequeueing strategies

    def dequeue_by_pct(self):
        # Queues are weighted according to how many messages they have and the
        # likelihood of further updates invalidating the queue's tiles.  (At
        # zoom level 0, every update invalidates the tile.  At zoom 1, an update
        # has a one-in-four chance of invalidating the tile, and so on.  Thus,
        # the higher the zoom level, the more weight they're given, so low-zoom
        # tiles are not rendered as often as their queue length might otherwise
        # dictate.)
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
        return self.expire_queues[chosen_queue].popleft()

    def dequeue_by_fixed_pct(self):
        # Considers only the total number of tiles at each zoom level, not the
        # number of tiles present.  (Exception: empty queues are not considered
        # at all.)  Good for clearing out high-zoom queues that the by_pct
        # strategy will neglect.
        queues = [ 2**z if len(self.expire_queues[z]) > 0 else 0 for z in range(0, self.maxz + 1) ]
        queue_pcts = [ float(t) / sum(queues) for t in queues ]
        chosen_pct = random.random()
        pct_sum = 0
        chosen_queue = -1
        for z in xrange(0, self.maxz + 1):
            pct_sum += queue_pcts[z]
            if chosen_pct < pct_sum and chosen_queue == -1:
                chosen_queue = z
        return self.expire_queues[chosen_queue].popleft()
    
if __name__ == "__main__":
    qm = Queuemaster(16)
    qm.run()
