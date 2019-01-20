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
`[<offset>:] <data-chunk> <data-chunk> ... <data-chunk><delimiter><comment>`  
where:  
**offset** is an optional offset in the binary file where the data will be placed. It is separated from the data part with colon. If omitted, writing will continue from the offset on the previous line + size of the data on the previous line. If the offset is not specified on the first line of the patch file, its data will be put to the beginning of the file.  
**data-chunk** is a sequence of hex digits representing the bytes that will be written to the output file starting at *offset*. The number of hex digits in a chunk must always be even because two hex digits represent a single byte. Chunks are separated by spaces; it's also okay to write data as a single chunk, without spaces. Please note that without explicit delimiter specification (`-d` command line option), two sequential spaces are treated as a *delimiter* (see below) and all text after two sequential spaces is ignored, so no more than one space should be used to separate chunks in that case. Explicit specification of the delimiter allows to remove this limitation.  
**delimiter**: any sequence of characters specified as an argument to the `-d` command line option; all text following this sequence to the end of the current line will be ignored  
**comment** is an arbitrary text starting with the first occurence *delimiter* (two spaces by default, controlled by `-d` command line option) and ending at the line end. Comments are simply ignored, they were added only for compatibility with the dump text format.  
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