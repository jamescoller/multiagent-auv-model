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

There are four primary agent classes in the system, all contain the same properties, as shown in the code snippet below. The four agent classes are ships, submarines, AUVs, and ASVs. Each agent will move, communicate, and detect or attack other agents from the opposition. The AUVs and Submarines will be below the surface, and the ASVs and Ships will be above the surface. The AUVs and ASVs will not be able to attack other agents. Submarines and Ships can attack all other enemies. Submarines and AUVs can see agents on the surface or underwater. Ships and ASVs can only see other agents on the surface. 

The various types of agents will each have unique movement structures. For instance, an AUV will not be able to travel as far as a ship. The AUVs will swarm together and move together, while Ships will move alone. These movement styles are subject to change. 


```python
class AUV(object):
	"""
	AUV Class, which encapsulates the behaviors of the AUVs present in the model. 
	"""

	def __init__(self,auv_id,start_x,start_y,velocity,endurance,strength,team,radius):
		# AUV Constructor 

		self.id = auv_id
		self.x = start_x
		self.y = start_y 
		self.speed = velocity
		self.endurance = endurance
		self.strength = strength # Do I want this? TBD... 
		self.height = -1 # we are below the water 
		self.team = team
		self.radius = radius # how far around itself the agent can "see"

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

Agents will interact with each other by being able to identify other agents within a set radius. Once identified, the agent will make an action dependent upon what has been identified. Agents on any given team will know the location of the other agents on the team. The agents will interact with the environment by moving throughout the environment. Individual agents will have the ability to move at different speeds depending upon the individual agent. 
 
**_Action Sequence_**

During a given turn of the model, the following sequence will be carried out for each agent. Each agent will complete the full sequence before the next agent moves. 

0. Agent will assess its strength. 
	1. If agent strength is 0, the turn is over. Agent is dead. 
1. Agent will assess its current position. 
	1. If it is with an enemy, it will move to the attack phase. 
	2. If it is with a friendly, it will reposition.
	3. If it is alone, it will reposition. 
	4. If the agent is out of endurance, the agent must remain in position until it can have its endurance reset. 
2. Agent will move (if needed). 
	1. If the agent knows where an enemy is, it will move toward that enemy. 
	2. If an agent does not know the location of the enemy, it will move following its standard movement procedure. 
3. Agent will reassess its position as it moves. 
	1. If it meets an enemy, it will stop. 
	2. If it does not meet an enemy, it will continue until it can no longer move for that turn. 
4. Agent will reassess its new position. 
	1. If it meet an enemy, it will move to the attack phase. 
	2. If it is alone or with a friendly, the turn ends. 
5. Agent will attack the enemy (if able).
	1. If able to, the agent will attack the enemy, reducing the strength of the enemy. 
	2. If more than one enemy is present, agent will attack the closest enemy. 
	3. If agent is unable to attack (only a messenger - such as the AUV or ASV), the agent will relay the locaton of the enemy to the rest of the friendly Navy. 
6. The turn is over. 

```python
def step():
	global time, agents, surf_envrionment, sub_environment

	time += 1

	for agent in agents:
		agent.step()
```

&nbsp; 
### 4) Model Parameters and Initialization

The global parameters of the model are primarily the environmental parameters. These include:
+ Environment width
+ Environment height
+ How many of each agent are present 

Individual agent parameters will include:
+ Strength
+ Speed
+ Endurance
+ Position
+ Team
+ Sight Radius 
+ Endurance recharge time

The model is initialzied following the code in the environment section of this document. This model will utilize the pycx package with a GUI that includes an initialization step. During the initization, the environmental variables and space are created and then each agent is created in a list. From there, each agent will step through its procedure in order. Each agent begins at its home base. The home base location will be hard coded into the environmental setup, along with where "land" is located. The agents will intially disperse from the home base in different directions.  

&nbsp; 

### 5) Assessment and Outcome Measures

Each agent will be attempting to help convey information to destroy the enemy. The primary metrics to be measured are (1) how long does it take to destroy the enemy, and (2) how much of the friendly force was lost in the process. 

The simulation will run until a timeout limit, or until the enemy is destroyed (or the friendly force is destroyed). These metrics will be assessed and compared with each other based on the simulation parameters. 

&nbsp; 

### 6) Parameter Sweep

Several parameters will be varied, both individually and simultaneously. These include:
+ Number of agents 
+ Speed of agents
+ Endurance of agents
+ Strength of agents

Since the goal of this simulation specifically is to look at the design characteristics of the autonomous vehicles (ASVs and AUVs), the parameters of those vehicles will vary, but the parameters of the ships and submarines will remain the same. 
