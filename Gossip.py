#!/usr/bin/env python3
import multiprocessing as mp
import ipaddress
import socket
from time import time
import select
import _thread
import pickle

## Fonctions de protocol Gossip
def Node(ID,IP,Server):
    c=1
    # se connecter au processus père
    socket=Node_Connect(Server[0],Server[1])
    #créer une socket d'écoute
    listen_socket=Node_listen(c,IP)
    #Les informations sur les sockets
    Info=listen_socket.getsockname()
    #préparation des données à envoyer
    Data=pickle.dumps([ID,Info[0],Info[1]]) #ID, IP, Port
    #Envoi des donées
    socket.send(Data)

    #while True:
        

        # read view received
        #view = client_socket.recv(1024).decode()

        # print message and the client's address
        #print(f"Received message '{view}' from {client_address}")

        # send a response back to other node with his view
        #response = f"Node {ID} received message '{view}'"
        #client_socket.send(response.encode())

        # close the connection with the client
        #client_socket.close()

    
    


    


def Create_Nodes(N):
    Server=Node_listen(N,"127.0.0.1")
    _thread.start_new_thread( Poll_Init, (N, Server, ) )
    #Node_poll(N,Server)
    Server_Infos=Server.getsockname()
    ID_array=ID_Array(N,10000001)
    IP_array=IP_Array(N,'127.0.0.2')
    for i in range(0,N):  
        Process=mp.Process(target=Node,args=(ID_array[i],IP_array[i],Server_Infos))
        Process.start()
        #print(f"Node:({ID_array[i]},{IP_array[i]})")
    # pour attendre 20 s
    fin = time() + 10 # l'heure actuelle + 20 (en secondes depuis epoch)
    while time()<fin:
        pass

def IP_Array(n,IP):
    IP = ipaddress.IPv4Address(IP)
    return [IP+i for i in range(n)]

def ID_Array(n,start):
    return [start+i for i in range(n)]
    
def Node_Connect(IP,Port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((IP, Port))
    except ConnectionRefusedError:
        print(f"Could not connect to node IP : {IP}, Port:{Port}")
    return client_socket

def Node_listen(N,IP):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((str(IP), 0))  # bind to a random port on the node's IP address
    try :
        server_socket.listen(N)
    except:
        print("Could not listen")
    return server_socket

def Poll_Init(N,Server_fd):
    pollerObject = select.poll()

    pollerObject.register(Server_fd, select.POLLIN)
    
    # Map file descriptors to socket objects
    fd_to_socket = { Server_fd.fileno(): Server_fd,}
    
    # Map ID to IP and Port
    Global_View={}

    fin = time() + 5 # l'heure actuelle + 20 (en secondes depuis epoch)
    while time()<fin:
        fdVsEvent = pollerObject.poll(N+1)

        for descriptor, Event in fdVsEvent:
            if descriptor==Server_fd.fileno():
                # accept connection
                client_socket, client_addr = Server_fd.accept()
                # Garde la socket dans un dict
                fd_to_socket[client_socket.fileno()]=client_socket
                # Ajouter la socket à la list des poll
                pollerObject.register(client_socket, select.POLLIN)
                #print(fd_to_socket[client_socket.fileno()])
                Event=0
            elif fd_to_socket[descriptor]!=None and Event==select.POLLIN:
                Data=fd_to_socket[descriptor].recv(100)
                if Data:
                    Infos=pickle.loads(Data)
                    Global_View[Infos[0]]=Infos[1:]
                Event=0
    print(Global_View)       



