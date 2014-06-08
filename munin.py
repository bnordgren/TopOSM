#!/usr/bin/python

import json
import lockfile
import math
import os
import os.path
import pickle
import sys
import time
import uuid

import pika

dir = os.environ.get('toposm_dir', '.')
with open(os.path.join(dir, 'stats'), 'r') as f:
    stats = pickle.load(f)

if len(sys.argv) > 1 and sys.argv[1] == 'config':
    print 'multigraph toposm_throughput'
    print 'graph_title TopOSM Rendering Throughput'
    print 'graph_args --base 1000 -l 0'
    print 'graph_vlabel metatiles per ${graph_period}'
    print 'graph_category toposm'
    first = True
    for z in sorted(stats):
        field = 'z{0}'.format(z)
        print '{0}.label z{1}'.format(field, z)
        print '{0}.type DERIVE'.format(field)
        print '{0}.min 0'.format(field)
        print '{0}.draw {1}'.format(field, 'AREA' if first else 'STACK')
        first = False
else:
    print 'multigraph toposm_throughput'
    for z in stats:
        print 'z{0}.value {1}'.format(z, stats[z]['total'][0])


def request_stats(chan, queue, correlation_id):
    chan.basic_publish(
        exchange='osm',
        routing_key='toposm.queuemaster',
        properties=pika.BasicProperties(reply_to=queue,
                                        correlation_id=correlation_id),
        body=json.dumps({'command': 'stats'}))

def queue_sort(a, b):
    try:
        return cmp(int(a), int(b))
    except ValueError:
        return cmp(a, b)

conn = pika.BlockingConnection(pika.ConnectionParameters())
chan = conn.channel()
queue = chan.queue_declare(exclusive=True).method.queue
chan.queue_bind(queue=queue, exchange='osm', routing_key='command')
chan.queue_bind(queue=queue, exchange='osm', routing_key='command.toposm')

correlation_id = str(uuid.uuid4())
time_sent = time.time()
request_stats(chan, queue, correlation_id)

result_received = False
while not result_received:
    (method, props, body) = chan.basic_get(queue=queue, no_ack=True)
    if method:
        message = json.loads(body)
        if 'command' in message and message['command'] == 'queuemaster online':
            request_stats(chan, queue, correlation_id)
        elif props.correlation_id == correlation_id:
            result_received = True
            if len(sys.argv) > 1 and sys.argv[1] == 'config':
                print 'multigraph toposm_queues'
                print 'graph_title TopOSM Queue Lengths'
                print 'graph_args --base 1000 -l 0'
                print 'graph_vlabel metatiles'
                print 'graph_category toposm'
                for q in sorted(message['queue'].keys(), queue_sort):
                    field = 'q{0}'.format(q)
                    print '{0}.label {1}'.format(field, q)
            else:
                print 'multigraph toposm_queues'
                for q, v in message['queue'].items():
                    field = 'q{0}'.format(q)
                    try:
                        if 'init' in message and message['init'] <= int(q):
                            print '{0}.value U'.format(field)
                        else:
                            print '{0}.value {1}'.format(field, v)
                    except ValueError:
                        print '{0}.value {1}'.format(field, v)
