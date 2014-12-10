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
BUFFER_SIZE = 5

def tcp_upload_file(conn, filename):
    try:
        file = open(filename, "rb")
    except Exception:
        print 'File not found'
        conn.send(chr(0))
        return 1

    file_length = str(os.path.getsize(filename))

    conn.send(chr(len(file_length)))
    conn.send(file_length)

    print file_length

    while True:
        msg = file.read(BUFFER_SIZE)
        if len(msg) == 0:
            break
        conn.send(msg)

    file.close

    return 0

def tcp_download_file(conn):
    filename_length = ord(conn.recv(1))
    filename = conn.recv(filename_length, socket.MSG_WAITALL)

    file = open('new_' + filename, "wb")

    file_size_length = ord(conn.recv(1))
    file_length = int(conn.recv(file_size_length, socket.MSG_WAITALL))

    while True:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            file.write(data)
        except Exception:
            file.close()
            print 'File Error'
            return

    file.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.settimeout(360)
s.listen(1)

while True:
    conn, addr = s.accept()
    print 'Connection address:', addr

    try:
        command_length = ord(conn.recv(1))
    except Exception:
        continue

    command = conn.recv(command_length, socket.MSG_WAITALL)

    if command == UPLOAD_COMMAND:
        tcp_download_file(conn)
    elif command == DOWNLOAD_COMMAND:
        filename_length = ord(conn.recv(1))
        filename = conn.recv(filename_length, socket.MSG_WAITALL)
        print filename
        tcp_upload_file(conn, filename)

    conn.close()
