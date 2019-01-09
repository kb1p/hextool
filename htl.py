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

VER3 = sys.version_info.major >= 3

def message(msg):
    sys.stderr.write(msg)
    sys.stderr.write(os.linesep)

class Converter(object):
    __slots__ = "nCols", "colSize"
    __printableChars = frozenset(string.printable) - frozenset(string.whitespace) | frozenset(" ")

    def __init__(self):
        self.nCols = 8
        self.colSize = 2

    def bin2text(self, fin, fout, offset, size):
        try:
            if size < 0:
                fin.seek(0, os.SEEK_END)
                size = fin.tell() - offset
            fin.seek(offset, os.SEEK_SET)
        except IOError:
            if size < 0:
                size = sys.maxsize
        addrFmt = "%%0%dx: " % int(math.ceil(math.log(offset + size, 16)))
        blockSize = self.nCols * self.colSize
        colRange = range(self.nCols)
        needMore = size > 0
        while needMore:
            reqSize = min(blockSize, size)
            data = memoryview(fin.read(reqSize))
            dataSize = len(data)
            if dataSize > 0:
                fout.write(addrFmt % offset)
                cols = ("".join("%02x" % (x if VER3 else ord(x)) \
                        for x in data[c * self.colSize:(c + 1) * self.colSize]) \
                        for c in colRange)
                fout.write(" ".join(cols))
                if blockSize > dataSize:
                    # padding
                    fout.write("  " * (blockSize - dataSize))
                fout.write("  ")
                fout.write("".join(c if c in self.__printableChars else "." \
                                   for c in (map(chr, data) if VER3 else data)))
                fout.write("\n")
            size -= dataSize
            offset += dataSize
            needMore = size > 0 and dataSize == reqSize

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
                if VER3:
                    bindata = bytes(int(chunk[x:x+2], 16) for x in range(0, len(chunk), 2))
                else:
                    bindata = "".join(chr(int(chunk[x:x+2], 16)) for x in xrange(0, len(chunk), 2))
                fout.write(bindata)

def parseNumber(strnum):
    if strnum.startswith("0x"):
        return int(strnum[2:], 16)
    elif strnum.startswith("0"):
        return int(strnum[1:], 8)
    else:
        return int(strnum)

def main(args):
    showUsage = False
    rev = False
    conv = Converter()
    offset, size = 0, -1
    opts, freeargs = getopt.getopt(args[1:], "hrc:w:f:s:")
    for o, a in opts:
        if o == "-r":
            rev = True
        elif o == "-c":
            conv.nCols = parseNumber(a)
        elif o == "-w":
            conv.colSize = parseNumber(a)
        elif o == "-f":
            offset = parseNumber(a)
        elif o == "-s":
            size = parseNumber(a)
        elif o == "-h":
            showUsage = True

    nFreeArgs = len(freeargs)
    showUsage = showUsage or (nFreeArgs == 0 and rev)
    if showUsage:
        usage = """Usage:
Dump:  %(prog)s [-c columns -w bytes_per_column -f offset -s size] [in-file] [out-file]
Patch: %(prog)s -r [in-file] out-file

Arguments in rectangular brackets are optional. When optional files
are not specified, use stdout (for dump) and stdin (for patch).
Numbers can be provided as hex literals (prefixed with '0x'), octal (prefixed with '0')
or decimal (default).
        """ % { "prog": args[0] }
        message(usage)
        return 1

    fin, fout = None, None
    try:
        if rev:
            fin = open(freeargs[0], "rt") if nFreeArgs > 1 else sys.stdin
            outFn = freeargs[-1]
            writeMode = "r+b" if os.path.exists(outFn) else "wb"
            fout = open(outFn, writeMode)
            conv.text2bin(fin, fout)
        else:
            fin = open(freeargs[0], "rb") if nFreeArgs > 0 else (sys.stdin.buffer if VER3 else sys.stdin)
            fout = open(freeargs[1], "wt") if nFreeArgs > 1 else sys.stdout
            conv.bin2text(fin, fout, offset, size)
    except IOError as err:
        message("I/O error: %s, file: \"%s\"" % (err.strerror, err.filename))
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
