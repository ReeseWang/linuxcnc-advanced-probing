#!/usr/bin/env python2
import math

def relativePos(stat):
    positions = stat.actual_position
    positions = [(i-j) for i, j in zip(positions, stat.tool_offset)]
    positions = [(i-j) for i, j in zip(positions, stat.g5x_offset)]

    t = -stat.rotation_xy
    t = math.radians(t)
    x = positions[0]
    y = positions[1]
    positions[0] = x * math.cos(t) - y * math.sin(t)
    positions[1] = x * math.sin(t) + y * math.cos(t)
    positions = [(i-j) for i, j in zip(positions, stat.g92_offset)]
    return positions
