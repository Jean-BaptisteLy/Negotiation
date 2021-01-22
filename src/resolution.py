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
def biggestTour(Z,agents):
	max_path = 0
	for z_key,z_value in Z.items():
		for agent in z_key:
			value_path = tour(agents[agent],z_value)
			if value_path > max_path:
				max_path = value_path
	return max_path

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

def agent_utility(greaterValue,tour_value):
	pass

# tournée entière
# tournées des deux agents
def conflict_point(greaterValue,Z,key_Z,agents,current_agent_1_utility_conflict=None,current_agent_2_utility_conflict=None):
	conflict_point = []
	for key in key_Z:
		conflict_point.append(greaterValue - tour(agents[key],Z[key_Z]))
	#return tuple(conflict_point)
	return conflict_point

def zeuthens():
	pass

def agreement():
	pass

def nash_product():
	pass

# Processus de négociation
# greater value than the cost of the largest possible tour (greaterValue)
def negotiation(agents,objects,d,greaterValue):

	# Initialisation
	agents_utilities = []

	# objets visibles avec la distance d
	agents_visible_objects = perception(agents,objects,d)
	print("agents_visible_objects :",agents_visible_objects)

	# ensemble Z (objets en commun)
	Z = set_Z(agents_visible_objects)
	print("Z :",Z)

	# la plus grande tournée
	biggestTour_value = biggestTour(Z,agents)
	print("biggestTour :",biggestTour_value)

	# valeur plus grande que le coût de la plus grande tournée possible
	greaterValue += biggestTour_value
	print("greaterValue :",greaterValue)

	# point de conflit
	key_Z = (1,2)
	conflict_point_value = conflict_point(greaterValue,Z,key_Z,agents,current_agent_1_utility_conflict=None,current_agent_2_utility_conflict=None)	
	print("conflict_point :",conflict_point_value)

	pass
