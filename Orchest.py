import os
import sys
import csv
import socket
import subprocess
import pickle
import time
import select
                                                   # # #  POLL FUNCTION  # # # 

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
                Out=os.read(descriptor,2048).decode()
                print(f"[ {Machines_Names[Index//2]} ] Out : {Out}",end="")

            elif Index%2==1 and Event & select.POLLIN:
                Err=os.read(descriptor,2048).decode()
                print(f"[ {Machines_Names[Index//2]} ] Err : {Err}",end="")


                                                    # # # <---  Functions ---> # # #

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
    sys.stdout.flush()
    sys.stderr.flush()

    return peer_conn, proc_id
    



    

    


         ############## MAIN ###############

def main():
    # Verifier les arguments
    if len(sys.argv)<7:
        print("Usage : ./Orchest machine_file executable ID_Base N Storage IP_Base...")
        exit()
    else:
        Executable=sys.argv[2]
        id_base=sys.argv[3]
        N=sys.argv[4]
        max_storage=sys.argv[5]
        ip_adress=sys.argv[6]

    # Mapping des infos
    machine_dict={}

    # Mapping des sockets
    sockets={}
    # Fd des tubes
    fd_Pipes=[]

    # Machine names
    with open(sys.argv[1],'r') as file:
        machine_Names = list(filter(None,file.read().splitlines()))
    
    Nmbr_procs=len(machine_Names)
    
    # Id bases sent to different machines to identify which machine a node belongs to  
    ids_bases=[]
    for i in range (Nmbr_procs):
        ids_bases.append(int(id_base)+i*int(N)) 


    # récuperer le nom de la machine
    Hostname=socket.gethostname()

    # Socket d'écoute
    serversocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((Hostname,0))
    serversocket.listen(Nmbr_procs)
    Port=serversocket.getsockname()[1]


    # Lancer les procs
    for i in range(Nmbr_procs):
        #Liste des arguments
        OutpipeR ,OutpipeW=os.pipe()
        ErrpipeR ,ErrpipeW=os.pipe()
        Args=["ssh",machine_Names[i],"python3","~/Desktop/RAPTEE/"+Executable,Hostname,str(Port)]+[str(ids_bases[i])]+sys.argv[4:]
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
    
    #fonction Poll
    Poll_function(fd_Pipes, machine_Names)





if __name__ == '__main__':
    main()
