#!/usr/bin/env python3
import random
import socket
import time
import ipaddress
from Orchest import *
import sys
import threading
import select
import os



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
        self.port=self.sock.getsockname()[1]
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



def polling_nodes(listening_sock):
    

    pollerObject = select.poll()

    # Adding sockets
    pollerObject.register(listening_sock, select.POLLIN)
    while True:
        fdVsEvent = pollerObject.poll()

        for descriptor, Event in fdVsEvent:
            
            if Event==select.POLLIN:
               
                Acc_sock, addr=listening_sock.accept()
                

            


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


print(Nodes_infos[10008][1])



sys.stdout.flush()



node_threads=[]
for i in range (0,n):

    node_threads = node_threads + [threading.Thread(target=polling_nodes, args=(nodes[i+id_base].sock,))]


print('We are at the hostname :' + str(socket.gethostname()))


for i in range (0,n):
    
    print('We are at the i :' + str(i))
    
    try:
        
        node_threads[i].start()

        for j in range (0,max_storage):
            
            neighbor_id=nodes[i+id_base].Nu[j]
            
            print('Neighbour_id ' + str(neighbor_id))
         
            neighbor_ip = Nodes_infos[neighbor_id][0] 
        
            neighbour_port = Nodes_infos[neighbor_id][1] 
           
            print('neighbour_id ' + str(neighbor_id)+ ' neighbor ip ' + neighbor_ip + ' neighbor port ' + str(neighbour_port))
            
            Gossip_connect(neighbor_ip, neighbour_port)
    
        
    except Exception as e:
        
        print(e)
        
        sys.stdout.flush()
    




    

# # # Testing by sending and receiving IDs (push)

# for i in range(0, n):
#     # print ('\n  NEW NODE :')
   
#     for j in range (0,max_storage):
#         neighbor_id=nodes[i+id_base].Nu[j]
#         print("PARRRRRRR start")
#         print('key of node is '+str(neighbor_id))
       
#         neighbor_ip = Nodes_infos[neighbor_id][0]   # For the initial gossip connection, the nodes know their neighbors' connexion info. This won't be the case outside of this loop
       
      
#         neighbour_port = Nodes_infos[neighbor_id][1]
        
     
#         neighbor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket for neighbor j connection  
       
#         try:
#             neighbor_sock.connect((str(neighbor_ip), neighbour_port )) # node i connecting to neighbor j
#         except Exception as e:
#             print(e)
#             sys.stdout.flush()
        
#         conn, address = nodes[nodes[id_base+i].Nu[j]].sock.accept()   # neighbour j accepting the connection 
        
#         try:
#             conn, address = nodes[nodes[id_base+i].Nu[j]].sock.accept()   # neighbour j accepting the connection 
#         except Exception as e:
#             print(e)
#             sys.stdout.flush()
        



#         Port=conn.getsockname()[1]
      
#         nodes[id_base+i].neighbor_sockets_and_info[neighbor_id]=[[neighbor_ip,neighbour_port], neighbor_sock, conn]   # adding neighbor's info connection : his [IP,port],  
#         print("PARRRRRRR end")
      
    

while(1):
    continue