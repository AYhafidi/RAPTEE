#!/usr/bin/env python3
import random
import socket
import time
import ipaddress



id_base = 10000
n = 100


class Node:
    def __init__(self, max_storage, id,ip):
       
        # Node info 
        self.max_storage = max_storage  # maximum storage capacity of node
        self.id = id   # Node's ID
        self.ip = ip   # Node's IP address
        self.Nu = random.sample(range(id_base, id_base+n), max_storage)  # neighbor list
        self.Su = []  # sample list
       
        # Interconnections' info
        self.neighbor_sockets_and_info = []  # Neighbors' IPs and ports 
        self.personal_neighbor_sockets = []  # Sockets on node's end
        self.neighbor_sockets = []   # Sockets on his neighbors' end
       
        # Listening socket and binding 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Listening socket
        self.sock.bind((str(self.ip), id))  # bind socket to node id 
        self.sock.listen(5)  # listen for incoming connections
        print("Node", self.id, "listening on port", id)
    
    def get_Nui(self, i):
        if i < len(self.Nu):
            return self.Nu[i]
        else:
            return None

    def get_Sui(self, i):
        if i < len(self.Su):
            return self.Su[i]
        else:
            return None
        

    def update_neighbor_list(self, Nu_t):
        # This method updates the sample list of the node with the first max_storage elements of the list Su
        self.Nu = Nu_t[:self.max_storage]  # update neighbor list with the first max_storage elements
 
    def update_sample_list(self, Su_t):
        # This method updates the sample list of the node with the first max_storage elements of the list Su
        self.Su = Su_t[:self.max_storage]  # update sample list with the first max_storage elements
 
   


# Sampling class

class Sampler:
    def __init__(self, size):
        self.h = self.minwise_hash(size)
        self.min_value = float('inf')
        self.values = set()
        
    def next(self, value):
        hash_value = self.h(value)
        if hash_value < self.min_value:
            self.min_value = hash_value
            self.values = set([value])
        elif hash_value == self.min_value:
            self.values.add(value)
            
    def sample(self):
        return random.sample(self.values, 1)[0]
    
    def minwise_hash(self, size):
        a = random.randint(1, size - 1)
        b = random.randint(0, size - 1)
        return lambda x: (a * x + b) % size
    


# Creating and initiaizing nodes

nodes = []
base_ip = ipaddress.IPv4Address('127.0.0.1')

for i in range(0, n):
    nodes.append(Node(5, id_base+i, base_ip+i))


# Connecting each node with his neighbors

for i in range(0, n):

    print ('\n  NEW NODE :')
    for j in range (0,5):

        neighbor_ip = nodes[nodes[i].Nu[j]-10000].ip   # For the initial gossip connection, the nodes know their neighbors' connexion info. This won't be the case outside of this loop

        neighbor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket for neighbor j connection  
        print('Neighbour ' + str(j+1) + ' is ' + str(nodes[i].Nu[j] - 10000))
        neighbor_sock.connect((str(neighbor_ip), nodes[i].Nu[j])) # node i connecting to neighbor j
        conn, address = nodes[nodes[i].Nu[j] - 10000].sock.accept()   # neighbour j accepting the connection 
       
        nodes[i].neighbor_sockets_and_info.append((address))   # adding neighbor's info connection : his IP and port 
        nodes[i].neighbor_sockets.append(neighbor_sock)   # adding neighbor j's socket to list of neighbor sockets
        nodes[i].personal_neighbor_sockets.append(conn)   # adding the node's socket used to communicate with that neighbor
        
        print(address) 
       
        


# Testing by sending and receiving IDs (push)

print('\n TESTING EXCHANGES :')

nodes[9].neighbor_sockets[3].send(str(nodes[9].id).encode())
print('Node ' + str(9) + ' sent his ID to his 3rd neighbor ')
string = nodes[9].personal_neighbor_sockets[3].recv(1024).decode()
print('Node ' + str(nodes[9].Nu[3]-id_base) + ' received : ' + str(string))


nodes[80].neighbor_sockets[1].send(str(nodes[80].id).encode())
print('Node ' + str(80) + ' sent his ID to his 1st neighbor ')
string = nodes[80].personal_neighbor_sockets[1].recv(1024).decode()
print('Node ' + str(nodes[80].Nu[1]-id_base) + ' received : ' + str(string))
 
