#!/usr/bin/env python

### bit manipulator test ###

import binascii
import struct

# panda type data input
print ''
d = '\x12\x34\x56\x78\x90\xab\xcd\xef'
print 'input string from panda: ', d

# converted to 8 byte string
print ''
db = '0x' + binascii.hexlify(d)
print 'db input: ', db

# byte level + shfiting tests
print ''
b0 = '0x'+db[:4][2:]
print 'byte 0: ', b0 ,' ', 'int b0 w/ mask 0xf0 >> 4: ', hex((int(b0,0)&0xf0)>>4)
b1 = '0x'+db[:6][4:]
print 'byte 1: ', b1, ' ', 'int b1 w/ mask 0xf0 >> 4: ', hex((int(b1,0)&0xf0)>>4)
b2 = '0x'+db[:8][6:]
print 'byte 2: ', b2, ' ', 'int b2 w/ mask 0xf0 >> 4: ', hex((int(b2,0)&0xf0)>>4)
b3 = '0x'+db[:10][8:]
print 'byte 3: ', b3, ' ', 'int b3 w/ mask 0xf0 >> 4: ', hex((int(b3,0)&0xf0)>>4)
b4 = '0x'+db[:12][10:]
print 'byte 4: ', b4, ' ', 'int b4 w/ mask 0xf0 >> 4: ', hex((int(b4,0)&0xf0)>>4)
b5 = '0x'+db[:14][12:]
print 'byte 5: ', b5, ' ', 'int b5 w/ mask 0xf0 >> 4: ', hex((int(b5,0)&0xf0)>>4)
b6 = '0x'+db[:16][14:]
print 'byte 6: ', b6, ' ', 'int b6 w/ mask 0xf0 >> 4: ', hex((int(b6,0)&0xf0)>>4)
b7 = '0x'+db[:18][16:]
print 'byte 7: ', b7, ' ', 'int b7 w/ mask 0xf0 >> 4: ', hex((int(b7,0)&0xf0)>>4)

# 16 bit level
print ''
i0 = db[:6][2:]
print 'int 0: ', '0x'+i0
i1 = db[:10][6:]
print 'int 1: ', '0x'+i1
i2 = db[:14][10:]
print 'int 2: ', '0x'+i2
i3 = db[:18][14:]
print 'int 3: ', '0x'+i3

# packing bytes back together in a string
print ''
dbm = '0x' + b0[2:] + b1[2:] + b2[2:] + b3[2:] + b4[2:] + b5[2:] + b6[2:] + b7[2:]
print 'dbm: ', dbm

# byte string to int
print ''
dbmi = int(dbm,0)
print 'dbmi: ', dbmi

# int to packed byte array to send via p.can_send(<addr>, dbmip, <bus>)
print ''
dbmip = struct.pack('>Q', dbmi)
print 'output string to panda: ', dbmip
print ''