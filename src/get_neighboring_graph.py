import permutation as perm

permutations = perm.get_permutations_from_stdin()

edges = []

for p in permutations:
    for q in permutations:
        if q > p:
            continue
        if q in perm.get_neighborhood(p):
            edges.append((p,q))

print("\n".join([ "".join(map(str,p)) for p in permutations]))
print("\n".join([ "".join(map(str,p))+" "+"".join(map(str,q)) for p,q in edges]))