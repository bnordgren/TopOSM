#!/usr/bin/python

import sys, os, time

from amqplib import client_0_8 as amqp

from env import *
from toposm import *
from stats import *
import dequeue

REFERENCE_FILE = '/srv/tiles/tirex/planet-import-complete'
REFERENCE_MTIME = path.getmtime(REFERENCE_FILE)
REFERENCE_TILESET = 'composite_h'


class ContinuousRenderThread:
    def __init__(self, dequeueStrategy, maxz, amqp_channel, threadNumber):
        console.printMessage("Creating thread %d" % (threadNumber))
        self.maxz = maxz
        self.chan = amqp_channel
        self.threadNumber = threadNumber
        self.tilesizes = [ getTileSize(NTILES[z], True) for z in range(0, self.maxz + 1) ]
        self.maps = [ None for z in range(0, self.maxz + 1) ]

        self.dequeueStrategy = dequeueStrategy(threadNumber, maxz, amqp_channel)
        self.keepRendering = True

        self.commandQueue = self.chan.queue_declare(durable=False, exclusive=True, auto_delete=True)[0]
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command')
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.{0}'.format(os.uname()[1]))
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm')
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm.render')
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm.render.{0}'.format(os.uname()[1]))
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm.render.{0}.{1}'.format(os.uname()[1], os.getpid()))
        self.chan.queue_bind(queue=self.commandQueue, exchange='osm', routing_key='command.toposm.render.{0}.{1}.{2}'.format(os.uname()[1], os.getpid(), threadNumber + 1))
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
        self.printMessage("Received message %s" % (msg.body))
        z, metax, metay = [int(n) for n in msg.body.split('/')]
        layerTimes = None
        if metaTileNeedsRendering(z, metax, metay):
            message = 'Rendering {0}/{1}/{2}'.format(z, metax, metay)
            if not self.maps[z]:
                self.loadMaps(z)
            layerTimes = self.runAndLog(message, renderMetaTile, (z, metax, metay, NTILES[z], self.maps[z]))
        self.chan.basic_ack(msg.delivery_tag)
        if layerTimes:
            self.dequeueStrategy.recordRender(z, time.time() - start_time)
            stats.recordRender(z, time.time() - start_time, layerTimes)

    # There's got to be a better way to do this...
    def processCommands(self):
        msg = self.chan.basic_get(self.commandQueue, no_ack=True)
        while msg:
            parts = msg.body.split()
            if parts[0] == 'quit' or parts[0] == 'exit':
                self.printMessage('Exiting')
                self.keepRendering = False
            elif parts[0] == 'dequeue':
                try:
                    self.dequeueStrategy = getattr(globals()['dequeue'], parts[1])(self.threadNumber, self.maxz, self.chan)
                    self.printMessage('New dequeue strategy: ' + parts[1])
                except AttributeError:
                    self.printMessage('Unknown dequeue strategy: ' + parts[1])
                    self.dequeueStrategy = dequeue.DequeueByPctStrategy(self.threadNumber, self.maxz, self.chan)
            elif parts[0] == 'newmaps':
                self.loadMaps()
            elif parts[0] == 'reload':
                reload(globals()[parts[1]])
            else:
                self.printMessage('Unknown command: ' + msg.body)
            msg = self.chan.basic_get(self.commandQueue, no_ack=True)

    def renderLoop(self):
        while self.keepRendering:
            msg = self.chan.basic_get('toposm_missing')
            if not msg:
                msg = self.chan.basic_get('toposm_important')
            if not msg:
                msg = self.dequeueStrategy.getMessage()
            if msg:
                self.renderMetaTileFromMsg(msg)
            else:
                time.sleep(30)
            self.processCommands()


def isOldTile(z, x, y):
    tile_path = getTilePath(REFERENCE_TILESET, z, x, y)
    return path.isfile(tile_path) and path.getmtime(tile_path) < REFERENCE_MTIME

def tileNeedsRendering(z, x, y):
    return not tileExists(REFERENCE_TILESET, z, x, y) or isOldTile(z, x, y)

def isOldMetaTile(z, x, y):
    ntiles = NTILES[z]
    tile_path = getTilePath(REFERENCE_TILESET, z, x*ntiles, y*ntiles)
    return path.isfile(tile_path) and path.getmtime(tile_path) < REFERENCE_MTIME

def metaTileNeedsRendering(z, x, y):
    ntiles = NTILES[z]
    return not tileExists(REFERENCE_TILESET, z, x*ntiles, y*ntiles) or isOldMetaTile(z, x, y)


if __name__ == "__main__":
    maxz = int(sys.argv[1])
    if len(sys.argv) > 2:
        dequeueStrategy = getattr(globals()['dequeue'], sys.argv[2])
    else:
        dequeueStrategy = dequeue.DequeueByPctStrategy

    conn = amqp.Connection(host=DB_HOST, userid="guest", password="guest")
    chan = conn.channel()
    chan.exchange_declare(exchange="osm", type="direct", durable=True, auto_delete=False)
    chan.queue_declare(queue='toposm_important', durable=True, exclusive=False, auto_delete=False)
    chan.queue_bind(queue='toposm_important', exchange='osm', routing_key='toposm.render.important')
    chan.queue_declare(queue='toposm_missing', durable=True, exclusive=False, auto_delete=False)
    chan.queue_bind(queue='toposm_missing', exchange='osm', routing_key='toposm.render.missing')
    for z in range(0, maxz + 1):
        chan.queue_declare(queue='toposm_z{0}'.format(z), durable=True,
                           exclusive=False, auto_delete=False)
        chan.queue_bind(queue='toposm_z{0}'.format(z), exchange='osm',
                        routing_key='toposm.render.{0}'.format(z))
    chan.close()
    conn.close()

    renderers = {}
    for i in range(NUM_THREADS):
        rconn = amqp.Connection(host=DB_HOST, userid="guest", password="guest")
        rchan = rconn.channel()
        renderer = ContinuousRenderThread(dequeueStrategy, maxz, rchan, i)
        render_thread = threading.Thread(target=renderer.renderLoop)
        render_thread.start()
        renderers[i] = (render_thread, rconn, rchan)
    for thread, conn, chan in renderers.values():
        thread.join()
        rchan.close()
        rconn.close()
