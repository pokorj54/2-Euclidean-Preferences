import unittest
import too_many_candidates as tmc
import itertools
# import tqdm
import random
import permutation

P = permutation.permutation
PP = permutation.profile

class TMC_Test(unittest.TestCase):
    def original_instance(self):
        a0 = 0
        a1 = 1
        a2 = 2
        a3 = 3
        a12 = 4
        a13 = 5
        a23 = 6
        a123 = 7
        perms = PP([
            [a1,a12,a13,a123,a0,a2,a3,a23],
            [a2,a12,a23,a123,a0,a1,a3,a13],
            [a3,a13,a23,a123,a0,a1,a2,a12]
        ])
        return perms
    
    # TODO simplify
    # def test_too_many_candidates_all_minimal(self):
    #     perms = self.original_instance()
    #     pp = itertools.permutations([0,1,2,3])
    #     np = itertools.permutations([5,6,7])
    #     m = [ep+(4,)+en for ep, en in itertools.product(pp, np)]
    #     for maps in tqdm.tqdm(itertools.combinations(m, 3)):
    #         perms_copy = PP([list(map(lambda a: perms[i][a], maps[i])) for i in range(3)])
    #         self.assertTrue(tmc.too_many_candidates(perms_copy))

    

    def test_drawable(self):
        
        perms = [
            [0,1,2,3,4,5,6],
            [0,1,2,3,4,5,6],
            [0,1,2,3,4,5,6]
        ]
        for _ in range(100):
            for p in perms:
                random.shuffle(p)
            pp = PP(perms)
            self.assertFalse(tmc.too_many_candidates(pp))
            pcopy = [p.copy() for p in perms]
            for p in pcopy:
                p.append(7)
            pp = PP(pcopy)
            self.assertFalse(tmc.too_many_candidates(pp))
        
if __name__ == '__main__':
    unittest.main()