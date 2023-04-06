class Handler:
    def __init__(self, simpath):
        print('init handler')
        self.simpath = simpath

    def process_output(self, clobber):
        print('process output for handler')

    def verify_output(self):
        print('verify output for handler')

    def get_coll_data(self):
        print('grab collision data for handler')