import numpy as np
import glob as gl
import pandas as pd
import re

import KeplerOrbit

def make_coll_log(path):
    '''
    Grab collision data from a series of ChaNGa output files and store
    it in a Pandas data frame which is then written to disk
    Parameters:
    ----------
    path : string
        The path to the directory where the output files are stored and
        the collision log will be written
    '''

    def tryint(s):
        try:
            return int(s)
        except ValueError:
            return s

    def alphanum_key(s):
        return [tryint(c) for c in re.split('([0-9]+)', s)]

    def sort_nicely(l):
        return sorted(l, key=alphanum_key)

    filenames = sort_nicely(gl.glob(path+'output.*'))
    colnames = 'time iorder1 iorder2 m1 m2 r1 r2 x1x x1y x1z x2x x2y x2z xNewx ' \
    'xNewy xNewz v1x v1y v1z v2x v2y v2z vNewx vNewy vNewz w1x w1y w1z w2x w2y ' \
    'w2z wNewx wNewy wNewz'
    colnames = colnames.split(' ')
    print(len(colnames))

    merger_count = 0
    data = []
    time_str = 0.
    idx1 = 0
    for idx, val in enumerate(filenames):
        print(val)
        print("Processing file {0} of {1}\r".format(idx+1, len(filenames)))
        f = open (val)
        data_float = []
        for line in f:
            if line[0:5] == 'Merge' and line[6].isdigit():
                merger_count += 1
            if line[0:4] == 'Step':
                time_str = line.split(':')[2][1:8]
            if line[0].isdigit() and len(line) > 30 and "particles" not in line:
                data_str = line.split()
                for item in data_str:
                    data_float.append(float(item))
                line_count = 0
                data_float.insert(0, float(time_str))
                data.append(data_float)
                data_float = []
        f.close()

    d = pd.DataFrame(data, columns=colnames)
    d.to_csv(path+'collisions')
    print(str(merger_count) + ' collisions')

class Node:
    def __init__(self, iord):
        self.iord = iord
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

class CollisionLog:
    def __init__(self, path_to_table):
        self.coll = pd.read_csv(path_to_table)
        
        # There are two entries for each collision
        # Remove every other row
        self.coll = self.coll.iloc[::2]

    def build_tree_for(self, iord):
        '''
        Generate a tree for the collision history for a single particle.
        Parameters:
        ----------
        iord : int
            The iorder of the particle to generate a collision history for
        Returns:
        n : Node
            The root note of the collision history tree
        '''

        def build_tree_helper(n, coll_sub):
            # Given n.iord, find every collision that involves this ID
            colls1 = coll_sub[coll_sub['iorder2'] == n.iord]
            colls2 = coll_sub[coll_sub['iorder1'] == n.iord]
            child_iord = np.concatenate((colls1['iorder1'].values, colls2['iorder2'].values))
    
            # Remove these collisions from the table so they don't get counted again
            coll_sub = coll_sub.drop(np.concatenate((colls1.index, colls2.index)))
    
            # Generate a new child node for each of those collisions
            for iord in child_iord:
                child = Node(iord)
                build_tree_helper(child, coll_sub)
                n.add_child(child)

        coll_sub = self.coll
        n = Node(iord)
        build_tree_helper(n, coll_sub)

        return n
        
    def get_leaf_iords(self, n):
        '''
        Given a collision history tree, get the iorders of all leaf nodes
        Parameters:
        ----------
        n : Node
            The root node of the tree
        Returns:
        leafs : List
            A list of the iorders of the leaf nodes
        '''
        def get_leafs_helper(n, leafs):
            if not n.children:
                leafs.append(n.iord)
            else:
                for child in n.children:
                    get_leafs_helper(child, leafs)

        leafs = []
        get_leafs_helper(n, leafs)

        return leafs

    def get_coll_kepler(self, mc_c):
        '''
        Calculate the kepler orbital elements for each collision in the table.
        Add these parameters as extra columns to the dataframe
        Parameters:
        ----------
        mc_c : float
            The mass of the central body, in simulation units
        '''
        x_c_c1, y_c_c1, z_c_c1 = self.coll['x1x'], self.coll['x1y'], self.coll['x1z']
        vx_c_c1, vy_c_c1, vz_c_c1 = self.coll['v1x'], self.coll['v1y'], self.coll['v1z']
        m1_c = self.coll['m1']
        a_c_c1, e_c_c1, inc_c_c1, Omega_c_c1, omega_c_c1, M_c_c1 = \
        KeplerOrbit.cart2kepX(x_c_c1, y_c_c1, z_c_c1, vx_c_c1, vy_c_c1, vz_c_c1, mc_c, m1_c)
        x_c_c2, y_c_c2, z_c_c2 = self.coll['x2x'], self.coll['x2y'], self.coll['x2z']
        vx_c_c2, vy_c_c2, vz_c_c2 = self.coll['v2x'], self.coll['v2y'], self.coll['v2z']
        m2_c = self.coll['m2']
        a_c_c2, e_c_c2, inc_c_c2, Omega_c_c2, omega_c_c2, M_c_c2 = \
        KeplerOrbit.cart2kepX(x_c_c2, y_c_c2, z_c_c2, vx_c_c2, vy_c_c2, vz_c_c2, mc_c, m2_c)

        self.coll['a1'] = a_c_c1
        self.coll['e1'] = e_c_c1
        self.coll['inc1'] = inc_c_c1
        self.coll['Omega1'] = Omega_c_c1
        self.coll['omega1'] = omega_c_c1
        self.coll['M1'] = M_c_c1

        self.coll['a2'] = a_c_c2
        self.coll['e2'] = e_c_c2
        self.coll['inc2'] = inc_c_c2
        self.coll['Omega2'] = Omega_c_c2
        self.coll['omega2'] = omega_c_c2
        self.coll['M2'] = M_c_c2
