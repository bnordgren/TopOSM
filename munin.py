#!/usr/bin/python

import sys, os, os.path, pickle
import lockfile

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
