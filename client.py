#!/usr/bin/env python

import socket
import sys
import os

if len(sys.argv) < 3:
    print 'Usage: client.py HOST PORT'
    sys.exit(0)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
UPLOAD_COMMAND = 'upload'
DOWNLOAD_COMMAND = 'download'
BUFFER_SIZE = 2

def tcp_upload_file(filename):
    try:
        file = open(filename, "rb")
    except Exception:
        print 'File not found'
        return 1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    file_length = str(os.path.getsize(filename))
    filename_length = len(filename)

    s.send(chr(len(UPLOAD_COMMAND)))
    s.send(UPLOAD_COMMAND)
    s.send(chr(filename_length))
    s.send(filename)
    s.send(chr(len(file_length)))
    s.send(file_length)

    while True:
        msg = file.read(BUFFER_SIZE)
        if len(msg) == 0:
            break
        s.send(msg)

    file.close
    s.close

    return 0

def tcp_download_file(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    s.send(chr(len(DOWNLOAD_COMMAND)))
    s.send(DOWNLOAD_COMMAND)

    filename_length = len(filename)
    s.send(chr(filename_length))
    s.send(filename)

    file_size_length = ord(s.recv(1))

    if file_size_length == 0:
        print 'File not found'
        return 1

    file_size = int(s.recv(file_size_length, socket.MSG_WAITALL))

    file = open('old_' + filename, "wb")

    while True:
        try:
            data = s.recv(BUFFER_SIZE)
            if not data:
                break
            file.write(data)
        except Exception:
            file.close()
            print 'File Error'
            return

    file.close()
    s.close

    return 0

while True:
    command = raw_input('').rstrip('\n')
    command = str.split(command)
    if len(command) != 2:
        continue
    if command[0] == 'upload':
        tcp_upload_file(command[1])
    elif command[0] == 'download':
        tcp_download_file(command[1])
