#!/usr/bin/python

import argparse

from env import *

from amqplib import client_0_8 as amqp

parser = argparse.ArgumentParser(description='Dumps contents of a AMQP queue to stdout.')
parser.add_argument('-q', '--queue', default='expire_toposm',
                    help='The queue to dump.  Defaults to the TopOSM expire queue.')
args = parser.parse_args()

conn = amqp.Connection(host=DB_HOST, userid="guest", password="guest")
chan = conn.channel()
chan.exchange_declare(exchange="osm", type="direct", durable=True, auto_delete=False)
chan.queue_declare(queue=args.queue, durable=True, exclusive=False, auto_delete=False)
chan.queue_bind(queue=args.queue, exchange="osm", routing_key="expire")

msg = chan.basic_get(args.queue)
while msg:
    print msg.body
    chan.basic_ack(msg.delivery_tag)
    msg = chan.basic_get(args.queue)
