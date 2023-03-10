#!/usr/bin/env python3
import multiprocessing as mp

## Fonctions de protocol Gossip


def Node(ID,V):

    print(f"Je suis le noeud d'ID : {ID}")
    
def Create_Nodes(N):
    ID=100001
    for i in range(0,N):
        Process=mp.Process(target=Node,args=(ID,[],))
        ID+=1
        Process.start()