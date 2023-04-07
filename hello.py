#!/usr/bin/env python3
import random
import socket
import time
import ipaddress
from Orchest import *
import sys
import threading



class Node:
    def __init__(self, max_storage, id,ip):
       
        # Node info 
        self.max_storage = max_storage  # maximum storage capacity of node
        self.id = id   # Node's ID
        self.ip = ip   # Node's IP address
        self.Nu = random.sample(range(id_base,id_base+n),max_storage)  # neighbor list
        self.Su = []  # sample list
       
        # Interconnections' info
        self.neighbor_sockets_and_info = {}  # Neighbors' IPs and ports 
       
        # Listening socket and binding 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Listening socket
        self.sock.bind((str(self.ip), 0))  # bind socket to node id
        self.port=self.sock.getsockname()[1] 
        self.sock.listen(max_storage)  # listen for incoming connections
        #print("Node", self.id, "listening on port", self.port)
    
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
                                                               
          


# machine_socks=[]
# s=0
# for i in machine_sock
#     machine_socks.append(machine_sock[s][1])
#     s=s+1
#     print(i)
# print(machine_socks)

          
# def Poll_machines_function(machine_socks):
#     # Initialisation
#     pollerObject = select.poll()

#     # Adding sockets
#     for sock in machine_socks:
#         pollerObject.register(sock, select.POLLIN)

#     # Traiter les données
#     while True:
#         fdVsEvent = pollerObject.poll()

#         for descriptor, Event in fdVsEvent:
#             index = machine_socks.index(descriptor)
#             if Event & select.POLLIN:
#                 data = os.read(descriptor, 2048).decode()
#                 print(f"Received data from socket {index}: {data}")
#             elif Event & select.POLLERR:
#                 print(f"Error reading data from socket {index}")
#                 pollerObject.unregister(descriptor)
#                 descriptor.close()
#                 machine_socks.remove(descriptor)




# t = threading.Thread(target=Poll_machines_function, args=(machine_socks,))
# t.start()
                

        





 ##### Parameters #####

id_base=int(sys.argv[3])
n=int(sys.argv[4])
max_storage=int(sys.argv[5])
base_ip=ipaddress.IPv4Address(sys.argv[6])
# print(f"id_base :{id_base}\nN : {n}\nmax_storage : {max_storage}\nip_adress : {base_ip}")
sys.stdout.flush()



##### Initialisation des connexions #####


machine_socks=Net_init()
print(machine_socks)




                              
    
    
    
         







def sending_and_receiving(node, num_neighbour, data):
    send_data(node.neighbor_sockets_and_info[node.Nu[num_neighbour]][1],data)
    print(f"Node :{node.id - id_base} sent his ID to his {num_neighbour+1} neighbor")
    string=recv_data(node.neighbor_sockets_and_info[node.Nu[num_neighbour]][2],1024)
    print('Node ' + str(node.Nu[num_neighbour]-id_base) + ' received : ' + str(string))
    sys.stdout.flush()
    sys.stderr.flush()
     

# Creating and initiaizing nodes




# Nodes
# base_ip = ipaddress.IPv4Address('127.0.0.1')
nodes=[Node(n, id_base+i, base_ip+i) for i in range(n)]


for i in range(0, n):
    # print ('\n  NEW NODE :')
    for j in range (0,max_storage):
        neighbor_id=nodes[i].Nu[j]
        neighbor_ip = nodes[neighbor_id-id_base].ip   # For the initial gossip connection, the nodes know their neighbors' connexion info. This won't be the case outside of this loop
        neighbour_port = nodes[nodes[i].Nu[j]-id_base].port
        neighbor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket for neighbor j connection  
        # print('Neighbour ' + str(j+1) + ' is ' + str(nodes[i].Nu[j] - 10000))
        neighbor_sock.connect((str(neighbor_ip), neighbour_port )) # node i connecting to neighbor j
        conn, address = nodes[nodes[i].Nu[j] - id_base].sock.accept()   # neighbour j accepting the connection 
        Port=conn.getsockname()[1]
        nodes[i].neighbor_sockets_and_info[neighbor_id]=[[neighbor_ip,neighbour_port], neighbor_sock, conn]   # adding neighbor's info connection : his [IP,port],  
        
    

# # Testing by sending and receiving IDs (push)

# print('\n TESTING EXCHANGES :')


sending_and_receiving(nodes[1], 0, nodes[1].id)
# nodes[80].neighbor_sockets[1].send(str(nodes[80].id).encode())
# print('Node ' + str(80) + ' sent his ID to his 1st neighbor ')
# string = nodes[80].personal_neighbor_sockets[1].recv(1024).decode()
# print('Node ' + str(nodes[80].Nu[1]-id_base) + ' received : ' + str(string))

while(1):
    continue