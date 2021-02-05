import random
import copy
import time
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
from sys import maxsize
from itertools import permutations, product
from itertools import combinations
from operator import itemgetter

def manhattanDistance(p1,p2):
    """
    Renvoie la distance de Manhattan entre les points p1 et p2
    """
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

def tour(depart, objects):
    """
    list , list[lists] -> int
    Tournée
    Renvoye le coût de la plus courte tournée qui passe par tous les objects donnés en paramètre.
    """
    # Calcul de tous les possibles permutations (de taille len(objects)) de 'objects'
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
    """
    Calcule le coût des tournées complètes pour tous les agents et prend le maximum parmi eux.
    """
    max_path = 0
    for z_key,z_value in Z.items():
        for agent in z_key:
            value_path = tour(agents[agent],z_value)
            if value_path > max_path:
                max_path = value_path
    return max_path


def perception(agents,objects,d):
    """
    list, list, int -> {a:[(x,y)]}
    Étant donné un rayon de perception d, et en utilisant la distance de
    Manhattan, calcule la liste des objets perçus par chacun des agents.
    """
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


def set_Z(agents_visible_objects):
    """
    {a:[(x,y)]} -> dict (agent1,agent2) : [(x,y)]
    Renvoie un dictionnaire représentant les objects communs entre chaque couple d'agents.
    """
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


# C'est directement implémenté dans negotiation() pour l'instant... à voir plus tard si on met ça au propre

# Merci Pampam !

def zeuthens(u1a1, u1a2, u2a1, u2a2, conflict_point_value):
    """
    Calcule les valeurs de Zeuthen z1 et z2 selon la formule du cours,
    à l'aide des utilités des offres proposés et le point de conflit.
    """
    # Z1
    if(u1a1 == conflict_point_value[0]):
        z1 = 1
    else:			
        z1 = (u1a1 - u1a2) / (u1a1 - conflict_point_value[0])

    # Z2
    if(u2a2 == conflict_point_value[1]):
        z2 = 1
    else:			
        z2 = (u2a2 - u2a1) / (u2a2 - conflict_point_value[1])
    
    return z1, z2

def agreement(offer, allocations):
    """
    Renvoie l'allocation accordée (normalement offer_a1 = offer_a2) et leur utilité.
    """
    return [ offer, allocations[offer][0], allocations[offer][1] ]

def nash_product(offer, allocations, conflict_point):
    """
    Renvoie le produit de Nash d'après l'utlité de l'allocation accordé et le point de conflit.
    """
    return (allocations[offer][0] - conflict_point[0] )* ( allocations[offer][1] - conflict_point[1])


# Processus de négociation
# greater value than the cost of the largest possible tour (greaterValue)
#def negotiation(agents,objects,d,greaterValue, ids = ('1', '2', '3')):
#def negotiation(agents,objects,d,greaterValue):
def negotiation(world,d,greaterValue):

    agents = world.get_agents()
    objects = world.get_objects()

    """
    Négotiation bilatéral selon le MCP et la strátegie de Zeuthen
    """
    print("Caractéristiques du problème :\n")
    print("Agents :",agents)
    print("Objets :",objects)
    print("Distance de perception des agents :",d)
    
    # objets visibles avec la distance d
    agents_visible_objects = perception(agents,objects,d)
    print("Objets visibles par les agents :",agents_visible_objects)

    # ensemble Z (objets en commun)
    Z = set_Z(agents_visible_objects)
    print("Ensembles Z :",Z)

    # la plus grande tournée
    biggestTour_value = biggestTour(Z,agents)
    print("Coût de la plus grande tournée :",biggestTour_value)
    print("Valeur supplémantaire ajoutée à :",greaterValue)

    # valeur plus grande que le coût de la plus grande tournée possible
    greaterValue += biggestTour_value
    print("Valeur plus grande que le coût de la plus grande tournée possible :",greaterValue)

    # point de conflit
    #key_Z = (1,2) # pour tester...
    #conflict_point_value = conflict_point(greaterValue,Z,key_Z,agents,current_agent_1_utility_conflict=None,current_agent_2_utility_conflict=None)	
    #print("conflict_point :",conflict_point_value)

    agreements = {}
    nash_products = {}
    utilities_conflict = {}

    print("")

    # Négociation par Monotonic Concession Protocol
    for z_key,z_value in Z.items():

        print("-----------------------------------------------------------------------")
        print("Négociation par Monotonic Concession Protocol entre les agents",z_key[0],"et",z_key[1],":")
        print("-----------------------------------------------------------------------")

        # Initialisation :
        rounds = 0
        #conflict_point_value = conflict_point(greaterValue,Z,key_Z,agents,utilities_conflict)	
        conflict_point_value = conflict_point(greaterValue,Z,z_key,agents,utilities_conflict)
        print("Point de conflit :",conflict_point_value)
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

        #print("allocations_pre_traitement :",allocations_pre_traitement)

        allocations_post_traitement = non_dominated_po(allocations_pre_traitement)

        allocations = deepcopy(allocations_post_traitement)
        allocations_a1 = deepcopy(allocations_post_traitement)
        allocations_a2 = deepcopy(allocations_post_traitement)

        allocations_a1_bis = deepcopy(allocations_post_traitement)
        allocations_a2_bis = deepcopy(allocations_post_traitement)

        print("Allocation avec bargaining :")
        if(allocations_a1 == allocations_a2):
            print(allocations_a1)
        else:
            print("problem somewhere...")

        offer_a1 = max(allocations_a1, key=lambda k: allocations_a1[k][0])
        offer_a2 = max(allocations_a2, key=lambda k: allocations_a2[k][1])

        # ids
        id_1, id_2 = z_key[0], z_key[1]

        historic = []
        #historic.append("round 		offer_a1 		offer_a2 		u1a1,u1a2 	u2a1,u2a2")
        historic.append("round 		offer_a" + str(id_1) + " 		offer_a" + str(id_2) + " 		u" + str(id_1) + "a" + str(id_1) + ",u" + str(id_1) + "a" + str(id_2) + " 	u" + str(id_2) + "a" +  str(id_1) + ",u" + str(id_2) + "a" +  str(id_2) + "   z" + str(id_1) + "  z" + str(id_2))
        #print("round 		offer_a1 		offer_a2 		u1a1,u1a2 		u2a1,u2a2")

        cas = 0
        rounds_bis = 0
        negotiation_failed = False

        # Chaque agent propose comme offre celle qui lui convient le plus
        offer_a1 = max(allocations_a1, key=lambda k: allocations_a1[k][0])
        offer_a2 = max(allocations_a2, key=lambda k: allocations_a2[k][1])

        # Tests
        #offer_a1 = ((1,), (3, 2))
        #offer_a2 = ((1,), (3, 2))

        # Calcul des utilités selon les offres
        u1a1 = allocations[offer_a1][0]
        u1a2 = allocations[offer_a2][0]
        u2a1 = allocations[offer_a1][1]
        u2a2 = allocations[offer_a2][1]

        # Tant que les agents ne sont pas arrivés à un accord ou que la négotiation n'a pas echoué
        # TODO: on prend une allocation meme si elle nous donne comme utilité la meme chose que le point de conflit? ou il faut que ça soit strictement superieur?

        #while(offer_a1 != offer_a2) and not negotiation_failed:
        while (rounds == 0) or (u1a2 < u1a1 and u2a1 < u2a2 and not negotiation_failed):
        # u1a2 >= u1a1 or u2a1 >= u2a2 alors agreement

            print("Round",rounds+1,":")

            if rounds > 0: # pour éviter de recalculer au premier round, optimisation mdr...
                # Chaque agent propose comme offre celle qui lui convient le plus
                offer_a1 = max(allocations_a1, key=lambda k: allocations_a1[k][0])
                offer_a2 = max(allocations_a2, key=lambda k: allocations_a2[k][1])

                # Tests
                #offer_a1 = ((1,), (3, 2))
                #offer_a2 = ((1,), (3, 2))

                # Calcul des utilités selon les offres
                u1a1 = allocations[offer_a1][0]
                u1a2 = allocations[offer_a2][0]
                u2a1 = allocations[offer_a1][1]
                u2a2 = allocations[offer_a2][1]

            '''
            rounds += 1
            historic.append(str(str(rounds)+"		"+str(offer_a1)+"		"+str(offer_a2)+"		"+str((u1a1,u1a2))+"		"+str((u2a1,u2a2))))
            #print(rounds,"		",offer_a1," 	",offer_a2,"	",(u1a1,u1a2),"		",(u2a1,u2a2))
            '''

            # Calcul des valeurs de Zeuthen
            z1, z2 = zeuthens(u1a1, u1a2, u2a1, u2a2, conflict_point_value)
            
            '''
            print("offer_a1 :",offer_a1)
            print("offer_a2 :",offer_a2)
            print("z1 :",z1)
            print("z2 :",z2)
            '''

            # l'agent avec le z le plus petit concède, si z1 == z2 alors les deux concedent,
            # puis soit i l'agent qui concède et j l'autre, l'agent i fait de sorte à faire un offre 
            # tel qu'au prochain tour zj <= zi

            # inférieur/supérieur ou égal pour les z ?????
            # traiter cas particulier si on """concède""" tout ? cad si on supprime tous les éléments du dico => PROBLEME à gérer #TODO
            # Je crois que si on concède tout, alors la négotiation échoue et donc on obtient ce qu'on aurait au point de conflit(?)
            # Ah peut-être... ! Faudrait demander à Maudet !

            if cas == 1: # Le premier agent a concédé précédemment
                if z1 >= z2:
                    cas = 0
                    allocations_a1 = deepcopy(allocations_a1_bis)
                else:  # z1 < z2
                    #del allocations_a1[offer_a1]
                    #allocations_a1_bis = deepcopy(allocations_a1)
                    #del allocations_a1_bis[offer_a1]
                    del allocations_a1[offer_a1]
                    print("Agent",z_key[0],": Mauvaise concession ! Je ne concède pas",offer_a1,"!")
                    #print("offer_a",z_key[0],":",offer_a1)
                    #print("offer_a",z_key[1],":",offer_a2)
                    #print("allocations_a",z_key[0],":",allocations_a1)
                    #print("allocations_a",z_key[1],":",allocations_a2)
            elif cas == 2: # Le second agent a concédé précédemment
                if z1 <= z2:
                    cas = 0
                    allocations_a2 = deepcopy(allocations_a2_bis)
                else:
                    #del allocations_a2[offer_a2]
                    #allocations_a2_bis = deepcopy(allocations_a2)
                    #del allocations_a2_bis[offer_a2]
                    del allocations_a2[offer_a2]
                    print("Agent",z_key[1],": Mauvaise concession ! Je ne concède pas",offer_a2,"!")
                    #print("offer_a",z_key[0],":",offer_a1)
                    #print("offer_a",z_key[1],":",offer_a2)
                    #print("allocations_a",z_key[0],":",allocations_a1)
                    #print("allocations_a",z_key[1],":",allocations_a2)

            # TO DELETE RIEN A FAIRE EN VRAI POUR CE CAS 3
            # SAUF SI CONTESTATION
            elif cas == 3: # Les deux agents ont concédé précédemment
                '''
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
                '''
                pass
            elif cas == 0:
                cas = 0 # LOL c'est un bouche-trou
            else:
                print("########## !!! Erreur !!! ##########")
                print("cas :",cas)
                input()
            

            # concession
            if(cas == 0):
                rounds += 1
                historic.append(str(str(rounds)+"		"+str(offer_a1)+"		"+str(offer_a2)+"		"+str((u1a1,u1a2))+"		"+str((u2a1,u2a2))+"  "+str(z1)+"  "+str(z2)))
                #print(historic[-1])
                if(z1 == z2):
                    del allocations_a1[offer_a1]
                    del allocations_a2[offer_a2]
                    #cas = 3
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
                '''
                print("allocations_a"+str(z_key[0])+" :",allocations_a1_bis)
                print("allocations_a"+str(z_key[1])+" :",allocations_a2_bis)
                '''

            '''
            print("allocations_a",z_key[0],":",allocations_a1)
            print("allocations_a",z_key[1],":",allocations_a2)
            '''
            #input()

            # négociation échouée
            if allocations_a1 == {} or allocations_a2 == {}:
                print("La négociation a échouée...")
                negotiation_failed = True
                     


        '''
        # TO DELETE !!! tests en attendant le prof...
        # Tests
        print("---------- ATTENTION TESTS ATTENTION ----------")
        if z_key == (1,2):
            offer_a1 = ((1,), (3, 2))
            offer_a2 = ((1,), (3, 2))
        # TO DELETE !!! tests en attendant le prof...
        '''

        if not negotiation_failed:
            #if offer_a1 == offer_a2:
            if u1a2 >= u1a1 or u2a1 >= u2a2:
                # Agreement :
                agreements[z_key] = agreement(offer_a1, allocations)
                print("agreement :", agreements[z_key])

                # Nash product :
                nash_products[z_key] = nash_product(offer_a1, allocations, conflict_point_value)
                print("nash_products :",nash_products[z_key])
            else:
                print("Error somewhere...")

        # Mettre à jour le point de conflit pour la prochaine négociation
        utilities_conflict[z_key[0]] = allocations[offer_a1][0]
        utilities_conflict[z_key[1]] = allocations[offer_a2][1]

        print("-------------------------------------------------------------------------------------------------------")
        print("Négociation entre les agents",z_key[0],"et",z_key[1],":")
        for h in historic:
            print(h)
        print("-------------------------------------------------------------------------------------------------------\n\n")

        #break

    print("Balanced outcome. End.")
