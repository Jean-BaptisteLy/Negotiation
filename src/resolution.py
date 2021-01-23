import random
import copy
import time
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
from sys import maxsize
from itertools import *
from itertools import permutations
from itertools import combinations
from operator import itemgetter

def manhattanDistance(p1,p2):
	(x1,y1) = p1
	(x2,y2) = p2
	return abs(x1 - x2) + abs(y1 - y2)

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
    de chaque partition, on fait le traitement des partitions de manière à enlever celles
    qui sont Pareto-dominées.
    """
    # List of pareto-optimal points
    #po = []
    po = {}
    for part, ut in partitions.items():
        dominated = False
        # We add the task only if it is not dominated
        for other_part, other_ut in partitions.items():
            if other_ut[0] >= ut[0] and other_ut[1] >= ut[1] and other_part != part:
                dominated = True
                continue
        if not dominated:
            #po.append(part)
            po[part] = ut
        
    return po

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
	couples = list(map(dict,combinations(agents_visible_objects.items(), 2)))
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
def conflict_point(greaterValue,Z,key_Z,agents,utilities_conflict):
	conflict_point = []
	for key in key_Z:
		if key in utilities_conflict:
			conflict_point.append(utilities_conflict[key])
		else:
			conflict_point.append(greaterValue - tour(agents[key],Z[key_Z]))
	#return tuple(conflict_point)
	return conflict_point

'''
# C'est directement implémenté dans negotiation() pour l'instant... à voir plus tard si on met ça au propre
def zeuthens():
	# TODO
	pass

def agreement():
	# TODO
	pass

def nash_product():
	# TODO
	pass
'''

# Processus de négociation
# greater value than the cost of the largest possible tour (greaterValue)
def negotiation(agents,objects,d,greaterValue):

	print("agents :",agents)
	print("objets :",objects)
	print("distance d :",d)
	print("valeur supplémantaire :",greaterValue)

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
	#key_Z = (1,2) # pour tester...
	#conflict_point_value = conflict_point(greaterValue,Z,key_Z,agents,current_agent_1_utility_conflict=None,current_agent_2_utility_conflict=None)	
	#print("conflict_point :",conflict_point_value)

	agreements = {}
	nash_products = {}
	utilities_conflict = {}

	# Négociation par Monotonic Concession Protocol
	for z_key,z_value in Z.items():

		# Initialisation :
		rounds = 0
		#conflict_point_value = conflict_point(greaterValue,Z,key_Z,agents,utilities_conflict)	
		conflict_point_value = conflict_point(greaterValue,Z,z_key,agents,utilities_conflict)
		print("conflict_point :",conflict_point_value)
		# allocations # TODO
		'''
		combinaisons_allocations = list(permutations(z_value, len(z_value))) 
		print("combinaisons_allocations :",combinaisons_allocations)
		allocations_pre_traitement = {}
		allocations_post_traitement = {} # bargaining
		'''

		'''
		o1 = (3, 6)
		o2 = (6, 8)
		o3 = (5, 6)

		({o1, o2, o3}, O) = (3, 10)
		({o1, o2}, o3) = (3, 8)
		({o1, o3}, o2) = (6,7)
		({o2, o3}, o1) = (4, 6)
		(O, {o1, o2, o3}) = (10, 2)
		(o3, {o1, o2}) = (6, 2)
		(o2, {o1, o3}) = (7,6)
		(o1, {o2, o3}) = (8,5)
		'''

		# OUTPUT :  # TODO
		'''
		allocations_pre_traitement = (
			(	((3, 6), (6, 8), (5, 6))	,	((None,None))	)	,
			(	((3, 6), (6, 8))	,	((5, 6))	)	,
			(	((3, 6), (5, 6))	,	((6, 8))	)	,
			(	((6, 8), (5, 6))	,	((3, 6))	)	,
			(	((None,None))	,	((3, 6), (6, 8), (5, 6))	)	,
			(	((5, 6))	,	((3, 6), (6, 8))	)	,
			(	((6, 8))	,	((3, 6), (5, 6))	)	,
			(	((3, 6))	,	((6, 8), (5, 6))	)	,
		)
		allocations_post_traitement = (
			(	((3, 6), (6, 8), (5, 6))	,	((None,None))	)	,
			(	((3, 6), (5, 6))	,	((6, 8))	)	,
			(	((None,None))	,	((3, 6), (6, 8), (5, 6))	)	,
			(	((6, 8))	,	((3, 6), (5, 6))	)	,
			(	((3, 6))	,	((6, 8), (5, 6))	)	,
		)
		'''
		'''
		allocations_pre_traitement = (
			(	(1, 2, 3)	,	(None)	)	,
			(	(1, 2)	,	(3,)	)	,
			(	(1, 3)	,	(2,)	)	,
			(	(2, 3)	,	(1,)	)	,
			(	()	,	(1, 2, 3)	)	,
			(	(3,)	,	(1, 2)	)	,
			(	(2,)	,	(1, 3)	)	,
			(	(1,)	,	(2, 3)	)	,
		)
		allocations_post_traitement = (
			(	(1, 2, 3)	,	()	)	,
			(	(1, 3)	,	(2,)	)	,
			(	()	,	(1, 2, 3)	)	,
			(	(2,)	,	(1, 3)	)	,
			(	(1,)	,	(2, 3)	)	,
		)
		'''

		tasks = []
		for i in z_value:
			tasks.append(list(objects.keys())[list(objects.values()).index(i)])
		#print("tasks :",tasks)

		partitions = partition(tasks)
		#print("partitions :",partitions)
		
		allocations_pre_traitement = {}
		allocations_a1 = {}
		allocations_a2 = {}
		for allocation in partitions:
			objects_agent_1 = [ objects[i] for i in allocation[0] ]
			objects_agent_2 = [ objects[i] for i in allocation[1] ]
			tour1 = tour(agents[z_key[0]],objects_agent_1)
			tour2 = tour(agents[z_key[1]],objects_agent_2)
			allocations_pre_traitement[allocation] = (greaterValue - tour1 , greaterValue - tour2)
			#allocations_a1[allocation] = (greaterValue - tour1 , greaterValue - tour2)
			#allocations_a2[allocation] = (greaterValue - tour1 , greaterValue - tour2)

		print("allocations_pre_traitement :",allocations_pre_traitement)

		allocations_post_traitement = non_dominated_po(allocations_pre_traitement)

		allocations = deepcopy(allocations_post_traitement)
		allocations_a1 = deepcopy(allocations_post_traitement)
		allocations_a2 = deepcopy(allocations_post_traitement)

		allocations_a1_bis = deepcopy(allocations_post_traitement)
		allocations_a2_bis = deepcopy(allocations_post_traitement)

		print("allocations_a1 :",allocations_a1)
		print("allocations_a2 :",allocations_a2)

		offer_a1 = max(allocations_a1, key=lambda k: allocations_a1[k][0])
		offer_a2 = max(allocations_a2, key=lambda k: allocations_a2[k][1])

		historic = []
		historic.append(str("round 		offer_a1 		offer_a2 		u1a1,u1a2 	u2a1,u2a2"))
		#print("round 		offer_a1 		offer_a2 		u1a1,u1a2 		u2a1,u2a2")

		cas = 0
		rounds_bis = 0

		while(offer_a1 != offer_a2):

			

			offer_a1 = max(allocations_a1, key=lambda k: allocations_a1[k][0])
			offer_a2 = max(allocations_a2, key=lambda k: allocations_a2[k][1])

			# Tests
			#offer_a1 = ((1,), (3, 2))
			#offer_a2 = ((1,), (3, 2))

			u1a1 = allocations[offer_a1][0]
			u1a2 = allocations[offer_a2][0]
			u2a1 = allocations[offer_a1][1]
			u2a2 = allocations[offer_a2][1]

			'''
			rounds += 1
			historic.append(str(str(rounds)+"		"+str(offer_a1)+"		"+str(offer_a2)+"		"+str((u1a1,u1a2))+"		"+str((u2a1,u2a2))))
			#print(rounds,"		",offer_a1," 	",offer_a2,"	",(u1a1,u1a2),"		",(u2a1,u2a2))
			'''

			if(u1a1 == conflict_point_value[0]):
				z1 = 1
			else:			
				z1 = (u1a1 - u1a2) / (u1a1 - conflict_point_value[0])

			if(u2a2 == conflict_point_value[1]):
				z2 = 1
			else:			
				z2 = (u2a2 - u2a1) / (u2a2 - conflict_point_value[1])
			
			print("z1 :",z1)
			print("z2 :",z2)
			print("offer_a1 :",offer_a1)
			print("offer_a2 :",offer_a2)

			# inférieur/supérieur ou égal pour les z ?????
			# traiter cas particulier si on """concède""" tout ? cad si on supprime tous les éléments du dico => PROBLEME à gérer #TODO

			
			if cas == 1: # Le premier agent a concédé précédemment
				if z1 >= z2:
					cas = 0
					allocations_a1 = deepcopy(allocations_a1_bis)
				else:
					#del allocations_a1[offer_a1]
					allocations_a1_bis = deepcopy(allocations_a1)
					#del allocations_a1_bis[offer_a1]
					del allocations_a1[offer_a1]
			elif cas == 2: # Le second agent a concédé précédemment
				if z1 <= z2:
					cas = 0
					allocations_a2 = deepcopy(allocations_a2_bis)
				else:
					#del allocations_a2[offer_a2]
					allocations_a2_bis = deepcopy(allocations_a2)
					#del allocations_a2_bis[offer_a2]
					del allocations_a2[offer_a2]
			elif cas == 3: # Les deux agents ont concédé précédemment
				if z1 == z2:
					# TODO
					if rounds_bis == 0:
						rounds_bis += 1
						allocations_a1_bis = deepcopy(allocations_a1)
						allocations_a2_bis = deepcopy(allocations_a2)
						agent_fixe = 1
						del allocations_a2[offer_a2]
					else:
						if agent_fixe == 1 and allocations_a2:
							del allocations_a2[offer_a2]
						elif agent_fixe == 1 and not allocations_a2:
							agent_fixe = 2
							allocations_a2 = deepcopy(allocations_a2_bis)
							del allocations_a1[offer_a1]
						elif agent_fixe == 2 and allocations_a1:
							del allocations_a1[offer_a1]
						elif agent_fixe == 2 and not allocations_a1:
							agent_fixe = 1
							allocations_a1 = deepcopy(allocations_a1_bis)
							rounds_bis = 0
							cas = 0
				else:
					cas = 0
					allocations_a1 = deepcopy(allocations_a1_bis)
					allocations_a2 = deepcopy(allocations_a2_bis)
					rounds_bis = 0
			elif cas == 0:
				cas = 0
			else:
				print("########## !!! Erreur !!! ##########")
				print("cas :",cas)
				input()
			

			# concession
			if(cas == 0):
				rounds += 1
				historic.append(str(str(rounds)+"		"+str(offer_a1)+"		"+str(offer_a2)+"		"+str((u1a1,u1a2))+"		"+str((u2a1,u2a2))))
				print(historic[-1])
				if(z1 == z2):
					del allocations_a1[offer_a1]
					del allocations_a2[offer_a2]
					cas = 3
					cas = 0
					if offer_a1 != offer_a2:
						print("L'agent",z_key[0],"et l'agent",z_key[1],"concèdent.")
				elif(z1 < z2):
					del allocations_a1[offer_a1]
					cas = 1
					#cas = 0
					if offer_a1 != offer_a2:
						print("L'agent",z_key[0],"concède.")
				else: # z1 > z2
					del allocations_a2[offer_a2]
					cas = 2
					#cas = 0
					if offer_a1 != offer_a2:
						print("L'agent",z_key[1],"concède.")
				allocations_a1_bis = deepcopy(allocations_a1)
				allocations_a2_bis = deepcopy(allocations_a2)

			print("allocations_a1 :",allocations_a1)
			print("allocations_a2 :",allocations_a2)
			#input()


		'''
		# TO DELETE !!! tests en attendant le prof...
		# Tests
		print("---------- ATTENTION TESTS ATTENTION ----------")
		if z_key == (1,2):
			offer_a1 = ((1,), (3, 2))
			offer_a2 = ((1,), (3, 2))
		# TO DELETE !!! tests en attendant le prof...
		'''


		# Agreement :
		agreements[z_key] = [ offer_a1,offer_a2,allocations[offer_a1][0],allocations[offer_a2][1] ]
		print("agreement :",agreements[z_key])

		# Nash product :
		nash_products[z_key] = ( allocations[offer_a1][0] - conflict_point_value[0] ) * ( allocations[offer_a2][1] - conflict_point_value[1] )
		print("nash_products :",nash_products[z_key])

		# Mettre à jour le point de conflit pour la prochaine négociation
		utilities_conflict[z_key[0]] = allocations[offer_a1][0]
		utilities_conflict[z_key[1]] = allocations[offer_a2][1]

		
		print("Négociation entre les agents",z_key[0],"et",z_key[1],":")
		for h in historic:
			print(h)
		#break

	print("Balanced outcome. End.")
