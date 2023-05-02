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

def Ending_poll(sockets):
    global N_ready
    N_ready=0
    pollerObject = select.poll()

    # Adding sockets
    [pollerObject.register(sockets[i], select.POLLIN) for i in sockets ]
    while True:
        if N_ready==Nmbr_procs:
            break
        fdVsEvent = pollerObject.poll()

        for descriptor, Event in fdVsEvent:

            if Event==select.POLLIN:

                data=recv_data(sockets[descriptor], 4096)
                if data=="END":
                    N_ready+=1

class Node:
    def __init__(self, max_storage, id):

        # Node info
        self.max_storage = max_storage  # maximum storage capacity of node
        self.id = id   # Node's ID
        self.ip = socket.gethostname()   # Node's IP address
        self.Nu = random.sample(range(id_base-n*proc_id,id_base+n*(Nmbr_procs-proc_id)),max_storage)  # neighbor list
        self.Su = []  # sample list

        # Interconnections' info
        self.neighbor_sockets = {}  # Neighbors' IPs and ports

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
Time_periode=int(sys.argv[6])


                                        ##### Initialisation des connexions #####


Orchest_sock, Nmbr_procs, proc_id, peer_conn=Net_init()


# Tableau des sockets

Sockets={peer_conn[rang][1].fileno():peer_conn[rang][1] for rang in peer_conn}
t=threading.Thread(target=Ending_poll, args=(Sockets, ))
t.start()

def polling_nodes(listening_sock):

    Sockets={}
    pollerObject = select.poll()

    # Adding sockets
    pollerObject.register(listening_sock, select.POLLIN)
    while True:
        fdVsEvent = pollerObject.poll()

        for descriptor, Event in fdVsEvent:

            if listening_sock.fileno()==descriptor and Event==select.POLLIN:

                Acc_sock, addr=listening_sock.accept()
                # Adding socket
                pollerObject.register(Acc_sock, select.POLLIN)
                Sockets[Acc_sock.fileno()]=Acc_sock
            
            elif listening_sock.fileno()!=descriptor and Event==select.POLLIN:
                data=recv_data(Sockets[descriptor],4096)
                print(f"[ DATA ]: {data}")





# Creating and initiaizing nodes
nodes={id_base+i : Node(max_storage, id_base+i) for i in range(n)}
Local_Nodes_infos={Id:[nodes[Id].ip, nodes[Id].port] for Id in nodes}

node_threads=[]
for i in range (0,n):
    node_threads = node_threads + [threading.Thread(target=polling_nodes, args=(nodes[i+id_base].sock,))]
# Envoi des informations des noeuds
data_to_send=pickle.dumps(Local_Nodes_infos)
send_data(Orchest_sock, len(data_to_send))
send_data(Orchest_sock, Local_Nodes_infos)


# Recieve the len of the encrypted dict
length=recv_data(Orchest_sock,4096)

# Recieve the dict

data=Orchest_sock.recv(4096)
while len(data)<length:
    data+=Orchest_sock.recv(4096)
Nodes_infos=pickle.loads(data)


for i in range (0,n):

    # print('We are at the i :' + str(i))

    try:

        node_threads[i].start()

        for j in range (0,max_storage):

            neighbor_id=nodes[i+id_base].Nu[j]

            # print('Neighbour_id ' + str(neighbor_id))

            neighbor_ip = Nodes_infos[neighbor_id][0]

            neighbour_port = Nodes_infos[neighbor_id][1]

            # print('neighbour_id ' + str(neighbor_id)+ ' neighbor ip ' + neighbor_ip + ' neighbor port ' + str(neighbour_port))
            sys.stdout.flush()

            nodes[i+id_base].neighbor_sockets[neighbor_id] = Gossip_connect(neighbor_ip, neighbour_port)
            
            
                
            send_data(nodes[i+id_base].neighbor_sockets[neighbor_id],"Hi! you little peasant.")

    except Exception as e:

        print(e)

        sys.stdout.flush()

# Prêt à ce terminer


N_ready+=1
for i in Sockets:
    send_data(Sockets[i], "END")

# Fin du code
while (N_ready<Nmbr_procs):
    continue
t.join()
print("END!")
sys.stdout.flush()
