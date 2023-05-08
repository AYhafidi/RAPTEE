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
import multiprocessing
import datetime
import json




          
class Node:
    def __init__(self, id, View):

        # Node info
        self.id = id   # Node's ID
        self.ip = socket.gethostname()   # Node's IP address
        self.Nu = View  # neighbor list
        self.Hu = []  # historic list
        self.PUSH_IDS=[] # Pushed IDS
        self.PULL_IDS=[] # Pulled IDS
        self.Public_key=[]
        # Interconnections' info
        self.neighbor_sockets = {}  # Neighbors' IPs and ports
        self.neighbor_acc_sock= {}
        self.neighbor_info = {}
        # Listening socket and binding
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Listening socket
        self.sock.bind((self.ip, 0))  # bind socket to node id
        self.port=self.sock.getsockname()[1]
        self.sock.listen(n)  # listen for incoming connections
        #print("Node", self.id, "listening on port", self.port)

    def get_Nu(self):
        return self.Nu
    
    def get_Hu(self):
        return self.Hu

    def get_Nui(self, i):
        if i < len(self.Nu):
            return self.Nu[i]
        else:
            return None

    def get_Hui(self, i):
        if i < len(self.Hu):
            return self.Hu[i]
        else:
            return None

class Trusted(Node):
    def __init__(self, id, View, Key):
        super().__init__(id, View)
        self.Private_key=Key

class Byzantine(Node):
    def __init__(self, id, View, B_ids):
        super().__init__(id, View)
        self.B_ids=B_ids # ID des autres noeuds byzantin


    def update_neighbor_list(self, Nu_t):
        # This method updates the sample list of the node with the first max_storage elements of the list Su
        self.Nu = Nu_t[:self.max_storage]  # update neighbor list with the first max_storage elements

    def update_sample_list(self, Su_t):
        # This method updates the sample list of the node with the first max_storage elements of the list Su
        self.Su = Su_t[:self.max_storage]  # update sample list with the first max_storage elements

def Ending_poll(sockets):
    global event 
    global N_ready
    N_ready = 0
    event = threading.Event()
    pollerObject = select.poll()

    # Adding sockets
    [pollerObject.register(sockets[i], select.POLLIN or select.POLLHUP) for i in sockets ]
    while True:
        if event.is_set():
            break
        fdVsEvent = pollerObject.poll(2)

        for descriptor, Event in fdVsEvent:
            if Event==select.POLLHUP:
                continue
            elif Event==select.POLLIN:
                data=recv_data(sockets[descriptor], 4096)
                if data=="END":
                    N_ready+=1
                Event=0
                pollerObject.unregister(sockets[descriptor])

    

def polling_nodes(Node, N_event):
    
    listening_sock=Node.sock
    Sockets={}
    pollerObject = select.poll()



    # Adding sockets
    pollerObject.register(listening_sock, select.POLLIN)
    for sock_N in Node.neighbor_sockets:
        pollerObject.register(Node.neighbor_sockets[sock_N], select.POLLIN or select.POLLHUP)
        Sockets[Node.neighbor_sockets[sock_N].fileno()]=Node.neighbor_sockets[sock_N]

    for sock_N in Node.neighbor_acc_sock:
        pollerObject.register(Node.neighbor_acc_sock[sock_N], select.POLLIN or select.POLLHUP)
        Sockets[Node.neighbor_acc_sock[sock_N].fileno()]=Node.neighbor_acc_sock[sock_N]
    
    
    while not N_event.is_set():
       
        fdVsEvent = pollerObject.poll(2)
        for descriptor, Event in fdVsEvent:

            if listening_sock.fileno()==descriptor and Event==select.POLLIN:

                Acc_sock, addr=listening_sock.accept()
                # Adding socket
                Node.neighbor_acc_sock[Acc_sock.fileno()]=Acc_sock

                Sockets[Acc_sock.fileno()]=Acc_sock

                Event=0
            
            elif listening_sock.fileno()!=descriptor and Event==select.POLLIN:
                
                Req=recv_data(Sockets[descriptor],4096)
                if Req==None:
                    continue
                else :
                    if Req.type==R_type.PUSH:

                        Node.PUSH_IDS.append(Req.source)

                    elif Req.type==R_type.PULL_REQ:

                        if Node.__class__.__name__==Byzantine:
                            view_to_pull = Request(Req.destinataire, Req.source, 2, Node.Nu)
                        else:
                            view_to_pull = Request(Req.destinataire, Req.source, 2, Node.Nu)

                        send_data(Sockets[descriptor],view_to_pull)                


                    elif Req.type==R_type.PULL_RES:
                            
                        Node.PULL_IDS.extend(Req.message)

                    Event=0

                
                    
                    
                    
                    
                    
                    
                    

                

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
Launching_time=sys.argv[3]
id_base=int(sys.argv[4])
n=int(sys.argv[5])
max_storage=int(sys.argv[6])
Rounds=int(sys.argv[7])
T_Round=int(sys.argv[9])
alpha=float(sys.argv[10])
beta=float(sys.argv[11])
gamma=float(sys.argv[12])


                                        ##### Initialisation des connexions #####


Orchest_sock, Nmbr_procs, proc_id, peer_conn=Net_init()

# Recieving dict of Nodes initial views
    # Recieve the len of the encrypted dict
length=recv_data(Orchest_sock,4096)
sys.stdout.flush()
    # Recieve dict
data=Orchest_sock.recv(4096)
while len(data)<length:
    data+=Orchest_sock.recv(4096)
Nodes_Views=pickle.loads(data)

# Tableau des sockets
Sockets={peer_conn[rang][1].fileno():peer_conn[rang][1] for rang in peer_conn}

# Poll pour finir le programme
t=threading.Thread(target=Ending_poll, args=(Sockets,))
t.start()

nodes={}
Local_Nodes_infos={}
# Creating and initiaizing nodes
for i in range(n):
    Id=i+id_base
    if Nodes_Views[Id][0]=="B":
        nodes[Id]=Byzantine(Id, Nodes_Views[Id][1], Nodes_Views[Id][1])

    elif Nodes_Views[Id][0]=="T":
        nodes[Id]=Trusted(Id, Nodes_Views[Id][1], 0)
    else :
        nodes[Id]=Node(Id, Nodes_Views[Id][1])
    Local_Nodes_infos[Id]=[nodes[Id].ip, nodes[Id].port]
    
node_threads=[]
thread_event=[]

for i in range (0,n):
    thread_event.append(threading.Event())
    node_threads.append(threading.Thread(target=polling_nodes, args=(nodes[i+id_base], thread_event[i],)))
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

sys.stdout.flush()
                                                    ###  Connexion entre noeuds  ###

for i in range (0,n):

    try:

        node_threads[i].start()

        for j in range (0,max_storage):

            neighbor_id=nodes[i+id_base].Nu[j]
            
            neighbor_ip = Nodes_infos[neighbor_id][0]

            neighbour_port = Nodes_infos[neighbor_id][1]

            nodes[i+id_base].neighbor_info[neighbor_id] = [neighbor_ip, neighbour_port]

            nodes[i+id_base].neighbor_sockets[neighbor_id] = Gossip_connect(neighbor_ip, neighbour_port)


    except Exception as e:

        print(e)

        sys.stdout.flush()
                                                        ### Ending threads ###

for t_event in thread_event:
    t_event.set()

for N_thread in node_threads:
    N_thread.join()

Data={k:{id:{"View":[],"History":[]} for id in nodes} for k in range(Rounds)}

                                                       ### Commencer l'échange au même temps ###
print("[+] Launching...")
sys.stdout.flush()
while(datetime.datetime.now().strftime("%H:%M:%S")!=Launching_time):
    continue

                                                    ### Commencer les communications ###
for k in range(Rounds):
    Current_time = datetime.datetime.now() # Temps actuelle
    Round_ending_time=Current_time+datetime.timedelta(seconds=T_Round) # Temps de fin du round
    Round_ending_time_F= Round_ending_time.strftime("%H:%M:%S")
    Current_time_F=Current_time.strftime("%H:%M:%S")
    print(" "*15,"<","="*10,f"  Round :{k}  ","="*10,">",f"\nRound beginned at {Current_time_F}  and finishes at {Round_ending_time_F}")
    sys.stdout.flush()
    node_threads=[]
    for i in range (0,n):
        node_threads.append(threading.Thread(target=polling_nodes, args=(nodes[i+id_base], thread_event[i],)))


    # Envoi des informations des noeuds   

    for i in range(n):
        thread_event[i].clear()
        try :
            node_threads[i].start()
        
        except Exception as e:

            print(e)

            sys.stdout.flush()



                                                        ###  Échange entre noueds  ###

    for Id in nodes:
        
        
        neighbour_samples_push = random.sample(nodes[Id].Nu, (max_storage//2)+1)
        
        neighbour_samples_pull = random.sample(nodes[Id].Nu, (max_storage//2)+1)


        for Neighbour_Id in neighbour_samples_push:
        
            to_send_push = Request(Id, Neighbour_Id, 3, None)

            send_data(nodes[Id].neighbor_sockets[Neighbour_Id],to_send_push)

        for Neighbour_Id in neighbour_samples_pull:

            to_send_pull = Request(Id, Neighbour_Id, 1, None)

            send_data(nodes[Id].neighbor_sockets[Neighbour_Id], to_send_pull)

                                                            ### Attendre la fin du round ###
    while(datetime.datetime.now().strftime("%H:%M:%S")!=Round_ending_time_F):
        continue

    for t_event in thread_event:
        t_event.set()

    for N_thread in node_threads:
        N_thread.join()
    
    for id in nodes:
        Data[k][id]["View"]=nodes[id].get_Nu()
        Data[k][id]["History"]=nodes[id].get_Hu()


                                                        ### Sending data to Orchestrator ###
# Envoi des informations des noeuds
data_to_send=pickle.dumps(Data)
send_data(Orchest_sock, len(data_to_send))
send_data(Orchest_sock, Data)
                                                        ###  Ending Programme  ###

N_ready+=1

for i in Sockets:
    send_data(Sockets[i], "END")

# Fin du code
while (N_ready<Nmbr_procs):
    continue

print("END.")
sys.stdout.flush()
event.set()
t.join()




