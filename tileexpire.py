#!/usr/bin/python

"""
OSMTileExpire, a class for managing tile expirations in a memory efficient
way.
"""

__author__      = "Phil! Gold <phil_g@pobox.com>"
__copyright__   = "waived; see license"
__license__     = "CC0: http://creativecommons.org/publicdomain/zero/1.0/"

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
        if targetz < self.z:
            raise Exception('zoom {0} is lower than this zoom, {1}'.format(targetz, self.z))
        elif targetz == self.z:
            yield (self.x, self.y)
        elif self.full:
            exp = 2**(targetz - self.z)
            for t in hilbert(self.x*exp, self.y*exp, exp, 0, 0, exp, targetz - self.z):
                yield t
        else:
            for c in self.children:
                if c:
                    for t in c.expiredAt(targetz):
                        yield t

def hilbert(x, y, xi, xj, yi, yj, n):
    if n <= 0:
        yield (x + (xi+yi)/2, y + (xj+yj)/2)
    else:
        for h in hilbert(x, y, yi/2, yj/2, xi/2, xj/2, n-1):
            yield h
        for h in hilbert(x+xi/2, y+xj/2, xi/2, xj/2, yi/2, yj/2, n-1):
            yield h
        for h in hilbert(x+xi/2+yi/2, y+xj/2+yj/2, xi/2, xj/2, yi/2, yj/2, n-1):
            yield h
        for h in hilbert(x+xi/2+yi, y+xj/2+yj, -yi/2, -yj/2, -xi/2, -xj/2, n-1):
            yield h
