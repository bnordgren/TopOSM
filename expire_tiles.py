#!/usr/bin/python

import sys, os
import argparse
from os import path

from amqplib import client_0_8 as amqp

from toposm import *
from renderd import *
from tileexpire import OSMTileExpire


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

seen_payloads = set()
def queue_for_render(z, mx, my, chan, args):
    render_payload = '{0}/{1}/{2}'.format(z, mx, my)
    if render_payload in seen_payloads:
        return
    seen_payloads.add(render_payload)
    console.printMessage('queueing for render: ' + render_payload)
    ntiles = NTILES[z]
    for x in xrange(mx*ntiles, (mx+1)*ntiles):
        for y in xrange(my*ntiles, (my+1)*ntiles):
            tile_path = getTilePath('composite_h', z, x, y)
            if path.isfile(tile_path):
                os.utime(tile_path, (0, 0))
    if args.missing:
        key = 'toposm.render.missing'
    elif args.important:
        key = 'toposm.render.important'
    else:
        key = 'toposm.render.{0}'.format(z)
    chan.basic_publish(amqp.Message(render_payload, delivery_mode=2),
                       exchange="osm", routing_key=key)

def queue_tile_if_needed(z, x, y, chan, args):
    ntiles = NTILES[z]
    if tileExists(REFERENCE_TILESET, z, x, y):
        if args.render_queued or path.getmtime(getTilePath(REFERENCE_TILESET, z, x, y)) > REFERENCE_MTIME:
            queue_for_render(z, x/ntiles, y/ntiles, chan, args)
    elif args.render_missing:
        queue_for_render(z, x/ntiles, y/ntiles, chan, args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Processes a tile expiration list and queues existing tiles for rerendering.')
    parser.add_argument('-m', '--render-missing', action='store_true',
                        help='Queues tiles for rendering even if they don\'t exist in the filesystem')
    parser.add_argument('-q', '--render-queued', action='store_true',
                        help='Queues tiles even if it appears they\'ve already been queued.')
    parser.add_argument('--min-zoom', type=int, default=2,
                        help='The lowest zoom level to expire.')
    parser.add_argument('--max-zoom', type=int, default=16,
                        help='The highest zoom level to expire.')
    parser.add_argument('--important', action='store_true',
                        help='If set, puts all messages into the "important" queue instead of the usual -er-zoom-level queues.')
    parser.add_argument('--missing', action='store_true',
                        help='If set, puts all messages into the "missing" queue instead of the usual -er-zoom-level queues.')
    parser.add_argument('file', nargs='*',
                        help='The file(s) from which to read the expire list.  If no files are given, standard input is used.')
    args = parser.parse_args()

    conn = amqp.Connection(host=DB_HOST, userid="guest", password="guest")
    chan = conn.channel()
    chan.exchange_declare(exchange="osm", type="topic", durable=True, auto_delete=False)

    expired = read_tiles(args)
    for z in xrange(args.min_zoom, args.max_zoom+1):
        for (x, y) in expired.expiredAt(z):
            queue_tile_if_needed(z, x, y, chan, args)
