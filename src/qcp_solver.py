import gurobipy as gp
from gurobipy import GRB

import embeddding

def increasing_bound_QCP(permutations, max_coordinate, timeout=10, coordinate_mul=10, timeout_mul=2, repeats=3):
    i = 0
    while i < repeats:
        qcp_res = QCP_model(permutations, max_coordinate=max_coordinate, timeout=timeout).compute()
        if qcp_res:
            return qcp_res
        max_coordinate*=coordinate_mul
        timeout_mul*=timeout_mul
        i+=1
    return None

class QCP_model:
    """Formulates the problem as dist(v,a) < dist(v, b) for v: any < a < b < any in 2D euclidean space.
    Non strict operator with epsilon is used.
    Every point for votes and candidates is enclosed in a square"""
    def __init__(self, permutations, timeout, max_coordinate):
        self.c_vars = dict()
        self.v_vars = dict()
        self.penalties = dict()
        env = gp.Env(empty=True)
        env.setParam('OutputFlag', 0)
        env.setParam('Threads', 1)
        env.setParam('NonConvex', 2)
        env.start()
        self.model = gp.Model("qcp", env=env)
        self.epsilon = 1
        self.max_coord = max_coordinate
        self.timeout = timeout
        self.permutations = permutations
        self.create_model()
        self.lb = -self.epsilon*self.permutations.n*(self.permutations.m-1)

    def add_positions_variables(self, point, variables, prefix):
        varx = self.model.addVar(lb=-self.max_coord, ub=self.max_coord, name=f"{prefix}_x_{point}")
        vary = self.model.addVar(lb=-self.max_coord, ub=self.max_coord, name=f"{prefix}_y_{point}")
        variables[point] = [varx, vary]

    def distance_constraint(self, vote, c1, c2):
        vx, vy = self.v_vars[vote]
        c1x, c1y = self.c_vars[c1]
        c2x, c2y = self.c_vars[c2]
        d = self.model.addVar(lb=-self.epsilon, name=f"e{vote}_{c1}_{c2}")
        self.penalties[(vote,c1,c2)] = d
        self.model.addConstr((vx-c1x)**2 + (vy-c1y)**2 <= d + (vx-c2x)**2 + (vy-c2y)**2, name=f"c{vote}_{c1}_{c2}")

    def create_model(self):
        for i,_ in enumerate(self.permutations):
            self.add_positions_variables(i,self.v_vars,'v')
        for i in self.permutations[0]:
            self.add_positions_variables(i, self.c_vars, 'c')

        for i,v in enumerate(self.permutations):
            for j in range(0, len(v)-1):
                self.distance_constraint(i, v[j], v[j+1])

        # fixing one candidate to 0,0 and other one to be on y axis
        self.model.addConstr(self.c_vars[self.permutations[0][0]][0] == 0)
        self.model.addConstr(self.c_vars[self.permutations[0][0]][1] == 0)
        self.model.addConstr(self.c_vars[self.permutations[0][1]][0] == 0)

    def check_valid_embedding(self):
        v_coords = {i:[None, None] for i,_ in enumerate(self.permutations)}
        c_coords = {c:[None, None] for c in self.permutations[0]}
        for var in self.model.getVars():
            t, c, i = var.VarName.split('_')
            if t != 'v' and t != 'c':
                continue
            coords = v_coords if t == 'v' else c_coords
            coords[int(i)][ord(c)-ord('x')] = var.X
        assert embeddding.valid_embedding(self.permutations, v_coords, c_coords)

    def return_val(self):
        if self.model.Status in {GRB.TIME_LIMIT, GRB.INTERRUPTED}:
            return None
        res = self.model.ObjVal
        embeddable = res == self.lb # as long as epsilon is perfectly represantable this should be ok
        if embeddable:
            self.check_valid_embedding()
        return embeddable

    def compute(self):
        obj = 0
        for key in self.penalties:
            obj += self.penalties[key]
        self.model.setObjective(obj, GRB.MINIMIZE)
        self.model.setParam('TimeLimit', self.timeout)
        self.model.optimize()
        return self.return_val()
