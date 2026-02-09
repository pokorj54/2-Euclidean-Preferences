# Code instruction

For licences and general information see the root level `README.md`.

## Installation
- you will need to install packages in `requirements.txt` -- run `pip3 install -r requirements.txt`
- the solver `Gurobi Optimizer` requires a licence for nontrivial instances
- to be able to use the EST heuristic (https://zenodo.org/records/8157233), a symbolic link `solver_link` to the solver has to be provided to the folder containing `main` (compiled executable)

## Measurements
- all the instances we used are taken from preflib repository: https://github.com/PrefLib/PrefLib-Data
- we used only the `.soc` files

## Running the solver
- run the solver as a `python3 main.py --filename path_to_instance.soc`
- on stdout there will be outputed:
  - first the name of the instance
  - how much was the instance reduced in the format `m m_after_reductions [used_reduction_rules]`
  - one line for each runned heuristic in the format `heuristic_name result running_time`
- on stderr there may be extra information about the heuristics
- the solver can be modified with adding the configuration file with `-c config.json`, it only recursively overwrites the config entries in `main.py`
- the heuristics names differ slightly from the paper, use the following map to translate the names 
{
    "hull++": "Hull",
    "valtr": "EST",
    "TMC": "3-8",
    "IR": "ILP"
}
- the program can be run on multiple instances with the use of the script `measure.sh`.

## Creating the visualizations
- run `python3 visualizations.py ../data/data.csv`
- the images will be in folder `../imgs`

