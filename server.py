#!/usr/bin/env python

import socket
import sys
import os

if len(sys.argv) < 3:
    print 'Usage: server.py HOST PORT'
    sys.exit(0)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
UPLOAD_COMMAND = 'upload'
DOWNLOAD_COMMAND = 'download'
BUFFER_SIZE = 5

class LastClient:
    addr = ''
    file_name = ''
    command = ''

    @classmethod
    def print_variables(self):
        print self.addr
        print self.file_name
        print self.command

def get_file_offset(filename):
    try:
        return os.path.getsize(filename)
    except Exception:
        return 0

def get_file_mode(file_offset):
    if file_offset == '0':
        return 'wb'
    else:
        return 'ab'

def tcp_upload_file(conn, filename):
    file_offset_length = ord(conn.recv(1))
    file_offset = int(conn.recv(file_offset_length, socket.MSG_WAITALL))

    try:
        file = open(filename, "rb")
    except Exception:
        print 'File not found'
        conn.send(chr(0)) # send file size
        return 1

    file_length = os.path.getsize(filename)
    file_length -= file_offset
    file_length = str(file_length)

    conn.send(chr(len(file_length)))
    conn.send(file_length)

    file.seek(file_offset)

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

    file_offset = str(get_file_offset('new_' + filename))
    file_offset = str(file_offset)
    conn.send(chr(len(file_offset)))
    conn.send(file_offset)

    LastClient.file_name = filename

    file = open('new_' + filename, get_file_mode(file_offset))

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
    #print 'Connection address:', addr
    #LastClient.print_variables()

    LastClient.addr = addr[0]

    try:
        command_length = ord(conn.recv(1))
    except Exception:
        continue

    command = conn.recv(command_length, socket.MSG_WAITALL)

    if command == UPLOAD_COMMAND:
        LastClient.command = UPLOAD_COMMAND
        tcp_download_file(conn)
    elif command == DOWNLOAD_COMMAND:
        LastClient.command = DOWNLOAD_COMMAND
        filename_length = ord(conn.recv(1))
        filename = conn.recv(filename_length, socket.MSG_WAITALL)
        LastClient.file_name = filename
        tcp_upload_file(conn, filename)

    conn.close()
