#!/usr/bin/env python3
import Pyro4

HOST = 'localhost'  
PORT = 5000  

nodes = []  

class MyNode():
    def __init__(self):
        print("Hello! ")




node = MyNode()

daemon = Pyro4.Daemon()  
uri = daemon.register(node)  

print("Ready. Object uri =", uri)

ns = Pyro4.locateNS()  # Récupère une référence vers le serveur de noms Pyro
ns.register("client", uri)  # Enregistre le client auprès du serveur de noms



