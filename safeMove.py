#!/usr/bin/env python2

import linuxcnc
import logging
import mdiCodeExec
import math
from misc import relativePos


class safeMove:

    def _move(self, gcode, commandedCoords):
        self.stat.poll()
        prevPos = relativePos(self.stat)
        assert self.mdi.exe(gcode) == linuxcnc.RCS_DONE
        self.stat.poll()
        nowPos = relativePos(self.stat)
        if 910 in self.stat.gcodes:  # Incremental mode
            for i, c in commandedCoords.iteritems():
                self.logger.debug("Now at {}, commanded {}".format(
                    nowPos[i], prevPos[i] + c))
                assert abs(nowPos[i] - prevPos[i] - c) < self.tolerance
        else:
            for i, c in commandedCoords.iteritems():
                self.logger.debug("Now at {}, commanded {}".format(
                    nowPos[i], c))
                assert abs(nowPos[i] - c) < self.tolerance

    def move(self,
             x=None,
             y=None,
             z=None,
             a=None,
             b=None,
             c=None,
             u=None,
             v=None,
             w=None):
        commandedCoords = {}
        gcode = "G38.3 "
        if x is not None:
            commandedCoords[0] = x
            gcode += "X{:.4f} ".format(x)
        if y is not None:
            commandedCoords[1] = y
            gcode += "Y{:.4f} ".format(y)
        if z is not None:
            commandedCoords[2] = z
            gcode += "Z{:.4f} ".format(z)
        if a is not None:
            commandedCoords[3] = a
            gcode += "A{:.4f} ".format(a)
        if b is not None:
            commandedCoords[4] = b
            gcode += "B{:.4f} ".format(b)
        if c is not None:
            commandedCoords[5] = c
            gcode += "C{:.4f} ".format(c)
        if u is not None:
            commandedCoords[6] = u
            gcode += "U{:.4f} ".format(u)
        if v is not None:
            commandedCoords[7] = v
            gcode += "V{:.4f} ".format(v)
        if w is not None:
            commandedCoords[8] = w
            gcode += "W{:.4f} ".format(w)

        if commandedCoords:
            gcode += "F{:.3f}".format(self.safeFeed)
            self._move(gcode, commandedCoords)
        else:
            raise Exception("No coordinates provided.")

    def __init__(self,
                 mdi,
                 accel=250.0,
                 safeDist=3.0,
                 tolerance=0.00001):
        self.logger = logging.getLogger(__name__)
        self.stat = linuxcnc.stat()
        self.mdi = mdi
        self.safeFeed = 60.0 * \
            math.sqrt(2 * accel * safeDist)
        self.tolerance = tolerance


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    with mdiCodeExec.mdiCodeExec() as mdi:
        s = safeMove(mdi)
        mdi.exe("G90")
        s.move(x=100, y=80)
        s.move(x=0, y=0)
        logger.info("Absolute Distance Mode OK.")
        mdi.exe("G91")
        s.move(x=100, y=0)
        s.move(x=-100, y=80)
        logger.info("Incremental Distance Mode OK.")
        mdi.exe("G90")
        mdi.exe("G10 L2 P0 R45")  # Rotate current CS 45 deg
        s.move(x=10, y=20)
        s.move(x=0, y=0)
        logger.info("Absolute Distance Mode in rotated CS OK.")
        mdi.exe("G91")
        s.move(x=10, y=20)
        s.move(x=-10, y=-20)
        logger.info("Incremental Distance Mode in rotated CS OK.")
        mdi.exe("G90")
        mdi.exe("G10 L2 P0 R0")  # Rotate current CS 0 deg
