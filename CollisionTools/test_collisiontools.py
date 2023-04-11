from collisiontools import CollisionTools
from unittest import TestCase
import numpy as np

class TestCollisiontools(TestCase):
    def test_single(self):
        tools = CollisionTools()
        tools.add_handler('ChaNGa', '../tests/changasim/')
        tools.process_output(clobber=True)
        tools.verify_output()
        tools.build_tree()

        coll1, d1, s1 = tools.handler.get_coll_data()

        self.assertEqual(len(coll1), 7557)
        self.assertEqual(len(np.unique(d1)), 9189)

        root = tools.get_tree()

        massmask = tools.handler.final_snap['mass'] > np.min(tools.handler.snap0['mass'])
        self.assertEqual(len(root.children), len(tools.handler.final_snap[massmask]))