#!/usr/bin/env python3
import random
import socket
import time
import ipaddress
from Orchest import *
import sys
import threading
import select



class Node:
    def __init__(self, max_storage, n, id):
       
        # Node info 
        self.max_storage = max_storage  # maximum storage capacity of node
        self.id = id   # Node's ID
        self.ip = socket.gethostname()   # Node's IP address
        self.Nu = random.sample(range(id_base,id_base+n),max_storage)  # neighbor list
        self.Su = []  # sample list
       
        # Interconnections' info
        self.neighbor_sockets_and_info = {}  # Neighbors' IPs and ports 
       
        # Listening socket and binding 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Listening socket
        self.sock.bind((self.ip, 0))  # bind socket to node id
        self.port=self.sock.getsockname()
        self.sock.listen(n)  # listen for incoming connections
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
                                                               
          


                                                ##### Parameters #####

id_base=int(sys.argv[3])
n=int(sys.argv[4])
max_storage=int(sys.argv[5])


                                        ##### Initialisation des connexions #####


Orchest_sock, Nmbr_procs=Net_init()
    

def sending_and_receiving(node, num_neighbour, data):
    send_data(node.neighbor_sockets_and_info[node.Nu[num_neighbour]][1],data)
    print(f"Node :{node.id - id_base} sent his ID to his {num_neighbour+1} neighbor")
    string=recv_data(node.neighbor_sockets_and_info[node.Nu[num_neighbour]][2],1024)
    print('Node ' + str(node.Nu[num_neighbour]-id_base) + ' received : ' + str(string))
    sys.stdout.flush()
    sys.stderr.flush()

# Creating and initiaizing nodes
nodes={id_base+i : Node(max_storage, n*Nmbr_procs, id_base+i) for i in range(n)}
Local_Nodes_infos={Id:[nodes[Id].ip, nodes[Id].port] for Id in nodes}

# Sending Nodes info to Orchestrator
try :
    Size=sys.getsizeof(pickle.dumps((Local_Nodes_infos)))
    send_data(Orchest_sock,Size)
    send_data(Orchest_sock,Local_Nodes_infos)
except:
    print("Couldn't send")
    sys.stdout.flush()

# Recieving Nodes infos Size
Size=recv_data(Orchest_sock, 1024)
print(f"Size : {Size}")
sys.stdout.flush()

# Recieving Nodes infos
size_recv=0
data=b""
while size_recv<Size:
    parcket=Orchest_sock.recv(1024)
    sys.stdout.flush()
    size_recv+=sys.getsizeof(parcket)
    data+=parcket
Nodes_infos=pickle.loads(data)
print(Nodes_infos)
sys.stdout.flush()







# print(Nodes_infos)
# sys.stdout.flush()
# for i in range(0, n):
#     # print ('\n  NEW NODE :')
#     for j in range (0,max_storage):
#         neighbor_id=nodes[i].Nu[j]
#         neighbor_ip = nodes[neighbor_id-id_base].ip   # For the initial gossip connection, the nodes know their neighbors' connexion info. This won't be the case outside of this loop
#         neighbour_port = nodes[nodes[i].Nu[j]-id_base].port
#         neighbor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket for neighbor j connection  
#         neighbor_sock.connect((str(neighbor_ip), neighbour_port )) # node i connecting to neighbor j
#         conn, address = nodes[nodes[i].Nu[j] - id_base].sock.accept()   # neighbour j accepting the connection 
#         Port=conn.getsockname()[1]
#         nodes[i].neighbor_sockets_and_info[neighbor_id]=[[neighbor_ip,neighbour_port], neighbor_sock, conn]   # adding neighbor's info connection : his [IP,port],  
        
    

# # # Testing by sending and receiving IDs (push)

# sending_and_receiving(nodes[1], 0, nodes[1].id)

while(1):
    continue