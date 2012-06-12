#!/usr/bin/python

"""
OSMTileExpire, a class for managing tile expirations in a memory efficient
way.
"""

__author__      = "Phil! Gold <phil_g@pobox.com>"
__copyright__   = "waived; see license"
__license__     = "CC0: http://creativecommons.org/publicdomain/zero/1.0/"

# Mapping from hilbert subcurve to child subscripts in order of processing.
hilbert_order = {
    0: [0, 2, 3, 1],
    1: [3, 2, 0, 1],
    2: [3, 1, 0, 2],
    3: [0, 1, 3, 2]
}
# For each hilbert subcurve, gives the subcurve of the next level down for each
# child.  Order of next subcurve number matches child subscripts, so
# [ul, ur, ll, lr].
hilbert_next = {
    0: [3, 1, 0, 0],
    1: [1, 0, 1, 2],
    2: [2, 2, 3, 1],
    3: [0, 3, 2, 3]
}

class OSMTileExpire:

    """
    Manages tile expirations.

    To instantiate, simply create with no arguments:

        expiredTiles = OSMTileExpire()

    Use the expire() method to mark individual tiles as expired:

        expiredTiles.expire(15, 16384, 16384)
    
    Marking a given tile as expired will also mark every tile below it and
    every tile above it as expired, too.  Thus, the above code will also
    expire 14/8192/8192, 16/32768/32768, 16/32769/32768, 16/32768/32769,
    and 16/32769/32769, among others.

    To list all expired tiles at a given zoom level, use the expiredAt()
    method:

        for t in expiredTiles.expiredAt(13):
            # Do something here.
    """

    def __init__(self, myz=0, myx=0, myy=0):
        self.z = myz
        self.x = myx
        self.y = myy
        self.children = [None, None, None, None]
        self.full = False

    def expire(self, targetz, targetx, targety):
        """Mark the supplied tile as expired."""
        if targetz < self.z:
            return False
        elif self.full:
            return True
        elif targetz == self.z:
            self.markFull()
            return True
        xoff = (targetx >> (targetz - self.z - 1)) - (self.x << 1)
        yoff = (targety >> (targetz - self.z - 1)) - (self.y << 1)
        if xoff > 1 or 0 > xoff:
            raise Exception(
                'z:{0}, x:{1} out of bounds for tile z:{2}, x:{3}, y{4}'.format(
                    targetz, targetx, self.z, self.x, self.y))
        if yoff > 1 or 0 > yoff:
            raise Exception(
                'z:{0}, y:{1} out of bounds for tile z:{2}, x:{3}, y{4}'.format(
                    targetz, targety, self.z, self.x, self.y))
        i = 2*yoff + xoff
        if not self.children[i]:
            self.children[i] = OSMTileExpire(
                self.z + 1, self.x * 2 + xoff, self.y * 2 + yoff)
        child_full = self.children[i].expire(targetz, targetx, targety)
        if child_full and self.checkFull():
            self.markFull()
            return True
        return False

    def checkFull(self):
        return self.full or (all(self.children) and all([c.full for c in self.children]))
                
    def markFull(self):
        self.full = True
        self.children = [None, None, None, None]

    def expiredAt(self, targetz):
        """Yield (as a generator) all the expired tiles at the given zoom."""
        return self._expiredAt(targetz, 0)
    
    def _expiredAt(self, targetz, hilbert_curve):
        if targetz < self.z:
            raise Exception('zoom {0} is lower than this zoom, {1}'.format(targetz, self.z))
        elif targetz == self.z:
            yield (self.x, self.y)
        elif self.full:
            for t in enumeratePoints(self.x, self.y, targetz - self.z, hilbert_curve):
                yield t
        else:
            for hi in hilbert_order[hilbert_curve]:
                if self.children[hi]:
                    for t in self.children[hi]._expiredAt(targetz, hilbert_next[hilbert_curve][hi]):
                        yield t
        

def enumeratePoints(x, y, n, hilbert_curve):
    if n == 0:
        yield (x, y)
    else:
        for hi in hilbert_order[hilbert_curve]:
            x1 = 2 * x + hi % 2
            y1 = 2 * y + hi / 2
            for t in enumeratePoints(x1, y1, n - 1, hilbert_next[hilbert_curve][hi]):
                yield t
