#!/usr/bin/env python3

import Raptee
import Gossip
import Brahms
import Pyro4

node1 = Gossip.MyNode(100)
print(node1.ID)

node2 = Gossip.MyNode(101)
print(node2.ID)

daemon = Pyro4.Daemon() 
uri = []

uri1 = daemon.register(node1)  
uri2= daemon.register(node2)  

uri = [uri1, uri2]

print("Ready. Object uri =", uri)
