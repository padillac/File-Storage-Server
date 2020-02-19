'''
A simple "echo" client written in Python.

author:  Amy Csizmar Dalal and [YOUR NAMES HERE]
CS 331, Spring 2018
date:  2 April 2018
'''
import sys, socket

def usage():
    print ("Usage:  python SimpleTCPClient <server IP> <port number> <message>")

def main():
    # Process command line args (server, port, message)
    if len(sys.argv) == 4:
        try:
            server = sys.argv[1]
            port = int(sys.argv[2])
            message = sys.argv[3]
            hostName = "The Computer"
        except ValueError as e:
            usage()

        serverSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        serverSock.connect((server, port))
        print ("Connected to server; sending message")

        serverSock.send(message.encode("ascii"))
        
        print ("Sent message; waiting for reply")
        
        serverSock.send(("hostName:" + hostName).encode("ascii"))
        
        print ("Sent hostname.")

        returned = serverSock.recv(1024)
        print ("Received reply: "+ returned.decode("ascii"))

        serverSock.close()

    else:
        usage()

main()