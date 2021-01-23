from itertools import *

def partition(tasks):
    """
    Cacule toutes les partitions possibles étant donné un ensemble de tâches.
    """
    l1 = []
    l2 = []
    for pattern in product([True,False],repeat=len(tasks)):
        l1.append(tuple([x[1] for x in zip(pattern,tasks) if x[0]]))
        l2.append(tuple([x[1] for x in zip(pattern,tasks) if not x[0]]))

    return list(zip(l1,l2))


def non_dominated_po(partitions):
    """
    Étant donné un dictionnaire de partitions qui nous permet de connaître la valeur
    de chaque partition, on fait le traitement des partitions de manière à enlèver celles
    qui sont Pareto-dominées.
    """
    # List of pareto-optimal points
    po = {}
    for part, ut in partitions.items():
        dominated = False
        # We add the task only if it is not dominated
        for other_part, other_ut in partitions.items():
            if (other_ut[0] > ut[0] and other_ut[1] > ut[1] and other_part != part) or (other_ut[0] > ut[0] and other_ut[1] == ut[1] and other_part != part) or (other_ut[0] == ut[0] and other_ut[1] > ut[1] and other_part != part) or (ut in po.values()):
                dominated = True
                continue
        if not dominated:
            po[part] = ut
        
    return po