from changa import ChaNGaHandler
from genga import gengaHandler
import numpy as np
import glob as gl
import pandas as pd
from tree import Tree

class CollisionTools:
    def __init__(self):
        print('init collisiontools')
        self.handler = None

    def add_handler(self, type, path):
        if type == 'ChaNGa':
            self.handler = ChaNGaHandler(path)
        elif type == 'genga':
            self.handler = gengaHandler(path)
        else:
            raise Exception(type + ' handler not a recognized type')

    def process_output(self, clobber=False):
        self.handler.process_output(clobber)

    def verify_output(self):
        self.handler.verify_output()

    def build_tree(self):
        # Load the collision and deletion logs
        collfile = gl.glob(self.simpath + '*.coll')[0]
        coll1 = pd.read_csv(collfile)
        delfile = gl.glob(self.simpath + 'delete*')[0]
        d1, s1 = np.loadtxt(delfile, dtype='int', unpack=True)

        tree = Tree(coll1, d1, s1)
        tree.build()