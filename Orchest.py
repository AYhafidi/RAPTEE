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
                print(f"[ {Machines_Names[Index//2]}, rang{[Index//2]} ] Out : {Out}",end="")

            elif Index%2==1 and Event & select.POLLIN:
                Err=os.read(descriptor,4096).decode()
                print(f"[ {Machines_Names[Index//2]}, rang{[Index//2]} ] Err : {Err}",end="")


           

                                                    # # # <---  Functions ---> # # #
 
def Nodes_info_recv(socket, Nodes_infos):

    # Recieve the len of the dict chiffré
    length=recv_data(socket,4096)
    # Recieve the dict
    data=socket.recv(4096)
    while len(data)<length:
        data+=socket.recv(4096)
    Nodes_infos.update(pickle.loads(data))


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
    data_to_send=pickle.dumps(data)
    Size=len(data_to_send)
    Size_sent=0
    while(Size_sent<Size):
        Size_sent+=socket.send(data_to_send[Size_sent:])


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
    Nmbr_procs, proc_id, machine_dict=recv_data(conn_socket,4096)
    
    
    # Lancer l'écoute
    clientsocket.listen(Nmbr_procs-1)

    time.sleep(1)
    # accepter les connexions des machines de rang supérieur
    for i in range(proc_id,Nmbr_procs-1):
        sock, addr = clientsocket.accept()
        rang = recv_data(sock,1024)
        peer_conn[rang]=[machine_dict[rang][2], sock, machine_dict[rang][0]]

    # se connecter avec les machines de rang inférieur
    for i in range(0,proc_id):
        peer_conn[i]=[machine_dict[i][2], Gossip_connect(machine_dict[i][0], machine_dict[i][1]), machine_dict[i][0]]
        send_data(peer_conn[i][1],proc_id)


    return conn_socket, Nmbr_procs, proc_id
    



    

    


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
    machine_Names_c=machine_Names.copy()
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
        print("\nThere are no machines to run the script on")
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
    try:
        serversocket=Listening_socket(Hostname, 0, Nmbr_procs)
    except Exception as e:
        print(e)
        exit(1)
    Port=serversocket.getsockname()[1]


    # Lancer les procs
    for i in range(Nmbr_procs):
        #Liste des arguments
        OutpipeR ,OutpipeW=os.pipe()
        ErrpipeR ,ErrpipeW=os.pipe()
        Args=["ssh",Machine_Dispo[i],"python3","~/RAPTEE/"+Executable,Hostname,str(Port)]+[str(ids_bases[i])]+sys.argv[4:]
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

    #fonction Poll thread + Node_info threads
    t=threading.Thread(target=Poll_function, args=(fd_Pipes, Machine_Dispo,))
    t.start()
    Node_info_threads=[]

    # dict containing nodes infos
    Nodes_infos={}
    # Accepter les connexions
    for i in range(Nmbr_procs):
        sock_accept,addr=serversocket.accept()
        Acc_infos=recv_data(sock_accept,4096)+[ids_bases[i]] # Hostname, port, Id_base
        rang=Machine_Dispo.index(Acc_infos[0]) # Le rang de la mchine
        if rang in machine_dict :
            machine_Names_c.remove(Acc_infos[0])
            rang=machine_Names_c.index(Acc_infos[0])+1
        machine_dict[rang]=Acc_infos
        sockets[rang]=sock_accept
    # Envoi Nombre de processus + rang + Mapping des machines
    for i in range(Nmbr_procs):
        send_data(sockets[i],[Nmbr_procs,i,machine_dict])
        Node_info_threads.append(threading.Thread(target=Nodes_info_recv, args=(sockets[i], Nodes_infos,)))

    # Lancer les threads pour récupérer les informations des noeuds
    for i in range(Nmbr_procs):
        Node_info_threads[i].start()
    
    for i in range(Nmbr_procs):
        Node_info_threads[i].join()

    # Envoyer les information à chaque machine
    data_to_send=pickle.dumps(Nodes_infos)
    for i in range(Nmbr_procs):
        send_data(sockets[i], len(data_to_send))
        send_data(sockets[i], Nodes_infos)

if __name__ == '__main__':
    main()
