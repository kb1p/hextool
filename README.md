# hextool
Cross-platform utility to create hex dumps and patching binary files.

- Requires Python (compatible with versions 2.7 and 3+)
- Inspired by (not copypasted from) linux utility *xxd* authored by Juergen Weigert

## Usage examples

1. Dump all contents of a file "foo.bar" to stdout with default layout (8 columns, 2 bytes per column):  
`$ python htl.py foo.bar`

2. Same as (1) but with 5 columns, 4 bytes per column:  
`$ python htl.py -c 5 -w 4`

3. Dump to stdout 100 bytes of a file "foo.bar" starting with 256th byte (default layout):  
`$ python htl.py -f 0x100 -s 100 foo.bar`

4. Edit binary file "foo.bar":  
`$ python htl.py foo.bar foo.bar.txt`  
(edit file "foo.bar.txt", don't change spaces; only hex data modifications will be taken into account when patching)  
`$ python htl.py -r foo.bar.txt foo.bar`

5. Patching of a binary file "foo.bar":  
5.1. Create a text file "foo.bar.patch", fill it with lines of text each having the following layout:  
`[<offset>:] <data-chunk> <data-chunk> ... <data-chunk>  <comment>`  
where:  
**offset** is an optional offset in the binary file where the data will be placed. It is separated from the data part with colon. If omitted, writing will continue from the offset on the previous line + size of the data on the previous line. If the offset is not specified on the first line of the patch file, its data will be put to the beginning of the file.  
**data-chunk** is a hex string representing the bytes that will be written starting at *offset*. Data chunks may be separated from each other and the offset with no more than *one* space. Spaces are allowed for compatibility with the dump; it's okay to write a single hex string without spaces.  
**comment** is an arbitrary text starting with the first occurence *two* or more sequential spaces. When hextool detects two sequential spaces on the line it ignores everything to the end of this line.  
Empty lines are ignored.  
5.2. Apply the patch to the file:  
`$ python htl.py -r foo.bar.patch foo.bar`

### Note
Always backup your files before editing them with this hextool as they may become corrupted due to a program bug or misuse.

## Limitations
- No endianness support (bytes are dumped in order they appear in file or stdin)
- No special "repeat previous line" support in patching mode
- Patching mode can't write to stdout (only to files)
- Poor performance when dumping / creating big files (partial dumping and patching can be helpful in this case)