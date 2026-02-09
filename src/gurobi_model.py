import permutation as perm # not nice to import it
import gurobipy as gp
from gurobipy import GRB

class GurobiModel:
    def __init__(self):
        env = gp.Env(empty=True)
        env.setParam('OutputFlag', 0)
        env.setParam('Threads', 1)
        env.start()
        self.model = gp.Model("mip", env=env)
        self.x = dict() # vote has a region
        self.i = dict() # is inner region
        self.c = 0

    def add_variable(self, elem, exists=False):
        varx = self.model.addVar(vtype=GRB.BINARY, name=f"x{elem}")
        self.x[elem] = varx 
        vari = self.model.addVar(vtype=GRB.BINARY, name=f"i{elem}")
        self.i[elem] = vari
        self.model.addConstr(0 <= varx - vari, f"ix{elem}")
        if exists:
            self.model.addConstr(varx == 1, f"x1{elem}")

    def implication(self, left, right):
        expr = sum([1-self.x[v] for v in left]) + sum([self.x[v] for v in right])
        self.model.addConstr(expr >= 1, f"impl{'_'.join([str(a) for a in left])}")

    def neighbours_constraint(self, v, vr, neighbours):
        self.model.addConstr(self.i[v] + self.i[vr] <= 1, f"r{v}") # inner region does not have reverse
        self.model.addConstr(self.x[v] - self.x[vr] - self.i[v] + self.i[vr] == 0, f"r{v}") # outer regions must have reverse
        all_neighbours = sum([self.x[v] for v in neighbours])
        self.model.addConstr(all_neighbours >= 2*(self.x[v])+self.i[v], f"n{v}") # inner regions have degree at least 3 and outer regions at least 2
        outneighbours = sum([self.x[v]-self.i[v] for v in neighbours])
        self.model.addConstr(outneighbours >= 2*(self.x[v]-self.i[v]), f"no{v}") # outer regions have 2 outer neighbours

    def linear_constraint(self, muls, k):
        sum = 0
        for a in muls:
            sum += muls[a]*self.x[a]
        self.model.addConstr(sum<= k, f"l{self.c}")
        self.c += 1

    def at_least_one(self, votes):
        vars = [self.x[v] for v in votes]
        self.model.addConstr(sum(vars) >= 1, f"alo")

    def at_most_k(self, votes, k):
        vars = [self.x[v] for v in votes]
        self.model.addConstr(sum(vars) <= k, f"amk")

    def compute(self, max_inner, max_outer):
        inner = sum([self.i[v] for v in self.x])
        self.model.addConstr(inner <= max_inner, f"inner")

        outer = sum([self.x[v] - self.i[v] for v in self.x])
        self.model.addConstr(outer <= max_outer, f"outer")
        
        obj = sum([self.x[v] for v in self.x])
        self.model.setObjective(obj, GRB.MINIMIZE)
        self.model.optimize()

        if self.model.Status == GRB.INFEASIBLE:
            return False
        obj = int(self.model.ObjVal)
        x = dict()
        i = dict()
        for v in self.model.getVars():
            p = perm.permutation(list(map(int, v.VarName[3:-1].split(",")))) # TODO suboptimal
            if v.VarName[0] == 'x':
                x[p] = int(v.X)
            else:
                i[p] = int(v.X)
        return obj, x, i
