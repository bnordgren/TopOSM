#!/usr/bin/python

import sys, os, time

import pika
import uuid
import xattr

from env import *
from toposm import *
from stats import *

REFERENCE_FILE = '/srv/tiles/tirex/planet-import-complete'
REFERENCE_MTIME = path.getmtime(REFERENCE_FILE)
REFERENCE_TILESET = 'composite_h'


class ContinuousRenderThread:
    def __init__(self, maxz, dequeue_strategy, amqp_channel, threadNumber):
        console.printMessage("Creating thread %d" % (threadNumber))
        self.maxz = maxz
        self.dequeue_strategy = dequeue_strategy
        self.chan = amqp_channel
        self.threadNumber = threadNumber
        self.tilesizes = [ getTileSize(NTILES[z], True) for z in range(0, self.maxz + 1) ]
        self.maps = [ None for z in range(0, self.maxz + 1) ]

        self.queuemaster_available = True

        self.commandQueue = self.chan.queue_declare(exclusive=True).method.queue
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command')
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.{0}'.format(os.uname()[1]))
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm')
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm.render')
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm.render.{0}'.format(os.uname()[1]))
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm.render.{0}.{1}'.format(os.uname()[1], os.getpid()))
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm.render.{0}.{1}.{2}'.format(os.uname()[1], os.getpid(), threadNumber + 1))
        self.chan.basic_consume(self.on_command, queue=self.commandQueue)
        self.printMessage("Created thread")

    def loadMaps(self, zoom):
        self.maps[zoom] = {}
        for mapname in MAPNIK_LAYERS:
            console.debugMessage('Loading mapnik.Map: {0}/{1}'.format(zoom, mapname))
            self.maps[zoom][mapname] = mapnik.Map(self.tilesizes[zoom], self.tilesizes[zoom])
            mapnik.load_map(self.maps[zoom][mapname], mapname + ".xml")

    def printMessage(self, message):
        message = '[%02d] %s' % (self.threadNumber+1,  message)
        console.printMessage(message)

    def runAndLog(self, message, function, args):
        message = '[%02d] %s' % (self.threadNumber+1,  message)
        console.printMessage(message)
        try:
            return function(*args)        
        except Exception as ex:
            console.printMessage('Failed: ' + message)
            errorLog.log('Failed: ' + message, ex)
            raise

    def renderMetaTileFromMsg(self, msg):
        if not msg:
            return
        start_time = time.time()
        z, metax, metay = [int(n) for n in msg.split('/')]
        layerTimes = None
        if metaTileNeedsRendering(z, metax, metay):
            message = 'Rendering {0}/{1}/{2}'.format(z, metax, metay)
            if not self.maps[z]:
                self.loadMaps(z)
            layerTimes = self.runAndLog(message, renderMetaTile, (z, metax, metay, NTILES[z], self.maps[z]))
        if layerTimes:
            stats.recordRender(z, time.time() - start_time, layerTimes)

    # There's got to be a better way to do this...
    def on_command(self, chan, method, props, body):
        self.printMessage('Received message: ' + body)
        parts = body.split()
        if parts[0] == 'quit' or parts[0] == 'exit':
            chan.stop_consuming()
        elif parts[0] == 'newmaps':
            self.maps = [ None for z in range(0, self.maxz + 1) ]
        elif parts[0] == 'reload':
            reload(globals()[parts[1]])
        elif parts[0] == 'render':
            self.renderMetaTileFromMsg(parts[1])
            self.request_rendering()
        elif parts[0] == 'queuemaster_online':
            if not self.queuemaster_available:
                self.request_rendering()
        else:
            self.printMessage('Unknown command: ' + body)
        chan.basic_ack(delivery_tag=method.delivery_tag)

    def request_rendering(self):
        self.request_id = str(uuid.uuid4())
        self.printMessage('Requesting metatile.  ID: ' + self.request_id)
        self.queuemaster_available = self.chan.basic_publish(
            exchange='osm',
            routing_key='toposm.queuemaster',
            properties=pika.BasicProperties(reply_to=self.commandQueue,
                                            correlation_id=self.request_id),
            body='request ' + self.dequeue_strategy,
            mandatory=True)

    def renderLoop(self):
        self.request_rendering()
        self.chan.start_consuming()


def isOldTile(z, x, y):
    tile_path = getTilePath(REFERENCE_TILESET, z, x, y)
    return path.isfile(tile_path) and 'user.toposm_dirty' in xattr.listxattr(tile_path)

def tileNeedsRendering(z, x, y):
    return not tileExists(REFERENCE_TILESET, z, x, y) or isOldTile(z, x, y)

def isOldMetaTile(z, x, y):
    ntiles = NTILES[z]
    tile_path = getTilePath(REFERENCE_TILESET, z, x*ntiles, y*ntiles)
    return path.isfile(tile_path) and 'user.toposm_dirty' in xattr.listxattr(tile_path)

def metaTileNeedsRendering(z, x, y):
    ntiles = NTILES[z]
    return not tileExists(REFERENCE_TILESET, z, x*ntiles, y*ntiles) or isOldMetaTile(z, x, y)


if __name__ == "__main__":
    console.printMessage('Initializing.')
    maxz = int(sys.argv[1])

    if len(sys.argv) >= 3:
        dequeue_strategy = sys.argv[2]
    else:
        dequeue_strategy = 'by_pct'
    
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=DB_HOST))
    chan = conn.channel()
    chan.exchange_declare(exchange="osm", type="direct", durable=True, auto_delete=False)
    conn.close()

    console.printMessage('Starting renderers.')
    renderers = {}
    for i in range(NUM_THREADS):
        rconn = pika.BlockingConnection(pika.ConnectionParameters(host=DB_HOST))
        rchan = rconn.channel()
        renderer = ContinuousRenderThread(maxz, dequeue_strategy, rchan, i)
        render_thread = threading.Thread(target=renderer.renderLoop)
        render_thread.start()
        renderers[i] = (render_thread, rconn, rchan)
    for thread, conn, chan in renderers.values():
        thread.join()
        rconn.close()
