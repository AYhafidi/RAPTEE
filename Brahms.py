#!/usr/bin/env python3

## Fonctions de protocol Brahms

## implémentation en code du pseudo code décrivant le protocol brahms dans le document :



from typing import List, Tuple
import random
import time


#initialisation des samplers


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


#auxilary functions : rand et updatesample utilisé dans gossip 


def rand(self, V: Tuple[int], n: int) -> List[int]:
  #return n random choice from V
   return random.sample(list(V), n)
  
def updateSample(self, V: List[int]):
    for id in V:
        for s in self.S:
            s.next(id)  

#gossip protocol


def gossip(self):

        while True:

            self.Vpush = []
            self.Vpull = []


            for i in range (self.alpha*len(self.V)):
                #limited push
                receiver = random.choice(self.rand(self.V,1))
                self.send_push_request(i,receiver)

            for i in range (self.beta*len(self.V)):
                receiver = random.choice(self.rand(self.V,1))
                self.send_pull_request(i,receiver)

            #wait(1)
            time.sleep(1)

            for (i,id) in self.receive_push_requests():
                self.Vpush.append(id)

            for (i, id) in self.receive_pull_requests():
                self.send_pull_reply(i, id)

            for (i, V_i) in self.receive_pull_replies():
                if i in self.sent_pull_requests and len(self.Vpull) == 0:
                    self.Vpull = V_i

            if len(self.Vpush) <= self.alpha*len(self.V) and self.Vpush and self.Vpull:
                V_new = self.rand(self.Vpush, self.alpha*len(self.V)) + self.rand(self.Vpull, self.beta*len(self.V)) + self.rand(self.S, self.gamma*len(self.V))
                self.V = tuple(V_new)
                self.updateSample(self.Vpush + self.Vpull)
            


#fonctions annexes permettant les push et pull request/reply/receive dans le gossip

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