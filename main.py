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
    def __init__(self, max_storage, id):
       
        # Node info 
        self.max_storage = max_storage  # maximum storage capacity of node
        self.id = id   # Node's ID
        self.ip = socket.gethostname()   # Node's IP address
        self.Nu = random.sample(range(id_base-n*proc_id,id_base+n*(Nmbr_procs-proc_id)),max_storage)  # neighbor list
        self.Su = []  # sample list
        
        # Interconnections' info
        
        self.neighbor_sockets = []
        self.neighbor_personal_sockets = []
       
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


Orchest_sock, Nmbr_procs, proc_id = Net_init()
    

# def echo_server(sockfd):
#     MSG_LEN = 10*1024
#     print("MOUUUR MSG LEN")
#     while True:
#         print("ÇBEL RECEIVE")
#         # Receiving message
#         data = sockfd.recv(MSG_LEN)
#         print("mouraaaaaaaaaah")
#         if not data:
#             print("HNAAAAAAYAAAAA")
#             break
        
#         else:
#             print(data)

        
        
        
# def on_new_client(clientsocket,addr):
#     while True:
#         msg = clientsocket.recv(1024)
#         #do some checks and if msg == someWeirdSignal: break:
#         print addr, ' >> ', msg
#         msg = raw_input('SERVER >> ')
#         #Maybe some code to compute the last digit of PI, play game or anything else can go here and when you are done.
#         clientsocket.send(msg)
#     clientsocket.close()






def polling_nodes(listening_sock,id_base, length, max_storage):
    
    pollerObject = select.poll()

    # Adding sockets
    pollerObject.register(listening_sock, select.POLLIN)

    global neighbour_matrix 

    neighbour_matrix = [[None] * max_storage for _ in range(length)]

    print(neighbour_matrix) 
   
    while True:
   
        fdVsEvent = pollerObject.poll()

        fds={}

        for descriptor, Event in fdVsEvent:
            
            if descriptor == listening_sock.fileno() and Event==select.POLLIN :
               
                Acc_sock, addr = listening_sock.accept()
                
                received_bytes = Acc_sock.recv(1024)
                
                received_list = pickle.loads(received_bytes)

                neighbour_matrix[received_list[0]-id_base][received_list[1]] = Acc_sock
        
                print(received_list)

                







                
                
                
                
                
                
                # fds[Acc_sock.fileno()] = Acc_sock
                # tata=recv_data(Acc_sock,10*1024)
                # print(tata)
                # data = "batataaaaaaaaaaaaaaaaaaaa"
                # acc_sock.sendall(data.encode())
                # pollerObject.register(Acc_sock, select.POLLIN)



                
            
                

           


# Creating and initiaizing nodes
nodes={id_base+i : Node(max_storage, id_base+i) for i in range(n)}
Local_Nodes_infos={Id:[nodes[Id].ip, nodes[Id].port] for Id in nodes}



# Envoi des informations des noeuds
data_to_send=pickle.dumps(Local_Nodes_infos)
send_data(Orchest_sock, len(data_to_send))
send_data(Orchest_sock, Local_Nodes_infos)


# Recieve the len of the dict chiffré
length=recv_data(Orchest_sock,4096)

# Recieve the dict
data=Orchest_sock.recv(4096)
while len(data)<length:
    data+=Orchest_sock.recv(4096)
Nodes_infos=pickle.loads(data)

# Recevoir les informations de tout les noeuds
neighbour_matrix=[]

node_threads=[]
for i in range (0,n):
    node_threads = node_threads + [threading.Thread(target=polling_nodes, args=(nodes[i+id_base].sock,id_base,len(Nodes_infos),max_storage,))]


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
            
            sys.stdout.flush()

            conn = Gossip_connect(neighbor_ip, neighbour_port)
            
            nodes[i+id_base].neighbor_sockets.append(conn)

            to_send= [nodes[i+id_base].id,j]

            to_send = [nodes[i+id_base].id, j]
           
            to_send_bytes = pickle.dumps(to_send)
           
            conn.sendall(to_send_bytes)

            


# for i in range (0,n):      
#     nodes[i].neighbor_personal_sockets = neighbour_matrix[]
            



            
            
            

            


            
            
            
           

          

            



        
    except Exception as e:
        
        print(e)
        
        sys.stdout.flush()

        exit(1)


time.sleep(2)
print(neighbour_matrix)         
                


print("END !")
sys.stdout.flush()



while(1):
    continue