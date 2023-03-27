from handler import Handler
import glob as gl

class ChaNGaHandler(Handler):
    def __init__(self, sim_path, two_phase=False):
        print('init changa handler')
        self.two_phase = two_phase
        Handler.__init__(self, sim_path)

    def process_output(self):
        print('process ChaNGa output at ' + self.simpath)
        get_sim_propeties()
        build_deletion_list()
        build_coll_log()
        trim_coll_log()

    def get_sim_properties(self):
        print('getting sim properties')
        param_files = gl.glob(self.simpath + '*.param')
        if len(param_files) == 0:
            raise Exception('ChaNGa could not find a param file')
        d = {}
        with open(self.simpath + param_files[0]) as f:
            for line in f:
                spl = line.split()
                if len(spl) > 0:
                    key, eq, val = spl[0:3]
                    d[key] = val

         self.m_central = float(d['dCentMass'])
         self.delta_t = float(d['dDelta'])

    def build_deletion_list(self):
        print('building deletion list')
        
        outputs = ns.natsorted(gl.glob(self.simpath + 'output*'))

        if not os.path.exists(self.simpath + 'delete1'):
            os.system(" grep 'Merge' " + outputs[0] + " | awk -F 'Merge' '{print $2}' \
                    | awk '{print $1, $3}' > " + self.simpath + "delete1")
        if two_phase and not os.path.exists(self.simpath + 'delete2'):
            os.system(" grep 'Merge' " + ' '.join(outputs[1:]) + " | awk -F 'Merge' '{print $2}' \
                    | awk '{print $1, $3}' > " + self.simpath + "delete2")

    def build_coll_log(self):
        print('build collision log')
        if not os.path.exists(self.simpath + 'collide.coll'):
            os.system("grep 'collision:' " + outputs[0] + " | cut -d' ' -f2- > " + self.simpath + \
                    "fullDiskVHi.coll")
        if two_phase and not os.path.exists(self.simpath + 'collide1.coll'):
            os.system("grep 'collision:' " + ' '.join(outputs[1:]) + " | cut -d' ' -f2- > " + self.simpath \
                    + "fullDiskVHi1.coll")

    def build_tree(self):
        print('build ChaNGa collision tree at ' + self.simpath)

