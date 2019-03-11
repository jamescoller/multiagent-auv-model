#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 2019

Implementation of a ABM for Design Criteria Impact of AUVs and ASVs 
CMPLXSYS 530 Final Project Winter 2019

@author: jcoller
"""
# Imports 
import matplotlib
matplotlib.use('TkAgg')

import pylab as plt
import random 
import scipy 
import numpy as np

import sys

# Environmental Variables 
width = 1000
height = 100 

# Define the agent Classes

class AUV(object):
	"""
	AUV Class, which encapsulates the behaviors of the AUVs present in the model. 
	"""

	def __init__(self,auv_id,start_x,start_y,velocity,endurance,strength,team):
		# AUV Constructor 

		self.id = auv_id
		self.x = start_x
		self.y = start_y 
		self.speed = velocity
		self.endurance = endurance
		self.strength = strength # Do I want this? TBD... 
		self.height = -1 # we are below the water 
		self.team = team

	def move(self):
		# Function for AUV to move around the map 
		# To be written 

	def attack(self): 
		# Function to attack or identify the enemy 
		# To be written 

	def report(self):
		# function to report information back to other agents 

class ASV(object):
	"""
	ASV Class, which encapsulates the behaviors of the ASVs present in the model. 
	"""

	def __init__(self,auv_id,start_x,start_y,velocity,endurance,strength,team):
		# AUV Constructor 

		self.id = auv_id
		self.x = start_x
		self.y = start_y 
		self.speed = velocity
		self.endurance = endurance
		self.strength = strength # Do I want this? TBD... 
		self.height = 1 # we are above the water 
		self.team = team

	def move(self):
		# Function for ASV to move around the map 
		# To be written 

	def attack(self): 
		# Function to attack or identify the enemy 
		# To be written 

	def report(self):
		# function to report information back to other agents 

# Similar classes for ships and submarines... 

# Setup the environment 

def init():
	global time, agents, surf_envrionment, sub_environment

	time = 0 

	# Still debating how to best represent the continuous environment... 
	surf_envrionment = np.zeros((width, height), dtype=np.int8) # Do I want this to be a grid? 
	sub_environment = np.zeros((width, height), dtype=np.int8)

	# Set Land areas 
	# Set land areas here in surf_environment and sub_environment by setting their number to be something
	# other than 0. -1 maybe? 

	# Set home ports for enemy and friendly 
	# Set locations here in surf_environment and sub_environment by setting their number to be 
	# something other than 0. 2 maybe? 1 would be occiupied... 

	# The problem here with doing a grid is I'm making this a discrete environment... how do I 
	# represent the environment as a continuous space? 

	# Setup the agents in the environment 
	agents = []
	for i in xrange(num_agents):
		# Loop through and place all of the agents in their starting locations 

def draw():
	# Code here to visually represent what is going on 

def step():
	global time, agents, surf_envrionment, sub_environment

	time += 1

	for agent in agents:
		agent.step()

		
import pycxsimulator
pycxsimulator.GUI().start(func=[init,draw,step])





