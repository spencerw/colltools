from changa import ChaNGaHandler
from genga import gengaHandler
import numpy as np
import glob as gl
import pandas as pd
from tree import Tree
import pickle
import sys

class CollisionTools:
    def __init__(self):
        print('init collisiontools')
        self.handler = None

    def add_handler(self, type, simpath):
        self.simpath = simpath
        if type == 'ChaNGa':
            self.handler = ChaNGaHandler(simpath)
        elif type == 'genga':
            self.handler = gengaHandler(simpath)
        else:
            raise Exception(type + ' handler not a recognized type')

    def process_output(self, clobber=False):
        self.handler.process_output(clobber)

    def verify_output(self):
        self.handler.verify_output()

    def build_tree(self):
        coll1, d1, s1 = self.handler.get_coll_data()
        # If there are two simulations, need to grab collision data for second one
        # And then consolidate logs

        tree = Tree(coll1, d1, s1)
        tree.build()

        # Write the tree data to a pickle object
        treepath = self.simpath + 'tree.dat'
        with open(treepath, 'wb') as f:
            pickle.dump(tree.root, f)

        tree.verify_build(self.handler.snap0, self.handler.final_snap)

    def get_tree(self):
        with open(self.simpath + '/tree.dat', 'rb') as f:
            root = pickle.load(f)

        return root

    def get_root_property(self, prop, snap=None, time=sys.float_info.max):
        if snap is None:
            snap = self.handler.final_snap
        with open(self.simpath + '/tree.dat', 'rb') as f:
            root = pickle.load(f)

        def find(node, iord):
            if node.iord == iord:
                return node
            elif node.children:
                for c in node.children:
                    result = find(c, iord)
                    if result:
                        return result

        root_iord = np.ones(len(self.handler.snap0)) * -1

        def get_roots_at(node, time, parent_iord):
            root_iord[node.iord] = parent_iord
            for c in node.children:
                if c.parent_time < time:
                    get_roots_at(c, time, parent_iord)

        # Need to filter out the earth colliders first
        for iord in snap['iord']:
            node = find(root, iord)
            get_roots_at(node, time, node.iord)

        root_prop = []
        for i in range(len(snap)):
            child_ind = np.argwhere(root_iord == snap['iord'][i])
            root_prop.append(pl0[prop][child_ind])

        return root_prop