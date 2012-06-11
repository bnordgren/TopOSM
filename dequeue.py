from env import *
from common import *
from renderd import *


class DequeueByPctStrategy:
    def __init__(self, thread_number, amqp_channel):
        self.thread_number = thread_number
        self.chan = amqp_channel
        self.render_count = [ 0 for z in range(0, MAXZ + 1) ]
        self.render_time = [ 0 for z in range(0, MAXZ + 1) ]
        self.chan.basic_recover(requeue=True)

    def recordRender(self, zoom, time):
        self.render_count[zoom] += 1
        self.render_time[zoom] += time
        
    def getMessage(self):
        # Queues are weighted according to how many messages they have and the
        # likelihood of further updates invalidating the queue's tiles.  (At
        # zoom level 0, every update invalidates the tile.  At zoom 1, an update
        # has a one-in-four chance of invalidating the tile, and so on.  Thus,
        # the higher the zoom level, the more weight they're given, so low-zoom
        # tiles are not rendered as often as their queue length might otherwise
        # dictate.)
        # Rendering performance is based on how much time has been spent on each
        # queue.  We try to make the time-spent-rendering percentages match the
        # weighted queue percentages.
        weighted_queues = [ self.chan.queue_declare(queue='toposm_z{0}'.format(z), passive=True)[1] * pow(4, z) / pow(NTILES[z], 2) for z in range(0, MAXZ + 1) ]
        queue_pcts = [ float(t) / sum(weighted_queues) for t in weighted_queues ]
        render_sum = sum(self.render_time) if sum(self.render_time) > 0 else 1
        render_pcts = [ float(t) / render_sum for t in self.render_time ]
        # Seed choice with the last queue that has stuff in it.
        for z in range(0, MAXZ + 1):
            if weighted_queues[z] > 0:
                chosen_queue = z
                pct_diff = queue_pcts[z] - render_pcts[z]
        # See if there's a more-neglected queue.
        for z in range(0, chosen_queue):
            if queue_pcts[z] - render_pcts[z] > pct_diff:
                chosen_queue = z
                pct_diff = queue_pcts[z] - render_pcts[z]
        console.printMessage('q%: ' + ' '.join([ '%.2f' % (n * 100) for n in queue_pcts ]))
        console.printMessage('r%: ' + ' '.join([ '%.2f' % (n * 100) for n in render_pcts ]))
        console.printMessage('c: ' + ' '.join([ '%d:%d' % (i, self.render_count[i]) for i in range(len(self.render_count)) ]))
        console.printMessage('t/c: ' + ' '.join([ '%d:%.1f' % (i, self.render_time[i] / self.render_count[i] if self.render_count[i] > 0 else 0) for i in range(len(self.render_time)) ]))
        # Now that we know which queue is most in need of rendering, do it.  If
        # it's empty (possible, since someone else could have taken the last
        # message while we were thinking), just try again.
        msg = self.chan.basic_get('toposm_z{0}'.format(chosen_queue))
        if msg:
            return msg
        else:
            return self.getMessage()

class DequeueByZoomStrategy:
    def __init__(self, thread_number, amqp_channel):
        self.thread_number = thread_number
        self.chan = amqp_channel

        self.render_count = [ 0 for z in range(0, MAXZ + 1) ]
        self.render_time = [ 0 for z in range(0, MAXZ + 1) ]

        self.z = MAXZ + 1
        self.msgs = []

        self.chan.basic_recover(requeue=True)
        self.nextZoom()

    def recordRender(self, zoom, time):
        self.render_count[zoom] += 1
        self.render_time[zoom] += time
        
    def getMessage(self):
        while len(self.msgs) == 0 and self.z > 0:
            self.nextZoom()

        console.printMessage('z: %d:%d' % (self.z, len(self.msgs)))
        console.printMessage('c: ' + ' '.join([ '%d:%d' % (i, self.render_count[i]) for i in range(len(self.render_count)) ]))
        console.printMessage('t/c: ' + ' '.join([ '%d:%.1f' % (i, self.render_time[i] / self.render_count[i] if self.render_count[i] > 0 else 0) for i in range(len(self.render_time)) ]))

        if len(self.msgs) > 0:
            return self.msgs.pop()
        else:
            return None
        
    def nextZoom(self):
        self.z -= 1
        if self.z == 0:
            self.z = MAXZ
        msg = self.chan.basic_get('toposm_z{0}'.format(self.z))
        while msg:
            self.msgs.append(msg)
            msg = self.chan.basic_get('toposm_z{0}'.format(self.z))
        self.msgs.reverse()
