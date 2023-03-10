#!/usr/bin/env python3
import multiprocessing as mp
import ipaddress
import random

## Fonctions de protocol Gossip


def Node(ID,IP,V):

    print(f"Je suis le noeud d'ID {ID} et d'IP : {IP} ")
    
    
def Create_Nodes(N):
    ID=100000
    for i in range(0,N):
        IP_1 = random.choice(range(0,255))
        IP_2 = random.choice(range(0,255))
        IP = f'192.168.{IP_1}.{IP_2}'
        ID+=1
        Process=mp.Process(target=Node,args=(ID,IP,[],))
        
        
        Process.start()

