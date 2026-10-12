# interleave.py <upper> <lower> <out>: 68000 16-bit bus, upper ROM = even (high) byte, lower = odd byte
import sys
u, l = open(sys.argv[1], "rb").read(), open(sys.argv[2], "rb").read()
out = bytearray(len(u) * 2)
out[0::2], out[1::2] = u, l
open(sys.argv[3], "wb").write(out)
print(sys.argv[3], len(out), "SP=%08x PC=%08x" % (int.from_bytes(out[0:4], "big"), int.from_bytes(out[4:8], "big")))
