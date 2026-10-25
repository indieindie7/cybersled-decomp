"""Cyber Sled polygon colour code -> RGB.

In-game 3D palette (slave spr.bin, pal_load_ramps_by_state 0xe048 / pal_load_ramps_mode3 0xe028):
  per level sel (= 0x900300 value 0,4,..,28) one 256-entry ramp is copied to ALL 16 rows of the 3D palette
  (0x744000+0x400*r R,G words ; 0x754001+0x400*r B bytes), entry i = code i (pen = 0x2000 + code).
  Source tables: pair pointer tables at spr 0xe12a (state "ahead") and 0xe16a (default), entry for sel at
  table + sel*2: [B ptr (256 bytes), RG ptr (512 bytes, R = high byte, G = low byte)] into the data ROM (0x800000).
  Depth cue (pal_load_depthcue_ramps 0xdad2): level0 = ramp, level1 = v - 2*(v>>2) (~1/2), level2 = level1 - (v>>2) (~1/4).
  Codes with bit 9 (512..767) are the same ramp (row 1) -> code & 0xff.
Entries (0,204,0) / (0,255,0) / (42,42,42) are unassigned markers; they are filled from other levels.
usage: py -3.13 -I cspal.py [--shade 0|1|2]
"""
import struct, glob, os, re, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spr = open(os.path.join(ROOT, 'bin', 'spr.bin'), 'rb').read()
dat = open(os.path.join(ROOT, 'bin', 'data.bin'), 'rb').read()
L = lambda a: struct.unpack('>I', spr[a:a + 4])[0]
PH = {(0, 0xcc, 0), (0, 0xff, 0), (0x2a, 0x2a, 0x2a)}
shade = int(sys.argv[sys.argv.index('--shade') + 1]) if '--shade' in sys.argv else 0

def ramp(tab, sel):
    p = tab + sel * 2
    B = dat[L(p) - 0x800000:][:256]; RG = dat[L(p + 4) - 0x800000:][:512]
    return [(RG[2 * i], RG[2 * i + 1], B[i]) for i in range(256)]

def dim(c, lvl):  # 0x3f3f3f3f trick per byte
    r = []
    for v in c:
        h = v >> 2
        v1 = v - 2 * h
        r.append((v, v1, v1 - h)[lvl])
    return tuple(r)

# preference order: ahead-state table (more colourful) sel 4 first, then other levels, then default table
order = [(0xe12a, s) for s in (4, 8, 0, 20, 28, 24, 12, 16)] + [(0xe16a, s) for s in (4, 8, 0, 28, 20, 24, 12, 16)]
ramps = [ramp(t, s) for t, s in order]
pal = []
for i in range(256):
    c = next((r[i] for r in ramps if r[i] not in PH), (128, 128, 128))
    pal.append(dim(c, shade))

with open(os.path.join(ROOT, 'models', 'palette_codes.txt'), 'w') as f:
    for i, c in enumerate(pal): f.write('%02x %d %d %d\n' % ((i,) + c))
im = Image.new('RGB', (16 * 24, 16 * 24))
for i, c in enumerate(pal):
    im.paste(c, ((i % 16) * 24, (i // 16) * 24, (i % 16) * 24 + 24, (i // 16) * 24 + 24))
im.save(os.path.join(ROOT, 'models', 'palette_codes.png'))

for fn in glob.glob(os.path.join(ROOT, 'models', 'vehicles', '*.obj')):
    txt = open(fn).read()
    names = sorted({int(m) for m in re.findall(r'^usemtl c(\d+)', txt, re.M)})
    base = os.path.splitext(os.path.basename(fn))[0]
    with open(os.path.join(os.path.dirname(fn), base + '.mtl'), 'w') as f:
        for n in names:
            r, g, b = pal[n & 0xff]
            f.write('newmtl c%d\nKd %.4f %.4f %.4f\nKa 0 0 0\nKs 0 0 0\n\n' % (n, r / 255, g / 255, b / 255))
    if not txt.startswith('mtllib '):
        open(fn, 'w').write('mtllib %s.mtl\n' % base + txt)
print('wrote palette_codes.txt/png and mtl files')
for n in (25, 31, 33, 55, 92, 150, 252): print(n, pal[n])
