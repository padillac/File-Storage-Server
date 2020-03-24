
import sys, os, socket, time
from multiprocessing import Process, Lock


class FileServer:
    def __init__(self):
        self.stdoutLock = Lock()
        iface, port, storageDir = self.read_config_file()
        self.port = port
        self.host = iface
        self.storageDir = storageDir
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))


    def read_config_file(self):
        with open("fileserver.conf", 'r') as conf:
            for line in conf.readlines():
                if line[0] == '#':
                    continue
                line = line.split(":")
                if line[0].strip() == "Interface":
                    iface = line[1].strip()
                if line[0].strip() == "Port":
                    port = int(line[1].strip())
                if line[0].strip() == "StorageDirectory":
                    storageDir = line[1].strip()
        return iface, port, storageDir


    def safe_print(self, s):
        self.stdoutLock.acquire()
        print(s)
        self.stdoutLock.release()


    def looper(self):
        self.safe_print("Serving files from: {0}".format(self.storageDir))
        listenerProcess = Process(target=self.listen)
        listenerProcess.start()
        # Input handler:
        while True:
            time.sleep(.1)
            c = input(">").lower()
            
            if c == "exit":
                self.safe_print("exiting..")
                listenerProcess.terminate()
                sys.exit()
            if c == "h" or c == "help":
                self.safe_print("HELP MENU")



    def listen(self):
        
        self.safe_print("Listening on {0}:{1}..".format(self.host, self.port))
        self.sock.listen(10)

        while True:
            #initialize new socket
            newSock = socket.socket()
            newSock.bind((self.host, 0))
            freePort = newSock.getsockname()[1]

            #receive connection and start handler process
            clientSock, clientAddr = self.sock.accept()
            newSock.close()
            Process(target=self.connection_manager, args=(freePort,)).start()
            self.safe_print("\n-- New connection received from {0}".format(clientSock.getpeername()))
            
            self.safe_print("Routing to new socket on port: {0}".format(freePort))

            clientSock.sendall(str(freePort).encode())
            clientSock.close()



    def connection_manager(self, p):
        newSock = socket.socket()
        newSock.bind((self.host,p))
        newSock.settimeout(20)
        newSock.listen(0)
        self.safe_print("New handler created on {0}".format(p))
        try:
            clientSock, clientAddr = newSock.accept()
            clientDescriptor = "Client at {0} on handler {1}".format(clientAddr[0], p)
        except socket.timeout:
            self.safe_print("No connection received on handler {0}, exiting..".format(p))
            return    
        
        # Parse message and execute command
        rawdata = clientSock.recv(1024).decode("ascii").strip()
        if not rawdata:
            clientSock.close()
            return
        
        msg = rawdata.split()

        self.safe_print("{0} sent message: {1}".format(clientDescriptor, str(msg)))

        # List files
        if msg[0] == "l":
            if len(msg) > 1:
                path = os.path.join(self.storageDir, msg[1])
            else:
                path = self.storageDir
            self.safe_print("{0} requested directory contents of {1}".format(clientDescriptor, path))
            if not os.path.isdir(path):
                clientSock.sendall("Error: requested directory does not exist".encode())
                self.safe_print("!-- Error: {0} requested to list directory that does not exist: {1}".format(clientDescriptor, path))
                clientSock.close()
                return

            fileList = os.listdir(path)
            if len(fileList) == 0:
                response = "<Empty>"
            else:
                response = ""
                for f in fileList:
                    response += f + "\n"
            clientSock.sendall("ok".encode())
            time.sleep(0.0001)
            self.safe_print("Sending directory contents of {0} to {1}".format(path, clientDescriptor))
            clientSock.sendall(response.encode())


        # Download file
        if msg[0] == 'd':
            filePath = os.path.join(self.storageDir, msg[1])
            if not os.path.isfile(filePath):
                clientSock.sendall("Error: file does not exist".encode())
                self.safe_print("!-- Error: {0} requested file that does not exist: {1}".format(clientDescriptor, filePath))
                clientSock.close()
                return
            self.safe_print("{0} requested file: {1}".format(clientDescriptor, filePath))
            try:
                with open(filePath, 'rb') as f:
                    clientSock.sendall("ok".encode())
                    clientSock.sendfile(f)
                    self.safe_print("Sent file.")
                    clientSock.close()
            except:
                self.safe_print("!-- Error sending requested file {0} to {1}".format(filePath, clientDescriptor))
                clientSock.close()
                return


        # Upload file
        if msg[0] == 'u':
            filePath = os.path.join(self.storageDir, msg[1])
            self.safe_print("{0} wants to upload file: {1}".format(clientDescriptor, filePath))
            if os.path.exists(filePath):
                self.safe_print("!-- File {0} already exists, cannot be uploaded ({1})".format(filePath, clientDescriptor))
                clientSock.sendall("!-- File {0} already exists, cannot be uploaded ({1})".format(filePath, clientDescriptor).encode())
                clientSock.close()
                return
            with open(filePath, 'wb') as f:
                clientSock.sendall("ok".encode())
                f.write(clientSock.recv(4096))
            self.safe_print("Uploaded file {0}".format(filePath))
            


        self.safe_print("--closing connection {0}--".format(clientSock))
        clientSock.close()
        return




############################################ REDO MAIN FUNCTION FOR BETTER COMMAND LINE FUNCTIONALITY
def main():
    print("Starting file storage server.\nType 'help' for help menu or 'exit' to close the program.")
    # Create a server
    server = FileServer()
        
    # Start main handler loop
    server.looper()


if __name__ == "__main__":
    main()
