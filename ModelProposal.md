# Model Proposal for a Multiagent AUV Design Simulation 

James Coller
* Course ID: CMPLXSYS 530
* Course Title: Computer Modeling of Complex Systems
* Term: Winter, 2019

&nbsp; 

### Goal 
*****
 
The goal of this model is to provide knowledge for designers how design choices in autonomous marine vehicles impact wartime effectiveness in a Naval combat setting. In early stages of design, it can be difficult for designers and owners to choose key requirements such as speed and endurance whithout understanding the broader implications of these design choices. This model is aimed to allow designers to gain knowledge on the wartime impacts of those design choices. 

&nbsp;  
### Justification
****

Agent based modeling is an appropriate tool for this scenario becasue it directly represents the eventual end use case of the items being designed. Autonomous underwater vehicles (AUVs) and autonomous surface vehicles (ASVs) are being designed and built for unmanned missions where they will interact with other unmanned platforms as well as manned platforms, both friendly and combative in the case of military vehicles. Agent based models allow these vehicles to be expressed as agents and have the interactions (both macro-level and micro-level) invesitigated. Other design simulation tools, such as finite element analysis, or computational fluid dynamics, allow for investigating design impacts on a single vehicle. These tools, and many tools, do not allow to see how the dynamics of multiple vehicles impact performance. That is the goal of this simulation and is the advantage of agent based modeling. 

&nbsp; 
### Main Micro-level Processes and Macro-level Dynamics of Interest
****

On a microscopic level, the abilty for an invididual agent to be able to carry out a given mission from the design parameters of that agent will be of particular focus. For example, if an AUV agent has design parameters X,Y, and Z, can it successfully complete Mission 1? 

On a macroscopic level, the ability for multiple vehicles to communicate with each other and work together will be investigated. Additionally, examining how combinations of multiple vehicle types may lead to different results in mission effectiveness. The agents will all be interacting throughout the world together trying to accomplish invididual and common goals. How these goals are achieved or failed based on individual design parameters will be of particular interest. 

&nbsp; 


## Model Outline
****
&nbsp; 
### 1) Environment

The environment will similate a limted three dimensional grid. A two dimensional plane extending in a given width and height will represent the primary space for the agents to interact. The third dimension represents surface level versus subsea agents, as some agents (submarines, AUVs) will be subsurface, and other agents (ships, ASVs) will be on the surface level. The grid will have continuous spacing (non-discrete) to allow for movement freedom. 

Some areas of the grid will represent land where agents cannot move. Other areas will represent the ocean where agents are able to freely move. Home bases will represent the intitial starting location for the agents. The environment will include wrapping. 

```python
import numpy as np

# Environmental Variables 
width = 1000
height = 100 

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
```

&nbsp; 

### 2) Agents

There are four primary agent classes in the system, all contain the same properties, as shown in the code snippet below. The four agent classes are ships, submarines, AUVs, and ASVs. 


```python
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
```

&nbsp; 

### 3) Action and Interaction 
 
**_Interaction Topology_**

_Description of the topology of who interacts with whom in the system. Perfectly mixed? Spatial proximity? Along a network? CA neighborhood?_
 
**_Action Sequence_**

_What does an agent, cell, etc. do on a given turn? Provide a step-by-step description of what happens on a given turn for each part of your model_

1. Step 1
2. Step 2
3. Etc...

&nbsp; 
### 4) Model Parameters and Initialization

_Describe and list any global parameters you will be applying in your model._

_Describe how your model will be initialized_

_Provide a high level, step-by-step description of your schedule during each "tick" of the model_

&nbsp; 

### 5) Assessment and Outcome Measures

_What quantitative metrics and/or qualitative features will you use to assess your model outcomes?_

&nbsp; 

### 6) Parameter Sweep

_What parameters are you most interested in sweeping through? What value ranges do you expect to look at for your analysis?_
