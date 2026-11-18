import fs from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const root = path.resolve(import.meta.dirname, "..");
const source = path.join(root, "tilesets/aurora_tiles_v3_source.png");
const atlasPath = path.join(root, "tilesets/aurora_tiles_v3.png");
const mapPath = path.join(root, "vila-aurora.tmj");
const cell = 32;
const cols = 8;

// The source is an 8x8 illustrated atlas. Crop off its generated cell seams,
// then reduce each cell independently so no seam can bleed into the sprites.
const sourceMeta = await sharp(source).metadata();
const parts = [];
const tiles = [];
for (let id = 0; id < 64; id++) {
  const col = id % cols;
  const row = Math.floor(id / cols);
  const x0 = Math.round(col * sourceMeta.width / cols);
  const x1 = Math.round((col + 1) * sourceMeta.width / cols);
  const y0 = Math.round(row * sourceMeta.height / cols);
  const y1 = Math.round((row + 1) * sourceMeta.height / cols);
  const margin = 7;
  const tileBuffer = await sharp(source)
    .extract({ left: x0 + margin, top: y0 + margin, width: x1 - x0 - margin * 2, height: y1 - y0 - margin * 2 })
    .resize(cell, cell, { kernel: "nearest" })
    .png().toBuffer();
  tiles.push(tileBuffer);
  parts.push({ input: tileBuffer, left: col * cell, top: row * cell });
}
await sharp({ create: { width: cols * cell, height: cols * cell, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } })
  .composite(parts).png().toFile(atlasPath);

const map = JSON.parse(await fs.readFile(mapPath, "utf8"));
const W = map.width;
const H = map.height;
const ground = Array(W * H).fill(1);
const decor = Array(W * H).fill(0);
const collision = Array(W * H).fill(0);
const at = (x, y) => y * W + x;
const put = (layer, x, y, gid) => { if (x >= 0 && x < W && y >= 0 && y < H) layer[at(x, y)] = gid; };
const rect = (layer, x, y, w, h, gid) => {
  for (let yy = y; yy < y + h; yy++) for (let xx = x; xx < x + w; xx++) put(layer, xx, yy, gid);
};

// Varied grass base, sandy streets, a compact plaza and two ponds.
for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
  if ((x * 7 + y * 11) % 7 === 0) put(ground, x, y, 2 + ((x * 3 + y) % 7));
}
rect(ground, 23, 2, 2, 32, 11);
rect(ground, 3, 17, 42, 2, 10);
rect(ground, 18, 13, 12, 10, 49);
for (let y = 13; y < 23; y++) for (let x = 18; x < 30; x++) {
  if ((x + y) % 3 === 0) put(ground, x, y, 49 + ((x * 3 + y) % 3));
}
rect(ground, 2, 3, 8, 6, 17);
rect(ground, 38, 28, 8, 5, 18);
for (let x = 2; x < 10; x++) { put(ground, x, 2, 22); put(ground, x, 9, 23); }
for (let y = 3; y < 9; y++) { put(ground, 1, y, 24); put(ground, 10, y, 24); }
for (let x = 38; x < 46; x++) { put(ground, x, 27, 22); put(ground, x, 33, 23); }
for (let y = 28; y < 33; y++) { put(ground, 37, y, 24); put(ground, 46, y, 24); }

// Six four-tile storefronts and homes, with doors facing the walking lanes.
const houses = [[14,5,0],[29,5,0],[3,12,1],[41,12,2],[3,24,0],[41,24,1]];
for (const [x, y, facade] of houses) {
  for (let dx = 0; dx < 4; dx++) {
    put(decor, x + dx, y, 41 + (dx % 3));
    let wall = 33 + facade;
    if (dx === 1 || dx === 3) wall = 34 + ((facade + dx) % 5);
    if (dx === 2) wall = 37 + facade;
    put(decor, x + dx, y + 1, wall);
    put(collision, x + dx, y, 64); put(collision, x + dx, y + 1, 64);
  }
}

// Tree groves, hedges, gardens and readable plaza furniture.
const trees = [[1,11],[9,11],[12,3],[12,8],[32,3],[36,10],[45,10],[1,21],[9,23],[12,30],[32,30],[37,22],[45,23],[7,30],[32,9],[35,24],[1,30],[14,32],[30,4],[46,31],[17,10],[30,24],[18,25],[29,11]];
for (let i = 0; i < trees.length; i++) {
  const [x, y] = trees[i];
  put(decor, x, y, 25 + (i % 4));
  put(collision, x, y, 64);
}
for (const [x,y,gid] of [[11,14,29],[36,14,30],[2,15,31],[46,16,32],[2,26,29],[46,27,30],[19,12,52],[26,12,53],[19,22,52],[26,22,53],[20,17,54],[27,17,54],[23,15,61],[24,20,61],[23,18,56],[17,17,57],[30,18,58],[21,14,59],[26,21,60],[16,21,62],[31,14,64]]) put(decor,x,y,gid);

for (const layer of map.layers) {
  if (layer.name === "ground") layer.data = ground;
  if (layer.name === "decor") layer.data = decor;
  if (layer.name === "collision") layer.data = collision;
}
map.tilesets = [{
  firstgid: 1, name: "aurora_tiles_v3", image: "tilesets/aurora_tiles_v3.png",
  imagewidth: 256, imageheight: 256, tilewidth: 32, tileheight: 32,
  tilecount: 64, columns: 8, margin: 0, spacing: 0,
  tiles: [...Array.from({ length: 20 }, (_, i) => i + 24), 63].map(id => ({
    id, properties: [{ name: "collides", type: "bool", value: true }]
  }))
}];
await fs.writeFile(mapPath, JSON.stringify(map, null, 2) + "\n");

// Render a 3x nearest-neighbor thumbnail directly from the map's two art layers.
const overlays = [];
for (const [layer, values] of [[ground, ground], [decor, decor]]) {
  for (let i = 0; i < values.length; i++) {
    const gid = values[i];
    if (!gid) continue;
    overlays.push({ input: tiles[gid - 1], left: (i % W) * cell, top: Math.floor(i / W) * cell });
  }
}
await sharp({ create: { width: W * cell, height: H * cell, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 255 } } })
  .composite(overlays).resize(512, 384, { kernel: "nearest" }).png().toFile(path.join(root, "map.png"));
console.log("Rebuilt the 64-tile atlas, Vila Aurora TMJ and 512x384 preview.");
