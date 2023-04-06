from collisiontools import CollisionTools

tools = CollisionTools()
tools.add_handler('ChaNGa', 'changasim/')

tools.process_output(True)
tools.verify_output()
tools.build_tree()

#tools.get_root_property('a')