'''
A simple TCP "echo" server written in Python.

author:  Amy Csizmar Dalal and [YOUR NAMES HERE]
CS 331, Spring 2018
date:  2 April 2018
'''
import sys, socket

class TCPServer:
    def __init__(self, port=50000):
        self.port = port
        self.host = ""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))


    def listen(self):
        self.sock.listen(5)

        while True:
            clientSock, clientAddr = self.sock.accept()
            print ("Connection received from ",  clientSock.getpeername())

            while True:
                data = clientSock.recv(1024).decode("ascii")
                if not len(data):
                    break
                
                print ("Received message:  " + data)
                
                if data == "s":
                    clientSock.sendall(open("text.txt").read().encode("ascii"))
                if data == "h":
                    clientSock.sendall(open("text2.txt").read().encode("ascii"))
                
                if data.split(":")[0] == "hostName":
                    clientSock.sendall(("I don't want to talk to you, " + data.split(":")[1]).encode())
                
                

                clientSock.sendall(data.encode())
            clientSock.close()

def main():
    # Create a server
    if len(sys.argv) > 1:
        try:
            server = TCPServer(int(sys.argv[1]))
        except ValueError as e:
            print ("Error in specifying port. Creating server on default port.")
            server = TCPServer()
    else:
        server = TCPServer()

    # Listen forever
    print ("Listening on port " + str(server.port))
    server.listen()

main()