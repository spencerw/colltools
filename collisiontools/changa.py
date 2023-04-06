from handler import Handler
import glob as gl
import natsort as ns
import os
import pynbody as pb
import numpy as np
import pandas as pd
import KeplerOrbit as ko

class ChaNGaHandler(Handler):
    def __init__(self, simpath, two_phase=False):
        print('init changa handler')
        self.two_phase = two_phase

        Handler.__init__(self, simpath)

        self.get_sim_properties()

        icfile = gl.glob(self.simpath + '*.ic')
        if len(icfile) == 0:
            raise Exception('No IC file for ChaNGa handler')
        icfile = icfile[0]
        self.snap0 = ko.orb_params(pb.load(icfile), isHelio=True, mCentral=self.m_central)

        final_snap = ns.natsorted(gl.glob(self.simpath + '*.[0-9]*[0-9]'))
        if len(final_snap) == 0:
            raise Exception('No snapshot files for ChaNGa handler')
        final_snap = final_snap[-1]
        self.final_snap = ko.orb_params(pb.load(final_snap), isHelio=True, mCentral=self.m_central)

    def process_output(self, clobber):
        print('process ChaNGa output at ' + self.simpath)
        self.build_deletion_list(clobber)
        self.build_coll_log(clobber)

    def verify_output(self):
        collfile = gl.glob(self.simpath + '*.coll')[0]
        coll1 = pd.read_csv(collfile)

        delfile = gl.glob(self.simpath + 'delete*')[0]
        d1, s1 = np.loadtxt(delfile, dtype='int', unpack=True)

        print('Snapshot difference | collision log size | deletion log size | merger deletions | # unique deletions')
        print(len(self.snap0) - len(self.final_snap), len(coll1), len(d1), len(d1[s1 >= 0]), len(np.unique(d1)))

        if (len(self.snap0) - len(self.final_snap)) == len(coll1) == len(d1) == len(np.unique(d1)):
            print('ChaNGa output counts match')
        else:
            print('Warning: ChaNGa output verification failure!')

    def get_sim_properties(self):
        print('getting sim properties')
        param_files = gl.glob(self.simpath + '*.param')
        if len(param_files) == 0:
            raise Exception('ChaNGa could not find a param file')
        d = {}
        with open(param_files[0]) as f:
            for line in f:
                spl = line.split()
                if len(spl) > 0:
                    key, eq, val = spl[0:3]
                    d[key] = val

        self.m_central = float(d['dCentMass'])
        self.delta_t = float(d['dDelta'])

    def build_deletion_list(self, clobber):
        print('building deletion list')
        
        outputs = ns.natsorted(gl.glob(self.simpath + 'output*'))

        if not os.path.exists(self.simpath + 'delete1') or clobber:
            print('creating new deletion file')
            os.system(" grep 'Merge' " + outputs[0] + " | awk -F 'Merge' '{print $2}' \
                    | awk '{print $1, $3}' > " + self.simpath + "delete1")
            os.system(" grep -o 'Particle [^\s]*' " + outputs[0] + \
                      " | awk '{print $2 \" -2\"}' >> " + self.simpath + "delete1")

        if self.two_phase and (not os.path.exists(self.simpath + 'delete2') or clobber):
            os.system(" grep 'Merge' " + ' '.join(outputs[1:]) + " | awk -F 'Merge' '{print $2}' \
                    | awk '{print $1, $3}' > " + self.simpath + "delete2")

        # For twophase, lets remap iorders and merge these into a single file

    def build_coll_log(self, clobber):
        print('build collision log')

        outputs = ns.natsorted(gl.glob(self.simpath + 'output*'))

        if not os.path.exists(self.simpath + 'coll1.coll') or clobber:
            print('creating new collision file')
            os.system("grep 'collision:' " + outputs[0] + " | cut -d' ' -f2- > " + self.simpath + \
                    "coll1.coll")
        if self.two_phase and (not os.path.exists(self.simpath + 'coll2.coll') or clobber):
            os.system("grep 'collision:' " + ' '.join(outputs[1:]) + " | cut -d' ' -f2- > " + self.simpath \
                    + "coll2.coll")

        # For twophase, remap iorders and merge into a single file

    def get_coll_data(self):
        collfile = gl.glob(self.simpath + '*.coll')[0]
        nam = ['time', 'collType', 'iord1', 'iord2', 'm1', 'm2', 'r1', \
               'r2', 'x1x', 'x1y', 'x1z', 'x2x', 'x2y', 'x2z', 'v1x', \
               'v1y', 'v1z', 'v2x', 'v2y', 'v2z', 'w1x', 'w1y', 'w1z', \
               'w2x', 'w2y', 'w2z']
        coll1 = pd.read_csv(collfile, names=nam, sep=' ', index_col=False)
        delfile = gl.glob(self.simpath + 'delete*')[0]
        d1, s1 = np.loadtxt(delfile, dtype='int', unpack=True)
        return coll1, d1, s1