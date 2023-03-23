#!/usr/bin/env python3

class Node:
    def __init__(self, max_storage):
        self.max_storage = max_storage  # maximum storage capacity of node
        self.Nu = []  # neighbor list
        self.Su = []  # sample list

    def update_neighbor_list(self, Nu_t):
        #This method updates the sample list of the node with the first max_storage elements of the list Su
        self.Nu = Nu_t[:self.max_storage]  # update neighbor list with the first max_storage elements

    def update_sample_list(self, Su_t):
        #This method updates the sample list of the node with the first max_storage elements of the list Su
        self.Su = Su_t[:self.max_storage]  # update sample list with the first max_storage elements

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
