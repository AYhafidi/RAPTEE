
import os
import sys
import csv
import socket
import subprocess
import pickle


def main():
    # Verifier les arguments
    if len(sys.argv)<3:
        print("Usage : ./Orchest machine_file executable arg1 arg2 ...")
        exit()
    else:
        Executable=sys.argv[2]

    # Mapping des infos
    machine_dict={}

    # Machine names
    with open(sys.argv[1],'r') as file:
        machine_Names = list(filter(None,file.read().splitlines()))
    Nmbr_procs=len(machine_Names)

    # récuperer le nom de la machine
    Hostname=socket.gethostname()

    # Socket d'écoute
    serversocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((Hostname,0))
    serversocket.listen(Nmbr_procs)
    Port=serversocket.getsockname()[1]

    # Lancer les procs
    for Name in machine_Names:
        #List des arguments
        Args=["ssh",Name,"python3","~/Desktop/RAPTEE/"+Executable,Hostname,str(Port)]+sys.argv[3:]
        subprocess.run(Args, timeout=None)

    # Accepter les connexions
    for i in range(Nmbr_procs):
        sock_accept,addr=serversocket.accept()
        machine_dict[i]=pickle.loads(sock_accept.recv(1024))
    print(machine_dict)



if __name__ == '__main__':
    main()
