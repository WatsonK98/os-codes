#! /usr/bin/env python3

import os
import sys 

class BufferedFdReader:

    def __init__(self, fd, bufLen = 1024*16):
        self.fd = fd
        self.buf = b""
        self.index = 0
        self.bufLen = bufLen

    def readByte(self):
        if self.index >= len(self.buf):
            self.buf = os.read(self.fd, self.bufLen)
            self.index = 0
        if len(self.buf) == 0:
            return None
        else:
            retval = self.buf[self.index]
            self.index += 1
            return retval
        
    def close(self):
        os.close(self.fd)

class BufferedFdWriter:

    def __init__(self, fd, bufLen = 1024*16):
        self.fd = fd
        self.buf = bytearray(bufLen)
        self.index = 0

    def writeByte(self, bVal):
        self.buf[self.index] = bVal
        self.index += 1
        if self.index >= len(self.buf):
            self.flush()

    def flush(self):
        startIndex, endIndex = 0, self.index
        while startIndex < endIndex:
            nWritten = os.write(self.fd, self.buf[startIndex:endIndex])
            if nWritten == 0:
                os.write(2, f"buf.BufferedFdWriter(fd={self.fd}): flush failed\n".encode())
                sys.exit(1)
            startIndex += nWritten
        self.index = 0

    def close(self):
        self.flush()
        os.close(self.fd)

def framer(filename, content):
    name_bytes = filename.encode('utf-8')  # Convert filename to bytes.
    name_length = len(name_bytes)
    content_length = len(content)
    
    # Use 4 bytes for name length and 8 bytes for content length.
    name_length_bytes = name_length.to_bytes(4, 'big')  # Filename length: 4 bytes
    content_length_bytes = content_length.to_bytes(8, 'big')  # Content length: 8 bytes

    # Delimiter to separate fields.
    delimiter = b'\x00\x00\x00\x00'
    
    # Return the combined byte stream: [name_length | name | delimiter | content_length | content]
    return name_length_bytes + name_bytes + delimiter + content_length_bytes + content

def deframer(buffer):
    filename_length = int.from_bytes(buffer[:2], 'big')
    filename = buffer[2:2+filename_length].decode()
    content_length = int.from_bytes(buffer[2+filename_length:10+filename_length], 'big')
    content = buffer[10+filename_length:10+filename_length+content_length]
    return filename, content

def createArchive(output_filename, input_filenames):
    with open(output_filename, 'wb') as archive_file:
        buffered_writer = BufferedFdWriter(archive_file.fileno())
        for input_filename in input_filenames:
            with open(input_filename, 'rb') as input_file:
                content = input_file.read()
                framed_data = framer(input_filename, content)
                buffered_writer.writeByte(framed_data)
        buffered_writer.flush()

def extractArchive(archive_filename):
    with open(archive_filename, 'rb') as archive_file:
        buffered_reader = BufferedFdReader(archive_file.fileno())
        while True:
            framed_data = buffered_reader.readByte()
            if framed_data is None:
                break
            filename, content = deframer(framed_data)
            with open(filename, 'wb') as output_file:
                output_file.write(content)

command = sys.argv[1]

if command == "c":
    output_file = sys.argv[2]
    input_files = sys.argv[3:]
    createArchive(output_file, input_files)
elif command == "x":
    archive_file = sys.argv[2]
    extractArchive(archive_file)

if len(sys.argv) > 4 and sys.argv[3] == ">":
    output_file = sys.argv[4]
    with open(output_file, 'w') as redirected_output:
        sys.stdout = redirected_output
        extractArchive(sys.argv[2])
