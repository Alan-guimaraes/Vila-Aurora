"""Rebuild Vila Aurora's 32 px pixel-art atlas, Tiled data, and thumbnail."""
from __future__ import annotations

import json
import random
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIZE = 32
COLS = ROWS = 8
TRANSPARENT = (0, 0, 0, 0)
INK = (39, 55, 49, 255)
PALETTE = {
    "grass": (104, 174, 92, 255), "grass2": (82, 153, 80, 255),
    "grass3": (137, 190, 94, 255), "path": (226, 194, 137, 255),
    "path_hi": (242, 215, 165, 255), "path_lo": (195, 157, 105, 255),
    "water": (52, 143, 195, 255), "water2": (39, 116, 176, 255),
    "foam": (157, 222, 225, 255), "soil": (131, 81, 57, 255),
    "wall": (247, 226, 182, 255), "wallshade": (222, 192, 145, 255),
    "red": (193, 83, 71, 255), "redhi": (224, 115, 83, 255),
    "blue": (67, 125, 183, 255), "bluehi": (109, 174, 207, 255),
    "gold": (217, 163, 71, 255), "goldhi": (240, 199, 105, 255),
    "wood": (130, 79, 49, 255), "woodhi": (178, 119, 67, 255),
    "leaf": (48, 119, 66, 255), "leafhi": (89, 161, 74, 255),
    "flower": (232, 103, 121, 255), "cream": (255, 244, 204, 255),
}


class Canvas:
    def __init__(self, w: int, h: int, color=TRANSPARENT):
        self.w, self.h = w, h
        self.p = [color] * (w * h)

    def rect(self, x, y, w, h, color):
        if isinstance(color, str): color = PALETTE[color]
        for yy in range(max(0, y), min(self.h, y + h)):
            start = yy * self.w + max(0, x)
            end = yy * self.w + min(self.w, x + w)
            self.p[start:end] = [color] * max(0, end - start)

    def dot(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y * self.w + x] = color

    def box(self, x, y, w, h, fill, edge=INK):
        self.rect(x, y, w, h, edge)
        self.rect(x + 1, y + 1, w - 2, h - 2, fill)

    def png(self, path: Path):
        raw = b"".join(b"\0" + bytes(v for px in self.p[y*self.w:(y+1)*self.w] for v in px) for y in range(self.h))
        def chunk(kind, payload):
            return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
        data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
        path.write_bytes(data)


tiles: list[Canvas] = []


def tile(fill=TRANSPARENT):
    c = Canvas(SIZE, SIZE, fill)
    tiles.append(c)
    return c


def grass(i=0):
    c = tile(PALETTE["grass"])
    seed = i * 7 + 2
    for n in range(5):
        x, y = (seed + n * 11) % 29 + 1, (seed * 3 + n * 13) % 29 + 1
        c.dot(x, y, PALETTE["grass2"])
        c.dot(x + 1, y, PALETTE["grass3"])
        if n % 2: c.dot(x, y + 1, PALETTE["grass2"])
    return c


for i in range(8): grass(i)
# Sandy paths and a slightly darker path seam.
for i in range(4):
    c = tile(PALETTE["path"])
    for x, y in [(4+i, 7), (22, 12+i), (9, 24), (27-i, 28), (15, 3)]:
        c.rect(x, y, 2, 1, PALETTE["path_hi"])
    if i == 1: c.rect(0, 0, 32, 2, PALETTE["grass"])
    if i == 2: c.rect(0, 30, 32, 2, PALETTE["grass"])
    if i == 3: c.rect(0, 0, 2, 32, PALETTE["grass"])
# Pond water, shore edges, and small ripple variants.
for i in range(4):
    c = tile(PALETTE["water"] if i % 2 == 0 else PALETTE["water2"])
    for x in range(4 + i, 28, 9): c.rect(x, 7 + (x % 3), 5, 1, PALETTE["foam"])
    c.rect(8 + i * 3, 20, 3, 1, PALETTE["bluehi"])
for edge in range(4):
    c = tile(PALETTE["water"])
    if edge == 0: c.rect(0, 0, 32, 7, PALETTE["grass"]); c.rect(0, 7, 32, 2, PALETTE["soil"])
    if edge == 1: c.rect(0, 25, 32, 7, PALETTE["grass"]); c.rect(0, 23, 32, 2, PALETTE["soil"])
    if edge == 2: c.rect(0, 0, 7, 32, PALETTE["grass"]); c.rect(7, 0, 2, 32, PALETTE["soil"])
    if edge == 3: c.rect(25, 0, 7, 32, PALETTE["grass"]); c.rect(23, 0, 2, 32, PALETTE["soil"])
    for x in range(4, 29, 12): c.rect(x, 14, 5, 1, PALETTE["foam"])
# Four quadrants build each tree as a coherent 64-by-64 scenery object.
for qy in range(2):
    for qx in range(2):
        c = tile()
        for y in range(32):
            gy = qy * 32 + y
            half = 12 + int(gy * 0.47) if gy < 30 else 26 - int((gy - 30) * 0.42)
            left = 32 - half
            for x in range(32):
                gx = qx * 32 + x
                if left <= gx <= 64 - left and 3 <= gy <= 58:
                    c.dot(x, y, PALETTE["leafhi"] if (gx * 3 + gy * 5) % 7 == 0 else PALETTE["leaf"])
        for gx, gy in [(12,14),(23,9),(42,16),(53,26),(15,35),(44,41),(28,23),(36,32)]:
            if gx // 32 == qx and gy // 32 == qy: c.rect(gx % 32, gy % 32, 3, 2, PALETTE["grass3"])
        if qy == 1:
            if qx == 0: c.rect(25, 1, 8, 31, PALETTE["wood"]); c.rect(28, 1, 3, 30, PALETTE["woodhi"])
            else: c.rect(0, 1, 8, 31, PALETTE["wood"]); c.rect(1, 1, 3, 30, PALETTE["woodhi"])
for i in range(4):
    c = tile()
    c.rect(4, 17, 24, 11, PALETTE["leaf"])
    c.rect(7, 12, 18, 11, PALETTE["leafhi"])
    c.rect(10 + i, 14, 3, 2, PALETTE["grass3"])
# Four roof palettes: roof cap, eaves and house wall parts.
for roof, hi in [("red", "redhi"), ("blue", "bluehi"), ("gold", "goldhi"), ("leaf", "leafhi")]:
    c = tile(PALETTE[roof]); c.rect(0, 4, 32, 25, PALETTE[roof]); c.rect(0, 3, 32, 3, PALETTE[hi])
    c.rect(0, 26, 32, 4, PALETTE["wood"]); c.rect(3, 9, 26, 2, PALETTE[hi])
    for x in range(4, 32, 8): c.rect(x, 14, 2, 10, PALETTE[hi])
    c = tile(PALETTE["wall"]); c.rect(0, 0, 32, 4, PALETTE["wood"]); c.rect(0, 4, 32, 3, PALETTE[hi])
    c.rect(0, 28, 32, 4, PALETTE["blue"])
    # wall windows and door variants follow each roof palette
    c = tile(PALETTE["wall"]); c.rect(0, 0, 32, 4, PALETTE["wood"]); c.rect(0, 4, 32, 3, PALETTE[hi]); c.rect(0, 28, 32, 4, PALETTE["blue"])
    c.box(7, 10, 18, 14, PALETTE["blue"]); c.rect(15, 11, 2, 12, PALETTE["cream"]); c.rect(8, 16, 16, 2, PALETTE["cream"])
    c = tile(PALETTE["wall"]); c.rect(0, 0, 32, 4, PALETTE["wood"]); c.rect(0, 4, 32, 3, PALETTE[hi]); c.rect(0, 28, 32, 4, PALETTE["blue"])
    c.box(10, 8, 13, 23, PALETTE["wood"]); c.rect(12, 10, 9, 18, PALETTE["woodhi"]); c.dot(19, 20, PALETTE["goldhi"])
# Plaza pavers, flower planters, benches, fountain, lights, signs, bridge.
for i in range(4):
    c = tile((207 + i*4, 195 + i*3, 158 + i*4, 255))
    shade = (183, 168, 139, 255)
    for x, y, w in [(2,7,10),(18,4,12),(7,19,13),(22,25,8),(0,29,7)]: c.rect(x, y + i % 2, w, 1, shade)
    for x, y in [(12,1),(27,12),(3,24),(17,14),(30,21)]: c.dot(x, y, PALETTE["cream"])
for color in ["flower", "goldhi"]:
    c = tile(PALETTE["grass"]); c.rect(2, 7, 28, 21, PALETTE["wood"]); c.rect(4, 5, 24, 20, PALETTE["leaf"])
    for x, y in [(8, 11), (16, 8), (23, 14), (12, 18), (20, 20)]: c.rect(x, y, 3, 3, color)
c = tile(); c.rect(5, 21, 22, 5, PALETTE["wood"]); c.rect(7, 14, 18, 7, PALETTE["woodhi"]); c.rect(5, 13, 22, 3, PALETTE["wood"]); c.rect(8, 26, 3, 5, PALETTE["wood"]); c.rect(21, 26, 3, 5, PALETTE["wood"])
c = tile(); c.rect(14, 13, 4, 18, PALETTE["wood"]); c.rect(10, 9, 12, 5, PALETTE["wood"]); c.rect(11, 5, 10, 4, PALETTE["goldhi"]); c.rect(13, 3, 6, 2, PALETTE["cream"])
c = tile(); c.rect(5, 22, 22, 8, PALETTE["soil"]); c.rect(7, 17, 18, 7, PALETTE["cream"]); c.rect(9, 12, 14, 6, PALETTE["blue"]); c.rect(14, 6, 4, 7, PALETTE["bluehi"]); c.rect(15, 2, 2, 5, PALETTE["foam"])
c = tile(); c.rect(8, 7, 16, 22, PALETTE["wood"]); c.rect(10, 9, 12, 17, PALETTE["goldhi"]); c.rect(12, 13, 8, 5, PALETTE["woodhi"])
c = tile(); c.rect(2, 15, 28, 15, PALETTE["wood"]); c.rect(4, 17, 24, 11, PALETTE["woodhi"]); c.rect(4, 16, 24, 3, PALETTE["blue"]); c.rect(6, 19, 20, 2, PALETTE["goldhi"])
c = tile(); c.rect(0, 21, 32, 11, PALETTE["wood"]); c.rect(0, 18, 32, 5, PALETTE["woodhi"]); c.rect(5, 23, 22, 2, PALETTE["goldhi"])
# Flower clumps, rocks, and accents.
for color in ["flower", "goldhi", "cream", "bluehi"]:
    c = tile(PALETTE["grass"])
    for x, y in [(6, 12), (15, 8), (24, 14), (12, 22), (21, 23)]:
        c.rect(x, y, 4, 4, PALETTE["leaf"]); c.rect(x+1, y-1, 2, 3, color); c.dot(x+2, y, PALETTE["cream"])
c = tile(PALETTE["grass"]); c.box(6, 18, 20, 9, (112, 119, 119, 255), (72, 83, 82, 255)); c.rect(10, 15, 9, 4, (169, 174, 164, 255))
c = tile(PALETTE["grass"]); c.rect(14, 13, 4, 18, PALETTE["wood"]); c.rect(8, 5, 16, 11, PALETTE["woodhi"]); c.rect(10, 7, 12, 7, PALETTE["goldhi"])
c = tile(PALETTE["grass"]); c.rect(11, 16, 10, 14, PALETTE["red"]); c.rect(9, 13, 14, 4, PALETTE["wood"]); c.rect(13, 19, 6, 3, PALETTE["cream"])
c = tile(PALETTE["grass"]); c.rect(3, 18, 26, 11, PALETTE["soil"]); c.rect(6, 14, 20, 8, PALETTE["woodhi"]); c.rect(9, 10, 14, 7, PALETTE["wood"]); c.rect(11, 11, 10, 4, PALETTE["goldhi"])

assert len(tiles) <= 64, len(tiles)
while len(tiles) < 64: tiles.append(Canvas(SIZE, SIZE))
atlas = Canvas(COLS * SIZE, ROWS * SIZE)
for i, t in enumerate(tiles):
    ox, oy = (i % COLS) * SIZE, (i // COLS) * SIZE
    for y in range(SIZE):
        atlas.p[(oy+y)*atlas.w+ox:(oy+y)*atlas.w+ox+SIZE] = t.p[y*SIZE:(y+1)*SIZE]
atlas_path = ROOT / "tilesets" / "aurora_tiles_v2.png"
atlas.png(atlas_path)

map_path = ROOT / "vila-aurora.tmj"
data = json.loads(map_path.read_text(encoding="utf-8"))
W, H = data["width"], data["height"]
ground = [1] * (W * H)
decor = [0] * (W * H)
collision = [0] * (W * H)
random.seed(42)

def put(layer, x, y, gid):
    if 0 <= x < W and 0 <= y < H: layer[y*W+x] = gid

def rect(layer, x, y, w, h, gid):
    for yy in range(y, y+h):
        for xx in range(x, x+w): put(layer, xx, yy, gid)

for y in range(H):
    for x in range(W):
        if (x * 7 + y * 11) % 9 == 0:
            put(ground, x, y, 2 + ((x + y) % 6))

# A green village ring with paths leading into a paved central plaza.
rect(ground, 22, 3, 4, 30, 9)
rect(ground, 4, 16, 40, 4, 9)
rect(ground, 17, 10, 14, 16, 45)
rect(ground, 21, 14, 6, 8, 46)
# Small pond in the northwest and a southern stream pool.
rect(ground, 2, 3, 9, 6, 13)
rect(ground, 37, 29, 8, 4, 14)
for x in range(2, 11): put(ground, x, 2, 17); put(ground, x, 9, 18)
for y in range(3, 9): put(ground, 1, y, 19); put(ground, 11, y, 20)
for x in range(37, 45): put(ground, x, 28, 17); put(ground, x, 33, 18)
for y in range(29, 33): put(ground, 36, y, 19); put(ground, 45, y, 20)
# Central garden beds and landmark fountain.
rect(ground, 19, 12, 3, 2, 49); rect(ground, 26, 22, 3, 2, 50)
put(decor, 23, 17, 53)
put(decor, 22, 13, 61); put(decor, 28, 23, 61)
# Six homes/businesses positioned beside their preserved interaction areas.
houses = [(16, 5, 29), (29, 5, 33), (4, 12, 37), (40, 12, 41), (4, 24, 29), (40, 24, 33)]
for hx, hy, roof in houses:
    wall = roof + 1
    for dx in range(3):
        put(decor, hx+dx, hy, roof)
        put(decor, hx+dx, hy+1, wall + (1 if dx != 1 else 0))
        put(decor, hx+dx, hy+2, wall + (2 if dx != 1 else 3))
        put(collision, hx+dx, hy, 64); put(collision, hx+dx, hy+1, 64); put(collision, hx+dx, hy+2, 64)
# Trees in green pockets, leaving paths and interaction spots open.
trees = [(2,10),(8,11),(12,3),(14,8),(33,3),(37,10),(44,10),(2,21),(9,23),(12,29),(33,29),(37,22),(44,24),(7,30),(32,9),(35,24)]
for x, y in trees:
    for dy in range(2):
        for dx in range(2):
            put(decor, x+dx, y+dy, 21 + dy*2 + dx)
            put(collision, x+dx, y+dy, 64)
# Shrubs and blossom beds frame the buildings and plaza paths.
for x, y, gid in [(1,12,25),(10,12,26),(12,11,27),(35,11,28),(46,13,25),(1,24,26),(9,24,27),(34,26,28),(46,26,25),(16,9,57),(31,9,58),(16,26,59),(31,26,60),(20,13,57),(27,22,58),(18,18,59),(29,18,60),(6,12,57),(41,12,58),(6,24,59),(41,24,60)]: put(decor, x, y, gid)
# Benches, lights, flower patches and signposts along the plaza paths.
for x, y, gid in [(19,15,51),(28,20,51),(19,21,52),(28,15,52),(23,12,62),(24,23,54),(16,18,61),(31,18,63),(20,15,57),(27,20,58),(20,20,59),(27,15,60)]: put(decor, x, y, gid)

for layer in data["layers"]:
    if layer["name"] == "ground": layer["data"] = ground
    elif layer["name"] == "decor": layer["data"] = decor
    elif layer["name"] == "collision": layer["data"] = collision

data["tilesets"] = [{
    "firstgid": 1, "name": "aurora_tiles_v2", "image": "tilesets/aurora_tiles_v2.png",
    "imagewidth": 256, "imageheight": 256, "tilewidth": 32, "tileheight": 32,
    "tilecount": 64, "columns": 8, "margin": 0, "spacing": 0,
    "tiles": [{"id": i, "properties": [{"name": "collides", "type": "bool", "value": True}]} for i in range(20, 44)] +
              [{"id": 63, "properties": [{"name": "collides", "type": "bool", "value": True}]}]
}]
map_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Export the thumbnail by compositing the two visible tile layers at native map size.
scale = 3
preview = Canvas(W*SIZE//scale, H*SIZE//scale)
for layer_data in (ground, decor):
    for i, gid in enumerate(layer_data):
        if gid == 0: continue
        src = tiles[gid-1]
        ox, oy = (i % W)*SIZE, (i // W)*SIZE
        for y in range(SIZE):
            for x in range(SIZE):
                px = src.p[y*SIZE+x]
                if px[3] and x % scale == 0 and y % scale == 0:
                    preview.dot((ox+x)//scale, (oy+y)//scale, px)
preview.png(ROOT / "map.png")
print(f"Wrote {atlas_path.name}, {map_path.name}, and map.png ({W}x{H} tiles)")
