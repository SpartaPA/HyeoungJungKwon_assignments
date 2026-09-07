import math

def distance(x, y, gx=0.0, gy=0.0):
    return math.hypot(gx - x, gy - y)

def normalize_angle(angle):
    return (angle + math.pi) % (2.0 * math.pi) - math.pi

def target_angle(x, y, gx, gy):
    return math.atan2(gy - y, gx - x)

def reached(x, y, gx, gy, tolerance):
    if tolerance < 0:
        raise ValueError('tolerance must be non-negative')
    return distance(x, y, gx, gy) <= tolerance
