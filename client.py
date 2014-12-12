#!/usr/bin/env python3

import socket
import sys
import os
import random

if len(sys.argv) < 3:
    print('Usage: client.py HOST PORT')
    sys.exit(0)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
UPLOAD_COMMAND = 'upload'
DOWNLOAD_COMMAND = 'download'
BUFFER_SIZE = 100

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

def tcp_upload_file(filename):
    sent_bytes = 0

    try:
        file = open(filename, "rb")
    except Exception:
        print('File not found')
        return 1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    file_length = os.path.getsize(filename)
    filename_length = len(filename)

    s.send(chr(len(UPLOAD_COMMAND)).encode())
    s.send(UPLOAD_COMMAND.encode())
    s.send(chr(filename_length).encode())
    s.send(filename.encode())

    file_offset_length = ord(s.recv(1).decode())
    file_offset = int(s.recv(file_offset_length, socket.MSG_WAITALL).decode())

    file_length -= file_offset
    file_length = str(file_length)

    s.send(chr(len(file_length)).encode())
    s.send(file_length.encode())

    file.seek(file_offset)

    oob_messages = 0
    oob_message = 97

    while True:
        oob_message = chr(oob_message)
        s.send(str(oob_message).encode(), socket.MSG_OOB)
        oob_message = ord(oob_message)
        print('Sent: ', chr(oob_message))
        oob_messages += 1

        if oob_message < ord('z'):
            oob_message += 1
        else:
            oob_message = 97

        msg = file.read(BUFFER_SIZE)
        if len(msg) == 0:
            break
        s.send(msg)
        sent_bytes += len(msg)

    print(oob_messages)

    file.close
    s.close

    return 0

def tcp_download_file(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    s.send(chr(len(DOWNLOAD_COMMAND)).encode())
    s.send(DOWNLOAD_COMMAND.encode())

    filename_length = len(filename)
    s.send(chr(filename_length).encode())
    s.send(filename.encode())

    file_offset = str(get_file_offset('old_' + filename))
    file_offset = str(file_offset)
    s.send(chr(len(file_offset)).encode())
    s.send(file_offset.encode())

    file_size_length = ord(s.recv(1).decode())

    if file_size_length == 0:
        print('File not found')
        return 1

    file_size = int(s.recv(file_size_length, socket.MSG_WAITALL).decode())

    file = open('old_' + filename, get_file_mode(file_offset))

    while True:
        try:
            data = s.recv(BUFFER_SIZE)
            if not data:
                break
            file.write(data)
        except Exception:
            file.close()
            print('File Error')
            return

    file.close()
    s.close

    return 0

while True:
    command = input('').rstrip('\n')
    command = str.split(command)
    if len(command) != 2:
        continue
    if command[0] == UPLOAD_COMMAND:
        tcp_upload_file(command[1])
    elif command[0] == DOWNLOAD_COMMAND:
        tcp_download_file(command[1])
