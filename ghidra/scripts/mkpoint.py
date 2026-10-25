import sys
R='rom/'
def ld(n): return open(R+n,'rb').read()
out=bytearray(0x400000)
for base,(h,m,l) in ((0,('cy1-poi-h1.2f','cy1-poi-lu1.2k','cy1-poi-ll1.2n')),(0x200000,('cy1-poi-h2.2j','cy1-poi-lu2.2l','cy1-poi-ll2.2p'))):
    for o,n in ((1,h),(2,m),(3,l)):
        d=ld(n); out[base+o:base+4*len(d):4]=d
open('bin/point24.bin','wb').write(out)
