#!/usr/bin/python

import sys, os
import argparse
from os import path

from amqplib import client_0_8 as amqp

from toposm import *
from tileexpire import OSMTileExpire

REFERENCE_FILE = '/srv/tiles/tirex/planet-import-complete'
REFERENCE_MTIME = path.getmtime(REFERENCE_FILE)


def read_tile_file(f, e):
    for line in f:
        z, x, y = line.split('/')
        e.expire(int(z), int(x), int(y))

def read_tiles(args):
    expired = OSMTileExpire()
    if len(args.file) == 0:
        read_tile_file(sys.stdin, expired)
    else:
        for filename in args.file:
            with open(filename, 'r') as f:
                read_tile_file(f, expired)
    return expired

def expire_tile(z, x, y, args):
    tile_path = getTilePath('composite_h', z, x, y)
    if not path.isfile(tile_path):
        if args.force_render:
            queue_tile_render(z, x, y)
        return
    
def queue_for_render(z, mx, my, chan):
    ntiles = NTILES[z]
    for x in xrange(mx*ntiles, (mx+1)*ntiles):
        for y in xrange(my*ntiles, (my+1)*ntiles):
            tile_path = getTilePath('composite_h', z, x, y)
            if path.isfile(tile_path):
                os.utime(tile_path, (0, 0))
    render_payload = '{0}/{1}/{2}'.format(z, mx, my)
    console.printMessage('queueing for render: ' + render_payload)
    chan.basic_publish(amqp.Message(render_payload, delivery_mode=2),
                       exchange="osm", routing_key='toposm.render.{0}'.format(z))

def is_old_tile(a, x, y):
    tile_path = getTilePath('composite_h', z, x, y)
    return path.isfile(tile_path) and path.getmtime(tile_path) > REFERENCE_MTIME

def queue_tile_if_needed(z, x, y, chan, args):
    if not is_old_tile(z, x, y) and not args.force_render:
        return
    ntiles = NTILES[z]
    queue_for_render(z, x/ntiles, y/ntiles, chan)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Processes a tile expiration list and queues existing tiles for rerendering.')
    parser.add_argument('-f', '--force-render', action='store_true',
                        help='Forces rendering of supplied tiles, even if they don\'t exist in the filesystem.')
    parser.add_argument('--min-zoom', type=int, default=2,
                        help='The lowest zoom level to expire.')
    parser.add_argument('--max-zoom', type=int, default=16,
                        help='The highest zoom level to expire.')
    parser.add_argument('file', nargs='*',
                        help='The file(s) from which to read the expire list.  If no files are given, standard input is used.')
    args = parser.parse_args()

    conn = amqp.Connection(host=DB_HOST, userid="guest", password="guest")
    chan = conn.channel()
    chan.exchange_declare(exchange="osm", type="direct", durable=True, auto_delete=False)

    expired = read_tiles(args)
    for z in xrange(args.min_zoom, args.max_zoom+1):
        for (x, y) in expired.expiredAt(z):
            queue_tile_if_needed(z, x, y, chan, args)
