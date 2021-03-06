from env import *
from common import *
from renderd import *


class DequeueByPctStrategy:
    def __init__(self, thread_number, maxz, amqp_channel):
        self.thread_number = thread_number
        self.maxz = maxz
        self.chan = amqp_channel
        self.render_count = [ 0 for z in range(0, maxz + 1) ]
        self.render_time = [ 0 for z in range(0, maxz + 1) ]
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
        weighted_queues = [ self.chan.queue_declare(queue='toposm_z{0}'.format(z), passive=True)[1] * pow(4, z) / pow(NTILES[z], 2) for z in range(0, self.maxz + 1) ]
        if sum(weighted_queues) == 0:
            return None
        queue_pcts = [ float(t) / sum(weighted_queues) for t in weighted_queues ]
        render_sum = sum(self.render_time) if sum(self.render_time) > 0 else 1
        render_pcts = [ float(t) / render_sum for t in self.render_time ]
        # Seed choice with the last queue that has stuff in it.
        for z in range(0, self.maxz + 1):
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

class DequeueByFixedPctStrategy:
    """Basically like DequeueByPctStrategy, but the target percentages are
    derived from the total number of tiles at each zoom level, not the
    current queue lengths."""

    def __init__(self, thread_number, maxz, amqp_channel):
        self.thread_number = thread_number
        self.maxz = maxz
        self.chan = amqp_channel
        self.render_count = [ 0 for z in range(0, maxz + 1) ]
        self.render_time = [ 0 for z in range(0, maxz + 1) ]
        self.queue_pcts = [ 2**z / float(2**(maxz+1) - 1) for z in range(0, maxz + 1) ]
        self.chan.basic_recover(requeue=True)

    def recordRender(self, zoom, time):
        self.render_count[zoom] += 1
        self.render_time[zoom] += time
        
    def getMessage(self):
        queues = [ self.chan.queue_declare(queue='toposm_z{0}'.format(z), passive=True)[1] for z in range(0, self.maxz + 1) ]
        render_sum = sum([ c for z, c in enumerate(self.render_count) if queues[z] > 0 ])
        if render_sum == 0:
            render_sum = 1
        render_pcts = [ float(c) / render_sum for c in self.render_count ]
        # Seed choice with the last queue that has stuff in it.
        chosen_queue = -1
        for z in range(0, self.maxz + 1):
            if queues[z] > 0:
                chosen_queue = z
        if chosen_queue == -1:
            return None
        scale = 2**(self.maxz - chosen_queue)
        pct_diff = self.queue_pcts[chosen_queue] * scale - render_pcts[chosen_queue]
        # See if there's a more-neglected queue.
        for z in range(0, chosen_queue):
            if queues[z] > 0 and self.queue_pcts[z] * scale - render_pcts[z] > pct_diff:
                chosen_queue = z
                pct_diff = self.queue_pcts[z] * scale - render_pcts[z]
        console.printMessage('q%: ' + ' '.join([ '%.2f' % (n * scale * 100) for n in self.queue_pcts ]))
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
    def __init__(self, thread_number, maxz, amqp_channel):
        self.thread_number = thread_number
        self.maxz = maxz
        self.chan = amqp_channel

        self.render_count = [ 0 for z in range(0, maxz + 1) ]
        self.render_time = [ 0 for z in range(0, maxz + 1) ]

        self.z = maxz + 1
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
            self.z = self.maxz
        msg = self.chan.basic_get('toposm_z{0}'.format(self.z))
        while msg:
            self.msgs.append(msg)
            msg = self.chan.basic_get('toposm_z{0}'.format(self.z))
        self.msgs.reverse()

class DequeueShortestFirstStrategy:
    def __init__(self, thread_number, maxz, amqp_channel):
        self.thread_number = thread_number
        self.maxz = maxz
        self.chan = amqp_channel
        self.render_count = [ 0 for z in range(0, maxz + 1) ]
        self.render_time = [ 0 for z in range(0, maxz + 1) ]
        self.chan.basic_recover(requeue=True)

    def recordRender(self, zoom, time):
        self.render_count[zoom] += 1
        self.render_time[zoom] += time
        
    def getMessage(self):
        queue_lengths = [ self.chan.queue_declare(queue='toposm_z{0}'.format(z), passive=True)[1] for z in range(0, self.maxz + 1) ]
        # Seed choice with the last queue that has stuff in it.
        for z in range(0, self.maxz + 1):
            if queue_lengths[z] > 0:
                chosen_queue = z
                chosen_length = queue_lengths[z]
        for z in range(0, chosen_queue):
            if 0 < queue_lengths[z] and queue_lengths[z] < chosen_length:
                chosen_queue = z
                chosen_length = queue_lengths[z]
        console.printMessage('c: ' + ' '.join([ '%d:%d' % (i, self.render_count[i]) for i in range(len(self.render_count)) ]))
        console.printMessage('t/c: ' + ' '.join([ '%d:%.1f' % (i, self.render_time[i] / self.render_count[i] if self.render_count[i] > 0 else 0) for i in range(len(self.render_time)) ]))
        msg = self.chan.basic_get('toposm_z{0}'.format(chosen_queue))
        if msg:
            return msg
        else:
            return self.getMessage()
