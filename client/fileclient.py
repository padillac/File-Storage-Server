#!/usr/bin/env python3

import sys, os, socket, time

def usage():
    print ("Usage: python fileclient.py hostname:port [options]\n\nOptions:\n\t-u FILE\t\tUpload file to server\n\t-d FILE\t\tDownload file from server\n\t-l [DIR]\tView files in DIR, or server root if no DIR.")


def makeConnection(server, port):
    try:
        serverSock = socket.socket()
        serverSock.connect((server, port))
        handlerPort = int(serverSock.recv(1024).decode())
    except:
        print("Could not connect to server at {0}:{1}".format(server, port))
        sys.exit(1)
    try:
        handlerSock = socket.socket()
        handlerSock.connect((server, handlerPort))
    except:
        try:
            time.sleep(.001)
            handlerSock = socket.socket()
            handlerSock.connect((server, handlerPort))
        except:
            try:
                time.sleep(.5)
                handlerSock = socket.socket()
                handlerSock.connect((server, handlerPort))
            except:
                print("Connected to server, but could not connect to request handler at {0}:{1}".format(server, handlerPort))
                sys.exit(1)
    return handlerSock


def listDir(sock, path):
    if path == None:
        path = '.'
    try:
        print("Listing {0}..".format(path))
        sock.sendall("l {0}".format(path).encode())
        resp = sock.recv(100).decode()
        if resp != "ok":
            print("Error message from server: {0}".format(resp))
            sys.exit(1)
        data = sock.recv(4096).decode()
        if path == '.':
            path = "server root"
        print("Directory listing for {0}:\n".format(path))
        print(data)
    except SystemExit:
        sys.exit(1)
    except:
        print("Error receiving directory contents from server.")

def downloadFile(sock, path):
    localPath = path.split("/")[-1]
    try:
        print("Downloading {0}, saving to: {1}..".format(path, localPath))
        sock.sendall("d {0}".format(path).encode())
        resp = sock.recv(100).decode().split()
        if resp[0] != "ok":
            print("Error message from server: {0}".format(resp))
            sys.exit(1)
        with open(localPath, "wb") as f:
            size = int(resp[1])
            data = b''
            while len(data) < size:
                remaining = size - len(data)
                data += sock.recv(8192 if remaining > 8192 else remaining)
                print("Downloading {0}/{1} bytes..".format(len(data), size), end="\r")
            f.write(data)
            print()
    except SystemExit:
        sys.exit(1)
    except:
        print("Error downloading file from server.")

def uploadFile(sock, path):
    remotePath = path.split("/")[-1]
    if not os.path.isfile(path):
        print("Error: Could not find file: {0}".format(path))
        sys.exit(1)
    try:
        with open(path, "rb") as f:
            size = os.fstat(f.fileno()).st_size
            print("Uploading {0}, ({1} bytes) to remote location: {2}..".format(path, size, remotePath))
            sock.sendall("u {0} {1}".format(remotePath, size).encode())
            resp = sock.recv(100).decode()
            if resp != "ok":
                print("Error message from server: {0}".format(resp))
                sys.exit(1)
            sock.sendfile(f)
            ack = sock.recv(100).decode()
            if ack.split()[0] != "ok":
                print("Error received from server: {0}".format(ack))
                sys.exit(1)
            print("{0}/{1} bytes received by server.".format(ack.split()[1], size))
    except SystemExit:
        sys.exit(1)
    except:
        print("Error uploading file to server.")



def main():
    # Validate and process command line args (server, port, message)
    try:
        server = sys.argv[1].split(":")[0]
        port = int(sys.argv[1].split(":")[1])
        option = sys.argv[2]
        if len(sys.argv) == 4:
            target = sys.argv[3]
        else:
            target = None
    except:
        usage()
        sys.exit(1)
    if option not in ["-u", "-d", "-l"]:
        usage()
        sys.exit(1)

    # Connect to server and initiate transaction
    handlerSock = makeConnection(server, port)

    if option == "-u":
        uploadFile(handlerSock, target)
    if option == "-d":
        downloadFile(handlerSock, target)
    if option == "-l":
        listDir(handlerSock, target)
    

    print("done.")
    sys.exit()


main()
