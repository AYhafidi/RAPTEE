import os
import sys
import csv
import socket
import subprocess
import pickle
import time
import select
import threading
from enum import Enum
class R_type(Enum):

    CONNECTION = 0
    PULL_REQ = 1
    PUSH_REQ = 2
    PULL_RES = 3
    PUSH_RES = 4

    
class Request:
    def __init__(self, source, destinataire, req, message):
        self.source=source
        self.destinataire=destinataire
        self.type=R_type[req]
        self.message=message

#                                                    # # #  POLL FUNCTIONS  # # # 

def Poll_function(sockets, Machines_Names):

    # Initialisation
    pollerObject = select.poll()

    # Adding sockets
    for i in sockets:
        pollerObject.register(i, select.POLLIN)

    # Traiter les données
    while(True):

        fdVsEvent = pollerObject.poll(-1)

        for descriptor, Event in fdVsEvent:
            Index=sockets.index(descriptor)
            if Index%2==0 and Event & select.POLLIN:
                Out=os.read(descriptor,4096).decode()
                print(f"[ {Machines_Names[Index//2]} ] Out : {Out}",end="")

            elif Index%2==1 and Event & select.POLLIN:
                Err=os.read(descriptor,4096).decode()
                print(f"[ {Machines_Names[Index//2]} ] Err : {Err}",end="")

# def Poll_machines_function(machine_socks, listen_socket, n):
#     pollerObject = select.poll()

#     # Copy dict to use in poll
#     poll_socks=machine_socks.copy()
#     poll_socks[listen_socket.fileno()]=[listen_socket, "Listen", 0]
#     # Adding sockets
#     for key in poll_socks:
#         pollerObject.register(poll_socks[key][0], select.POLLIN)

#     # Traiter les données
#     while True:
#         fdVsEvent = pollerObject.poll()

#         for descriptor, Event in fdVsEvent:
#             if descriptor==listen_socket.fileno() and Event & select.POLLIN:
#                 conn_socket, addr=listen_socket.accept()
#                 poll_socks[conn_socket.fileno()]=[conn_socket, "Noeud", 0]
#                 try:
#                     request=recv_data(conn_socket,1024)
#                     print(f"Request type :{request.type.value}")
#                 except Exception as err:
#                     print(f"ERR : {err}")
#                     sys.stdout.flush()  
#                 try:
#                     send_data(id_to_socket(machine_socks, request.destinataire, n),request)
#                 except Exception as err:
#                     print(f"ERR : {err}")
#                     sys.stdout.flush()  
                
#                 Event=0
#             elif descriptor!=listen_socket.fileno() and Event & select.POLLIN:
#                 request=recv_data(poll_socks[descriptor][0],1024)
#                 Req_N=request.type.value
#                 if Req_N==R_type.CONNECTION.value:
#                     print(f"Recieved request from {request.source} to connect with {request.destinataire}")
#                     sys.stdout.flush()
#                 Event=0
           

                                                    # # # <---  Functions ---> # # #

def id_to_socket(machine_socks, id, n):
    for i in machine_socks:
        if id in range(machine_socks[i][2], machine_socks[i][2]+n):
            print(f"Node in machine : {machine_socks[i][1]}")
            sys.stdout.flush()
            return machine_socks[i][0]
    return 0 

def Listening_socket(IP,Port,N):
    # Créer une socket d'écoute
    Hostname=socket.gethostname() #Nom de la machine
    clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.bind((IP,Port))
    Port=clientsocket.getsockname()[1]
    clientsocket.listen(N)
    return clientsocket

def Gossip_connect(IP_addr,Port):
    conn_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn_socket.connect((IP_addr, int(Port)))
    return conn_socket


def send_data(socket,data):
    socket.send(pickle.dumps(data))

def recv_data(socket,Size):
    return pickle.loads(socket.recv(Size))

                                                # # # Function d'initialisation # # #
def Net_init():
    # Peer connection mapping
    peer_conn={}

    # se connecter avec le processus pére
    conn_socket=Gossip_connect(sys.argv[1],sys.argv[2])

    # Créer une socket d'écoute
    Hostname=socket.gethostname() #Nom de la machine
    clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.bind((Hostname,0))
    Port=clientsocket.getsockname()[1]

    # Envoyer les infos
    data=[Hostname,Port]
    send_data(conn_socket,data)

    # Recv Nmbr de processus + rang + Mapping des machines
    Nmbr_procs, proc_id, machine_dict=recv_data(conn_socket,1024)

    
    
    # Lancer l'écoute
    clientsocket.listen(Nmbr_procs-1)
    

    # accepter les connexions des machines de rang supérieur
    for i in range(proc_id,Nmbr_procs-1):
        sock, addr = clientsocket.accept()
        rang = recv_data(sock,1024)
        peer_conn[rang]=[machine_dict[rang][2], sock, machine_dict[rang][0]]

    # se connecter avec les machines de rang inférieur
    for i in range(0,proc_id):
        peer_conn[i]=[machine_dict[i][2], Gossip_connect(machine_dict[i][0], machine_dict[i][1]), machine_dict[i][0]]
        send_data(peer_conn[i][1],proc_id)


    return conn_socket, Nmbr_procs
    



    

    


         ############## MAIN ###############

def main():
    # Verifier les arguments
    if len(sys.argv)<6:
        print("Usage : ./Orchest machine_file executable ID_Base N Storage IP_Base...")
        exit()
    else:
        Executable=sys.argv[2]
        id_base=sys.argv[3]
        N=sys.argv[4]
        max_storage=sys.argv[5]
        # # Check if we have root privileges
        # if os.geteuid() != 0:
        # # If not, try to elevate privileges
        #     os.seteuid(0)
        #     if os.geteuid() != 0:
        #         # If we still don't have privileges, exit with an error
        #         print("Error: Failed to elevate privileges")
        #         exit(1)

    # Mapping des infos
    machine_dict={}

    # Mapping des sockets
    sockets={}
    # Fd des tubes
    fd_Pipes=[]

    # Machine names
    with open(sys.argv[1],'r') as file:
        machine_Names = list(filter(None,file.read().splitlines()))


    # Vérifier la disponibilté des machines
    Machine_Dispo=[]
    print("[+]Connecting to machines ",end="")
    for Name in machine_Names:
        try :
            result=subprocess.check_output(["ssh", Name, "exit"], stderr=subprocess.PIPE)
            Machine_Dispo.append(Name)
            print("★ ",end="")
            sys.stdout.flush()
            sys.stderr.flush()
        except :
            print("☆ ",end="")
    # Le nombre des machines disponible 
    Nmbr_procs=len(Machine_Dispo)
    if Nmbr_procs==0:
        print("\nThere is no machines to run the script on")
        exit(1)
    else :
        print("OK")
    
    # Id bases sent to different machines to identify which machine a node belongs to  
    ids_bases=[]
    for i in range (Nmbr_procs):
        ids_bases.append(int(id_base)+i*int(N)) 


    # récuperer le nom de la machine
    Hostname=socket.gethostname()

    # Socket d'écoute
    serversocket=Listening_socket(Hostname, 0, Nmbr_procs)
    Port=serversocket.getsockname()[1]


    # Lancer les procs
    for i in range(Nmbr_procs):
        #Liste des arguments
        OutpipeR ,OutpipeW=os.pipe()
        ErrpipeR ,ErrpipeW=os.pipe()
        Args=["ssh",Machine_Dispo[i],"python3","~/Desktop/RAPTEE/"+Executable,Hostname,str(Port)]+[str(ids_bases[i])]+sys.argv[4:]
        pid=os.fork()    
        if pid==0:
            # Redirection des tubes
            os.close(OutpipeR)
            os.dup2(OutpipeW, sys.stdout.fileno())
            os.close(ErrpipeR)
            os.dup2(ErrpipeW, sys.stderr.fileno())
            os.close(OutpipeW)
            os.close(ErrpipeW)
            os.execvp(Args[0],Args)
        elif pid>0:
            os.close(OutpipeW)
            os.close(ErrpipeW)
            fd_Pipes.append(OutpipeR)
            fd_Pipes.append(ErrpipeR)

    # Accepter les connexions
    for i in range(Nmbr_procs):
        sock_accept,addr=serversocket.accept()
        machine_dict[i]=recv_data(sock_accept,1024)+[ids_bases[i]]
        sockets[i]=sock_accept

    # Envoi Nombre de processus + rang + Mapping des machines
    for i in range(Nmbr_procs):
        send_data(sockets[i],[Nmbr_procs,i,machine_dict])
    
    # Recevoir les infos des Noeuds
    Nodes_Infos={}
    for i in range(Nmbr_procs):
        Size=recv_data(sockets[i], 1024)
        data=recv_data(sockets[i], Size)
        Nodes_Infos.update(data)
    Size=sys.getsizeof(pickle.dumps(Nodes_Infos))
    for i in range(Nmbr_procs):
        send_data(sockets[i], Size)
        send_data(sockets[i], Nodes_Infos)

    #fonction Poll
    Poll_function(fd_Pipes, Machine_Dispo)





if __name__ == '__main__':
    main()
