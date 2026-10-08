"""Shared math helpers for the Pebble generator + preview renderer."""
import math
import numpy as np

def quat_from_euler_zyx(xd, yd, zd):
    """three.js Euler(x,y,z,'ZYX') -> quaternion (x,y,z,w); the order the Hytale plugin parses with."""
    x, y, z = (math.radians(v) for v in (xd, yd, zd))
    c1, c2, c3 = math.cos(x / 2), math.cos(y / 2), math.cos(z / 2)
    s1, s2, s3 = math.sin(x / 2), math.sin(y / 2), math.sin(z / 2)
    qx = s1 * c2 * c3 - c1 * s2 * s3
    qy = c1 * s2 * c3 + s1 * c2 * s3
    qz = c1 * c2 * s3 - s1 * s2 * c3
    qw = c1 * c2 * c3 + s1 * s2 * s3
    return (qx, qy, qz, qw)

def quat_mul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz)

def quat_to_mat(q):
    x, y, z, w = q
    n = math.sqrt(x * x + y * y + z * z + w * w) or 1.0
    x, y, z, w = x / n, y / n, z / n, w / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])

def mat4(rot3=None, trans=(0, 0, 0)):
    m = np.eye(4)
    if rot3 is not None:
        m[:3, :3] = rot3
    m[:3, 3] = trans
    return m

def nlerp(a, b, t):
    if sum(i * j for i, j in zip(a, b)) < 0:
        b = tuple(-v for v in b)
    q = tuple(i + (j - i) * t for i, j in zip(a, b))
    n = math.sqrt(sum(v * v for v in q)) or 1
    return tuple(v / n for v in q)

def r6(v):
    """round for JSON output (6 decimals like vanilla), avoid -0.0"""
    v = round(float(v), 6)
    return 0 if v == 0 else (int(v) if v == int(v) else v)

# Face directions in Hytale naming with their outward normals
FACE_NORMALS = {"front": (0, 0, 1), "back": (0, 0, -1), "left": (-1, 0, 0), "right": (1, 0, 0),
                "top": (0, 1, 0), "bottom": (0, -1, 0)}

def face_uv_size(face, size):
    w, h, d = size
    return {"front": (w, h), "back": (w, h), "left": (d, h), "right": (d, h), "top": (w, d), "bottom": (w, d)}[face]

def face_texel_to_local(face, size, u, v):
    """texel centre (u,v) in face-local pixel coords -> local point on the box surface (box centred at 0).
    Mapping verified against Blockbench 5.2.1 + Hytale plugin 0.10.0 (see README)."""
    w, h, d = size
    hx, hy, hz = w / 2, h / 2, d / 2
    if face == "front":   return (-hx + u, hy - v, hz)
    if face == "back":    return (hx - u, hy - v, -hz)
    if face == "left":    return (-hx, hy - v, -hz + u)
    if face == "right":   return (hx, hy - v, hz - u)
    if face == "top":     return (-hx + u, hy, -hz + v)
    if face == "bottom":  return (-hx + u, -hy, hz - v)
    raise ValueError(face)
