#!/usr/bin/env python3

import socket
import sys
import os

if len(sys.argv) < 3:
    print('Usage: server.py HOST PORT')
    sys.exit(0)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
UPLOAD_COMMAND = 'upload'
DOWNLOAD_COMMAND = 'download'
BUFFER_SIZE = 100

class LastClient:
    addr = ''
    file_name = ''
    command = ''

    @classmethod
    def print_variables(self):
        print(self.addr)
        print(self.file_name)
        print(self.command)

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
    file_offset_length = ord(conn.recv(1).decode())
    file_offset = int(conn.recv(file_offset_length, socket.MSG_WAITALL).decode())

    try:
        file = open(filename, "rb")
    except Exception:
        print('File not found')
        conn.send(chr(0).encode()) # send file size
        return 1

    file_length = os.path.getsize(filename)
    file_length -= file_offset
    file_length = str(file_length)

    conn.send(chr(len(file_length)).encode())
    conn.send(file_length.encode())

    file.seek(file_offset)

    while True:
        msg = file.read(BUFFER_SIZE)
        if len(msg) == 0:
            break
        conn.send(msg)

    file.close

    return 0

def tcp_download_file(conn):
    received_bytes = 0

    filename_length = ord(conn.recv(1).decode())
    filename = conn.recv(filename_length, socket.MSG_WAITALL).decode()

    file_offset = str(get_file_offset('new_' + filename))
    file_offset = str(file_offset)
    conn.send(chr(len(file_offset)).encode())
    conn.send(file_offset.encode())

    LastClient.file_name = filename

    file = open('new_' + filename, get_file_mode(file_offset))

    file_size_length = ord(conn.recv(1).decode())
    file_length = int(conn.recv(file_size_length, socket.MSG_WAITALL).decode())

    oob_messages = 0

    while True:
        try:
            data = conn.recv(1, socket.MSG_OOB).decode()
        except Exception:
            data = None        
        if data:
            print('Received: ', data)
            oob_messages += 1

        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            file.write(data)
            received_bytes += len(data)
        except Exception:
            file.close()
            print('File Error')
            return

    print(oob_messages)
    file.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.settimeout(360)
s.listen(1)

while True:
    conn, addr = s.accept()
    #print('Connection address:', addr)
    #LastClient.print_variables()

    LastClient.addr = addr[0]

    try:
        command_length = ord(conn.recv(1).decode())
    except Exception:
        continue

    command = conn.recv(command_length, socket.MSG_WAITALL).decode()

    if command == UPLOAD_COMMAND:
        LastClient.command = UPLOAD_COMMAND
        tcp_download_file(conn)
    elif command == DOWNLOAD_COMMAND:
        LastClient.command = DOWNLOAD_COMMAND
        filename_length = ord(conn.recv(1).decode())
        filename = conn.recv(filename_length, socket.MSG_WAITALL).decode()
        LastClient.file_name = filename
        tcp_upload_file(conn, filename)

    conn.close()
