#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue April 16, 2019

Implementation of a ABM for Design Criteria Impact of AUVs and ASVs
CMPLXSYS 530 Final Project Winter 2019

@author: jcoller

To-Do:
- Implement ASV and Submarine classes
- Implement endurance
- Update visualizations to reflect the number of enemies remaining over time
- Consider updating environmental constraints such as land masses etc.
- Consider adding structure to the movement patterns - such as the ships going out to a set area and then releasing AUVs to begin searching
- Consider how to set various agents to have limited powers, i.e. AUVs cannot attack - just find enemy ships or submarines
- Setup MC in parallel
"""

# Imports
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import random as rand
import scipy
import numpy as np
import math

from multiprocessing import Pool

import sys

width = 100
height = 100

class AUV(object):
	"""
	AUV Class, which encapsulates the behaviors of the AUVs present in the model.
	"""

	def __init__(self,auv_id,start_x,start_y,velocity,endurance,strength,team,radius):
		# AUV Constructor

		self.id = auv_id
		self.vehicle = "AUV"
		self.x = start_x
		self.y = start_y
		self.speed = velocity # max speed
		self.endurance = endurance
		self.strength = strength # Do I want this? TBD...
		self.height = -1 # we are below the water
		self.team = team
		self.radius = radius # how far around itself the agent can "see"
		self.flag = 0 # is there an enemy within range

	def move_randomly(self):
		theta = math.radians(rand.uniform(1,360))
		vel = rand.uniform(0, self.speed)
		self.x = self.x + vel*math.sin(theta)
		self.y = self.y + vel*math.cos(theta)
		self.check_boundaries()

	def check_boundaries(self):
		if self.x < 0:
			self.x = 0
		if self.y < 0:
			self.y = 0
		if self.x > (width - 1):
			self.x = (width - 1)
		if self.y > (height - 1):
			self.y = (height - 1)

	def move_to_point(self,x,y):
		# Function to move agent to a given point, instead of randomly

		# Calculate Distance
		delta_x = x - self.x
		delta_y = y - self.y
		distance = math.sqrt(delta_x**2 + delta_y**2)

		# Check if we can get there in one turn, if so move to there minus 1 unit
		if distance < self.speed:
			self.x = x-rand.uniform(-2,2)
			self.y = y-rand.uniform(-2,2)
			self.check_boundaries()
			return

		# Calculate angle to point
		theta = math.atan2(delta_y,delta_x)

		# Move as close as we can to the point
		vel = self.speed
		self.x = self.x + vel*math.cos(theta)
		self.y = self.y + vel*math.sin(theta)
		self.check_boundaries()

	def attack(self,list_of_enemies):
		# Quick funtion for the next part
		def pullDistance(the_object):
			return self.get_distance(the_object)

		# Find which vehcile is cloest of the list
		if len(list_of_enemies) > 1:
			the_enemy = min(list_of_enemies, key=pullDistance)
		else: the_enemy = list_of_enemies[0]

		#print "AUV ", self.id, " is attacking ", the_enemy.id
		#print "The enemy's strength is ", the_enemy.strength

		# Reduce the Strength of the enemy by 1
		the_enemy.strength -= 1

		# Check the enemy's remaining strength, if 0, kill them
		if the_enemy.strength < 1: # the enemy is dead!
			#print "AUV ", the_enemy.id, "has been lost in battle."
			global team1_killed
			global team2_killed
			if self.team == 1:
				sim.team2_killed += 1
			else: sim.team1_killed += 1
			if the_enemy.vehicle == "AUV":
				# Find the object and remove it
				for i in xrange(len(sim.auvs)):
					if sim.auvs[i].id == the_enemy.id: dead_enemy = i
				del sim.auvs[dead_enemy]

			if the_enemy.vehicle == "ASV":
				# Find the object and remove it
				for i in xrange(len(sim.asvs)):
					if sim.asvs[i].id == the_enemy.id: dead_enemy = i
				del sim.asvs[dead_enemy]

			if the_enemy.vehicle == "Submarine":
				# Find the object and remove it
				for i in xrange(len(sim.subs)):
					if sim.subs[i].id == the_enemy.id: dead_enemy = i
				del sim.subs[dead_enemy]

			if the_enemy.vehicle == "Ship":
				# Find the object and remove it
				for i in xrange(len(sim.ships)):
					if sim.ships[i].id == the_enemy.id: dead_enemy = i
				del sim.ships[dead_enemy]

	def check_for_enemies(self):
		list_enemies = []
		num_enemies = 0

		# run through the list of all AUVs
		for i in xrange(len(sim.auvs)):
			if (self.get_distance(sim.auvs[i]) < self.radius and sim.auvs[i].team != self.team):
				list_enemies.append(sim.auvs[i])
				num_enemies += 1

		# run through the list of all ships
		for i in xrange(len(sim.ships)):
			if (self.get_distance(sim.ships[i]) < self.radius and sim.ships[i].team != self.team):
				list_enemies.append(sim.ships[i])
				num_enemies += 1

		# run through the list of submarines
		for i in xrange(len(sim.subs)):
			if (self.get_distance(sim.subs[i]) < self.radius and sim.subs[i].team != self.team):
				list_enemies.append(sim.subs[i])
				num_enemies += 1

		# run through the list of ASVs
		for i in xrange(len(sim.asvs)):
			if (self.get_distance(sim.asvs[i]) < self.radius and sim.asvs[i].team != self.team):
				list_enemies.append(sim.asvs[i])
				num_enemies += 1

		# Check if we found any enemies
		if num_enemies > 0:
			self.flag = 1 # Enemy in sight!
		else: self.flag = 0

		return [num_enemies, list_enemies]

	def ask_nearby_friends(self):
		# Quick funtion for the next part
		def pullDistance(the_object):
			return self.get_distance(the_object)
		nearby_friends = []
		number_friends = 0

		for i in xrange(len(sim.auvs)):
			if sim.auvs[i].flag and sim.auvs[i].team == self.team and self.get_distance(sim.auvs[i]) < 0.25*width:
				nearby_friends.append(sim.auvs[i])
				number_friends += 1

		for i in xrange(len(sim.asvs)):
			if sim.asvs[i].flag and sim.asvs[i].team == self.team and self.get_distance(sim.asvs[i]) < 0.25*width:
				nearby_friends.append(sim.asvs[i])
				number_friends += 1

		for i in xrange(len(sim.subs)):
			if sim.subs[i].flag and sim.subs[i].team == self.team and self.get_distance(sim.subs[i]) < 0.25*width:
				nearby_friends.append(sim.subs[i])
				number_friends += 1

		for i in xrange(len(sim.ships)):
			if sim.ships[i].flag and sim.ships[i].team == self.team and self.get_distance(sim.ships[i]) < 0.25*width:
				nearby_friends.append(sim.ships[i])
				number_friends += 1

		if number_friends > 0:
			return [True,min(nearby_friends, key=pullDistance)]
		else: return [False]

	def get_distance(self,other):
		# Other is an object
		delta_x = other.x - self.x
		delta_y = other.y - self.y
		distance = math.sqrt(delta_x**2 + delta_y**2)
		return distance

	def step(self):
		# This is the main function that runs through the AUV moves
		if self.strength == 0: #You're dead
			return
		# Check if an enemy is within range
		[enemies, list_of_enemies] = self.check_for_enemies()
		if enemies > 0:
			#print "AUV ", self.id, " is attacking!"
			self.attack(list_of_enemies)
			return
		# Check if a nearby ship has enemies
		the_response = self.ask_nearby_friends()
		if the_response[0] == True:
			# Move to our friend!
			#print "AUV ", self.id, " is moving to assist an ally"
			self.move_to_point(the_response[1].x,the_response[1].y)
			return
		# Else, move randomly
		else:
			self.move_randomly()
			# print "AUV ", self.id, " is moving randomly"

class ASV(object):
	"""
	ASV Class, which encapsulates the behaviors of the ASVs present in the model.
	"""

	def __init__(self,asv_id,start_x,start_y,velocity,endurance,strength,team,radius):
		# AUV Constructor

		self.id = asv_id
		self.x = start_x
		self.y = start_y
		self.speed = velocity
		self.endurance = endurance
		self.strength = strength # Do I want this? TBD...
		self.height = 1 # we are above the water
		self.team = team
		self.radius = radius # how far around itself the agent can "see"

	def move(self):
		return
		# Function for ASV to move around the map
		# To be written

	def attack(self):
		return
		# Function to attack or identify the enemy
		# To be written

	def report(self):
		return
		# function to report information back to other agents

class Ship(object):
	"""
	Ship Class, which encapsulates the behaviors of the Ships present in the model.
	"""

	def __init__(self,ship_id,start_x,start_y,velocity,endurance,strength,team,radius):
		# AUV Constructor

		self.id = ship_id
		self.vehicle = "Ship"
		self.x = start_x
		self.y = start_y
		self.speed = velocity # max speed
		self.endurance = endurance
		self.strength = strength # Do I want this? TBD...
		self.height = -1 # we are below the water
		self.team = team
		self.radius = radius # how far around itself the agent can "see"
		self.flag = 0 # is there an enemy within range

	def move_randomly(self):
		theta = math.radians(rand.uniform(1,360))
		vel = rand.uniform(0, self.speed)
		self.x = self.x + vel*math.sin(theta)
		self.y = self.y + vel*math.cos(theta)
		self.check_boundaries()

	def check_boundaries(self):
		if self.x < 0:
			self.x = 0
		if self.y < 0:
			self.y = 0
		if self.x > (width - 1):
			self.x = (width - 1)
		if self.y > (height - 1):
			self.y = (height - 1)

	def move_to_point(self,x,y):
		# Function to move agent to a given point, instead of randomly

		# Calculate Distance
		delta_x = x - self.x
		delta_y = y - self.y
		distance = math.sqrt(delta_x**2 + delta_y**2)

		# Check if we can get there in one turn, if so move to there minus a buffer
		if distance < self.speed:
			self.x = x-rand.uniform(-2,2)
			self.y = y-rand.uniform(-2 ,2)
			self.check_boundaries()
			return

		# Calculate angle to point
		theta = math.atan2(delta_y,delta_x)

		# Move as close as we can to the point
		vel = self.speed
		self.x = self.x + vel*math.cos(theta)
		self.y = self.y + vel*math.sin(theta)
		self.check_boundaries()

	def attack(self,list_of_enemies):
		# Quick funtion for the next part
		def pullDistance(the_object):
			return self.get_distance(the_object)

		# Find which vehcile is cloest of the list
		if len(list_of_enemies) > 1:
			the_enemy = min(list_of_enemies, key=pullDistance)
		else: the_enemy = list_of_enemies[0]

		#print "Ship ", self.id, " is attacking ", the_enemy.id
		#print "The enemy's strength is ", the_enemy.strength

		# Reduce the Strength of the enemy by 1
		the_enemy.strength -= 1

		# Check the enemy's remaining strength, if 0, kill them
		if the_enemy.strength < 1: # the enemy is dead!
			#print "Ship ", the_enemy.id, "has been lost in battle."
			global team1_killed
			global team2_killed
			if self.team == 1:
				sim.team2_killed += 1
			else: sim.team1_killed += 1
			if the_enemy.vehicle == "AUV":
				# Find the object and remove it
				for i in xrange(len(sim.auvs)):
					if sim.auvs[i].id == the_enemy.id: dead_enemy = i
				del sim.auvs[dead_enemy]

			if the_enemy.vehicle == "ASV":
				# Find the object and remove it
				for i in xrange(len(sim.asvs)):
					if sim.asvs[i].id == the_enemy.id: dead_enemy = i
				del sim.asvs[dead_enemy]

			if the_enemy.vehicle == "Submarine":
				# Find the object and remove it
				for i in xrange(len(sim.subs)):
					if sim.subs[i].id == the_enemy.id: dead_enemy = i
				del sim.subs[dead_enemy]

			if the_enemy.vehicle == "Ship":
				# Find the object and remove it
				for i in xrange(len(sim.ships)):
					if sim.ships[i].id == the_enemy.id: dead_enemy = i
				del sim.ships[dead_enemy]

	def check_for_enemies(self):
		list_enemies = []
		num_enemies = 0

		# run through the list of all AUVs
		for i in xrange(len(sim.auvs)):
			if (self.get_distance(sim.auvs[i]) < self.radius and sim.auvs[i].team != self.team):
				list_enemies.append(sim.auvs[i])
				num_enemies += 1

		# run through the list of all ships
		for i in xrange(len(sim.ships)):
			if (self.get_distance(sim.ships[i]) < self.radius and sim.ships[i].team != self.team):
				list_enemies.append(sim.ships[i])
				num_enemies += 1

		# run through the list of submarines
		for i in xrange(len(sim.subs)):
			if (self.get_distance(sim.subs[i]) < self.radius and sim.subs[i].team != self.team):
				list_enemies.append(sim.subs[i])
				num_enemies += 1

		# run through the list of ASVs
		for i in xrange(len(sim.asvs)):
			if (self.get_distance(sim.asvs[i]) < self.radius and sim.asvs[i].team != self.team):
				list_enemies.append(sim.asvs[i])
				num_enemies += 1

		# Check if we found any enemies
		if num_enemies > 0:
			self.flag = 1 # Enemy in sight!
		else: self.flag = 0

		return [num_enemies, list_enemies]

	def ask_nearby_friends(self):
		# Quick funtion for the next part
		def pullDistance(the_object):
			return self.get_distance(the_object)
		nearby_friends = []
		number_friends = 0

		for i in xrange(len(sim.auvs)):
			if sim.auvs[i].flag and sim.auvs[i].team == self.team and self.get_distance(sim.auvs[i]) < 0.25*width:
				nearby_friends.append(sim.auvs[i])
				number_friends += 1

		for i in xrange(len(sim.asvs)):
			if sim.asvs[i].flag and sim.asvs[i].team == self.team and self.get_distance(sim.asvs[i]) < 0.25*width:
				nearby_friends.append(sim.asvs[i])
				number_friends += 1

		for i in xrange(len(sim.subs)):
			if sim.subs[i].flag and sim.subs[i].team == self.team and self.get_distance(sim.subs[i]) < 0.25*width:
				nearby_friends.append(sim.subs[i])
				number_friends += 1

		for i in xrange(len(sim.ships)):
			if sim.ships[i].flag and sim.ships[i].team == self.team and self.get_distance(sim.ships[i]) < 0.25*width:
				nearby_friends.append(sim.ships[i])
				number_friends += 1

		if number_friends > 0:
			return [True,min(nearby_friends, key=pullDistance)]
		else: return [False]

	def get_distance(self,other):
		# Other is an object
		delta_x = other.x - self.x
		delta_y = other.y - self.y
		distance = math.sqrt(delta_x**2 + delta_y**2)
		return distance

	def step(self):
		# This is the main function that runs through the AUV moves
		if self.strength == 0: #You're dead
			return
		# Check if an enemy is within range
		[enemies, list_of_enemies] = self.check_for_enemies()
		if enemies > 0:
			#print "Ship ", self.id, " is attacking!"
			self.attack(list_of_enemies)
			return
		# Check if a nearby ship has enemies
		the_response = self.ask_nearby_friends()
		if the_response[0] == True:
			# Move to our friend!
			#print "Ship ", self.id, " is moving to assist an ally"
			self.move_to_point(the_response[1].x,the_response[1].y)
			return
		# Else, move randomly
		else:
			self.move_randomly()
			# print "AUV ", self.id, " is moving randomly"

class Submarine(object):
	"""
	ASV Class, which encapsulates the behaviors of the ASVs present in the model.
	"""

	def __init__(self,sub_id,start_x,start_y,velocity,endurance,strength,team,radius):
		# AUV Constructor

		self.id = sub_id
		self.x = start_x
		self.y = start_y
		self.speed = velocity
		self.endurance = endurance
		self.strength = strength # Do I want this? TBD...
		self.height = -1 # we are below the water
		self.team = team
		self.radius = radius # how far around itself the agent can "see"

	def move(self):
		return
		# Function for ASV to move around the map
		# To be written

	def attack(self):
		return
		# Function to attack or identify the enemy
		# To be written

	def report(self):
		return
		# function to report information back to other agents

class Simulation(object):
	"""
	The simulator class which runs the simulation for the MC chains
	"""
	def __init__(self, simulation_number, auv_range = 5, auv_speed = 2, auv_endurance = 1, auv_strength = 2, max_iter = 1000):
		# Simulation Constructor

		# Simulation Variables
		self.id = simulation_number
		self.max_iter = max_iter
		self.run_status = True

		# History Variables
		self.Team1_history = []
		self.Team2_history = []

		# Setup Environmental variables
		global width
		global height
		self.width = width
		self.height = height
		self.num_ships = 10
		self.num_subs = 0
		self.num_auvs = 100
		self.num_asvs = 0
		self.num_agents = self.num_ships + self.num_subs + self.num_auvs + self.num_asvs
		self.team1_killed = 0
		self.team2_killed = 0
		self.time = 0

		# Make the environment
		self.surf_environment = np.zeros((self.width, self.height), dtype=np.int8)
		self.sub_environment = np.zeros((self.width, self.height), dtype=np.int8)

		# Set Land areas
		# surf_envrionment[1,1] = 1 # Land
		for i in xrange(int(round(0.1*self.width))):
			for j in xrange(int(round(0.1*self.height))):
				if i**2 + j**2 < (0.1*self.width)**2:
					self.surf_environment[i,j] = 1
					self.surf_environment[(self.width-1)-i,(self.height-1)-j] = -1

		# Put agents in the model
		self.ships = []
		self.auvs = []
		self.asvs = []
		self.subs = []

		# Enemy Ships - Held Constant (Team 1)
		for i in xrange(self.num_auvs):
			self.auvs.append(AUV(
				auv_id = i,
				start_x = rand.uniform(10, 30),
				start_y = rand.uniform(10, 30),
				velocity = 2,
				endurance = 1,
				strength = 2,
				team = 1,
				radius = 5
				))

		for i in xrange(self.num_ships):
			self.ships.append(Ship(
				ship_id = i,
				start_x = rand.uniform(10, 30),
				start_y = rand.uniform(10, 30),
				velocity = 5, #rand.uniform(4,10),
				endurance = 1,
				strength = 10,
				team = 1,
				radius = 10
				))

		# Friendly Ships - Chane with Simulation (Team 2)
		for i in xrange(self.num_auvs):
			self.auvs.append(AUV(
				auv_id = i + self.num_auvs,
				start_x = rand.uniform(70, 90),
				start_y = rand.uniform(70, 90),
				velocity = auv_speed,
				endurance = auv_endurance,
				strength = auv_strength,
				team = 2,
				radius = auv_range
				))

		for i in xrange(self.num_ships):
			self.ships.append(Ship(
				ship_id = self.num_ships + i,
				start_x = rand.uniform(70, 90),
				start_y = rand.uniform(70, 90),
				velocity = 5, #rand.uniform(4,10),
				endurance = 1,
				strength = 10,
				team = 2,
				radius = 10
				))

	def step(self):
		# Change time
		self.time += 1

		# Randomly shuffle the list of ships and auvs (a few times)
		rand.shuffle(self.auvs)
		rand.shuffle(self.ships)
		rand.shuffle(self.auvs)
		rand.shuffle(self.ships)
		rand.shuffle(self.auvs)
		rand.shuffle(self.ships)

		# Step through all of the agents
		for auv in self.auvs:
			auv.step()
		for ship in self.ships:
			ship.step()

		# Update history variables
		self.Team1_history.append(self.team1_killed)
		self.Team2_history.append(self.team2_killed)

		# Give a status update
		#if self.time%10 == 0:
		#print "Enemy Killed ", self.team1_killed
		#print "Friendly Killed ", self.team2_killed

		# Stopping Criteria
		if self.team1_killed == self.num_agents or self.team2_killed == self.num_agents or self.time > self.max_iter:
			print "Simulation ", self.id, " has ended."
			self.run_status = False

	def run_sim(self):
		# run Simulation
		while self.run_status:
			self.step()

# Iterate
num_simulations = 20
sim_history = []
win_history = []

# Parameters
auv_speed = 1
auv_endurance = 1
auv_strength = 2
auv_range = 5

sim_nums = range(1,11)

sim_speeds = np.linspace(0.5,10.0,num=50)
sim_ranges = np.linspace(1.0,20.0,num=50)
sim_strengths = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4,4,4,4,4,5,5,5,5,5,6,6,6,6,6,7,7,7,7,7,8,8,8,8,8,9,9,9,9,9,10,10,10,10,10]
sim_param = []

print "Beginning Simulations"

for i in xrange(num_simulations):
	sim = Simulation(simulation_number = i+1)
	sim.run_sim()
	sim_history.append(sim)
	if sim.team1_killed == sim.num_agents:
		win_history.append(2)
	else:
		win_history.append(1)

print "Writing to File"

# Print results to a file
with open('baseline2_win_results.txt', 'w') as filehandle:
	for listitem in win_history:
		filehandle.write('%1.0f\n' % listitem)

with open('baseline2_team1_results.txt', 'w') as filehandle:
	for listitem in sim_history[5].Team1_history:
		filehandle.write('%3.0f\n' % listitem)

with open('baseline2_team2_results.txt', 'w') as filehandle:
	for listitem in sim_history[5].Team2_history:
		filehandle.write('%3.0f\n' % listitem)

#with open('strength_list.txt', 'w') as filehandle:
#for listitem in sim_strengths:
#filehandle.write('%3.4f\n' % listitem)


print "Complete"

#plt.figure
#plt.hist(win_history)
