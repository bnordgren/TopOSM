#!/usr/bin/python

"""toposm.py: Functions to control TopOSM rendering."""

import sys, os, time, threading
import numpy
import multiprocessing
import cairo
import xattr

from Queue import Queue
from os import path
from subprocess import call

# PyPdf is optional, but render-to-pdf won't work without it.
try:
    from pyPdf import PdfFileWriter, PdfFileReader
except ImportError:
    print "WARNING: PyPdf not found. Render to PDF will not work."

import mapnik
from mapnik import Coord, Box2d

from env import *
from coords import *
from common import *
import NED
import areas
from JobManager import JobManager

__author__      = "Lars Ahlzen and contributors"
__copyright__   = "(c) Lars Ahlzen and contributors 2008-2011"
__license__     = "GPLv2"


##### Initialize Mapnik

# Import extra fonts
if EXTRA_FONTS_DIR != '':
    mapnik.register_fonts(EXTRA_FONTS_DIR)

# Check for cairo support
if not mapnik.has_cairo():
    print "ERROR: Your mapnik does not have Cairo support."
    sys.exit(1)


##### Render settings

# Set to true to save intermediate layers that are normally
# merged. Primarily useful for debugging and style editing.
SAVE_INTERMEDIATE_TILES = False

# Enables/disables saving the composite layers
SAVE_PNG_COMPOSITE = True
SAVE_JPEG_COMPOSITE = True
JPEG_COMPOSITE_QUALITY = 90

# Enable/disable the use of the cairo renderer altogether
USE_CAIRO = False

class RenderThread:
    def __init__(self, q, maxz, threadNumber):
        self.q = q
        self.maxz = maxz
        self.threadNumber = threadNumber
        self.currentz = 0
        
    def init_zoomlevel(self, z):
        self.currentz = z
        self.tilesize = getTileSize(NTILES[z], True)
        self.maps = {}
        for mapName in MAPNIK_LAYERS:
            console.debugMessage('Loading mapnik.Map: ' + mapName)
            self.maps[mapName] = mapnik.Map(self.tilesize, self.tilesize)
            mapnik.load_map(self.maps[mapName], mapName + ".xml")
    def runAndLog(self, message, function, args):
        message = '[%02d] %s' % (self.threadNumber+1,  message)
        console.printMessage(message)
        try:
            function(*args)        
        except Exception as ex:
            console.printMessage('Failed: ' + message)
            errorLog.log('Failed: ' + message, ex)
            raise

    def renderMetaTile(self, z, x, y):
        ntiles = NTILES[z]
        if (z != self.currentz):
            self.init_zoomlevel(z)
        if not (allConstituentTilesExist(z, x, y, ntiles)):
            msg = "Rendering meta tile %s %s %s (%sx%s)" % \
                (z, x, y, ntiles, ntiles)
            self.runAndLog(msg, renderMetaTile, (z, x, y, ntiles, self.maps))

    def renderLoop(self):
        self.currentz = 0
        while True:
            r = self.q.get()
            if (r == None):
                self.q.task_done()
                break
            self.renderMetaTile(*r)
            self.q.task_done()



class Tile:
    """Represents a single tile (or metatile)."""

    def __init__(self, z, x, y, is_metatile=False):
        self.z = z
        self.x = x
        self.y = y
        self.is_metatile = is_metatile

    @classmethod
    def fromstring(cls, str, is_metatile=False):
        """Creates a Tile instance from a string of the form z/x/y."""
        z, x, y = [ int(s) for s in str.split('/') ]
        return cls(z, x, y, is_metatile)

    @classmethod
    def fromjson(cls, o, ignored=False):
        """Takes a dict generated by Tile.tojson() and creates a new object
        instance from it."""
        return cls(o['z'], o['x'], o['y'], o['is_metatile'])

    def tojson(self):
        """Gives a dictionary representation of this object suitable for passing
        to json.dumps().  Tile.fromjson() is the inverse of this method."""
        return {'z': self.z, 'x': self.x, 'y': self.y, 'is_metatile': self.is_metatile}

    def __repr__(self):
        return 'Tile({0}, {1}, {2}, {3})'.format(self.z, self.x, self.y, self.is_metatile)

    def __str__(self):
        if self.is_metatile:
            return 'mt:{0}/{1}/{2}'.format(self.z, self.x, self.y)
        else:
            return '{0}/{1}/{2}'.format(self.z, self.x, self.y)

    def __cmp__(self, other):
        if not isinstance(other, Tile):
            return cmp(id(self), other)
        else:
            return cmp(self.is_metatile, other.is_metatile) or cmp(self.sort_key, other.sort_key)

    def __hash__(self):
        return hash(self.is_metatile) | hash(self.z) | hash(self.x) | hash(self.y)

    @property
    def metatile(self):
        """Returns the metatile for this tile."""
        if self.is_metatile:
            return self
        else:
            return Tile(self.z, self.x / NTILES[self.z], self.y / NTILES[self.z], True)

    @property
    def sort_key(self):
        return (self.z, self.x, self.y)

    @property
    def keytile(self):
        if self.is_metatile:
            return Tile(self.z, self.x * NTILES[self.z], self.y * NTILES[self.z], False)
        else:
            return self

    def path(self, tileset, suffix='png'):
        if self.is_metatile:
            return getMetaTilePath(tileset, self.z, self.x, self.y, suffix)
        else:
            return getTilePath(tileset, self.z, self.x, self.y, suffix)

    def exists(self, tileset, suffix='png'):
        if self.is_metatile:
            return self.keytile.exists(tileset, suffix)
        else:
            return tileExists(tileset, self.z, self.x, self.y, suffix)

    def is_old(self):
        if self.is_metatile:
            return self.keytile.is_old()
        else:
            return tileIsOld(self.z, self.x, self.y)

    @property
    def is_valid(self):
        if self.is_metatile:
            return 0 <= self.x and self.x < 2**self.z / NTILES[self.z] and \
                   0 <= self.y and self.y < 2**self.z / NTILES[self.z]
        else:
            return 0 <= self.x and self.x < 2**self.z and \
                   0 <= self.y and self.y < 2**self.z


def getCachedMetaTileDir(mapname, z, x):
    return path.join(TEMPDIR, mapname, str(z), str(x))

def getCachedMetaTilePath(mapname, z, x, y, suffix = "png"):
    return path.join(getCachedMetaTileDir(mapname, z, x), str(y) + '.' + suffix)

def cachedMetaTileExists(mapname, z, x, y, suffix = "png"):
    return path.isfile(getCachedMetaTilePath(mapname, z, x, y, suffix))

def getMetaTileDir(mapname, z):
    return path.join(BASE_TILE_DIR, mapname, str(z))

def getMetaTilePath(mapname, z, x, y, suffix = "png"):
    return path.join(getMetaTileDir(mapname, z), \
        's' + str(x) + '_' + str(y) + '.' + suffix)

def metaTileExists(mapname, z, x, y, suffix = "png"):
    return path.isfile(getMetaTilePath(mapname, z, x, y, suffix))

def getTileDir(mapname, z, x):
    return path.join(getMetaTileDir(mapname, z), str(x))

def getTilePath(mapname, z, x, y, suffix = "png"):
    return path.join(getTileDir(mapname, z, x), str(y) + '.' + suffix)

def tileExists(mapname, z, x, y, suffix = "png"):
    return path.isfile(getTilePath(mapname, z, x, y, suffix))

def tileIsOld(z, x, y):
    return 'user.toposm_dirty' in xattr.listxattr(getTilePath(REFERENCE_TILESET, z, x, y))

def getTileSize(ntiles, includeBorder = True):
    if includeBorder:
        return TILE_SIZE * ntiles + 2 * BORDER_WIDTH
    else:
        return TILE_SIZE * ntiles
        
def allTilesExist(mapname, z, fromx, tox, fromy, toy, suffix = "png"):
    for x in range(fromx, tox+1):
        for y in range(fromy, toy+1):
            if not tileExists(mapname, z, x, y, suffix):
                return False
    return True
            
def allConstituentTilesExist(z, x, y, ntiles):
    fromx = x*ntiles
    tox = (x+1)*ntiles - 1
    fromy = y*ntiles
    toy = (y+1)*ntiles - 1
    # NOTE: This only checks for the final "composite" tile set(s)...
    if SAVE_PNG_COMPOSITE:
        chExists = allTilesExist('composite_h', z, fromx, tox, fromy, toy, 'png')
        clExists = allTilesExist('composite_l', z, fromx, tox, fromy, toy, 'png')
        if (not chExists) or (not clExists):
            return False
    if SAVE_JPEG_COMPOSITE:
        jhExists = allTilesExist('jpeg90_h', z, fromx, tox, fromy, toy, 'jpg')
        jlExists = allTilesExist('jpeg90_l', z, fromx, tox, fromy, toy, 'jpg')
        if (not jhExists) or (not jlExists):
            return False
    return True

def renderMetaTile(z, x, y, ntiles, maps):
    """Renders the specified map tile and saves the result (including the
    composite) as individual tiles."""
    images = {}
    layerTimes = {}
    for layer in MAPNIK_LAYERS:
        startTime = time.time()
        images[layer] = renderMetatileLayer(layer, z, x, y, ntiles, maps[layer])
        layerTimes[layer] = time.time() - startTime
    composite_h = combineLayers(images)
    console.debugMessage(' Saving tiles')
    if SAVE_PNG_COMPOSITE:
        saveTiles(z, x, y, ntiles, 'composite_h', composite_h)
    if SAVE_JPEG_COMPOSITE:
        basename = 'jpeg' + str(JPEG_COMPOSITE_QUALITY)
        saveTiles(z, x, y, ntiles, basename+'_h', composite_h, 'jpg', basename)
    if SAVE_INTERMEDIATE_TILES:
        for layer in MAPNIK_LAYERS:
            saveTiles(z, x, y, ntiles, layer, images[layer])
    return layerTimes

def combineLayers(images):
    console.debugMessage(' Combining layers')
    #images['contour-mask'].set_grayscale_to_alpha()
    #images['features_mask'].set_grayscale_to_alpha()
    return getComposite((
        images['hypsorelief'],
        images['areas'],
        images['ocean'],
        images['contours'],
        images['features']))
        #getMask(images['contours'], images['contour-mask']),
        #images['contour-labels'],
        #getMask(images['features_outlines'], images['features_mask']),
        #images['features_fills'],
        #getMask(images['features_top'], images['features_mask']),
        #images['features_labels']))

def renderMetatileLayer(name, z, x, y, ntiles, map):
    """Renders the specified map tile (layer) as a mapnik.Image."""
    if name in CACHE_LAYERS and cachedMetaTileExists(name, z, x, y, 'png'):
        console.debugMessage(' Using cached:    ' + name)
        return mapnik.Image.open(getCachedMetaTilePath(name, z, x, y, 'png'))
    console.debugMessage(' Rendering layer: ' + name)
    env = getOutputTileEnv(z, x, y, ntiles, True)
    tilesize = getTileSize(ntiles, True)
    image = renderLayerProjected(name, env, tilesize, tilesize, map)
    if name in CACHE_LAYERS:
        ensureDirExists(getCachedMetaTileDir(name, z, x))
        image.save(getCachedMetaTilePath(name, z, x, y, 'png'))
    return image

def renderLayerProjected(name, env, xsize, ysize, map):
    """Renders the specified layer to an image.  ENV must be in the 
    output map projection"""
    map.zoom_to_box(env)
    if USE_CAIRO and name in CAIRO_LAYERS:
        assert mapnik.has_cairo()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, xsize, ysize)
        mapnik.render(map, surface)
        image = mapnik.Image.from_cairo(surface)
    else:            
        image = mapnik.Image(xsize, ysize)
        mapnik.render(map, image)
    return image

def renderLayerLL(name, env, xsize, ysize, map):
    return renderLayerProjected(name, LLToOutput(env), xsize, ysize, map)

def saveTiles(z, x, y, ntiles, mapname, image, suffix = 'png', imgtype = None):
    """Saves the individual tiles from a metatile image."""
    for dx in range(0, ntiles):
        tilex = x*ntiles + dx
        ensureDirExists(getTileDir(mapname, z, tilex))
        for dy in range(0, ntiles):    
            tiley = y*ntiles + dy
            offsetx = BORDER_WIDTH + dx*TILE_SIZE
            offsety = BORDER_WIDTH + dy*TILE_SIZE
            view = image.view(offsetx, offsety, TILE_SIZE, TILE_SIZE)
            tile_path = getTilePath(mapname, z, tilex, tiley, suffix)
            if imgtype:
                view.save(tile_path, imgtype)
            else:
                view.save(tile_path)
            if 'user.toposm_dirty' in xattr.listxattr(tile_path):
                try:
                    xattr.removexattr(tile_path, 'user.toposm_dirty')
                except IOError:
                    # Ignore the failure.  It means the attribute disappeared on
                    # its own.
                    pass


def getComposite(images):
    """Composites (stacks) the specified images, in the given order."""
    composite = mapnik.Image(images[0].width(), images[0].height())
    for image in images:
        composite.composite(image, mapnik.CompositeOp.src_over)
    return composite

def getMask(image, mask):
    """Returns only the parts of IMAGE that are allowed by MASK."""
    result = mapnik.Image(image.width(), image.height())
    result.composite(image)
    result.composite(mask, mapnik.CompositeOp.dst_in)
    return result

    
##### Public methods

def toposmInfo():
    print "Using mapnik version:", mapnik.mapnik_version()
    print "Has Cairo:", mapnik.has_cairo()
    print "Fonts:"
    for face in mapnik.FontEngine.face_names():
        print "\t", face

def prepareData(envLLs):
    if not hasattr(envLLs, '__iter__'):
        envLLs = (envLLs,)
    manager = JobManager()
    for envLL in envLLs:
        tiles = NED.getTiles(envLL)        
        for tile in tiles:
            manager.addJob("Preparing %s" % (tile[0]), NED.prepDataFile, tile)
    manager.finish()
    
    console.printMessage("Postprocessing contours...")
    NED.removeSeaLevelContours()
    NED.simplifyContours(1.0)
    NED.convertContourElevationsToFt()
    NED.clusterContoursOnGeoColumn()
    NED.analyzeContoursTable()

def renderTiles(envLLs, minz, maxz):
    if not hasattr(envLLs, '__iter__'):
        envLLs = (envLLs,)
    queue = Queue(32)
    renderers = {}
    for i in range(NUM_THREADS):
        renderer = RenderThread(queue, maxz, i)
        renderThread = threading.Thread(target=renderer.renderLoop)
        renderThread.start()
        renderers[i] = renderThread
    for envLL in envLLs:
        for z in range(minz, maxz+1):
            ntiles = NTILES[z]
            (fromx, tox, fromy, toy) = getTileRange(envLL, z, ntiles)
            for x in range(fromx, tox+1):
                for y in range(fromy, toy+1):
                    queue.put((z, x, y))
    for i in range(NUM_THREADS):
        queue.put(None)
    queue.join()
    for i in range(NUM_THREADS):
        renderers[i].join()       


def renderToPdf(envLL, filename, sizex, sizey):
    """Renders the specified Box2d and zoom level as a PDF"""
    basefilename = os.path.splitext(filename)[0]
    mergedpdf = None
    for mapname in MAPNIK_LAYERS:
        print 'Rendering', mapname
        # Render layer PDF.
        localfilename = basefilename + '_' + mapname + '.pdf';
        file = open(localfilename, 'wb')
        surface = cairo.PDFSurface(file.name, sizex, sizey) 
        envOutput = LLToOutput(envLL)
        map = mapnik.Map(sizex, sizey)
        mapnik.load_map(map, mapname + ".xml")
        map.zoom_to_box(envOutput)
        mapnik.render(map, surface)
        surface.finish()
        file.close()
        # Merge with master.
        if not mergedpdf:            
            mergedpdf = PdfFileWriter()
            localpdf = PdfFileReader(open(localfilename, "rb"))
            page = localpdf.getPage(0)
            mergedpdf.addPage(page)
        else:
            localpdf = PdfFileReader(open(localfilename, "rb"))
            page.mergePage(localpdf.getPage(0))
    output = open(filename, 'wb')
    mergedpdf.write(output)
    output.close()

class RenderPngThread(threading.Thread):
    def __init__(self, mapname, envLL, sizex, sizey, images, imagesLock):
        threading.Thread.__init__(self)
        self.mapname = mapname
        self.envLL = envLL
        self.sizex = sizex
        self.sizey = sizey
        self.images = images
        self.imagesLock = imagesLock
        
    def run(self):
        map = mapnik.Map(self.sizex, self.sizey)
        mapnik.load_map(map, self.mapname + ".xml")
        result = renderLayerLL(self.mapname, self.envLL, self.sizex, self.sizey, map)
        console.debugMessage(' Rendered layer: ' + self.mapname)
        self.imagesLock.acquire()
        self.images[self.mapname] = result
        self.imagesLock.release()
        
def renderToPng(envLL, filename, sizex, sizey):
    """Renders the specified Box2d as a PNG"""
    images = {}
    imageLock = threading.Lock()
    threads = []
    console.debugMessage(' Rendering layers')
    for mapname in MAPNIK_LAYERS:
        threads.append(RenderPngThread(mapname, envLL, sizex, sizey, images, imageLock))
        threads[-1].start()
    for thread in threads:
        thread.join()
    image = combineLayers(images)
    image.save(filename, 'png')

def printSyntax():
    print "Syntax:"
    print " toposm.py render <area(s)> <minZoom> <maxZoom>"
    print " toposm.py pdf <area> <filename> <sizeX> <sizeY>"
    print " toposm.py png <area> <filename> <sizeX> <sizeY>"
    print " toposm.py prep <area(s)>"
    print " toposm.py info"
    print "Areas are named entities in areas.py."

if __name__ == "__main__":
    if len(sys.argv) == 1:
        printSyntax()
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'render':
        areaname = sys.argv[2]
        minzoom = int(sys.argv[3])
        maxzoom = int(sys.argv[4])
        env = vars(areas)[areaname]            
        print "Render: %s %s, z: %d-%d" % (areaname, env, minzoom, maxzoom)
        BASE_TILE_DIR = path.join(BASE_TILE_DIR, areaname)
        renderTiles(env, minzoom, maxzoom)
    elif cmd == 'pdf' or cmd == 'png':
        areaname = sys.argv[2]
        filename = sys.argv[3]
        sizex = int(sys.argv[4])
        sizey = int(sys.argv[5])
        env = vars(areas)[areaname]
        if cmd == 'pdf':
          renderToPdf(env, filename, sizex, sizey)
        elif cmd == 'png':
          renderToPng(env, filename, sizex, sizey)
    elif cmd == 'prep':
        areaname = sys.argv[2]
        env = vars(areas)[areaname]
        print "Prepare data: %s %s" % (areaname, env)
        prepareData(env)
    elif cmd == 'info':
        toposmInfo()
    else:
        printSyntax()
        sys.exit(1)
