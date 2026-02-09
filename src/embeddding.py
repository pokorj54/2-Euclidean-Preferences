def sqr_dist(a, b):
    return (a[0] - b[0])**2+(a[1] - b[1])**2

def is_closer(v, a, b):
    return sqr_dist(v,a) < sqr_dist(v,b)

def valid_embedding(votes, v_coords, c_coords):
    for i,v in enumerate(votes):
        for j in range(len(v)-1):
            if not is_closer(v_coords[i], c_coords[v[j]], c_coords[v[j+1]]):
                return False
    return True
