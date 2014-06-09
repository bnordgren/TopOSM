#!/usr/bin/python

import json
import math
import time
import uuid

import pika

from toposm import *

def isint(s):
    try:
        dummy = int(s)
        return True
    except ValueError:
        return False

def queue_sort(a, b):
    try:
        return cmp(int(a), int(b))
    except ValueError:
        return cmp(a, b)

def print_stats(s):
    print 'expire queue: %s' % s['expire']['input']
    if s['expire']['status']:
        print 'currently expiring at zoom %s, %s tiles' % (s['expire']['status'][0], s['expire']['status'][1])
    if 'init' in s:
        print 'currently initializing at zoom %s' % s['init']
    print ''
    for renderer, status in s['render'].items():
        print '%s: %s' % (renderer, status)
    print ''
    weighted_queues = {}
    fixed_pct_queues = {}
    q_width = 1
    for k, v in s['queue'].items():
        if v > 0:
            w = int(math.ceil(math.log(v, 10)))
            if w > q_width:
                q_width = w
        if isint(k):
            z = int(k)
            if v > 0:
                fixed_pct_queues[k] = 2**z
            else:
                fixed_pct_queues[k] = 0
            weighted_queues[k] = v * pow(4, z) / pow(NTILES[z], 2)
    total_w = sum(weighted_queues.values())
    total_fp = sum(fixed_pct_queues.values())
    print 'queue  count  by_work  by_zoom'
    print '-----  -----  -------  -------'
    for k in sorted(s['queue'].keys(), queue_sort):
        count = s['queue'][k]
        if k in weighted_queues:
            count_w = weighted_queues[k]
            count_fp = fixed_pct_queues[k]
            print '{0:>5}: {1:>5}  {2:7.2%}  {3:7.3%}'.format(k, str(count).rjust(q_width),
                                                              float(count_w) / float(total_w),
                                                              float(count_fp) / float(total_fp))
        else:
            print '{0:>5}: {1:>5}'.format(k[0:4], str(count).rjust(q_width))

def request_stats(chan, queue):
    correlation_id = str(uuid.uuid4())
    chan.basic_publish(
        exchange='osm',
        routing_key='toposm.queuemaster',
        properties=pika.BasicProperties(reply_to=queue,
                                        correlation_id=correlation_id),
        body=json.dumps({'command': 'stats'}))
    return correlation_id
    
conn = pika.BlockingConnection(pika.ConnectionParameters(host=DB_HOST))
chan = conn.channel()
queue = chan.queue_declare(exclusive=True).method.queue
chan.queue_bind(queue=queue, exchange='osm', routing_key='command')
chan.queue_bind(queue=queue, exchange='osm', routing_key='command.toposm')

time_sent = time.time()
correlation_id = request_stats(chan, queue)

result_received = False
while not result_received:
    (method, props, body) = chan.basic_get(queue=queue, no_ack=True)
    if method:
        message = json.loads(body)
        if 'command' in message and message['command'] == 'queuemaster online':
            correlation_id = request_stats(chan, queue)
        elif props.correlation_id == correlation_id:
            print '%0.2f seconds to receive message' % (time.time() - time_sent)
            print ''
            print_stats(message)
            result_received = True
