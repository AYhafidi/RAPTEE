#!/usr/bin/env python3
import multiprocessing as mp
import ipaddress
import random
import socket

## Fonctions de protocol Gossip


def Node(ID,IP,V,nodes):

    print(f"Je suis le noeud d'ID {ID} et d'IP : {IP} ")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, 0))  # bind to a random port on the node's IP address
    server_socket.listen()

    port = server_socket.getsockname()
    nodes[ID] = (IP, port)
    print(f"Node {ID} listening on {IP}:{port}")


def Create_Nodes(N):
    ID=100000
    nodes = {}
    for i in range(0,N):
        IP_1 = random.choice(range(0,255))
        IP_2 = random.choice(range(0,255))
        #IP = f'192.168.{IP_1}.{IP_2}'
        IP = f'127.0.0.1'
        ID+=1
        Process=mp.Process(target=Node,args=(ID,IP,[],nodes))
        
        
        Process.start()

