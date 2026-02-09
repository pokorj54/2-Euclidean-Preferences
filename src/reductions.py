import permutation as perm
import itertools

def remove_middle_rightcopy_candidates(permuatations):
    """Removes candidates such that in each permutation the same candidate is one position to the right and there exist a candidate that is allways better (left)."""
    for c in permuatations.candidates():
        if permuatations.right_same(c) and permuatations.pareto_better(c) is not None:
            permuatations.remove_candidate(c)
            return True
    return False

def remove_middle_rightcopies(permuatations):
    while remove_middle_rightcopy_candidates(permuatations):
        continue
    return permuatations

def inducedlist(l, elems):
    """Recursively remove elements that are not in elems"""
    res = []
    for e in l:
        if isinstance(e, list):
            res.append(inducedlist(e, elems))
        elif e in elems:
            res.append(e)
    return res

def recursivemap(l, m):
    res = []
    for e in l:
        if isinstance(e, list):
            res.append(recursivemap(e,m))
        else:
            res.append(m(e))
    return res
    

def block_contains(big, small):
    if len(big[0]) < len(small[0]):
        return False
    for comb in itertools.combinations(big[0], len(small[0])):
        newb = inducedlist(big, comb)
        newnewb = recursivemap(newb, lambda e: small[0][newb[0].index(e)])
        if small == newnewb:
            return True
    return False
            


def remove_upto_k_block_copy(permutations, max_size):
    """Removes blocks of size at most max_size such that the block has a copy on different candidates and behind this block are only blocks of size maxsize or less"""
    bd = perm.block_decomposition(permutations)
    removed = [False for _ in bd]
    for i in range(len(bd)-1, -1, -1):
        b = bd[i]
        if len(b[0]) > max_size:
            break
        for j, bb in enumerate(bd):
            if i == j or removed[j]:
                continue
            if block_contains(bb, b):
                removed[i] = True
    new_bd = [ b for i, b in enumerate(bd) if not removed[i]]
    return perm.block_composition(new_bd)

def reduce_all(permutations):
    used = []
    old_m = permutations.m
    permutations = remove_middle_rightcopies(permutations)
    if old_m != permutations.m:
        used.append(("middle",(permutations.n, permutations.m)))
    old_m = permutations.m
    permutations = remove_upto_k_block_copy(permutations, 3)
    if old_m != permutations.m:
        used.append(("k-block",(permutations.n, permutations.m)))
    return permutations, used