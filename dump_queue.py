#!/usr/bin/python

from env import *

from amqplib import client_0_8 as amqp

conn = amqp.Connection(host=DB_HOST, userid="guest", password="guest")
chan = conn.channel()
chan.exchange_declare(exchange="osm", type="direct", durable=True, auto_delete=False)
chan.queue_declare(queue="expire_toposm", durable=True, exclusive=False, auto_delete=False)
chan.queue_bind(queue="expire_toposm", exchange="osm", routing_key="expire")

msg = chan.basic_get("expire_toposm")
while msg:
    print msg.body
    chan.basic_ack(msg.delivery_tag)
    msg = chan.basic_get("expire_toposm")
