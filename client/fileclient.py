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


def uploadFile(sock, path):
    print("Uploading {0}".format(path))

def downloadFile(sock, path):
    print("Downloading {0}".format(path))

def listDir(sock, path):
    print("Listing {0}".format(path))



def main():
    # Process command line args (server, port, message)
    try:
        server = sys.argv[1].split(":")[0]
        port = int(sys.argv[1].split(":")[1])
        option = sys.argv[2]
        if sys.argv[3]:
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
