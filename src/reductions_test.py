import unittest
import reductions as red
import permutation as perm

PP = perm.profile

class MyTest(unittest.TestCase):
    def test_remove_upto_k_block_copy(self):
        self.assertEqual(red.remove_upto_k_block_copy(PP([[0,1,2],[1,0,2]]), 3), PP([[0,1], [1,0]]))
        self.assertEqual(red.remove_upto_k_block_copy(PP([[0,1,2],[0,2,1]]), 3), PP([[0,1], [1,0]]))
        self.assertEqual(red.remove_upto_k_block_copy(PP([[0,1,2,3,4],[1,0,4,3,2]]), 3), PP([[0,1,2], [2,1,0]]))
        self.assertEqual(red.remove_upto_k_block_copy(PP([[0,1,2,3,4],[1,0,4,3,2]]), 2), PP([[0,1,2,3,4],[1,0,4,3,2]]))
        self.assertEqual(red.remove_upto_k_block_copy(PP([[0,1,2,3,4,5],[2,0,1,5,3,4],[1,2,0,4,5,3]]), 3), PP([[0,1,2], [2,0,1],[1,2,0]]))
        self.assertEqual(red.remove_upto_k_block_copy(PP([[0,1,2,3,4,5],[2,0,1,5,3,4],[1,2,0,4,5,3]]), 2), PP([[0,1,2,3,4,5],[2,0,1,5,3,4],[1,2,0,4,5,3]]))
        
        self.assertEqual(red.remove_upto_k_block_copy(PP([[0,1,2,3,4,5],[1,0,3,2,5,4]]), 2), PP([[0,1],[1,0]]))
        self.assertEqual(red.remove_upto_k_block_copy(
            PP([[0,1,2,3,4,5,6],[0,3,2,1,4,6,5],[0,2,1,3,4,6,5]]), 3
        ), PP([[0,1,2], [2,1,0], [1,0,2]])) # everything is 1,2 or 3 block, so 1 blocks (0, 5) are deleted, also 6 maps to 2, 5 maps to 1 to remove two blcok 5,6
        

    def test_remove_middle_rightcopy_candidates(self):
        self.assertEqual(red.remove_middle_rightcopies(PP([[0,1,2,3],[1,0,2,3]])), PP([[0,1,2],[1,0,2]]))
        self.assertEqual(red.remove_middle_rightcopies(PP([[0,1,2,3],[0,2,3,1]])), PP([[0,1,2],[0,2,1]]))
        self.assertEqual(red.remove_middle_rightcopies(PP([[0,1,2,3,4],[3,4,0,1,2],[0,2,3,4,1]])), PP([[0,1,2,3,4],[3,4,0,1,2],[0,2,3,4,1]]))
        self.assertEqual(red.remove_middle_rightcopies(PP([[0,1,2,3,4],[2,1,3,4,0],[0,2,3,4,1]])), PP([[0,1,2,3],[2,1,3,0],[0,2,3,1]]))


if __name__ == '__main__':
    unittest.main()