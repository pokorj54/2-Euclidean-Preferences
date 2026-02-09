import itertools


def indexes(permutation):
    """Calculates index for each element of permutation."""
    inv = [-1 for _ in permutation]
    for i, x in enumerate(permutation):
        assert(x >= 0 and x < len(permutation))
        inv[x] = i
    for i in range(len(permutation)):
        assert(inv[i] >= 0 and inv[i] < len(permutation))
    return inv

def normalized(permutation):
    """Array is mapped to elements from 0, to n-1, the order is kept the same."""    
    d = dict()
    for i, val in enumerate(sorted(permutation)):
        d[val] = i
    return [d[i] for i in permutation]

def are_permuted_arrays(arrays):
    """Checks whether each array contains the same elements, duplicates are not allowed."""
    if len(arrays[0]) != len(set(arrays[0])): # no duplicates
        return False
    ref = sorted(arrays[0])
    for a in arrays:
        if sorted(a) != ref:
            return False
    return True

class permutation:
    def __init__(self, array):
        self.p = tuple(array)
        self.indexes = indexes(array)

    def __getitem__(self, i):
        return self.p[i]
    
    def __str__(self):
        return "P"+str(self.p)
    
    def __repr__(self): 
        return str(self)
    
    def __len__(self):
        return len(self.p)
    
    def __eq__(self, other): 
        return self.p == other.p

    def __le__(self, other):
        return self.p <= other.p
    
    def __lt__(self, other):
        return self.p <= other.p
    
    def __hash__(self):
        return hash(self.p)
    
    def index(self, a):
        return self.indexes[a]
    
    def remove(self, c):
        new_p = []
        for a in self.p:
            if a != c:
                if a > c:
                    a -= 1
                new_p.append(a)
        self.p = tuple(new_p)
        self.indexes = indexes(self.p)
        
    def reverse(self):
        """Returns new permutation that is reverse of the current one"""
        r = list(self.p)
        r.reverse()
        return permutation(r)

    def swap_distance(self, other):
        """Computes the number of (neighboring) swaps needed to get from p to q"""
        q = list(other.p)
        dist = 0
        for i in range(len(self.p)):
            if self.p[i] == q[i]:
                continue
            qpos = q.index(self.p[i], i+1)
            dist += qpos-i
            q.insert(i, q.pop(qpos))
        return dist
    
    def swapped(self, other):
        """Returns all the pairs of elements that are swapped in other"""
        res = set()
        for p in self.p:
            for q in self.p:
                if self.index(p) <= self.index(q):
                    continue
                if other.index(p) < other.index(q):
                    res.add((min(p,q), max(p,q)))
        return res
    
    def one_swapped(self, other):
        """Returns all the pairs of elements that are swapped in other"""
        res = self.swapped(other)
        assert len(res) == 1
        return res.pop()

class profile:
    def __init__(self, permutations, normalize=False):
        if normalize:
            assert(are_permuted_arrays(permutations))
            permutations = [normalized(p) for p in permutations]
        self.permutations = [permutation(p) for p in permutations]
        self.m = len(permutations[0])
        self.n = len(permutations)

    def __getitem__(self, i):
        return self.permutations[i]
    
    def __eq__(self, other):
        if other.n != self.n:
            return False
        for i in range(self.n):
            if self[i] != other[i]:
                return False
        return True
    
    def copy(self):
        return profile(self.permutations)
    
    def __str__(self):
        return "["+",".join([str(p) for p in self.permutations])+"]"
    
    def __repr__(self):
        return str(self)
    
    def candidates(self):
        return range(self.m)
    
    def add(self, p:permutation):
        assert isinstance(p, permutation)
        if p not in self.permutations:
            self.permutations.append(p)
    
    def pareto_better(self, candidate):
        """Finds a candidate that is prefered in every permutation.
        Returns None if no such exists."""
        for c in self.candidates():
            better = True
            for p in self.permutations:
                better = better and p.index(c) < p.index(candidate)
            if better:
                return c
        return None
        
    def right_same(self, candidate):
        """Returns whether after the @candidate is allways the same candidate"""
        ic = self.permutations[0].index(candidate)
        if ic + 1 == self.m:
            return False
        after = self.permutations[0][ic+1]
        for p in self.permutations:
            if p.index(candidate) +1 == self.m or p[p.index(candidate)+1] != after:
                return False
        return True
    
    def remove_candidate(self, c):
        """Removes candidate and renames bigger candidates, so there is no gap."""
        self.m = self.m-1
        for p in self.permutations:
            p.remove(c)
            
            assert self.m == len(p)
        
def factorial(n):
    if n <= 1:
        return 1
    return n*factorial(n-1)

def types_of_bisectors(permutations):
    patterns = set()
    for a in range(len(permutations[0])):
        for b in range(len(permutations[0])):
            if a == b: 
                continue
            pattern = []
            for i in range(len(permutations)):
                pattern.append(permutations[i].index(a) < permutations[i].index(b))
            patterns.add(tuple(pattern))
    return patterns


def too_many_bisectors(permutations):
    for subperms in itertools.combinations(permutations, 4):
        bt = types_of_bisectors(subperms)
        bt.discard((True, True, True, True))
        bt.discard((False, False, False, False))
        if len(bt) >= 14:
            return True
    return False

def shortest_cycle_length(graph):
    """Returns None if no cycle"""
    visited = set()
    for vertex in graph:
        if len(graph[vertex]) <= 1:
            continue 
        current = graph[vertex][0]
        parent = vertex
        l = 1
        while current != vertex and len(graph[current]) == 2:
            tmp = current
            current = graph[current][1] if graph[current][0] == parent else graph[current][0]
            parent = tmp
            l+=1
        if current == vertex:
            return l
    return None

def too_many_hull_bisectors(permutations):
    for i in range(4,permutations.n+1):
        for subperms in itertools.combinations(permutations, i):
            bt = types_of_bisectors(subperms)
            bt = sorted(bt, key=lambda x: x.count(True))
            graph = dict()

            for b in bt:
                if b.count(True) == 1:
                    graph[b.index(True)] = []
                if b.count(True) == 2:
                    i = b.index(True)
                    j = b.index(True, i+1)
                    if i in graph and j in graph:
                        graph[i].append(j)
                        graph[j].append(i)
            for key in graph:
                if len(graph[key]) > 2:
                    return True
            cycle_len = shortest_cycle_length(graph)
            if cycle_len is not None and cycle_len < len(graph):
                return True
    assert not too_many_bisectors(permutations)
    return False

def subpermutations(permutations, subset):
    subset = sorted(subset)
    c = 0
    mapping = [-1 for i in permutations[0]]
    for i in subset:
        mapping[i] = c
        c +=1
    new_perms = []
    for perm in permutations:
        new_perm = [mapping[i] for i in perm if mapping[i] != -1]
        if new_perm not in new_perms:
            new_perms.append(new_perm)
    return profile(new_perms)

def valid_permutations(permuatations):
    valid = True
    ref = [i for i in range(len(permuatations[0]))]
    for p in permuatations:
        valid = valid and sorted(p) == ref
    return valid

def get_neighborhood(p):
    neighbors = []
    for i in range(len(p)-1):
        neighbors.append(permutation(list(p[:i])+[p[i+1]]+[p[i]]+list(p[i+2:])))
    return neighbors

def swap(p, i, j):
    p = list(p.p)
    elems = p[i], p[j]
    p[j], p[i] = elems
    return permutation(p)

def swap_next(p, i):
    return swap(p, i, i+1)

def block_decomposition(permutations):
    start = 0
    vals = set()
    blocks = []
    for i in range(len(permutations[0])):
        for p in permutations:
            vals.add(p[i])
        if len(vals) == i -start +1:
            blocks.append([list(p[start:i+1]) for p in permutations])
            start = i+1
            vals = set()
    if len(vals) != 0:
        blocks.append([list(p[start:i+1]) for p in permutations])
        vals = set()
    return blocks

def block_composition(bd):
    permutations = [[] for b in bd[0]]
    for block in bd:
        for i in range(len(block)):
            permutations[i] += block[i]
    return profile(permutations, normalize=True)

def permutations_to_string(permutations):
    return f"{len(permutations)} {len(permutations[0])}\n" + "\n".join([ " ".join([str(i) for i in p]) for p in permutations])

def get_permutations_from_stdin():
    permutations = []
    n, _ = [int(i) for i in input().split(' ')]
    for _ in range(n):
        permutations.append([int(i) for i in input().strip().split(' ')])
    return profile(permutations)

def import_from_soc(lines):
    permutations = []
    for line in lines:
        if line == '\n' or line[0] == '#':
            continue
        permutations.append([int(a)-1 for a in line.split(":")[1].strip().split(",")])
    return profile(permutations)

def identify_4cycle(cycle):
    assert(len(cycle) == 4)
    b1 = cycle[0].one_swapped(cycle[1])
    assert b1 == cycle[2].one_swapped(cycle[3]) 
    b2 = cycle[1].one_swapped(cycle[2]) 
    assert b2 == cycle[3].one_swapped(cycle[0]) 
    return (min(b1,b2), max(b1,b2))

def identify_6cycle(cycle):
    assert(len(cycle) == 6)
    b1 = cycle[0].one_swapped(cycle[1]) 
    assert b1 == cycle[3].one_swapped(cycle[4]) 
    b2 = cycle[1].one_swapped(cycle[2]) 
    assert b2 == cycle[4].one_swapped(cycle[5])
    b3 = cycle[2].one_swapped(cycle[3]) 
    assert b3 == cycle[5].one_swapped(cycle[0])
    res = {*b1, *b2, *b3}
    if len(res) != 3:
        return None
    return tuple(sorted(list(res)))

def export_to_soc(permutations, min_elem = 1):
    res = ""
    res += '# FILE NAME: file.soc\n'
    res += '# TITLE: Generated\n'
    res += '# DESCRIPTION: Generated\n'
    res += '# DATA TYPE: soc\n'
    res += '# MODIFICATION TYPE: synthetic\n'
    res += f'# NUMBER ALTERNATIVES: {permutations.m}\n' 
    res += f'# NUMBER VOTERS: {permutations.n}\n'
    res += f'# NUMBER UNIQUE ORDERS: {permutations.n}\n'
    min_val = min(permutations[0])
    offset = min_elem - min_val
    for perm in permutations:
        res += '1:' + ",".join(map(lambda x: str(x+offset), perm)) + "\n"
    return res

