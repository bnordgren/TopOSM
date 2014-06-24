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


# How often the tile expiry thread should wake up and see if it should process
# the dequeued expirations.
EXPIRE_SLEEP_INTERVAL = 10
# How long we can go without hearing from a renderer before we consider it
# stale.
RENDERER_STALE_TIME = 3600
# For the initial queue loading, wait until after this zoom level is complete
# before starting to render things.  (This prevents the renderers always being
# asked to render stuff at zoom 2 to start with.)
INITIAL_QUEUE_NOTIFY_ZOOM = 7

def log_message(message):
    console.printMessage(time.strftime('[%Y-%m-%d %H:%M:%S]') + ' ' + message)
    

class Renderer:
    def __init__(self, registration, render_queue, amqp_queue, channel):
        self.render_queue = render_queue
        self.amqp_queue = amqp_queue
        self.channel = channel
        self.hostname = registration['hostname']
        self.pid = registration['pid']
        self.threadid = registration['threadid']
        self.dequeue_strategy = registration['strategy']
        self.working_on = None
        self.last_activity = time.time()

    @property
    def name(self):
        return '%s.%s.%s' % (self.hostname, self.pid, self.threadid)

    @property
    def idle(self):
        return not self.working_on

    @property
    def status(self):
        if self.idle:
            return 'idle'
        base = 'rendering: %s' % self.working_on
        time_since_last_contact = time.time() - self.last_activity
        if time_since_last_contact > RENDERER_STALE_TIME:
            if time_since_last_contact > (60 * 60 * 24):
                stale = ' (STALE %d days)' % (time_since_last_contact / (60 * 60 * 24))
            elif time_since_last_contact > (60 * 60):
                stale = ' (STALE %d hours)' % (time_since_last_contact / (60 * 60))
            elif time_since_last_contact > 60:
                stale = ' (STALE %d minutes)' % (time_since_last_contact / 60)
            else:
                stale = ' (STALE %d seconds)' % time_since_last_contact
        else:
            stale = ''
        return base + stale

    def send_request(self):
        if self.idle:
            mt = self.render_queue.dequeue(self.dequeue_strategy)
            if mt:
                log_message('%s -> render %s' % (self.name, mt))
                self.working_on = mt
                self.last_activity = time.time()
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.amqp_queue,
                    properties=pika.BasicProperties(
                        content_type='application/json'),
                    body=json.dumps({'command': 'render',
                                     'metatile': mt}))

    def finished(self, metatile):
        # Check to see if it's what we think we're working on.  If not, assume
        # it's from a previous queuemaster and ignore the message.
        if self.working_on == metatile:
            self.working_on = None
        # This counts as the client being active, though.
        self.last_activity = time.time()


class Queue:
    def __init__(self, maxz):
        self.maxz = maxz
        self.lock = threading.Lock()
        self.queued_metatiles = set()
        self.zoom_queues = [ collections.deque() for z in range(0, self.maxz + 1) ]
        self.missing_queue = collections.deque()
        self.important_stack = collections.deque()
        self.pending_metatiles = set()

    def queue_metatile(self, z, x, y, queue, source):
        mt = '%s/%s/%s' % (z, x, y)
        if mt in self.pending_metatiles:
            log_message('skipping pending metatile: %s/%s/%s' % (z, x, y))
            return
        added = False
        if queue is self.zoom_queues[z]:
            # Ordinary, by-zoom queue.
            with self.lock:
                if mt not in self.queued_metatiles:
                    queue.append(mt)
                    self.queued_metatiles.add(mt)
                    added = True
        else:
            # Specialty queue.
            with self.lock:
                if mt not in queue:
                    queue.append(mt)
                    self.queued_metatiles.add(mt)
                    if mt in self.zoom_queues[z]:
                        self.zoom_queues[z].remove(mt)
                    added = True
        if added:
            if source:
                log_message('queue from %s: %s' % (source, mt))
            else:
                log_message('queue: %s' % mt)

    def queue_tile(self, z, x, y, queue='zoom', source=None):
        mz, mx, my = z, x / NTILES[z], y / NTILES[z]
        if queue == 'missing':
            self.queue_metatile(mz, mx, my, self.missing_queue, source)
        elif queue == 'important':
            self.queue_metatile(mz, mx, my, self.important_stack, source)
        elif queue == 'zoom':
            self.queue_metatile(mz, mx, my, self.zoom_queues[z], source)

    def dequeue(self, strategy):
        try:
            mt = self.missing_queue.popleft()
        except IndexError:
            if strategy == 'missing':
                return None
            try:
                mt = self.important_stack.pop()
            except IndexError:
                if strategy == 'important':
                    return None
                elif strategy == 'by_work_available':
                    mt = self.dequeue_by_work_available()
                elif strategy == 'by_zoom':
                    mt = self.dequeue_by_zoom()
                else:
                    log_message('unknown dequeue strategy: %s' % strategy)
                    return None
        if not mt:
            return None
        with self.lock:
            if mt in self.queued_metatiles:
                self.queued_metatiles.remove(mt)
            self.pending_metatiles.add(mt)
        return mt

    def mark_metatile_rendered(self, z, x, y):
        mt = '%s/%s/%s' % (z, x, y)
        with self.lock:
            if mt in self.pending_metatiles:
                self.pending_metatiles.remove(mt)

    def mark_metatile_abandoned(self, z, x, y):
        mt = '%s/%s/%s' % (z, x, y)
        with self.lock:
            if mt in self.pending_metatiles:
                self.pending_metatiles.remove(mt)
        self.queue_metatile(z, x, y, self.important_stack, 'abandoned')

    def get_stats(self):
        stats = {z: len(self.zoom_queues[z]) for z in xrange(0, self.maxz + 1)}
        stats.update({'important': len(self.important_stack),
                      'missing': len(self.missing_queue)})
        return stats

    def dequeue_by_work_available(self):
        # Queues are weighted according to how many messages they have and the
        # likelihood of further updates invalidating the queue's tiles.  (At
        # zoom level 0, every update invalidates the tile.  At zoom 1, an update
        # has a one-in-four chance of invalidating the tile, and so on.  Thus,
        # the higher the zoom level, the more weight they're given, so low-zoom
        # tiles are not rendered as often as their queue length might otherwise
        # dictate.)
        weighted_queues = [ len(self.zoom_queues[z]) * pow(4, z) / pow(NTILES[z], 2) for z in range(0, self.maxz + 1) ]
        if sum(weighted_queues) == 0:
            return None
        queue_pcts = [ float(t) / sum(weighted_queues) for t in weighted_queues ]
        chosen_pct = random.random()
        pct_sum = 0
        chosen_queue = self.maxz
        for z in xrange(0, self.maxz + 1):
            pct_sum += queue_pcts[z]
            if chosen_pct < pct_sum and chosen_queue == self.maxz:
                chosen_queue = z
        try:
            return self.zoom_queues[chosen_queue].popleft()
        except IndexError:
            return self.dequeue_by_work_available()

    def dequeue_by_zoom(self):
        # Considers only the total number of tiles at each zoom level, not the
        # number of tiles present.  (Exception: empty queues are not considered
        # at all.)  Good for clearing out nearly-empty high-zoom queues that the
        # by_pct strategy will neglect.
        queues = [ 2**z if len(self.zoom_queues[z]) > 0 else 0 for z in range(0, self.maxz + 1) ]
        if sum(queues) == 0:
            return None
        queue_pcts = [ float(t) / sum(queues) for t in queues ]
        chosen_pct = random.random()
        pct_sum = 0
        chosen_queue = self.maxz
        for z in xrange(0, self.maxz + 1):
            pct_sum += queue_pcts[z]
            if chosen_pct < pct_sum and chosen_queue == self.maxz:
                chosen_queue = z
        try:
            return self.zoom_queues[chosen_queue].popleft()
        except IndexError:
            return self.dequeue_by_zoom()
        

class QueueFiller(threading.Thread):
    def __init__(self, maxz, queue):
        threading.Thread.__init__(self)
        self.maxz = maxz
        self.queue = queue
        self.keep_running = True
        self.current_zoom = None
        self.lock = threading.Lock()
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host=DB_HOST))
        self.chan = self.conn.channel()
        
    def run(self):
        log_message('Initializing queue.')
        for z in xrange(2, self.maxz + 1):
            with self.lock:
                self.current_zoom = z
            for root, dirs, files in os.walk(os.path.join(BASE_TILE_DIR, REFERENCE_TILESET, str(z))):
                dirty_tiles = []
                for file in files:
                    full_path = os.path.join(root, file)
                    if 'user.toposm_dirty' in xattr.listxattr(full_path):
                        cs = root.split('/')
                        dirty_tiles.append(
                            (os.stat(full_path).st_mtime, int(cs[-2]), int(cs[-1]), int(file.split('.')[0])))
                    if not self.keep_running:
                        return
                dirty_tiles.sort()
                for t, z, x, y in dirty_tiles:
                    self.queue.queue_tile(z, x, y, 'zoom', 'init')
                if len(dirty_tiles) > 0 and z >= INITIAL_QUEUE_NOTIFY_ZOOM:
                    self.notify_queuemaster()
        with self.lock:
            self.current_zoom = -1
        log_message('Queue initialized.')

    def notify_queuemaster(self):
        self.chan.basic_publish(
            exchange='osm',
            routing_key='toposm.queuemaster',
            body=json.dumps({'command': 'queued'}))

    def get_status(self):
        with self.lock:
            return self.current_zoom

    def quit(self):
        self.keep_running = False


class TileExpirer(threading.Thread):
    def __init__(self, maxz, queue):
        threading.Thread.__init__(self)
        self.maxz = maxz
        self.queue = queue
        self.keep_running = True
        self.input_queue = collections.deque()
        self.lock = threading.Lock()
        self.current_expire = None
        self.current_expire_zoom = None

    def run(self):
        while self.keep_running or len(self.input_queue) > 0:
            try:
                if len(self.input_queue) > 0:
                    log_message('reading expiry input queue')
                    expire = tileexpire.OSMTileExpire()
                    while True:
                        (z, x, y) = self.input_queue.popleft()
                        expire.expire(z, x, y)
            except IndexError:
                log_message('expiry input queue empty; expiring')
                self.process_expire(expire)
                log_message('expiration pass finished')
            time.sleep(EXPIRE_SLEEP_INTERVAL)

    def process_expire(self, expire):
        with self.lock:
            self.current_expire = expire
        for z in xrange(self.maxz, 2 - 1, -1):
            with self.lock:
                self.current_expire_zoom = z
            for (x, y) in expire.expiredAt(z):
                tile_path = getTilePath(REFERENCE_TILESET, z, x, y)
                if path.isfile(tile_path):
                    if 'user.toposm_dirty' not in xattr.listxattr(tile_path):
                        xattr.setxattr(tile_path, 'user.toposm_dirty', 'yes')
                    tile_path = getTilePath(REFERENCE_TILESET, z, x/NTILES[z]*NTILES[z], y/NTILES[z]*NTILES[z])
                    if path.isfile(tile_path) and 'user.toposm_dirty' not in xattr.listxattr(tile_path):
                        xattr.setxattr(tile_path, 'user.toposm_dirty', 'yes')
                    self.queue.queue_tile(z, x, y, 'zoom', 'expire')
        with self.lock:
            self.current_expire = None
            self.current_expire_zoom = None

    def add_expired(self, tile):
        z, x, y = [ int(i) for i in tile.split('/') ]
        self.input_queue.append((z, x, y))

    def get_input_length(self):
        return len(self.input_queue)

    def get_expire_status(self):
        with self.lock:
            if self.current_expire:
                try:
                    return (self.current_expire_zoom, self.current_expire.countExpiredAt(self.current_expire_zoom))
                except:
                    return None
            else:
                return None

    def quit(self):
        self.keep_running = False


class Queuemaster:

    def __init__(self, maxz):
        self.maxz = maxz
        self.queue = Queue(self.maxz)
        self.initializer = None
        self.expirer = TileExpirer(self.maxz, self.queue)
        self.expirer.start()
        self.renderers = {}

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
            self.on_exchange_declare, exchange="osm", type="topic",
            durable=True, auto_delete=False)

    def on_exchange_declare(self, frame):
        self.channel.queue_declare(self.on_command_declare, exclusive=True)
        self.channel.queue_declare(self.on_expire_declare, queue='expire_toposm',
                                   durable=True, auto_delete=False)
            
    def on_expire_declare(self,frame):
        self.channel.queue_bind(
            self.on_expire_bind, queue='expire_toposm', exchange='osm',
            routing_key='expire')

    def on_expire_bind(self,frame):
        self.channel.basic_consume(self.on_expire, queue='expire_toposm',
                                   exclusive=True, no_ack=True)
        self.initializer = QueueFiller(self.maxz, self.queue)
        self.initializer.start()
    
    def on_command_declare(self, frame):
        self.command_queue = frame.method.queue
        self.channel.queue_bind(
            None, queue=self.command_queue,
            exchange='osm', routing_key='toposm.rendered.#')
        self.channel.queue_bind(
            self.on_command_bind, queue=self.command_queue,
            exchange='osm', routing_key='toposm.queuemaster')

    def on_command_bind(self, frame):
        self.channel.basic_consume(self.on_command, queue=self.command_queue,
                                   exclusive=True)
        log_message('queuemaster online')
        self.channel.basic_publish(exchange='osm',
                                   routing_key='command.toposm',
                                   body=json.dumps({'command': 'queuemaster online'}))


    ### AMQP commands.
    
    def on_expire(self, chan, method, props, body):
        self.expirer.add_expired(body)

    def on_command(self, chan, method, props, body):
        try:
            message = json.loads(body)
            command = message['command']
            if command == 'register':
                self.add_renderer(message, props.reply_to)
                self.send_render_requests()
            elif command == 'unregister':
                if props.reply_to in self.renderers:
                    self.remove_renderer(props.reply_to)
            elif command == 'rendered':
                if props.reply_to in self.renderers:
                    self.renderers[props.reply_to].finished(message['metatile'])
                z, x, y = [ int(s) for s in message['metatile'].split('/') ]
                self.queue.mark_metatile_rendered(z, x, y)
                self.send_render_requests()
            elif command == 'stats':
                chan.basic_publish(
                    exchange='',
                    routing_key=props.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=props.correlation_id,
                        content_type='application/json'),
                    body=self.get_stats())
            elif command == 'render':
                self.handle_render_request(message['tile'], props)
                self.send_render_requests()
            elif command == 'queued':
                self.send_render_requests()
            elif command == 'quit':
                self.quit()
            else:
                log_message('unknown message: %s' % body)
        except ValueError:
            log_message('Non-JSON message: %s' % body)
        chan.basic_ack(delivery_tag=method.delivery_tag)

    def get_stats(self):
        result = {'queue': self.queue.get_stats(),
                  'expire': {'input': self.expirer.get_input_length(),
                             'status': self.expirer.get_expire_status()},
                  'render': {r.name: r.status for r in self.renderers.values()}}
        if self.initializer and self.initializer.is_alive():
            result['init'] = self.initializer.get_status()
        return json.dumps(result)

    def add_renderer(self, message, queue):
        self.renderers[queue] =  Renderer(message, self.queue, queue, self.channel)

    def remove_renderer(self, queue):
        if self.renderers[queue].working_on:
            z, x, y = [ int(s) for s in self.renderers[queue].working_on.split('/') ]
            self.queue.mark_metatile_abandoned(z, x, y)
        del self.renderers[queue]

    def send_render_requests(self):
        for renderer in self.renderers.values():
            renderer.send_request()

    def handle_render_request(self, tile, props):
        z, x, y = [ int(i) for i in tile.split('/') ]
        mt = '%s/%s/%s' % (z, x / NTILES[z], y / NTILES[z])
        if tileExists(REFERENCE_TILESET, z, x, y):
            importance = 'important'
        else:
            importance = 'missing'
        self.queue.queue_tile(z, x, y, importance, 'request')

    def quit(self):
        log_message('Exiting.')
        self.channel.basic_cancel()
        self.initializer.quit()
        self.expirer.quit()
        self.expirer.join()
        self.initializer.join()
        self.connection.ioloop.stop()
        log_message('Shutdown process concluded.')


if __name__ == "__main__":
    qm = Queuemaster(16)
    qm.run()
