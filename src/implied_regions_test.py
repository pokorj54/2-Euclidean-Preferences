import unittest
import implied_regions as ir
import permutation as perm
    
P = perm.permutation
PP = perm.profile

class IR_test(unittest.TestCase):
    def validate_graph(self, permutations, lb, x, i):
        forced = ir.must_be_regions(permutations)
        for f in forced:
            self.assertTrue(x[f] == 1)
        for p in x:
            self.assertTrue(x[p] >= i[p])
            self.assertTrue(x[p] == 0 or x[p] == 1)
            self.assertTrue(i[p] == 0 or i[p] == 1)
            pr = p.reverse()
            if x[p] == 1:
                if i[p] == 0:
                    self.assertTrue(i[pr] == 0 and x[pr] == 1)
                elif i[p] == 1:
                    self.assertTrue(x[pr] == 0)
        


    def test_must_exist_regions(self):
        permutations = PP([[0,1,2],[2,0,1]])
        self.assertCountEqual(ir.must_be_regions(permutations), PP([[0,1,2],[2,0,1], [0,2,1]]))
        permutations = PP([[0,1,2,3,4,5],[5,0,1,2,3,4]])
        self.assertCountEqual(ir.must_be_regions(permutations), PP([[0,1,2,3,4,5],[0,1,2,3,5,4],[0,1,2,5,3,4],[0,1,5,2,3,4],[0,5,1,2,3,4],[5,0,1,2,3,4]]))
        permutations = PP([[0,1,2,3,4,5],[0,3,4,1,2,5]])
        self.assertCountEqual(ir.must_be_regions(permutations), PP([[0,1,2,3,4,5],[0,3,4,1,2,5],[0,3,1,4,2,5],[0,1,3,2,4,5]]))
        permutations = PP([[0,1,2,3,4],[2,0,3,1,4]])
        self.assertCountEqual(ir.must_be_regions(permutations), PP([[0,1,2,3,4],[2,0,3,1,4],[0,2,1,3,4]]))
        permutations = PP([
            [1, 0, 3, 2],
            [2, 1, 0, 3],
            [3, 0, 2, 1],
            [3, 1, 2, 0]
        ])

        implied = PP([
            [1, 0, 3, 2],
            [2, 1, 0, 3],
            [3, 0, 2, 1],
            [3, 1, 2, 0],
            [1, 0, 2, 3],
            [1, 2, 0, 3],
            [1, 2, 3, 0],
            [1, 3, 2, 0],
            [1, 3, 0, 2],
            [3, 1, 0, 2],
            [3, 0, 1, 2]
        ])
        self.assertCountEqual(ir.must_be_regions(permutations), implied)
        

    def test_get_lb_through_implied_regions(self):
        permutations = PP([[0,1,2],[2,1,0]])
        lb, x, i = ir.get_lb_through_implied_regions(permutations)
        self.assertEqual({P([0,1,2]):1, P([0,2,1]):1, P([1,0,2]):1,P([1,2,0]):1, P([2,0,1]):1, P([2,1,0]):1}, x)
        self.assertEqual({P([0,1,2]):0, P([0,2,1]):0, P([1,0,2]):0,P([1,2,0]):0, P([2,0,1]):0, P([2,1,0]):0}, i)
        permutations = PP([[0,1,2,3],[1,3,0,2]])
        lb, x, i = ir.get_lb_through_implied_regions(permutations)
        self.assertEqual({P([0,1,2,3]):1, P([1,3,0,2]):1, P([1,0,2,3]):1} | x, x)
        self.assertTrue(x[P([0,1,3,2])] + x[P([1,0,2,3])] == 1)

        permutations = PP([
            [1, 0, 3, 2],
            [2, 1, 0, 3],
            [3, 0, 2, 1],
            [3, 1, 2, 0]
        ])
        lb, x, i = ir.get_lb_through_implied_regions(permutations)
        self.validate_graph(permutations, lb, x, i)
    def test_max_4_cycles(self):
        self.assertEqual(ir.max_4_cycles(3),0) 
        self.assertEqual(ir.max_4_cycles(4),3) 
        self.assertEqual(ir.max_4_cycles(5),15) 

    def test_k_cycles(self):
        permutations = PP([
            [0,1,2,3],
            [1,0,2,3],
            [0,1,3,2],
            [1,0,3,2],
            [3,2,1,0]
        ])
        self.assertEqual(ir.find_k_cycles(permutations, 4), 
                         [[P([0, 1, 2, 3]), P([0, 1, 3, 2]), P([1, 0, 3, 2]), P([1, 0, 2, 3])]])
        permutations = PP([
            [0,1,2,3,4],
            [1,0,2,3,4],
            [0,1,3,2,4],
            [1,0,3,2,4],
            [0,1,2,4,3],
            [1,0,2,4,3],
        ])
        self.assertCountEqual(ir.find_k_cycles(permutations, 4), 
                         [[P([0, 1, 2, 3, 4]), P([0, 1, 3, 2, 4]), P([1, 0, 3, 2, 4]), P([1, 0, 2, 3, 4])], 
                          [P([0, 1, 2, 3, 4]), P([0, 1, 2, 4, 3]), P([1, 0, 2, 4, 3]), P([1, 0, 2, 3, 4])]])
        
        permutations = PP([
            [0,1,2,3,4,5],
            [0,2,1,3,4,5],
            [0,2,3,1,4,5],
            [0,3,2,1,4,5],
            [0,3,1,2,4,5],
            [0,1,3,2,4,5]
        ])
        self.assertCountEqual(ir.find_k_cycles(permutations, 6),  
            [[P([0,1,2,3,4,5]),
            P([0,1,3,2,4,5]),
            P([0,3,1,2,4,5]),
            P([0,3,2,1,4,5]),
            P([0,2,3,1,4,5]),
            P([0,2,1,3,4,5])
            ]])
        
        permutations = PP([
            [0,1,2,3,4,5],
            [1,0,2,3,4,5],
            [1,0,2,4,3,5],
            [1,0,4,2,3,5],
            [0,1,4,2,3,5],
            [0,1,2,4,3,5]
        ])
        self.assertCountEqual(ir.find_k_cycles(permutations, 6), [])
        
        
if __name__ == '__main__':
    unittest.main()