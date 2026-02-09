# Data

For licences and general information see the root level `README.md`.

Here is a single file containing the measurements of our implementation on the PrefLib dataset. 
Each approach has `_val` and `_time` column. The `_val` column is either `None`, `False` or `True`, answering the question "Is this instance 2-Euclidean?" where `None` means that the apporach is not able to decide.


The heuristics names differ slightly from the paper, use the following map to translate the names 
{
    "hull++": "Hull",
    "valtr": "EST",
    "TMC": "3-8",
    "IR": "ILP"
}

The heuristic `hull` is same as `hull++`, except `hull` is has a constraint that exactly 4 voters are used. 
