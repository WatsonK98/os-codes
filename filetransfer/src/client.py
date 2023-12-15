#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os
sys.path.append("../lib")       # for params
import params

from mytar import createArchive, extractArchive

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage  = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)

while 1:
    userInput = input("Enter command (stop to close): ")
    if userInput.lower() == "stop":
        break

    if userInput.startswith("send "):
        _, *input_files = userInput.split()

        createArchive("temp.dat", input_files)

        with open("temp_archive.dat", "rb") as archive_file:
            archive_data = archive_file.read()
            s.send(archive_data)

        data = s.recv(1024)
        print("Server response: ", data.decode())

        os.remove("temp.dat")

    elif userInput.startswith("receive "):
        _, archive_filename = userInput.split()

        s.send(userInput.encode())

        archive_data = s.recv(1024)

        with open("received.dat", "wb") as received_file:
            received_file.write(archive_data)

        extractArchive("received.dat")

        os.remove("received.dat")
    
    else:
        s.send(userInput.encode())
    
    if not userInput.startswith("send ") and not userInput.startswith("receive "):
        data = s.recv(1024)
        print("Server response: ", data.decode())

s.shutdown(socket.SHUT_WR)
