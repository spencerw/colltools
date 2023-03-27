from handler import Handler

class gengaHandler(Handler):
    def __init__(self, sim_path):
        Handler.__init__(self, sim_path)

    def process_output(self):
        print('process genga output at ' + self.simpath)

    def build_tree(self):
        print('build genga collision tree at ' + self.simpath)

