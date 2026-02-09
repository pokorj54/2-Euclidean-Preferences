import unittest
import itertools
import permutation as perm

PP = perm.profile
P = perm.permutation

class MyTest(unittest.TestCase):
    def test_swap(self):
        self.assertEqual(perm.swap(P([0,1,2,3,4,5]), 0,5),P([5,1,2,3,4,0]))
        self.assertEqual(perm.swap(P([0,1,2,3,4,5]), 2,4),P([0,1,4,3,2,5]))
        self.assertEqual(perm.swap_next(P([0,1,2,3]), 0),P([1,0,2,3]))
        self.assertEqual(perm.swap_next(P([0,1,2,3]), 1),P([0,2,1,3]))
        self.assertEqual(perm.swap_next(P([0,1,2,3]), 2),P([0,1,3,2]))

    def test_swap_distance(self):
        self.assertEqual(P([0,1,2]).swap_distance(P([0,1,2])), 0)
        self.assertEqual(P([0,2,1]).swap_distance(P([0,1,2])), 1)
        self.assertEqual(P([2,1,0]).swap_distance(P([0,1,2])), 3)
        p = P([1,3,0,2])
        q = P([0,1,2,3])
        self.assertEqual(p.swap_distance(q), 3)
        self.assertEqual(p, P([1,3,0,2]))
        self.assertEqual(q, P([0,1,2,3]))
        self.assertEqual(P([0,1,2,3,4,5]).swap_distance(P([1,3,5,0,2,4])), 6)
        
    def test_swapped(self):
        self.assertEqual(P([0,1,2]).swapped(P([0,1,2])), set())
        self.assertEqual(P([0,2,1]).swapped(P([0,1,2])), {(1,2)})
        self.assertEqual(P([2,1,0]).swapped(P([0,1,2])), {(1,2),(0,1),(0,2)})
        p = P([1,3,0,2])
        q = P([0,1,2,3])
        self.assertEqual(p.swapped(q), {(0,3),(2,3),(0,1)})
        self.assertEqual(p, P([1,3,0,2]))
        self.assertEqual(q, P([0,1,2,3]))
        self.assertEqual(P([0,1,2,3,4,5]).swapped(P([1,3,5,0,2,4])), {(0,1), (2,3),(0,3), (4,5),(2,5),(0,5)})

    def test_subpermutation(self):
        permutations = PP([
            [0, 1, 4, 3, 5, 2], 
            [0, 2, 3, 5, 4, 1], 
            [0, 3, 2, 1, 5, 4], 
            [1, 0, 4, 2, 5, 3], 
            [1, 3, 2, 5, 0, 4], 
            [1, 3, 5, 0, 2, 4], 
            [2, 0, 4, 5, 1, 3], 
            [2, 0, 5, 3, 4, 1]
        ])
        self.assertEqual(perm.subpermutations(permutations, [0,1,2,3,4,5]), permutations)

        self.assertEqual(perm.subpermutations(permutations, [1,3,4,5]), PP([
            [0,2,1,3],
            [1,3,2,0],
            [1,0,3,2],
            [0,2,3,1],
            [0,1,3,2],
            [2,3,0,1],
            [3,1,2,0]
        ]))

        permutations2 = PP([
            [4,0,1,2,3], 
            [0,4,1,2,3], 
            [0,1,4,2,3], 
            [0,1,2,4,3], 
            [0,1,2,3,4]
        ])
        self.assertCountEqual(perm.subpermutations(permutations2, [0,1,2,3]), PP([[0,1,2,3]]))


    def test_get_neighborhood(self):
        self.assertEqual(perm.get_neighborhood(P([0,1,2])), [P([1,0,2]),P([0,2,1])])

    def test_identify_4_cycles(self):
        C = [
            P([0,1,2,3]),
            P([1,0,2,3]),
            P([1,0,3,2]),
            P([0,1,3,2])
        ]
        self.assertEqual(perm.identify_4cycle(C), ((0,1), (2,3)))
        C2 = [
            P([0,2,1,3,4,5,6]),
            P([0,2,1,3,5,4,6]),
            P([0,1,2,3,5,4,6]),
            P([0,1,2,3,4,5,6])
        ]
        self.assertEqual(perm.identify_4cycle(C2), ((1,2), (4,5)))
        
    
    def test_identify_6_cycles(self):
        C = [
            P([0,1,2,3,4]),
            P([0,2,1,3,4]),
            P([0,2,3,1,4]),
            P([0,3,2,1,4]),
            P([0,3,1,2,4]),
            P([0,1,3,2,4])
        ]
        self.assertEqual(perm.identify_6cycle(C), (1,2,3))
        C = [
            P([1,2,0]),
            P([2,1,0]),
            P([2,0,1]),
            P([0,2,1]),
            P([0,1,2]),
            P([1,0,2])
        ]
        self.assertEqual(perm.identify_6cycle(C), (0,1,2))
        
        C = [
            P([0,1,2,3,4,5]),
            P([1,0,2,3,4,5]),
            P([1,0,3,2,4,5]),
            P([1,0,3,2,5,4]),
            P([0,1,3,2,5,4]),
            P([0,1,2,3,5,4]),
        ]
        self.assertIsNone(perm.identify_6cycle(C))

    def test_block_decomposition(self):
        self.assertEqual(perm.block_decomposition([[1,2], [1,2]]), [[[1],[1]], [[2], [2]]])
        self.assertEqual(perm.block_decomposition([[1,2,3], [1,3,2], [1,2,3]]), [[[1],[1],[1]], [[2,3], [3,2], [2,3]]])
        self.assertEqual(perm.block_decomposition([[1,2,3], [3,1,2], [2,1,3]]), [[[1,2,3], [3,1,2], [2,1,3]]])
        self.assertEqual(perm.block_decomposition([[4,3,2,5,1,6], [4,2,3,5,1,6], [4,5,3,2,1,6]]), 
                         [[[4], [4], [4]],[[3,2,5], [2,3,5], [5,3,2]],[[1], [1], [1]],[[6], [6], [6]]])


    def test_block_composition(self):
        self.assertEqual(perm.block_composition([[[1],[1]], [[2,3], [3,2]]]), PP([[0,1,2], [0,2,1]]))
        self.assertEqual(perm.block_composition([[[1],[1],[1]], [[2,3,4], [3,2,4], [2,4,3]]]), PP([[0,1,2,3], [0,2,1,3], [0,1,3,2]]))
        self.assertEqual(perm.block_composition([[[1,2,3], [3,1,2], [2,1,3]]]), PP([[0,1,2], [2,0,1], [1,0,2]]))
    
    def test_indexes(self):
        self.assertEqual(perm.indexes([0,1,2,3]), [0,1,2,3])
        self.assertEqual(perm.indexes([1,3,2,0]), [3,0,2,1])

    def test_types_of_bisectors(self):
        self.assertEqual(perm.types_of_bisectors([[0, 1, 2], [2, 1,0]]), {(True, False), (False, True)})

    def test_too_many_bisectors(self):
        permutations = PP([
            [5, 0, 4, 1, 3, 2],
            [1, 4, 5, 0, 3, 2],
            [4, 0, 5, 1, 2, 3],
            [0, 1, 3, 4, 5, 2]
        ])
        self.assertTrue(perm.too_many_bisectors(permutations))
        self.assertTrue(perm.too_many_hull_bisectors(permutations))
        permutations2 = list(itertools.permutations([0,1,2,3], 4))
        self.assertFalse(perm.too_many_bisectors(permutations2))

    
    def test_too_many_hull_bisectors(self):
        permutations = [
            [1,0,2,3,4,5,6,7,8,9,11,10,12,13,14,15,17,16],
            [0,1,3,2,4,5,6,7,8,9,11,10,13,12,14,15,16,17],
            [0,1,2,3,5,4,6,7,8,9,10,11,13,12,15,14,16,17],
            [0,1,2,3,4,5,7,6,8,9,10,11,12,13,15,14,17,16],
            [0,1,2,3,4,5,6,7,9,8,10,11,12,13,14,15,16,17]
        ]
        self.assertTrue(perm.too_many_hull_bisectors(PP(permutations)))
        permutations[4] = list(range(len(permutations[0])))
        self.assertFalse(perm.too_many_hull_bisectors(PP(permutations)))
if __name__ == '__main__':
    unittest.main()