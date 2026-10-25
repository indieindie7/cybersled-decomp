"""Cyber Sled point-ROM (System 21 C67 'point24') -> OBJ. Run: py -3.13 -I tools/poi2obj.py
Format (see NOTES.md 'Model rip (10-13)'):
 word = 24 bit. dir[code] (code < 0x1c01) -> list address; list = sub addresses until 0xffffff.
 sub = [len][qstart][nverts][0][x y z]*nverts [nquads]([i0 i1 i2 i3 colour])*nquads [0]
"""
import os, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = open(os.path.join(B, 'bin', 'point24.bin'), 'rb').read()
W = [int.from_bytes(d[i+1:i+4], 'big') for i in range(0, len(d), 4)]
def s24(x): return x - (1 << 24) if x & 0x800000 else x

def parse_sub(a):
    n = W[a]; r = W[a+1:a+1+n]
    if n < 6: return None
    qs, nv = r[0], r[1]
    p = 3 + 3*nv
    if nv == 0 or p >= n: return None
    v = [(s24(r[3+3*i]), s24(r[4+3*i]), s24(r[5+3*i])) for i in range(nv)]
    nq = r[p]; p += 1
    if p + 5*nq > n: return None
    q = [(tuple(r[p+5*i:p+5*i+4]), r[p+5*i+4]) for i in range(nq)]
    if any(i >= nv for f, c in q for i in f): return None
    return v, q

def parse_obj(la):
    vs, qs = [], []; a = la
    while W[a] != 0xffffff and a < la + 200:
        sp = parse_sub(W[a]); a += 1
        if not sp: continue
        v, q = sp; o = len(vs); vs += v
        qs += [(tuple(i+o for i in f), c) for f, c in q]
    return vs, qs

def all_objects():
    out = {}; seen = {}
    for code in range(0x1c01):
        la = W[code]
        vs, qs = parse_obj(la)
        if qs and la not in seen:
            seen[la] = code; out[code] = (vs, qs)
    return out

def write_obj(path, vs, qs, name):
    with open(path, 'w') as f:
        f.write('# %s\n' % name)
        for x, y, z in vs: f.write('v %d %d %d\n' % (x, y, z))
        cur = None
        for fi, c in qs:
            if c != cur: f.write('usemtl c%d\n' % c); cur = c
            idx = []
            for i in fi:
                if not idx or idx[-1] != i: idx.append(i)
            if len(idx) > 1 and idx[0] == idx[-1]: idx.pop()
            if len(idx) >= 3: f.write('f ' + ' '.join(str(i+1) for i in idx) + '\n')

if __name__ == '__main__':
    objs = all_objects()
    md = os.path.join(B, 'models'); os.makedirs(md, exist_ok=True)
    for code, (vs, qs) in objs.items():
        write_obj(os.path.join(md, 'obj_%03d.obj' % code), vs, qs, 'object %d (dir code 0x%x)' % (code, code))
    print(len(objs), 'objects', sorted(objs)[:10], '...', max(objs))
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    ids = sorted(objs); cols = 8; per = 64
    for pg in range(0, len(ids), per):
        chunk = ids[pg:pg+per]; rows = (len(chunk)+cols-1)//cols
        fig = plt.figure(figsize=(cols*2.2, rows*2.2))
        for k, code in enumerate(chunk):
            ax = fig.add_subplot(rows, cols, k+1, projection='3d')
            vs, qs = objs[code]
            polys = [[(vs[i][0], vs[i][2], -vs[i][1]) for i in f] for f, c in qs]
            ax.add_collection3d(Poly3DCollection(polys, facecolors='#8aa', edgecolors='k', linewidths=0.2))
            xs = [p[0] for pl in polys for p in pl]; ys = [p[1] for pl in polys for p in pl]; zs = [p[2] for pl in polys for p in pl]
            m = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs), 1)/2
            cx, cy, cz = (max(xs)+min(xs))/2, (max(ys)+min(ys))/2, (max(zs)+min(zs))/2
            ax.set_xlim(cx-m, cx+m); ax.set_ylim(cy-m, cy+m); ax.set_zlim(cz-m, cz+m)
            ax.set_box_aspect((1, 1, 1)); ax.view_init(25, -55); ax.set_axis_off()
            ax.set_title('%d' % code, fontsize=8, pad=-6)
        fig.tight_layout(pad=0.2)
        fn = 'contact.png' if len(ids) <= per else 'contact_%02d.png' % (pg//per)
        fig.savefig(os.path.join(md, fn), dpi=80); plt.close(fig)
