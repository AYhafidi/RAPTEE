
import socket
import sys
import pickle

Hostname=socket.gethostname()
clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.bind((Hostname,0))
clientsocket.listen(2)
Port=clientsocket.getsockname()[1]


s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((sys.argv[1], int(sys.argv[2])))

# Envoyer les infos
data=[Hostname,Port]
s.send(pickle.dumps(data))
