import random
import copy
import time
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
from sys import maxsize
from itertools import permutations

def smallestTour():
	# TODO
	pass

def manhattanDistance(p1,p2):
	(x1,y1) = p1
	(x2,y2) = p2
	return abs(x1 - x2) + abs(y1 - y2)

# Tournée
# INPUT : list , list[lists]
# OUTPUT : integer
def tour(depart, objects):
	tours = list(permutations(objects,len(objects)))
	#print(tours)
	min_path = maxsize
	for t in tours:
		valeur_tournee = 0
		#print(t)
		#print("######################")
		new_depart = depart
		for i in range(len(t)):
			#print(i)
			#if i != len(t): # si pas encore arrivé à la fin
			valeur_tournee += manhattanDistance(new_depart,t[i])
			new_depart = t[i]
			#print(valeur_tournee)
		if valeur_tournee < min_path:
			min_path = valeur_tournee
	return min_path

#def biggestTour(agents,objects):
def biggestTour(Z):
	pass

# matrix representation of graph using Manhattan distance for input TSP
# INPUT : 
# OUTPUT : 
def matrix_representation_graph(agents,objects):
	mrg = []
	for a_key,a_value in agents.items():
		mrg_a = []
		for o_key,o_value in objects.items():
			mrg_a.append(manhattanDistance(a_value,o_value))
		mrg.append(mrg_a)
	return mrg

# ce que perçoivent les robots avec la distance d
# INPUT : list list integer
# OUTPUT : {a:[(x,y)]}
def perception(agents,objects,d):
	#distance de manhattan sur tous les objets
	#pour chaque distance, si elle est inférieure à d
	#alors prendre en compte l'objet pour l'agent

	# objets perçus par les agents avec la distance
	agents_visible_objects = {}
	for a_key,a_value in agents.items():
		#print(a_key,a_value)
		visible_objects = []
		for o_key,o_value in objects.items():
			if manhattanDistance(a_value,o_value) <= d:
				visible_objects.append(o_value)
		agents_visible_objects[a_key] = visible_objects
	return agents_visible_objects


# INPUT : {a:[(x,y)]} 
# OUTPUT : dict (agent1,agent2) : [(x,y)]
def set_Z(agents_visible_objects):
	# objets en commun
	Z = {}
	# toutes les combinaisons possibles, formation des couples d'agents
	couples = list(map(dict, it.combinations(agents_visible_objects.items(), 2)))
	for couple in couples:
		fusion_liste = []
		partners = []
		for couple_key,couple_value in couple.items():
			fusion_liste.append(couple_value)
			partners.append(couple_key)
		# éléments en communs dans un couple d'agents
		common_elements = list(set(fusion_liste[0]).intersection(fusion_liste[1]))
		if common_elements: # si éléments en commun, couple confirmé
			Z[(partners[0],partners[1])] = common_elements
	return Z

def zeuthens():
	pass

def conflict_point():
	pass

def agreement():
	pass

def nash_product():
	pass

# Processus de négociation
def negotiation(agents,objects,d):
	
	#biggestTour() # TODO

	Z = perception(agents,objects,d)