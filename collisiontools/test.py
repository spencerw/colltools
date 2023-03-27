from collisiontools import CollisionTools

tools = CollisionTools()
tools.add_handler('ChaNGa', 'changasim/')

tools.process_output()
tools.build_tree()
