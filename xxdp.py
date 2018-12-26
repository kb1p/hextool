# -*- coding: utf-8 -*-
"""
Created on Wed Dec 26 12:08:40 2018

@author: kb1p
"""

import sys
import os
import os.path
import math
import string
import getopt

class Converter(object):
    __slots__ = "nCols", "colSize"
    __printableChars = frozenset(string.printable) - frozenset(string.whitespace) | frozenset(" ")

    def __init__(self):
        self.nCols = 8
        self.colSize = 2

    def bin2text(self, fin, fout):
        fin.seek(0, os.SEEK_END)
        size = fin.tell()
        fin.seek(0, os.SEEK_SET)
        addrFmt = "%%0%dx: " % int(math.ceil(math.log(size, 16)))
        blockSize = self.nCols * self.colSize
        colRange = range(self.nCols)
        eof = False
        while not eof:
            addr = fin.tell()
            data = fin.read(blockSize)
            rem = blockSize - len(data)
            eof = rem > 0
            if rem < blockSize:
                fout.write(addrFmt % addr)
                cols = ("".join("%02x" % ord(x) for x in buffer(data, c * self.colSize, self.colSize)) \
                        for c in colRange)
                fout.write(" ".join(cols))
                if eof:
                    # padding
                    fout.write("  " * rem)
                fout.write("  ")
                fout.write("".join(c if c in self.__printableChars else "." for c in data))
                fout.write(os.linesep)

    def text2bin(self, fin, fout):
        for line in fin:
            # allow partial modification of the binary file
            addrSep = line.find(":")
            if addrSep >= 0:
                addr = int(line[0:addrSep], 16)
                fout.seek(addr, os.SEEK_SET)
                start = addrSep + 1
            else:
                start = 0
            textSep = line.find("  ")
            data = line[start:textSep] if textSep > 0 else line[start:]
            for chunk in data.split():
                bindata = "".join(chr(int(chunk[x:x+2], 16)) for x in xrange(0, len(chunk), 2))
                fout.write(bindata)

def main(args):
    rev = False
    conv = Converter()
    opts, freeargs = getopt.getopt(args[1:], "rc:s:")
    for o, a in opts:
        if o == "-r":
            rev = True
        elif o == "-c":
            conv.nCols = int(a)
        elif o == "-s":
            conv.colSize = int(a)

    nFreeArgs = len(freeargs)
    if nFreeArgs == 0:
        usage = """Incorrect arguments. Usage:
Dump:  %(prog)s [-c columns -s bytes_per_column] in-file [out-file]
Patch: %(prog)s -r [in-file] out-file

Arguments in rectangular brackets are optional. When optional files
are not specified, use stdout (for dump) and stdin (for patch).
        """ % { "prog": args[0] }
        print >> sys.stderr, usage
        return 1

    fin, fout = None, None
    try:
        if rev:
            if nFreeArgs > 1:
                fin = open(freeargs[0], "rt")
            else:
                fin = sys.stdin
            outFn = freeargs[nFreeArgs - 1]
            writeMode = "r+b" if os.path.exists(outFn) else "wb"
            fout = open(outFn, writeMode)
            conv.text2bin(fin, fout)
        else:
            fin = open(freeargs[0], "rb")
            if nFreeArgs > 1:
                fout = open(freeargs[1], "wb")
            else:
                fout = sys.stdout
            conv.bin2text(fin, fout)
    except IOError as err:
        print >> sys.stderr, "I/O error: %s, file: \"%s\"" % (err.strerror, err.filename)
    finally:
        if fout != None:
            if fout == sys.stdout:
                fout.flush()
            else:
                fout.close()
        if fin not in (None, sys.stdin):
            fin.close()

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

