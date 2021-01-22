import random
import copy
import time
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

class World:

	def __init__(self, n):
		self.n = n
		self.grid = []
		for i in range(n):
			liste = []
			for j in range(n):
				liste.append(None)
			self.grid.append(liste)
		self.agents = {}
		self.objects = {}
		self.d = 0

	# crée les agents 
	# input : list[(x,y)]
	def create_agents(self, agents):
		id_agent = 0
		for a in agents:
			id_agent += 1
			self.agents[id_agent] = a
			self.grid[a[0]][a[1]] = ("a",id_agent)
		return self.agents

	# crée les objets
	# input : list[(x,y)]
	def create_objects(self, objects):
		id_object = 0
		for o in objects:
			id_object += 1
			self.objects[id_object] = o
			self.grid[o[0]][o[1]] = ("o",id_object)
		return self.objects

	def display_grid(self):
		data = np.zeros((self.n, self.n))
		for a_key,a_value in self.agents.items():
			x = self.n - a_value[1]
			y = a_value[0] - 1
			data[x][y] = 1
		for o_key,o_value in self.objects.items():
			x = self.n - o_value[1]
			y = o_value[0] - 1
			data[x][y] = 2
		cmap = colors.ListedColormap(['white','blue','red'])
		plt.figure(figsize=(6,6))
		plt.pcolor(data[::-1],cmap=cmap,edgecolors='k', linewidths=3)
		plt.show()

	'''
	def display_grid(self): # non fonctionnel
		print(self.grid)

		for row in self.grid:
			for e in row:
				if e == None:
					print(".",)
				elif e == "a":
					print("a"+str(e[1]),)
				elif e == "o":
					print("o"+str(e[1]),)
			print()
		
		for i in range(self.n):
			for j in range(self.n):
				if self.grid[i][j] == None:
					print(".")
				elif self.grid[i][j][0] == "a":
					print("a"+str(self.grid[i][j][1]))
				elif self.grid[i][j][0] == "o":
					print("o"+str(self.grid[i][j][1]))
		'''
		
	def get_agents(self):
		return self.agents

	def get_objects(self):
		return self.objects