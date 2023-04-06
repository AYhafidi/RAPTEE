#!/usr/bin/env python3

## Fonctions de protocol Brahms

## implémentation en code du pseudo code décrivant le protocol brahms dans le document :



from typing import List, Tuple
import random
import time


#classe "Sampler" qui est utilisée pour stocker des échantillons de nœuds. 
# Les échantillons sont utilisés pour sélectionner des nœuds de manière 
# aléatoire dans certaines étapes du protocole.


class Sampler:
    def __init__(self):
        self.sample_list = []
    
    def init(self):
        self.sample_list = []
    
    def next(self, id):
        self.sample_list.append(id)
    
    def sample(self):
        return self.sample_list



#initialisation des paramètre utilisé dans le protocol de gossip 


def __init__(self, V0: List[int], S: List[Sampler], alpha: int, beta: int, gamma: int):
        self.V = tuple(V0)
        self.S = tuple(S)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.Vpush = []
        self.Vpull = []


# Auxilary functions : rand et updatesample utilisé dans gossip 

# fonction "rand" qui prend une liste de nœuds et un nombre "n"
# et retourne une liste de "n" nœuds choisis au hasard dans la liste.

def rand(self, V: Tuple[int], n: int) -> List[int]:
  #return n random choice from V
   return random.sample(list(V), n)


#La fonction "updateSample" met à jour chaque échantillon avec les nouveaux nœuds reçus.
#  
def updateSample(self, V: List[int]):
    for id in V:
        for s in self.S:
            s.next(id)  

#Gossip protocol est la fonction principale qui implémente le protocole de gossip. 
# Il y a une boucle infinie qui contient plusieurs étapes ( while true)


def gossip(self):

        while True:

            self.Vpush = []
            self.Vpull = []


            for i in range (self.alpha*len(self.V)): # envoie des requêtes de type "push" à un nombre limité de nœuds choisis au hasard
                #limited push
                receiver = random.choice(self.rand(self.V,1))
                self.send_push_request(i,receiver)

            for i in range (self.beta*len(self.V)): #envoie des requêtes de type "pull" à un autre ensemble de nœuds choisis au hasard
                receiver = random.choice(self.rand(self.V,1))
                self.send_pull_request(i,receiver)

            #wait(1) Le code attend une seconde avant de poursuivre l'exécution.
            time.sleep(1)

            #Le code récupère ensuite les réponses "push" et "pull" des autres nœuds et 
            # stocke les nœuds reçus dans des listes "Vpush" et "Vpull".

            for (i,id) in self.receive_push_requests(): 
                self.Vpush.append(id)

            for (i, id) in self.receive_pull_requests():
                self.send_pull_reply(i, id)

            for (i, V_i) in self.receive_pull_replies():
                if i in self.sent_pull_requests and len(self.Vpull) == 0:
                    self.Vpull = V_i

            #le code combine les nœuds stockés dans les listes "Vpush" et "Vpull" 
            # avec d'autres nœuds choisis aléatoirement pour créer une nouvelle 
            # liste de nœuds à partir de laquelle les échantillons sont mis à jour.  

            if len(self.Vpush) <= self.alpha*len(self.V) and self.Vpush and self.Vpull:
                V_new = self.rand(self.Vpush, self.alpha*len(self.V)) + self.rand(self.Vpull, self.beta*len(self.V)) + self.rand(self.S, self.gamma*len(self.V))
                self.V = tuple(V_new)
                self.updateSample(self.Vpush + self.Vpull)
            


#fonctions annexes permettant les push et pull request/reply/receive dans le gossip
#entre les nœuds du réseau. Ces fonctions sont définies comme des coquilles vides avec la commande "pass".
# Il  faudra les compléméter une fois qu'on arrivera a connecter plusieurs noeuds entre eux 


def send_push_request(self, i: int, receiver: int):
    # Send push request i to receiver

    pass


def send_pull_request(self, i: int, receiver: int):
    # Send pull request i to receiver

    pass
    
def send_pull_reply(self, i: int, receiver: int):
    # Send pull reply with view V_i to receiver

    pass


def receive_push_requests(self) -> List[Tuple[int, int]]:
    # Receive and parse push requests
    
    return []
    
def receive_pull_requests(self) -> List[Tuple[int, int]]:
    # Receive and parse pull requests
  
    return []

def receive_pull_replies(self) -> List[Tuple[int, List[int]]]:
    # Receive and parse pull replies
   
    return []