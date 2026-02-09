import permutation as perm
import gurobi_model as gm
import itertools
import random
import math
import sys

def flatten(l):
    newl = []
    for ll in l:
        newl += ll
    return newl

def handle_must_be_regions_p_q(permutations, queue, visited, p,q):
    neighbors = get_neighbors_on_the_shortes_path(p,q)
    n = neighbors[0]
    if len(neighbors) == 1 and n != q and n not in permutations:
        for r in permutations:
            if n == r:
                continue
            enq(queue,visited, n, r)
        permutations.add(n)

def must_be_regions(permutations):
    permutations = set(permutations)
    queue = []
    visited = set()
    for p in permutations:
        for q in permutations:
            if p == q:
                continue
            enq(queue,visited,p,q)
    while len(queue) > 0:
        p,q = queue.pop(0)
        handle_must_be_regions_p_q(permutations,queue,visited,p,q)
        handle_must_be_regions_p_q(permutations,queue,visited,q,p)
    return permutations
        
def max_regions(m):
    return m*(3*m -10)*(m-1)*(m+1)//24 + m*(m - 1) + 1

def max_outer_regions(m):
    return m*(m-1)

def max_inner_regions(m):
    return max_regions(m) - max_outer_regions(m)

def max_4_cycles(m):
    return m*(m-1)*(m-2)*(m-3)//8

def max_bisector_neighbours(m):
    return m-1+(m-2)*(m-3)//2

def find_k_cycles_inner(existing, current, k, result, induced):
    if len(current) == k:
        if current[0].swap_distance(current[-1]) == 1:
            result.append(current.copy())
        return
    if len(current) == 0:
        for p in existing:
            current.append(p)
            find_k_cycles_inner(existing, current, k, result, induced)
            current.pop(0)
    else:
        for p in perm.get_neighborhood(list(current[-1])):
            if p not in existing or p <= current[0] or p in current:
                continue
            if len(current) == k-1 and p <= current[1]: # to eliminate taking reverse of the cycle
                continue
            if induced:
                not_induced = False
                pneighborhood = perm.get_neighborhood(p)
                for i,q in enumerate(current):
                    if q in pneighborhood and i != len(current)-1 and not (i == 0 and k == len(current)+1):
                        not_induced = True
                        break
                if not_induced:
                    continue
            current.append(p)
            find_k_cycles_inner(existing, current, k, result, induced)
            current.pop(-1)

def find_k_cycles(existing, k, induced = True):
    assert k > 3
    assert k % 2 == 0
    result = []
    find_k_cycles_inner(existing, [], k, result, induced)
    return result

class Model:
    def __init__(self, implementation, permutations):
        self.model = implementation
        self.permutations = permutations.copy()
        for p in permutations:
            self.model.add_variable(p, True)

    def encode(self, p):
        if type(p[0]) is perm.permutation:
            return [self.encode(q) for q in p]
        if p not in self.permutations:
            self.permutations.add(p)
            self.model.add_variable(p)
        return p

    def existing_permutations(self):
        return list(self.permutations)
    
    def implication(self, left, right):
        self.model.implication(self.encode(left), self.encode(right))

    def neighbours_constraint(self, p):
        neighbours = perm.get_neighborhood(p)
        pr = p.reverse()
        self.model.neighbours_constraint(p, self.encode(pr), self.encode(neighbours))

    def cycle_constraints(self, cycles):
        """Set of cycles that are identified by the same two bisectors or a triplet of candidates"""
        for c1,c2 in itertools.combinations(cycles, 2):
            assert len(c1) == len(c2)
            c = c1 + c2
            multiplicities = {p: c.count(p) for p in set(c)}
            self.model.linear_constraint(multiplicities, len(c)-1)

    def neighbours_constraints(self):
        for p in self.existing_permutations().copy():
            self.neighbours_constraint(p)

    def at_least_one(self, votes):
        self.model.at_least_one(votes)

    def at_most_k(self, votes, k):
        self.model.at_most_k(votes, k)

    def compute(self,single_subset_tries):
        m = len(next(iter(self.permutations)))
        self.neighbours_constraints()
        while True:
            single_subset_tries -= 1
            res = self.model.compute(max_inner_regions(m), max_outer_regions(m))
            if not res or single_subset_tries == 0 or not further_constraints(self, res[1], res[2]):
                return res
            print('lb', res[0], file=sys.stderr)
    
def get_neighbors_on_the_shortes_path(p, q):
    neighbours = perm.get_neighborhood(p)
    dist = p.swap_distance(q)
    return [neigh for neigh in neighbours if neigh.swap_distance( q) == dist-1]

def enq(queue, visited, p,q):
    assert(p != q)
    if q > p:
        return enq(queue, visited, q, p)
    if (p, q) in visited:
        return
    visited.add((p,q))
    queue.append((p,q))

def first_candidate_buckets(permutations):
    first = dict()
    for p in permutations:
        if p[0] not in first:
            first[p[0]] = []
        first[p[0]].append(p)
    return first

def somebody_prefers_each_candidate(model, permutations):
    further = False
    m = len(permutations)
    total = perm.factorial(m-1)
    first_candidates = first_candidate_buckets(permutations)
    for c in first_candidates:
        if len(first_candidates[c]) == total:
            model.at_least_one(first_candidates[c])
            further = True
    return further

def bisector_neighbors(model, permutations):
    further = False
    m = len(next(iter(permutations)))
    # for each bisector
    for a in range(m):
        for b in range(a+1, m):
            pairs = []
            for p in permutations:
                ia = p.index(a)
                if ia < m-1 and p[ia+1] == b:
                    pp = perm.swap_next(p, ia)
                    if pp in permutations:
                        pairs.append(p)
                        pairs.append(pp)
            mn = max_bisector_neighbours(m)
            if len(pairs)//2 > mn:
                # TODO add AND variable and remove pairs of them
                model.at_most_k(pairs, len(pairs)//2 + mn)
                further = True
    return further

def cycle_conflicts(x):
    conflicts = dict()
    for k, f in [(4, perm.identify_4cycle),(6, perm.identify_6cycle)]:
        cycles = find_k_cycles({a for a in x if x[a] == 1}, k)
        for cycle in cycles:
            id = f(cycle)
            if id is None:
                continue
            if id not in conflicts:
                conflicts[id] = []
            conflicts[id].append(cycle)
    return {id: conflicts[id] for id in conflicts if len(conflicts[id]) >= 2}

def further_constraints(model, x, i):
    further = False
    for p in x:
        for q in x:
            if q == p:
                continue
            neighbours = get_neighbors_on_the_shortes_path(p,q)
            unsat = x[q] + x[p] == 2
            for n in neighbours:
                if n not in x:
                    unsat = True
                    break
                unsat = unsat and x[n] == 0
            if unsat:
                model.implication([q,p], neighbours)
                further = True
        pneighbours = perm.get_neighborhood(p)
        if x[p] == 1:
            sum = 0
            outer_sum = 0
            for q in pneighbours:
                if q in x:
                    sum += x[q]
                    outer_sum += x[q] - i[q]
            if sum < 2 +i[p] or (i[p] == 0 and outer_sum < 2):
                model.neighbours_constraint(p)
                further = True
    conflicts = cycle_conflicts(x)
    for id in conflicts:
        model.cycle_constraints(conflicts[id])
        further = True
    subperms0 = list(filter(lambda p: p not in x or x[p] == 0, model.permutations))
    further = somebody_prefers_each_candidate(model, subperms0) or further
    subperms1 = list(filter(lambda p: p not in x or x[p] == 1, model.permutations))
    bisector_neighbors(model, subperms1)
    return further


def implied_regions_dumb(perms, model):
    seen = set()
    last_count = -1
    while last_count != model.permutations.n:
        last_count = model.permutations.n
        for p in model.existing_permutations():
            for q in model.existing_permutations():
                if p >= q or (p,q) in seen:
                    continue
                implied = get_neighbors_on_the_shortes_path(p,q)
                model.implication([p,q],implied)
                seen.add((p,q))

    # single_subset_tries: how many times can we add lazy constraints, 0 = no limit
def get_lb_through_implied_regions(perms,single_subset_tries=0):
    model = Model(gm.GurobiModel(), perms)
    implied_regions_dumb(perms, model)
    return model.compute(single_subset_tries)

def random_generator(all_elems, size):
    seen = set()
    while len(seen) < math.comb(len(all_elems), size):
        p = random.sample(all_elems, size)
        p = tuple(p)
        if p in seen:
            continue
        seen.add(p)
        yield p


def sorted_generator(all_elems, size):
    return itertools.combinations(all_elems, size)


def goat_path_refutation(permutations, draw_graph=False, skip_heuristic=None, single_subset_tries=0, random=False):
    """Returns False if we can refute it, None if we do not know"""
    all_elems = list(range(len(permutations[0])))
    generator = random_generator if random else sorted_generator
    for i in range(5, len(permutations[0])+1):
        for subset in generator(all_elems, i):
            subset_perms = perm.subpermutations(permutations, subset)
            if skip_heuristic is not None and skip_heuristic(subset_perms):
                print(len(subset), "skipped", subset, flush=True, file=sys.stderr)
                continue
            res = get_lb_through_implied_regions(subset_perms, single_subset_tries)
            if not res:
                print(len(subset), "infeasable", subset, flush=True, file=sys.stderr)
                return res
            lb, x, i = res
            if draw_graph:
                import draw_graph
                draw_graph.draw_graph(x,i,f'/tmp/graph{str(subset)}.pdf') #TODO - working directory?
            ub = max_regions(len(subset))
            print(len(subset), "ir_lb:",lb,"ub:",ub ,"set:", subset, flush=True, file=sys.stderr)
            if lb > ub:
                return False
    return None
