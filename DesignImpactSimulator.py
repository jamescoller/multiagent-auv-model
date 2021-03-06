#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 2019

Implementation of a ABM for Design Criteria Impact of AUVs and ASVs
CMPLXSYS 530 Final Project Winter 2019

April 2019: This file is dated and is held only for the purpose of saving the PYCX implementation.

@author: jcoller
"""

"""
To-Do:
- Implement endurance
- Add submarines and ASVs
- Change to be a class structure
- Remove PYCX
- Add Monte Carlo Simulation
- Update visualizations to reflect the number of enemies remaining over time
- Add a stopping criterion (everyone is dead)
- Consider updating environmental constraints such as land masses etc.
- Consider adding structure to the movement patterns - such as the ships going out to a set area and then releasing AUVs to begin searching
- Consider how to set various agents to have limited powers, i.e. AUVs cannot attack - just find enemy ships or submarines
"""

# Imports
import matplotlib
matplotlib.use('TkAgg')

import pylab as plt
import random as rand
import scipy
import numpy as np
import math

import sys

# Set Random Seed
rand.seed()

# Environmental Variables
width = 100
height = 100

# Simulation Parameters
num_ships = 10
num_subs = 0
num_auvs = 100
num_asvs = 0
team1_killed = 0
team2_killed = 0

# Define the agent Classes

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

		print "AUV ", self.id, " is attacking ", the_enemy.id
		print "The enemy's strength is ", the_enemy.strength

		# Reduce the Strength of the enemy by 1
		the_enemy.strength -= 1

		# Check the enemy's remaining strength, if 0, kill them
		if the_enemy.strength < 1: # the enemy is dead!
			print "AUV ", the_enemy.id, "has been lost in battle."
			global team1_killed
			global team2_killed
			if self.team == 1:
				team2_killed += 1
			else: team1_killed += 1
			if the_enemy.vehicle == "AUV":
				# Find the object and remove it
				for i in xrange(len(auvs)):
					if auvs[i].id == the_enemy.id: dead_enemy = i
				del auvs[dead_enemy]

			if the_enemy.vehicle == "ASV":
				# Find the object and remove it
				for i in xrange(len(asvs)):
					if asvs[i].id == the_enemy.id: dead_enemy = i
				del asvs[dead_enemy]

			if the_enemy.vehicle == "Submarine":
				# Find the object and remove it
				for i in xrange(len(subs)):
					if subs[i].id == the_enemy.id: dead_enemy = i
				del subs[dead_enemy]

			if the_enemy.vehicle == "Ship":
				# Find the object and remove it
				for i in xrange(len(ships)):
					if ships[i].id == the_enemy.id: dead_enemy = i
				del ships[dead_enemy]

	def check_for_enemies(self):
		list_enemies = []
		num_enemies = 0

		# Run through the list of all AUVs
		for i in xrange(len(auvs)):
			if (self.get_distance(auvs[i]) < self.radius and auvs[i].team != self.team):
				list_enemies.append(auvs[i])
				num_enemies += 1

		# Run through the list of all ships
		for i in xrange(len(ships)):
			if (self.get_distance(ships[i]) < self.radius and ships[i].team != self.team):
				list_enemies.append(ships[i])
				num_enemies += 1

		# Run through the list of submarines
		for i in xrange(len(subs)):
			if (self.get_distance(subs[i]) < self.radius and subs[i].team != self.team):
				list_enemies.append(subs[i])
				num_enemies += 1

		# Run through the list of ASVs
		for i in xrange(len(asvs)):
			if (self.get_distance(asvs[i]) < self.radius and asvs[i].team != self.team):
				list_enemies.append(asvs[i])
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

		for i in xrange(len(auvs)):
			if auvs[i].flag and auvs[i].team == self.team and self.get_distance(auvs[i]) < 0.25*width:
				nearby_friends.append(auvs[i])
				number_friends += 1

		for i in xrange(len(asvs)):
			if asvs[i].flag and asvs[i].team == self.team and self.get_distance(asvs[i]) < 0.25*width:
				nearby_friends.append(asvs[i])
				number_friends += 1

		for i in xrange(len(subs)):
			if subs[i].flag and subs[i].team == self.team and self.get_distance(subs[i]) < 0.25*width:
				nearby_friends.append(subs[i])
				number_friends += 1

		for i in xrange(len(ships)):
			if ships[i].flag and ships[i].team == self.team and self.get_distance(ships[i]) < 0.25*width:
				nearby_friends.append(ships[i])
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
			print "AUV ", self.id, " is attacking!"
			self.attack(list_of_enemies)
			return
		# Check if a nearby ship has enemies
		the_response = self.ask_nearby_friends()
		if the_response[0] == True:
			# Move to our friend!
			print "AUV ", self.id, " is moving to assist an ally"
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

		print "Ship ", self.id, " is attacking ", the_enemy.id
		print "The enemy's strength is ", the_enemy.strength

		# Reduce the Strength of the enemy by 1
		the_enemy.strength -= 1

		# Check the enemy's remaining strength, if 0, kill them
		if the_enemy.strength < 1: # the enemy is dead!
			print "Ship ", the_enemy.id, "has been lost in battle."
			global team1_killed
			global team2_killed
			if self.team == 1:
				team2_killed += 1
			else: team1_killed += 1
			if the_enemy.vehicle == "AUV":
				# Find the object and remove it
				for i in xrange(len(auvs)):
					if auvs[i].id == the_enemy.id: dead_enemy = i
				del auvs[dead_enemy]

			if the_enemy.vehicle == "ASV":
				# Find the object and remove it
				for i in xrange(len(asvs)):
					if asvs[i].id == the_enemy.id: dead_enemy = i
				del asvs[dead_enemy]

			if the_enemy.vehicle == "Submarine":
				# Find the object and remove it
				for i in xrange(len(subs)):
					if subs[i].id == the_enemy.id: dead_enemy = i
				del subs[dead_enemy]

			if the_enemy.vehicle == "Ship":
				# Find the object and remove it
				for i in xrange(len(ships)):
					if ships[i].id == the_enemy.id: dead_enemy = i
				del ships[dead_enemy]

	def check_for_enemies(self):
		list_enemies = []
		num_enemies = 0

		# Run through the list of all AUVs
		for i in xrange(len(auvs)):
			if (self.get_distance(auvs[i]) < self.radius and auvs[i].team != self.team):
				list_enemies.append(auvs[i])
				num_enemies += 1

		# Run through the list of all ships
		for i in xrange(len(ships)):
			if (self.get_distance(ships[i]) < self.radius and ships[i].team != self.team):
				list_enemies.append(ships[i])
				num_enemies += 1

		# Run through the list of submarines
		for i in xrange(len(subs)):
			if (self.get_distance(subs[i]) < self.radius and subs[i].team != self.team):
				list_enemies.append(subs[i])
				num_enemies += 1

		# Run through the list of ASVs
		for i in xrange(len(asvs)):
			if (self.get_distance(asvs[i]) < self.radius and asvs[i].team != self.team):
				list_enemies.append(asvs[i])
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

		for i in xrange(len(auvs)):
			if auvs[i].flag and auvs[i].team == self.team and self.get_distance(auvs[i]) < 0.25*width:
				nearby_friends.append(auvs[i])
				number_friends += 1

		for i in xrange(len(asvs)):
			if asvs[i].flag and asvs[i].team == self.team and self.get_distance(asvs[i]) < 0.25*width:
				nearby_friends.append(asvs[i])
				number_friends += 1

		for i in xrange(len(subs)):
			if subs[i].flag and subs[i].team == self.team and self.get_distance(subs[i]) < 0.25*width:
				nearby_friends.append(subs[i])
				number_friends += 1

		for i in xrange(len(ships)):
			if ships[i].flag and ships[i].team == self.team and self.get_distance(ships[i]) < 0.25*width:
				nearby_friends.append(ships[i])
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
			print "Ship ", self.id, " is attacking!"
			self.attack(list_of_enemies)
			return
		# Check if a nearby ship has enemies
		the_response = self.ask_nearby_friends()
		if the_response[0] == True:
			# Move to our friend!
			print "Ship ", self.id, " is moving to assist an ally"
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

# Setup the environment

def init():
	global time, auvs, ships, subs, asvs, surf_environment, sub_environment, team1_killed, team2_killed

	time = 0
	team1_killed = 0
	team2_killed = 0

	# Still debating how to best represent the continuous environment...
	surf_environment = np.zeros((width, height), dtype=np.int8)
	sub_environment = np.zeros((width, height), dtype=np.int8)

	# Set Land areas
	# surf_envrionment[1,1] = 1 # Land
	for i in xrange(int(round(0.1*width))):
		for j in xrange(int(round(0.1*height))):
			if i**2 + j**2 < (0.1*width)**2:
				surf_environment[i,j] = 1
				surf_environment[(width-1)-i,(height-1)-j] = -1

	# Set land areas here in surf_environment and sub_environment by setting their number to be something
	# other than 0. -1 maybe?

	# Set home ports for enemy and friendly
	# Set locations here in surf_environment and sub_environment by setting their number to be
	# something other than 0. 2 maybe? 1 would be occiupied...

	# The problem here with doing a grid is I'm making this a discrete environment... how do I
	# represent the environment as a continuous space?

	# Setup the agents in the environment
	ships = []
	auvs = []
	asvs = []
	subs = []

	for i in xrange(num_auvs):
		auvs.append(AUV(
			auv_id = i,
			start_x = rand.uniform(10, 30),
			start_y = rand.uniform(10, 30),
			velocity = rand.uniform(4,10),
			endurance = 1,
			strength = 4,
			team = 1,
			radius = 10
		))

	for i in xrange(num_ships):
		ships.append(Ship(
			ship_id = i,
			start_x = rand.uniform(10, 30),
			start_y = rand.uniform(10, 30),
			velocity = rand.uniform(4,10),
			endurance = 1,
			strength = 10,
			team = 1,
			radius = 20
		))

	for i in xrange(num_auvs):
		auvs.append(AUV(
			auv_id = i + num_auvs,
			start_x = rand.uniform(70, 90),
			start_y = rand.uniform(70, 90),
			velocity = rand.uniform(1,5),
			endurance = 1,
			strength = 2,
			team = 2,
			radius = 5
		))

	for i in xrange(num_ships):
		ships.append(Ship(
			ship_id = num_ships + i,
			start_x = rand.uniform(70, 90),
			start_y = rand.uniform(70, 90),
			velocity = rand.uniform(4,10),
			endurance = 1,
			strength = 10,
			team = 2,
			radius = 20
		))

#	auv1 = AUV(auv_id = 1, start_x = 50, start_y = 50, velocity = 10, endurance = 1, strength = 2, team = 1, radius = 5)

#	auv2 = AUV(auv_id = 2, start_x = 54, start_y = 50, velocity = 10, endurance = 1, strength = 2, team = 1, radius = 5)

#	auv3 = AUV(auv_id = 3, start_x = 52, start_y = 50, velocity = 10, endurance = 1, strength = 4, team = 2, radius = 5)

#	auv4 = AUV(auv_id = 4, start_x = 52, start_y = 52, velocity = 10, endurance = 1, strength = 2, team = 1, radius = 5)

#	auvs = [auv1,auv2,auv3,auv4]



def draw():
	plt.cla() # check
	plt.pcolor(surf_environment, cmap = 'bwr')
	plt.axis('image')
	auv_x_1 = []
	auv_y_1 = []
	auv_x_2 = []
	auv_y_2 = []
	ship_x_1 = []
	ship_y_1 = []
	ship_x_2 = []
	ship_y_2 = []
	for auv in auvs:
		if auv.team == 1:
			auv_x_1.append(auv.x)
			auv_y_1.append(auv.y)
		if auv.team == 2:
			auv_x_2.append(auv.x)
			auv_y_2.append(auv.y)
	for ship in ships:
		if ship.team == 1:
			ship_x_1.append(ship.x)
			ship_y_1.append(ship.y)
		if ship.team == 2:
			ship_x_2.append(ship.x)
			ship_y_2.append(ship.y)
	plt.scatter(auv_x_1,auv_y_1,c = 'C1')
	plt.scatter(auv_x_2,auv_y_2,c = 'C0')
	plt.scatter(ship_x_1,ship_y_1,c = 'C1',marker = '^')
	plt.scatter(ship_x_2,ship_y_2,c = 'C0',marker = '^')
	plt.title('time step = ' + str(time))

def step():
	global time, agents, surf_environment, sub_environment, team1_killed, team2_killed

	time += 1

	rand.shuffle(auvs)
	rand.shuffle(ships)

	for auv in auvs:
		auv.step()

	for ship in ships:
		ship.step()

	if time%10 == 0:
		print "Team 1 Killed ", team1_killed
		print "Team 2 Killed ", team2_killed

	team_total = num_asvs + num_auvs + num_subs + num_ships

	if team1_killed == team_total or team2_killed == team_total:
		print "Game over"

import pycxsimulator
sim_gui = pycxsimulator.GUI().start(func=[init,draw,step])
