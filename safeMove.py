#!/usr/bin/env python2

import linuxcnc
import logging
import mdiCodeExec
import math


class safeMove:

    def _stopDist(self):
        self.stat.poll()
        delta = [(i-j) for i, j in
                 zip(self.stat.actual_position,
                     self.stat.probed_position)]
        return math.sqrt(delta[0] ** 2 + delta[1] ** 2 + delta[2] ** 2)

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
            self.stat.poll()
            self.mdi.exe("G94")
            assert self.mdi.exe(gcode) != -1  # May have error
            if 930 in self.stat.gcodes:
                self.mdi.exe("G93")
            self.stat.poll()
            if self.stat.probe_tripped:
                raise Exception(
                    "Unexpected probe trip, managed to "
                    "stop within {} machine units".format(self._stopDist()))
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
            math.sqrt(accel * safeDist)  # Don't know the exact formula
        self.tolerance = tolerance


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    with mdiCodeExec.mdiCodeExec() as mdi:
        s = safeMove(mdi)
        s.move(x=100, y=80, z=140)
        s.move(x=0, y=0, z=150)
        logger.info("Moved to destination without the probe being tripped.")
