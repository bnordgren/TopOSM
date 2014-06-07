#!/usr/bin/python

import lockfile
import os.path
import pickle

class StatsManager:
    lock = lockfile.FileLock('stats')
    def __init__(self):
        with self.lock:
            if not os.path.isfile('stats'):
                with open('stats', 'w') as f:
                    pickle.dump({}, f)

    def recordRender(self, zoom, totalTime, layerTimes):
        with self.lock:
            with open('stats', 'r') as f:
                stats = pickle.load(f)
            (c, t) = stats.setdefault(zoom, {}).setdefault('total', (0, 0))
            stats[zoom]['total'] = (c + 1, t + totalTime)
            for layer in layerTimes:
                (c, t) = stats[zoom].setdefault(layer, (0, 0))
                stats[zoom][layer] = (c + 1, t + layerTimes[layer])
            with open('stats', 'w') as f:
                pickle.dump(stats, f)

stats = StatsManager()
