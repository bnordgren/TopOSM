#!/usr/bin/python

import os
import sys
import time
import httplib
import json
import urllib2
import socket
import datetime
import StringIO

import cgi
import cgitb; cgitb.enable()

import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key

import pika

from toposm import *

CONTENT_TYPES = {'jpg': 'image/jpeg', 'png': 'image/png'}
LOW_BANDWIDTH_TILESET = ('jpeg90_h', 'jpg')
HIGH_BANDWIDTH_TILESET = ('composite_h', 'png')

LOCAL_BASE = 'elros.aperiodic.net/phil/tiles'

# Don't rerender tiles if their zoom level is lower than this.
RERENDER_MIN_ZOOM = 13

# Failsafe: don't wait more than an hour for a tile to render.
MISSING_TIMEOUT = 3600

# Three scenarios:
#  * Local request.  Assume it's for mapping purposes.  Wait a long time for
#    rerendering to complete, send high-bandwidth response.
#  * Remote non-mobile request.  Wait a short while for rerendering.  Upload new
#    tiles to AWS.  Redirect client to AWS with low-bandwidth tiles.
#  * Remote mobile request.  Assume speed is of utmost priority.  Request
#    rerendering but don't wait for it to complete.  Upload new tiles to AWS.
#    Redirect client to AWS with low-bandwidth tiles.
#
# In any case, wait indefinitely for missing tiles to render.
LOCAL_PREFIX = '192.168.12.'
if os.environ['REMOTE_ADDR'].startswith(LOCAL_PREFIX) or os.environ['REMOTE_ADDR'].startswith('127.'):
    # Local
    TILESET = HIGH_BANDWIDTH_TILESET
    RERENDER_TIMEOUT = 30
    AWS_UPLOAD = False
elif os.environ['HTTP_USER_AGENT'].startswith('OsmAnd'):
    # Mobile remote
    TILESET = LOW_BANDWIDTH_TILESET
    RERENDER_TIMEOUT = 0
    AWS_UPLOAD = True
else:
    # Non-mobile remote
    TILESET = LOW_BANDWIDTH_TILESET
    RERENDER_TIMEOUT = 2
    AWS_UPLOAD = True


def get_tile_url(ts, t):
    return '/{0}/{1}/{2}/{3}.{4}'.format(ts[0], t.z, t.x, t.y, ts[1])

def render_tile(t, timeout):
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=DB_HOST))
    chan = conn.channel()
    queue = chan.queue_declare(exclusive=True).method.queue
    chan.queue_bind(queue=queue, exchange='osm', routing_key='toposm.rendered.{0}.{1}.{2}'.format(t.z, t.metatile.x, t.metatile.y))
    chan.basic_publish(
        exchange='osm',
        routing_key='toposm.queuemaster',
        body=json.dumps({'command': 'render',
                         'tile': tile.tojson()}))
    start_time = time.time()
    while time.time() - start_time < timeout:
        (method, props, body) = chan.basic_get(queue=queue, no_ack=True)
        if method:
            return

def render_missing(t):
    sys.stderr.write("missing {0}\n".format(t))
    render_tile(t, MISSING_TIMEOUT)

def rerender(t):
    sys.stderr.write("rerender {0}\n".format(t))
    render_tile(t, RERENDER_TIMEOUT)

def upload_tile(t):
    if not AWS_UPLOAD:
        return
    sys.stderr.write("uploading {0}\n".format(t))
    s3 = S3Connection(AWS_ACCESS, AWS_SECRET)
    bucket = s3.get_bucket(AWS_BUCKET)
    k = Key(bucket)
    k.key = get_tile_url(TILESET, t)
    k.set_contents_from_filename(
        t.path(TILESET[0], TILESET[1]),
        reduced_redundancy=True, policy='public-read',
        headers={'Content-Type': CONTENT_TYPES[TILESET[1]]})

def upload(t):
    s3_connection = httplib.HTTPConnection(AWS_BUCKET)

    s3_connection.request('HEAD', get_tile_url(TILESET, t))
    r = s3_connection.getresponse()
    if r.status / 100 == 2:
        # Tile exists remotely.  See if it needs refreshing.
        mtime = time.mktime(time.gmtime(os.stat(t.path(TILESET[0], TILESET[1])).st_mtime))
        s3_time = time.mktime(time.strptime(r.getheader('last-modified'), '%a, %d %b %Y %H:%M:%S %Z'))
        if mtime <= s3_time:
            return
        upload_tile(t)
    elif r.status / 100 == 4:
        # Tile does not exist remotely.  Upload it without qualms.
        upload_tile(t)
    else:
        sys.stderr.write("{0} unknown status: {1} {2}".format(t, r.status, r.reason))
        print 'Status: 500 Internal Server Error'
        print 'Content-type: text/plain'
        print ''
        print 'Don\'t know how to handle status {0}: {1}'.format(r.status, r.reason)
        exit(1)


def redirect(t):
    if AWS_UPLOAD:
        print 'Location: http://{0}{1}'.format(AWS_BUCKET, get_tile_url(TILESET, t))
    else:
        print 'Location: http://{0}{1}'.format(LOCAL_BASE, get_tile_url(TILESET, t))
    print ''
    exit(0)

def print_tile_status(t):
    if not t.exists(TILESET[0], TILESET[1]):
        print 'Tile has never been rendered.'
        return
    if tile.is_old():
        print 'Tile is dirty.'
    else:
        print 'Tile is clean.'
    tstat = os.stat(tile.path(TILESET[0], TILESET[1]))
    mt = t.metatile
    print 'Metatile is {0}/{1}/{2}.'.format(mt.z, mt.x, mt.y)
    print 'Last rendered at {0} GMT.'.format(time.asctime(time.gmtime(tstat.st_mtime)))
    print 'Last accessed at {0} GMT.'.format(time.asctime(time.gmtime(tstat.st_atime)))


try:
    components = os.environ['PATH_INFO'].split('/')[-4:]
    if components[3] == 'status':
        command = components[-1]
        z, x, y = [ int(s) for s in components[:3] ]
        tile = Tile(z, x, y)
    else:
        command = 'fetch'
        z, x, y = [ int(s) for s in components[1:] ]
        tile = Tile(z, x, y)

    sys.stderr.write("request: {0} {1}\n".format(command, tile))

    if command == 'status':
        print 'Content-type: text/plain'
        print ''
        print_tile_status(tile)
        exit(0)

    if not tile.exists(TILESET[0], TILESET[1]):
        render_missing(tile)
    elif z >= RERENDER_MIN_ZOOM and tile.is_old():
        rerender(tile)

    upload(tile)
    redirect(tile)

except ValueError:
    print 'Status: 404 Not Found'
    print 'Content-type: text/plain'
    print ''
    print 'That doesn\'t look like a tile URL to me.'
