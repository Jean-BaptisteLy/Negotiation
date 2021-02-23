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

'''
TODO :
non_dominated_po
concession

utiliser pandas pour afficher l'historique...?

implémenter un autre format qu'une grille ?
comme ça on peut tester les exemples du cours mais aussi de l'article
qui n'a pas de grille

théoriquement, le multilateral généralise tout,
donc il serait possible de l'utiliser aussi pour le cas de deux agents seulement ?

'''

def manhattanDistance(p1,p2):
    """
    Renvoie la distance de Manhattan entre les points p1 et p2
    """
    (x1,y1) = p1
    (x2,y2) = p2
    return abs(x1 - x2) + abs(y1 - y2)


def partition(tasks):
    """
    Calcule toutes les partitions possibles étant donné un ensemble de tâches.
    """
    l1 = []
    l2 = []
    for pattern in product([True,False],repeat=len(tasks)):
        l1.append(tuple([x[1] for x in zip(pattern,tasks) if x[0]]))
        l2.append(tuple([x[1] for x in zip(pattern,tasks) if not x[0]]))

    return list(zip(l1,l2))

def partition_k(tasks, k):
    """
    Cacule toutes les partitions possibles étant donné un ensemble de tâches et k agents.
    """
    agent_lists = [[] for i in range(k)]
    for pattern in product([i for i in range(k)],repeat=len(tasks)):
        for j in range(k):
            agent_lists[j].append(tuple([x[1] for x in zip(pattern,tasks) if x[0] == j]))
    return list(zip(*agent_lists))

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
    min_path = maxsize
    for t in tours:
        valeur_tournee = 0
        new_depart = depart
        for i in range(len(t)):
            valeur_tournee += manhattanDistance(new_depart,t[i])
            new_depart = t[i]
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
    Renvoie un dictionnaire représentant les objects communs entre chaque groupe d'agents.
    """
    # objets en commun
    Z = {}
    # toutes les combinaisons possibles, formation des groupes d'agents
    i = len(agents_visible_objects)
    groupes = []
    while(i > 1):
        groupe = list(map(dict,combinations(agents_visible_objects.items(), i)))             
        groupes += groupe
        i -= 1
    for groupe in groupes:
        fusion_liste = []
        partners = []
        for groupe_key,groupe_value in groupe.items():
            fusion_liste.append(groupe_value)
            partners.append(groupe_key)
        # éléments en communs dans un groupe d'agents
        common_elements_before = set(fusion_liste[0])
        for s in fusion_liste[1:]:
            common_elements_before.intersection_update(s)
        common_elements_after = deepcopy(common_elements_before)
        for key,value in Z.items():
            if set(tuple(partners)).issubset(key):
                for c in common_elements_before:
                    if c in value:
                        common_elements_after.remove(c)
        if common_elements_after: # si éléments en commun, groupe confirmé (si liste non vide en fait...)
            Z[tuple(partners)] = common_elements_after     
    return Z

# tournée entière
def conflict_point(greaterValue,Z,key_Z,agents,utilities_conflict):
    conflict_point = []
    for key in key_Z:
        if key in utilities_conflict:
            conflict_point.append(utilities_conflict[key])
        else:
            conflict_point.append(greaterValue - tour(agents[key],Z[key_Z]))
    return conflict_point

#------------------------------------------------------------------------------------------
# 3 généralisations de la stratégie de Zeuthen :
def zeuthen_Willingness_to_Risk_Conflict(utilities, conflict_point_value):
    z = []
    for u in range(len(utilities)):
        if utilities[u][u] == 0:
            z.append(1)
        else:
            print("utilities[",u,"][",u,"] =",utilities[u][u])
            # je ne sais pas, c'est pour éviter d'avoir un zéro dans le dénominateur...
            if ( utilities[u][u] - conflict_point_value[u] == 0 ):
                temp = 1
            else:
                temp = ( utilities[u][u] - min(utilities[u]) ) / ( utilities[u][u] - conflict_point_value[u] )
            #temp = ( utilities[u][u] - min(utilities[u]) ) / ( utilities[u][u] - conflict_point_value[u] )
            z.append(temp)  
    return z
def zeuthen_A_Product_increasing_Strategy(utilities, conflict_point_value):
    z = []
    for u in range(len(utilities)):
        temp = 1
        for k in range(len(utilities)):
            temp = temp * utilities[k][u]
        z.append(temp)
    return z
def zeuthen_Sum_of_Products_of_Pairs(utilities, conflict_point_value):
    z = []
    for u in range(len(utilities)):
        temp = 1
        for j in range(len(utilities)):
            for k in range(len(utilities)):
                if j != k:
                    temp += utilities[j][u] * utilities[k][u]
        z.append(temp)
    return z
#------------------------------------------------------------------------------------------

def agreement(offer, allocations):
    """
    Renvoie l'allocation accordée et leur utilité.
    """
    return [offer] + [allocations[offer][i] for i in range(len(allocations[offer]))]

def nash_product(offer, allocations, conflict_point):
    """
    Renvoie le produit de Nash d'après l'utlité de l'allocation accordé et le point de conflit.
    """
    nash_product = 1
    for i in range(len(allocations[offer])):
        nash_product = nash_product * ( allocations[offer][i] - conflict_point[i] )
    return nash_product


# Processus de négociation
def negotiation(world,d,greaterValue,zeuthenStrategy="zeuthen_Sum_of_Products_of_Pairs"):

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

    # TO DELETE
    # Tests :
    #Z = {(1, 2, 3): [(6, 4), (8, 3), (6, 8), (5, 6), (3, 6), (9, 5)]}
    #Z = {(1, 2, 3): [(8,5),(8,7),(10,6)]}
    # TO DELETE

    print("Ensembles Z :",Z)

    # la plus grande tournée
    biggestTour_value = biggestTour(Z,agents)
    print("Coût de la plus grande tournée :",biggestTour_value)
    print("Valeur supplémantaire ajoutée à :",greaterValue)

    # valeur plus grande que le coût de la plus grande tournée possible
    greaterValue += biggestTour_value
    print("Valeur plus grande que le coût de la plus grande tournée possible :",greaterValue)

    agreements = {}
    nash_products = {}
    utilities_conflict = {}

    print("")

    # Négociation par Monotonic Concession Protocol
    for z_key,z_value in Z.items():

        print("-----------------------------------------------------------------------")
        print("Négociation par Monotonic Concession Protocol entre les agents",z_key,":")
        print("-----------------------------------------------------------------------")

        # Initialisation :
        rounds = 0
        conflict_point_value = conflict_point(greaterValue,Z,z_key,agents,utilities_conflict)
        print("Point de conflit :",conflict_point_value)

        tasks = []
        for i in z_value:
            tasks.append(list(objects.keys())[list(objects.values()).index(i)])
        print("tasks :",tasks)

        partitions = partition(tasks)

        '''
        # TO DELETE
        # Tests
        partitions = [((1, 2, 3), (), ()), ((1, 2), (3,), ()), ((1, 3), (2,), ()), ((1,), (2, 3),()), ((2, 3), (1,), ()), ((2,), (1, 3), ()), ((3,), (1, 2), ()), ((), (1, 2, 3), ())]
        partitions += [((1, 2), (), (3,)), ((1, 3), (), (2,)), ((1,), (), (2, 3)), ((2, 3), (), (1,)), ((2,), (), (1, 3)), ((3,), (), (1, 2))]
        partitions += [((), (1, 2), (3,)), ((), (1, 3), (2,)), ((), (1,), (2, 3)), ((), (2, 3), (1,)), ((), (2,), (1, 3)), ((), (3,), (1, 2))]
        partitions += [((1,), (2,), (3,))]
        partitions += [((), (), (1, 2, 3))]
        # TO DELETE
        '''

        print("partitions :",partitions)
        
        allocations_pre_traitement = {}
        allocations_a1 = {}
        allocations_a2 = {}
        #tours = []
        for allocation in partitions:
            tours = []
            #print("allocation :",allocation)
            '''
            objects_agent_1 = [ objects[i] for i in allocation[0] ]
            objects_agent_2 = [ objects[i] for i in allocation[1] ]
            tour1 = tour(agents[z_key[0]],objects_agent_1)
            tour2 = tour(agents[z_key[1]],objects_agent_2)
            '''
            for a in range(len(allocation)):
                tours.append( tour( agents[z_key[a]] , [ objects[i] for i in allocation[a] ] ) )
                    
            #allocations_pre_traitement[allocation] = (greaterValue - tour1 , greaterValue - tour2)
            allocations_pre_traitement[allocation] = []
            for t in tours:
                allocations_pre_traitement[allocation].append(greaterValue - t)

        print("allocations_pre_traitement :",allocations_pre_traitement)
        
        allocations_post_traitement = non_dominated_po(allocations_pre_traitement)

        # TO DELETE
        # tests...
        allocations_post_traitement = allocations_pre_traitement
        # TO DELETE

        allocations = deepcopy(allocations_post_traitement)
        allocations_a = []
        allocations_a_bis = []
        for i in range(len(z_key)):
            allocations_a.append(deepcopy(allocations_post_traitement))
            allocations_a_bis.append(deepcopy(allocations_post_traitement))

        print("allocations_a :",allocations_a)

        ''' TO DELETE
        allocations_a1 = deepcopy(allocations_post_traitement)
        allocations_a2 = deepcopy(allocations_post_traitement)

        allocations_a1_bis = deepcopy(allocations_post_traitement)
        allocations_a2_bis = deepcopy(allocations_post_traitement)
        '''

        print("Allocation avec bargaining :")
        print(allocations_a[0])

        ''' TO DELETE ???
        if(allocations_a1 == allocations_a2):
            print(allocations_a1)
        else:
            print("problem somewhere...")
        '''

        # Chaque agent propose l'offre celle qui lui convient le plus
        offers = []
        for i in range(len(z_key)):
            offers.append(max(allocations_a[i], key=lambda k: allocations_a[i][k][i]))
        #print("offers :",offers)

        ''' TO DELETE
        offer_a1 = max(allocations_a1, key=lambda k: allocations_a1[k][0])
        offer_a2 = max(allocations_a2, key=lambda k: allocations_a2[k][1])
        '''

        # TO DELETE
        #id_1, id_2 = z_key[0], z_key[1]

        #historic = []
        #historic.append("round 		offer_a" + str(id_1) + " 		offer_a" + str(id_2) + " 		u" + str(id_1) + "a" + str(id_1) + ",u" + str(id_1) + "a" + str(id_2) + " 	u" + str(id_2) + "a" +  str(id_1) + ",u" + str(id_2) + "a" +  str(id_2) + "   z" + str(id_1) + "  z" + str(id_2))

        cas = -1
        rounds_bis = 0
        negotiation_failed = False

        # Calculs des utilités selon les offres
        utilities = []
        for i in range(len(z_key)):
            temp = []
            for j in range(len(z_key)):
                temp.append(allocations[offers[j]][i])
            utilities.append(temp)
        #print("utilities :",utilities)

        ''' TO DELETE
        # Calcul des utilités selon les offres
        u1a1 = allocations[offer_a1][0]
        u1a2 = allocations[offer_a2][0]
        u2a1 = allocations[offer_a1][1]
        u2a2 = allocations[offer_a2][1]
        '''

        agreement_bool = False
        # Tant que les agents ne sont pas arrivés à un accord ou que la négotiation n'a pas echoué
        # Tant que pas d'agreement
        while (rounds == 0) or (not agreement_bool and not negotiation_failed):
        # u1a2 >= u1a1 or u2a1 >= u2a2 alors agreement

            print("Round",rounds+1,":")

            if rounds > 0: # pour éviter de recalculer au premier round, optimisation mdr...
                # Chaque agent propose l'offre celle qui lui convient le plus
                offers = []
                for i in range(len(z_key)):
                    offers.append(max(allocations_a[i], key=lambda k: allocations_a[i][k][i]))
                #print("offers :",offers)

                # Calculs des utilités selon les offres
                utilities = []
                for i in range(len(z_key)):
                    temp = []
                    for j in range(len(z_key)):
                        temp.append(allocations[offers[j]][i])
                    utilities.append(temp)
                #print("utilities :",utilities)

            print("offers :",offers)
            print("utilities :",utilities)

            # Calculs des valeurs de Zeuthen
            #z1, z2 = zeuthens(u1a1, u1a2, u2a1, u2a2, conflict_point_value)
            if (zeuthenStrategy == "zeuthen_Willingness_to_Risk_Conflict"): # the worst
                zeuthen = zeuthen_Willingness_to_Risk_Conflict(utilities, conflict_point_value)
            elif (zeuthenStrategy == "zeuthen_A_Product_increasing_Strategy"): # so so la la
                zeuthen = zeuthen_A_Product_increasing_Strategy(utilities, conflict_point_value)
            elif (zeuthenStrategy == "zeuthen_Sum_of_Products_of_Pairs"): # the best
                zeuthen = zeuthen_Sum_of_Products_of_Pairs(utilities, conflict_point_value)
            print("zeuthen :",zeuthen)

            # l'agent avec le z le plus petit concède, si z1 == z2 alors les deux concedent,
            # puis soit i l'agent qui concède et j l'autre, l'agent i fait de sorte à faire un offre 
            # tel qu'au prochain tour zj <= zi

            # inférieur/supérieur ou égal pour les z ?????
            # traiter cas particulier si on """concède""" tout ? cad si on supprime tous les éléments du dico => PROBLEME à gérer #TODO
            # Je crois que si on concède tout, alors la négotiation échoue et donc on obtient ce qu'on aurait au point de conflit(?)
            # Ah peut-être... ! Faudrait demander à Maudet !

            '''
            if cas == 1: # Le premier agent a concédé précédemment
                if z1 >= z2:
                    cas = 0
                    allocations_a1 = deepcopy(allocations_a1_bis)
                else:  # z1 < z2
                    del allocations_a1[offer_a1]
                    print("Agent",z_key[0],": Mauvaise concession ! Je ne concède pas",offer_a1,"!")
            elif cas == 2: # Le second agent a concédé précédemment
                if z1 <= z2:
                    cas = 0
                    allocations_a2 = deepcopy(allocations_a2_bis)
                else:
                    del allocations_a2[offer_a2]
                    print("Agent",z_key[1],": Mauvaise concession ! Je ne concède pas",offer_a2,"!")

            elif cas == 3: # Les deux agents ont concédé précédemment
                pass
            elif cas == 0:
                cas = 0 # LOL c'est un bouche-trou
            else:
                print("########## !!! Erreur !!! ##########")
                print("cas :",cas)
                input()
            '''

            # concession
            if(cas == -1):
                rounds += 1
                #historic.append(str(str(rounds)+"		"+str(offer_a1)+"		"+str(offer_a2)+"		"+str((u1a1,u1a2))+"		"+str((u2a1,u2a2))+"  "+str(z1)+"  "+str(z2)))
                #print(historic[-1])

                # on prend les agents qui ont la valeur minimale de zeuthen
                agents_concede = [i for i, x in enumerate(zeuthen) if x == min(zeuthen)]
                print("agents_concede :",agents_concede)

                # ces agents concèdent leur offre
                for ac in agents_concede:
                    del allocations_a[ac][offers[ac]]
                print("allocations_a :",allocations_a)

                # on met à les allocations (car certains ont concédé avant)
                for i in range(len(allocations_a_bis)):
                    allocations_a_bis[i] = deepcopy(allocations_a[i])

            # négociation échouée
            for a in allocations_a:
                if a == {}:
                    print("La négociation a échouée...")
                    negotiation_failed = True
                    break

            # vérification de l'agreement
            if not negotiation_failed:
                best_agents_offers = []     
                for i in range(len(z_key)):
                    for j in range(len(z_key)):
                        if utilities[j][i] < utilities[j][j]:
                            break
                        else:
                            if j == len(z_key)-1: # on a atteint le dernier agent, donc tous les agents sont contents mdr
                                agreement_bool = True
                                #best_offer = i
                                best_agents_offers.append(i)
                    #if agreement_bool:
                        #break

            #input() # pour regarder chaque round petit à petit

        if not negotiation_failed and agreement_bool:

            #print("best_offer :",best_offer)
            #offer_agreement = offers[best_offer] # par défaut

            # mais on peut faire un flip si plusieurs agents sont agree
            print("on fait un flip dice sur ces agents qui possèdent les meilleures offres :")
            print("best_agents_ offers :",best_agents_offers)
            offer_agreement = offers[random.choice(best_agents_offers)]

            '''
            if u1a2 >= u1a1 or u2a1 >= u2a2:
                if u1a2 >= u1a1 and u2a1 >= u2a2:
                    print("u1a2 >= u1a1 and u2a1 >= u2a2")
                    print("use random because many agents agree")
                    offer_agreement = random.choice([offer_a1,offer_a2])
                elif u1a2 >= u1a1:
                    print("u1a2 >= u1a1")
                    offer_agreement = offer_a2
                elif u2a1 >= u2a2:
                    print("u2a1 >= u2a2")
                    offer_agreement = offer_a1
                else:
                    print("impossible... erreur")
            '''

            # Agreement :
            agreements[z_key] = agreement(offer_agreement, allocations)
            print("agreement :", agreements[z_key])

            # Nash product :
            nash_products[z_key] = nash_product(offer_agreement, allocations, conflict_point_value)
            print("nash_products :",nash_products[z_key])

        # Mettre à jour le point de conflit pour la prochaine négociation
        for i in range(len(z_key)):
            utilities_conflict[z_key[i]] = allocations[offers[i]][z_key[i]-1]
        '''
        utilities_conflict[z_key[0]] = allocations[offer_a1][0]
        utilities_conflict[z_key[1]] = allocations[offer_a2][1]
        '''

        print("-------------------------------------------------------------------------------------------------------")
        print("Négociation entre les agents",z_key,":")
        '''
        for h in historic:
            print(h)
        '''
        print("-------------------------------------------------------------------------------------------------------\n\n")

    print("Balanced outcome. End.")
