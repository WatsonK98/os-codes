#! /usr/bin/env python3

# Echo server program

import socket, sys
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )



progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(1)              # allow only one outstanding request
# s is a factory for connected sockets

conn, addr = s.accept
print('Connected by', addr) # wait until incoming connection request (and accept it)

while True:
    data = conn.recv(1024)
    if not data:
        break
    conn.send(data)
    

conn.send(b"world")
conn.shutdown(socket.SHUT_WR)