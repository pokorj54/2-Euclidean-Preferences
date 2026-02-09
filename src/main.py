import argparse
import permutation as perm
import reductions as red
import implied_regions as ir
import solver_wrapper as sw
import qcp_solver as qcp
from too_many_candidates import too_many_candidates

import psutil
import multiprocessing 
import time
from timeit import default_timer as timer
import os
import sys
import signal
import resource
import traceback

working_folder = '/tmp/folder/'
solver_folder = './solver_link/'

DEFAULT_CONFIG = {
    # If True every heuristic is run even if the result is already known, else it stops when the result is known
    # (if parallel = false, then only heuristics that can answer the same thing are run)
    "run_all":True,
    "timeout":100,
    "parallel": True,
    "reduce": True,
    'memory_limit': 1024**3,
    # Array of heuristics that will be run, default values for each possible argument
    "heuristics": {
        "hull":{},
        "hull++":{},
        "TMC":{},
        "valtr":{
            "solver_directory": solver_folder, 
            "working_directory": working_folder},
        "QCP":{
            "timeout":10,
            "max_coordinate":100,
            "coordinate_mul":10,
            "timeout_mul":2,
            "repeats":3},
        "IR":{
            "draw_graph":False,
            "skip_heuristic": None,
            "single_subset_tries":20,
            "random":True
         },
    },
}

MEMORY_LIMIT = 1024**3

def signal_handler(sig, frame):
    print('Terminating', file=sys.stderr)
    sys.exit(0) 

def init():
    signal.signal(signal.SIGINT, signal_handler)
    if not os.path.isdir(working_folder):
        os.mkdir(working_folder)
    parser = argparse.ArgumentParser('')
    parser.add_argument('--filename', '-f', action='store', help='.soc file for input')
    parser.add_argument('--config', '-c', action='store', help='.json config file determining what will be run')
    return parser.parse_args()

def valtr_heuristic(permutations, **kwargs):
    return sw.SolverWrapper(**kwargs).run(permutations)

def get_skip_heuristic(config):
    valtr = config["heuristics"]["valtr"] if "valtr" in config["heuristics"]["valtr"] else None
    valtr_f = lambda p: None
    if valtr != None:
        valtr = valtr.copy()
        valtr["timeout"] = 3
        SW = sw.SolverWrapper(**valtr["params"])
        valtr_f = lambda p: SW.run(p)
    reducible = lambda p: len(red.reduce_all(p)[1]) > 0
    return lambda p: True if trivial(p) or reducible(p) else valtr_f(p)

refutation_map = {True: False, False: None}
name_to_heuristic = {
        'hull': lambda p, **kwargs: refutation_map[perm.too_many_bisectors(p, **kwargs)],
        'hull++': lambda p, **kwargs: refutation_map[perm.too_many_hull_bisectors(p, **kwargs)],
        'TMC': lambda p, **kwargs: refutation_map[too_many_candidates(p, **kwargs)],
        'valtr': valtr_heuristic,
        'QCP': qcp.increasing_bound_QCP,
        'IR': lambda p, **kwargs: ir.goat_path_refutation(p,**kwargs)
}

possible_answers = {
    'hull': [None, False],
    'hull++': [None, False],
    'TMC': [None, False],
    'valtr': [None, False, True],
    'QCP': [None, True],
    'IR': [None, False]
}

def read_input(args):
    filename = args.filename
    if filename is not None:
        print(filename, file=sys.stderr)
        with open(filename) as f:
            permutations = perm.import_from_soc(f.readlines())
    else:
        permutations = perm.get_permutations_from_stdin()
    assert(perm.valid_permutations(permutations))
    return permutations

def stats_template(config, file, permutations):
    stats = {}
    stats["instance"] = file
    stats["votes"] = permutations.n
    stats["candidates"] = permutations.m
    stats["trivial"] = None
    stats["reductions"] = None
    for heuristic in config["heuristics"]:
        stats[f"{heuristic}_val"] = None
        stats[f"{heuristic}_time"] = None
    return stats

def reductions_string(used):
    strings = [f'{rule}({n};{m})' for rule,(n,m) in used]
    return "|".join(strings)

def print_stats(stats):
    head = ""
    data = ""
    for key in stats:
        head += key + ","
        data += str(stats[key]) + ","
    print(head[:-1])
    print(data[:-1])

def trivial(permutations):
    """
    Solves triviall Yes and No instances - for given n,m all instances are known to be one answer.

    Returns True when the instance is small enough that only YES instances are possible.
    From 2-Dimensional Euclidean Preferences by Laurent Bulteau, Jiehua Chen available at https://arxiv.org/abs/2205.14687
    
    Returns False when the number of permutations is bigger than upperbound on the number of regions.
    """
    if permutations.n < 3 or (permutations.n == 3 and permutations.m <= 7) or permutations.m <= 3:
        return True
    if permutations.n > ir.max_regions(len(permutations[0])):
        return False
    return None


def run_heuristic(name, permutations, args):
    memory_limit = MEMORY_LIMIT
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
    start = timer()
    f = name_to_heuristic[name]
    res = None
    try:
        res = f(permutations, **args)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
    end = timer()
    duration = end - start
    return name, res, duration

def update_config(config):
    heuristics = config["heuristics"]
    if "valtr" in heuristics and "timeout" not in heuristics["valtr"]:
        heuristics["valtr"]["timeout"] = config["timeout"]
    for h in heuristics:
        if "skip_heuristic" in heuristics[h] and heuristics[h]["skip_heuristic"]:
            heuristics[h]["skip_heuristic"] = get_skip_heuristic(config)

def solve_parallel(permutations,config, stats):
    pool = multiprocessing.Pool()
    arglists = []
    heuristics = config["heuristics"]
    for h in heuristics:
        arglists.append((h, permutations, heuristics[h]))

    pool_res = []
    for args in arglists:
        p = pool.apply_async(run_heuristic, args)
        pool_res.append(p)
    
    start = time.time()
    res = None
    while time.time() - start <= config["timeout"]:
        val = None
        i = 0
        while i < len(pool_res): 
            if pool_res[i].ready():
                name, val, duration = pool_res[i].get()
                print(name, val, duration, file=sys.stderr)
                stats[f"{name}_time"] = duration
                stats[f"{name}_val"] = val
                pool_res.pop(i)
                if val is not None:
                    if res is not None:
                        assert res == val
                    res = val
            else:
                i += 1
        if res is not None and not config["run_all"]:
            break
        if len(pool_res) == 0:
            break
        time.sleep(0.1)
    children = [c.pid for c in multiprocessing.active_children()]
    parent = psutil.Process(multiprocessing.current_process().pid)
    psu_children = parent.children(recursive=True)
    pool.terminate()
    # pool will not ensure grandchildren are terminated
    for child in psu_children:
        try:
            if child.pid not in children:
                child.terminate()
        except:
            pass # there is no need to terminate it if already terminated
    return res

def raise_timeout_exception(signum, frame):
    raise TimeoutError()

def run_with_timeout(func, timeout):
    signal.signal(signal.SIGALRM, raise_timeout_exception)
    signal.alarm(timeout)
    try:
        result = func()
        signal.alarm(0)  # Cancel the alarm
        return result
    except TimeoutError:
        return None

def solve_singethreaded(permutations, config, stats):
    heuristics = config["heuristics"]
    res = None
    for h in heuristics:
        if not config["run_all"] and res not in possible_answers[h]:
            print(h, "skipped", file=sys.stderr)
            continue
        fres = run_with_timeout(lambda: run_heuristic(h, permutations, heuristics[h]), config["timeout"])
        if fres is None:
            print(h, "timeout", file=sys.stderr)
            continue
        name, val, duration = fres
        print(name, val, duration, file=sys.stderr)
        stats[f"{name}_time"] = duration
        stats[f"{name}_val"] = val
        if val is not None:
            if res is not None:
                assert res == val
            res = val
    return res
    
def solve(permutations, config, stats):
    stats["trivial"] = trivial(permutations)
    if stats["trivial"] is not None:
        return True

    old = len(permutations[0])
    if config["reduce"]:
        permutations, used = red.reduce_all(permutations)
        stats["reductions"] = reductions_string(used)
    print(old, len(permutations[0]), used, file=sys.stderr)
    
    update_config(config)
    if config["parallel"]:
        return solve_parallel(permutations, config, stats)
    return solve_singethreaded(permutations,config, stats)


def merge_configs(default, changes):
    for key in changes:
        if isinstance(changes[key], dict):
            default[key] = merge_configs(default[key], changes[key])
        else:
            default[key] = changes[key]
    return default

def get_config(args):
    if args.config is not None:
        import json
        with open(args.config, 'r') as f:
            config = json.load(f)
        return merge_configs(DEFAULT_CONFIG, config)
    return DEFAULT_CONFIG

def main():
    args = init()
    permutations = read_input(args)
    config = get_config(args)
    if 'memory_limit' in config:
        global MEMORY_LIMIT
        MEMORY_LIMIT = config['memory_limit']
    stats = stats_template(config, args.filename,permutations)
    result = solve(permutations, config, stats)
    print_stats(stats)
    print("result:", result, file=sys.stderr)

if __name__ == "__main__":
    main()
