import sys, socket, time

def usage():
    print ("Usage: python fileclient.py hostname:port [options]\n\nOptions:\n\t-u FILE\tUpload file to server\n\t-d FILE\tDownload file from server\n\t-l [DIR]\tView files in DIR, or server root if no DIR.")


def makeConnection(server, port):
    try:
        serverSock = socket.socket()
        serverSock.connect((server, port))
        handlerPort = int(serverSock.recv(1024).decode())
        print("handler:", handlerPort)
    except:
        print("Could not connect to server at {0}:{1}".format(server, port))
        sys.exit(1)
    try:
        handlerSock = socket.socket()
        handlerSock.connect((server, handlerPort))
    except:
        try:
            time.sleep(.0001)
            handlerSock = socket.socket()
            handlerSock.connect((server, handlerPort))
        except:
            try:
                time.sleep(.5)
                handlerSock = socket.socket()
                handlerSock.connect((server, handlerPort))
            except:
                print("Could not connect to handler at {0}:{1}".format(server, handlerPort))
                sys.exit(1)
    return handlerSock


def listDir(sock, path):
    if path == None:
        path = '.'
    try:
        print("Listing {0}".format(path))
        sock.sendall("l {0}".format(path).encode())
        resp = sock.recv(1024).decode()
        if resp != "ok":
            print("Error message from server: {0}".format(resp))
            sys.exit(1)
        data = sock.recv(1024).decode()
        print("Directory listing for {0}:\n".format(path))
        print(data)
    except:
        print("Error downloading file from server.")

def downloadFile(sock, path):
    try:
        print("Downloading {0}".format(path))
        sock.sendall("d {0}".format(path).encode())
        resp = sock.recv(1024).decode()
        if resp != "ok":
            print("Error message from server: {0}".format(resp))
            sys.exit(1)
        with open(path, "wb") as f:
            f.write(sock.recv(1024))
    except:
        print("Error downloading file from server.")

def uploadFile(sock, path):
    try:
        print("Uploading {0}".format(path))
        sock.sendall("u {0}".format(path).encode())
        resp = sock.recv(1024).decode()
        if resp != "ok":
            print("Error message from server: {0}".format(resp))
            sys.exit(1)
        with open(path, "rb") as f:
            sock.sendfile(f)
    except:
        print("Error uploading file to server.")



def main():
    # Process command line args (server, port, message)
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

    print("server: {0}, port: {1}, option: {2}, target: {3}".format(server, port, option, target))

    handlerSock = makeConnection(server, port)

    if option == "-u":
        uploadFile(handlerSock, target)
    elif option == "-d":
        downloadFile(handlerSock, target)
    elif option == "-l":
        listDir(handlerSock, target)

    print("done.")
    sys.exit()



main()
