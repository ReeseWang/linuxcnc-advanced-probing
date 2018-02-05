#!/usr/bin/env python2

import mdiCodeExec
import safeMove
import logging
import linuxcnc
import math
import time

probeToolNumber = 6
pointsInHalfCircle = 10
numAPos = 8
numXPos = 5
xStart = 105.0
xEnd = 225.0
testBarDia = 17.2
probeDia = 2.0
prepareDist = 3.0
latchDist = 0.5
travZCleariance = 5
testFeed = 200.0
probeFeed = 50.0
latchFeed = 600.0

zSafe = travZCleariance + (testBarDia + probeDia) / 2.0
prepareRad = testBarDia / 2.0 + prepareDist
angAcrossHalfCircle = math.pi / (pointsInHalfCircle - 1)
tangentRad = ((testBarDia + probeDia) / 2.0 + latchDist) / \
    math.cos(angAcrossHalfCircle/2.0)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    s = linuxcnc.stat()

    with mdiCodeExec.mdiCodeExec() as mdi:
        with open('result.txt', 'w') as f:
            move = safeMove.safeMove(mdi)
            mdi.exe("G17 G8 G21 G40 G49 G64 P0.001 G80 G90 G91.1 G92.2 G94 G97 G98")
            # Make sure current CS coincident to G53
            mdi.exe("G10 L2 P0 X0 Y0 Z0 R0")
            # May timeout
            assert mdi.exe("T{} M6".format(probeToolNumber)) != -1
            mdi.exe("G43")
            move.move(z=zSafe)

            for a in [360.0 / numAPos * x for x in range(0, numAPos)]:
                move.rapid(a=a)
                for xx in [xStart + (xEnd - xStart) / (numXPos - 1) * x
                          for x in range(0, numXPos)]:
                    move.move(x=xx, y=prepareRad)
                    for ang in [angAcrossHalfCircle * x
                                for x in range(0, pointsInHalfCircle)]:
                        mdi.exe("G1 Y{:.3f} Z{:.3f} F1000".format(prepareRad * math.cos(ang),
                                  prepareRad * math.sin(ang)))
                        #move.move(y=prepareRad * math.cos(ang),
                        #          z=prepareRad * math.sin(ang))
                        #time.sleep(0.1)
                        #mdi.exe("G38.2 Y0 Z0 F{}".format(testFeed))
                        #mdi.exe("G91")
                        #time.sleep(0.1)
                        #mdi.exe("G1 Y{:.3f} Z{:.3f} F{}".format(latchDist * math.cos(ang),
                        #          latchDist * math.sin(ang), latchFeed))
                        #mdi.exe("G90")
                        mdi.exe("G38.2 Y0 Z0 F{}".format(probeFeed))
                        s.poll()
                        pr = s.probed_position
                        f.write("{}\t{}\t{}\t{}\t{}\n".format(pr[0], pr[1], pr[2], a, xx))
                        mdi.exe("G91")
                        mdi.exe("G1 Y{:.3f} Z{:.3f} F{}".format(latchDist * math.cos(ang),
                                  latchDist * math.sin(ang), latchFeed))
                        mdi.exe("G90")
                        pass
                    move.move(y=-prepareRad)
                    move.move(z=zSafe)
                    pass
                pass
            pass
