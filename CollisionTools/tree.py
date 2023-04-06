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
        print('Building collision tree...')
        for idx in np.arange(len(self.coll['time']))[::-1]:
            self.add(idx, self.root)

        # Remove central body colliders from tree
        cen_coll = self.d1[self.s1 < 0]
        for idx, n in enumerate(self.root.children):
            if np.isin(n.iord, cen_coll):
                del self.root.children[idx]
        print('Complete!')

    def verify_build(self, snap0, snap_final):
        root_iords = np.zeros(len(self.root.children))
        for idx in range(len(self.root.children)):
            root_iords[idx] = self.root.children[idx].iord

        # Ensure root iords and remaining iords of final snapshot match
        if not np.array_equal(np.sort(root_iords), np.sort(snap_final['iord'])):
            print('Warning: root iords and final snapshot iords dont match')
            m0 = np.min(snap0['mass'])
            print(len(root_iords), len(snap_final[snap_final['mass'] > m0]))

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
        survivor_node = self.find(s_iord, root)

        if survivor_node is None:
            survivor_node = Node()
            survivor_node.iord = s_iord
            survivor_node.parent = root
            root.children.append(survivor_node)

        # create new leaf node for deleted particle
        n = Node()
        n.iord = d_iord
        n.parent = survivor_node
        n.parent_time = self.coll['time'][idx]
        survivor_node.children.append(n)