import subprocess
import permutation as perm

class SolverWrapper:
    def __init__(self, solver_directory, working_directory, timeout):
        self.solver_dir = solver_directory
        self.work_dir = working_directory
        self.timeout = timeout
        

    def run(self, permutations):
        new_filename = self.work_dir + str(hash(str(permutations)))
        with open(new_filename,  "w") as f:
            f.write(perm.export_to_soc(permutations))

        return self.run_from_file(new_filename)
        # TODO clean created files - solver creates also debug file
    
    def parse_result(lines):
        result = lines[len(lines)-2]
        i = len(lines)-1
        while i >= 0 and '1' not in lines[i]:
            i -=1
        assert i >= 0
        result = None if 'NOT DECIDED' in lines[i] else 'YES' in lines[i]
        return result
    
    def run_from_file(self, filename):
        # default timeout 1h
        p = subprocess.run(['./main', '-in', filename, '-timeout', str(self.timeout)], cwd=self.solver_dir, stdout=subprocess.PIPE)
        out = p.stdout
        if len(out) == 0:
            return None 
        lines = bytes.decode(out).split('\n')
        # TODO verify embedding
        return SolverWrapper.parse_result(lines)