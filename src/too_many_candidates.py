import permutation as perm
import itertools

def too_many_candidates(permutations):
    """Returns true if is a forbidden profile from Bogomolnaia, Anna & Laslier, Jean-Francois. (2004). Euclidean preferences. 
    Else returns False.
    Particularly, the instance has to have 3 voters of form i: a_P1, a_P2, ... a_0, a_N1, a_N2, ..., where i is in every P and not in any N."""
    if len(permutations[0]) < 8:
        return False 
    for subperms in itertools.combinations(permutations, 3):
        val = too_many_candidates_inner(perm.profile(subperms))
        if val:
            return val
    return False


def too_many_candidates_inner(permutations):
    if permutations.n != 3:
        return False
    # choose one candidate
    for c in permutations.candidates():
        seen = 1 # set as integer
        # compare every other candidate whether to get comparison vector (list of pre)
        for cc in permutations.candidates():
            if c == cc:
                continue
            a = [p.index(c) > p.index(cc) for p in permutations]
            seen = seen | (2**(a[0]+2*a[1]+4*a[2])) 
        # 8 possible vectors, but (0,0,0) does not happen
        if seen == 2**8-1:
            return True
    return False