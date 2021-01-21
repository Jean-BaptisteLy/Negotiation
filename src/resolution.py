import random
import copy
import time
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt

def biggestTour():
	pass

def manhattanDistance(p1,p2):
	(x1,y1) = p1
	(x2,y2) = p2
	return abs(x1 - x2) + abs(y1 - y2)

# ce que perçoivent les robots avec la distance d
# OUTPUT : {a:[(x,y)]}
def perception(agents,objects,d):
	#distance de manhattan sur tous les objets
	#pour chaque distance, si elle est inférieure à d
	#alors prendre en compte l'objet pour l'agent
	agents_visible_objects = {}
	id_agent = 0
	for a in agents:
		id_agent += 1
		visible_objects = []
		for o in objects:
			if manhattanDistance(a,o) == d:
				visible_objects.append(o)
		agents_visible_objects[id_agent] = visible_objects
	return visible_objects
