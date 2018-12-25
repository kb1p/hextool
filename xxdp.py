# -*- coding: utf-8 -*-
"""
Created on Tue Dec 25 23:28:56 2018

@author: kb1p
"""

import sys
import os
import math

def bin2str(binstr):
    return "".join("%02x" % ord(x) for x in binstr)

class Converter(object):
    __slots__ = "nCols", "colSize"

    def bin2text(self, fin, fout):
        fin.seek(0, os.SEEK_END)
        srcSize = fin.tell()
        fin.seek(0, os.SEEK_SET)
        addrFormat = "%%0%dx:" % int(math.ceil(math.log(srcSize, 16)))
        blockSize = self.nCols * self.colSize
        while True:
            startAddr = fin.tell()
            block = fin.read(blockSize)
            nRead = len(block)
            if nRead > 0:
                print >> fout, addrFormat % startAddr,
                for c in xrange(self.nCols):
                    print >> fout, bin2str(buffer(block, c * self.colSize, self.colSize)),
                print >> fout
            if nRead < blockSize:
                break

    def text2bin(self, fin, fout):
        pass

def main(args):
    if len(args) < 2:
        print >> sys.stderr, "Usage: %s <in-file> [<out-file>]" % args[0]
        return 1

    conv = Converter()
    fnIn = args[1]
    fnOut = args[2] if len(args) > 2 else args[1] + "-dump.txt"
    bin2text = True
    conv.nCols = 8
    conv.colSize = 2

    with open(fnIn, "rb") as fin, open(fnOut, "wb") as fout:
        if bin2text:
            conv.bin2text(fin, fout)
        else:
            conv.text2bin(fin, fout)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
