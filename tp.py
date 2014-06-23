#!/usr/bin/python

import os
import sys
import time
import httplib
import json
import urllib2
import uuid
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


def get_tile_url(ts, z, x, y):
    return '/{0}/{1}/{2}/{3}.{4}'.format(ts[0], z, x, y, ts[1])

def render_tile(z, x, y, timeout):
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=DB_HOST))
    chan = conn.channel()
    queue = chan.queue_declare(exclusive=True).method.queue
    correlation_id = str(uuid.uuid4())
    chan.basic_publish(
        exchange='osm',
        routing_key='toposm.queuemaster',
        properties=pika.BasicProperties(reply_to=queue,
                                        correlation_id=correlation_id),
        body=json.dumps({'command': 'render',
                         'tile': '{0}/{1}/{2}'.format(z, x, y)}))
    start_time = time.time()
    while time.time() - start_time < timeout:
        (method, props, body) = chan.basic_get(queue=queue, no_ack=True)
        if method and props.correlation_id == correlation_id:
            return

def render_missing(z, x, y):
    sys.stderr.write("missing {0}/{1}/{2}\n".format(z, x, y))
    render_tile(z, x, y, MISSING_TIMEOUT)

def rerender(z, x, y):
    sys.stderr.write("rerender {0}/{1}/{2}\n".format(z, x, y))
    render_tile(z, x, y, RERENDER_TIMEOUT)

def upload_tile(z, x, y):
    if not AWS_UPLOAD:
        return
    sys.stderr.write("uploading {0}/{1}/{2}\n".format(z, x, y))
    s3 = S3Connection(AWS_ACCESS, AWS_SECRET)
    bucket = s3.get_bucket(AWS_BUCKET)
    k = Key(bucket)
    k.key = get_tile_url(TILESET, z, x, y)
    k.set_contents_from_filename(
        getTilePath(TILESET[0], z, x, y, TILESET[1]),
        reduced_redundancy=True, policy='public-read',
        headers={'Content-Type': CONTENT_TYPES[TILESET[1]]})

def upload(z, x, y):
    s3_connection = httplib.HTTPConnection(AWS_BUCKET)

    s3_connection.request('HEAD', get_tile_url(TILESET, z, x, y))
    r = s3_connection.getresponse()
    if r.status / 100 == 2:
        # Tile exists remotely.  See if it needs refreshing.
        mtime = os.stat(getTilePath(TILESET[0], z, x, y, TILESET[1])).st_mtime
        s3_time = time.mktime(time.strptime(r.getheader('last-modified'), '%a, %d %b %Y %H:%M:%S %Z'))
        if mtime <= s3_time:
            return
        upload_tile(z, x, y)
    elif r.status / 100 == 4:
        # Tile does not exist remotely.  Upload it without qualms.
        upload_tile(z, x, y)
    else:
        sys.stderr.write("{0}/{1}/{2} unknown status: {3} {4}".format(z, x, y, r.status, r.reason))
        print 'Status: 500 Internal Server Error'
        print 'Content-type: text/plain'
        print ''
        print 'Don\'t know how to handle status {0}: {1}'.format(r.status, r.reason)
        exit(1)


def redirect(z, x, y):
    if AWS_UPLOAD:
        print 'Location: http://{0}{1}'.format(AWS_BUCKET, get_tile_url(TILESET, z, x, y))
    else:
        print 'Location: http://{0}{1}'.format(LOCAL_BASE, get_tile_url(TILESET, z, x, y))
    print ''
    exit(0)

try:
    z, x, y = [ int(s) for s in os.environ['PATH_INFO'].split('/')[-3:] ]

    sys.stderr.write("{0}/{1}/{2}: {3}\n".format(z, x, y, os.environ['HTTP_USER_AGENT']))

    if not tileExists(TILESET[0], z, x, y, TILESET[1]):
        render_missing(z, x, y)
    elif z >= RERENDER_MIN_ZOOM and tileIsOld(z, x, y):
        rerender(z, x, y)

    upload(z, x, y)
    redirect(z, x, y)

except ValueError:
    print 'Status: 404 Not Found'
    print 'Content-type: text/plain'
    print ''
    print 'That doesn\'t look like a tile URL to me.'
