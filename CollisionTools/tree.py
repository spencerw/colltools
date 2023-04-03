import sys
import numpy as np

class Node:
    def __init__(self):
        self.iord = -1
        self.children = []
        self.parent = None
        self.parent_time = sys.float_info.max # Time at which this node connected to the parent

class Tree:
    def __init__(self, coll, d1, s1):
        self.root = Node()
        self.coll = coll
        self.d1 = d1
        self.s1 = s1

    def build(self):
        for idx in np.arange(len(self.coll['time']))[::-1]:
            self.add(idx, self.root)

    # Iterate through collision log and add nodes one by one
    # If I go backward, don't need to worry about time of collision,
    # since internal nodes will always be added first
    # find the node corresponding to a given iorder in the tree
    def find(self, iorder, node):
        if node.iord == iorder:
            return node
        elif node.children:
            for child in node.children:
                result = self.find(iorder, child)
                if result:
                    return result

    def add(self, idx, root):
        s_iord, d_iord = self.s1[idx], self.d1[idx]
        if self.coll['time'][idx] > sys.float_info.max:
            raise Exception('Bad colltime value: ' + str(self.coll['time'][idx]) +
                            str(self.s1[idx]) + str(self.d1[idx])  + str(idx))
        survivor_node = self.find(s_iord, root)

        if survivor_node is None:
            survivor_node = Node()
            survivor_node.iord = s_iord
            survivor_node.parent = root
            survivor_node.parent_time = self.coll['time'][idx]
            root.children.append(survivor_node)

        # create new leaf node for deleted particle
        del_node = Node()
        del_node.iord = d_iord
        del_node.parent = survivor_node
        del_node.parent_time = self.coll['time'][idx]
        survivor_node.children.append(del_node)

        # Make sure both nodes have their times set
        if survivor_node.parent_time == sys.float_info.max or \
                del_node.parent_time == sys.float_info.max:
            raise Exception('Node not set: ' +
                            str(self.coll['time'][idx]) + str(self.s1[idx]) +
                            str(self.d1[idx]) + str(idx))
