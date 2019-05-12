from colorfight import Colorfight
import time
import random
from colorfight.constants import BLD_GOLD_MINE, BLD_ENERGY_WELL, BLD_FORTRESS
import operator
import collections


# def findHome():
# 	for cell in game.me.cells.values():
# 		if cell.building.name == "home":
# 			print("Found Home")
# 			return cell

# Create a Colorfight Instance. This will be the object that you interact
# with.
global game
game = Colorfight()

# Connect to the server. This will connect to the public room. If you want to
# join other rooms, you need to change the argument
game.connect(room = 'smallpublic')

# game.register should return True if succeed.
# As no duplicate usernames are allowed, a random integer string is appended
# to the example username. You don't need to do this, change the username
# to your ID.
# You need to set a password. For the example AI, the current time is used
# as the password. You should change it to something that will not change 
# between runs so you can continue the game if disconnected.
if game.register(username = '200IQ', \
		password = 'hello'):
	# This is the game loop
	while True:
		# The command list we will send to the server
		cmd_list = []
		# The list of cells that we want to attack
		my_attack_list = []
		# update_turn() is required to get the latest information from the
		# server. This will halt the program until it receives the updated
		# information. 
		# After update_turn(), game object will be updated.   
		game.update_turn()


		# Check if you exist in the game. If not, wait for the next round.
		# You may not appear immediately after you join. But you should be 
		# in the game after one round.
		if game.me == None:
			continue

		me = game.me

		hcLevel = 1

		# homeCell = findHome()

		# game.me.cells is a dict, where the keys are Position and the values
		# are MapCell. Get all my cells.
		for cell in game.me.cells.values():

			# if me.gold > 1000 * homeCell.building.level and me.energy > 1000 * homeCell.building.level:
			if cell.building.can_upgrade and \
					cell.building.is_home and \
					cell.building.upgrade_gold < me.gold and \
					cell.building.upgrade_energy < me.energy:
				cmd_list.append(game.upgrade(cell.position))
				print("We upgraded ({}, {})".format(cell.position.x, cell.position.y))
				me.gold   -= 1000 * cell.building.level
				me.energy -= 1000 * cell.building.level

			# Check the surrounding position
			cellDict = {}
			for pos in cell.position.get_surrounding_cardinals():
				# Get the MapCell object of that position
				c = game.game_map[pos]
				# Attack if the cost is less than what I have, and the owner
				# is not mine, and I have not attacked it in this round already
				# We also try to keep our cell number under 100 to avoid tax
				# if c.attack_cost < me.energy and c.owner != game.uid \
				# 		and c.position not in my_attack_list:
				EG = c.energy + c.gold
				value = c.attack_cost - 30 * EG
				cellDict[pos] = value
					# Add the attack command in the command list
					# Subtract the attack cost manually so I can keep track
					# of the energy I have.
					# Add the position to the attack list so I won't attack
					# the same cell
			
			sortedDict = sorted(cellDict.items(), key = operator.itemgetter(1))
			sortedCellDict = collections.OrderedDict(sortedDict)

			for item in sortedCellDict:
				c = game.game_map[item]
				if c.owner != me.uid and c.attack_cost < me.energy:
					cmd_list.append(game.attack(item, c.attack_cost))
					print("We are attacking ({}, {}) with {} energy. It's gold is {} and energy is {}".format(pos.x, pos.y, c.attack_cost, c.gold, c.energy))
					game.me.energy -= c.attack_cost
					my_attack_list.append(c.position)

			#building
			buildingList = {}
			if cell.owner == me.uid and cell.building.is_empty and me.gold >= 100:
				# if cell.gold > 5 or cell.energy * 1.5 > 5:
				# 	building = BLD_GOLD_MINE if cell.gold > 1.5*cell.energy else BLD_ENERGY_WELL
				# else:
				# 	building = BLD_ENERGY_WELL
				val = 0
				list = []
				if game.turn < 50:
					building = BLD_ENERGY_WELL
					val = cell.energy
				elif game.turn < 150:
					if cell.energy > 5:
						building = BLD_ENERGY_WELL
						val = cell.energy
					else:
						building = BLD_FORTRESS
						sum = 0
						for p in cell.position.get_surrounding_cardinals():
							sum += game.game_map[p].energy + game.game_map[p].gold
						val = sum / 8
				else:
					if cell.gold > 5:
						building = BLD_GOLD_MINE
						val = 2 * cell.building.gold
					else:
						building = BLD_FORTRESS
						sum = 0
						for p in cell.position.get_surrounding_cardinals():
							sum += game.game_map[p].energy + game.game_map[p].gold
						val = sum / 8

				buildingList[cell] = val

			sortedDict = sorted(buildingList.items(), key = operator.itemgetter(1))
			sortedCellDict = collections.OrderedDict(sortedDict)

			for c in sortedCellDict:
				if me.gold >= 100:
					cmd_list.append(game.build(c.position, building))
					print("We building")
					me.gold -= 100
			

			# If we can upgrade the building, upgrade it.
			# Notice can_update only checks for upper bound. You need to check
			# tech_level by yourself.
			if cell.building.can_upgrade and \
					(cell.building.is_home or cell.building.level < me.tech_level) and \
					cell.building.upgrade_gold < me.gold and \
					cell.building.upgrade_energy < me.energy:
				cmd_list.append(game.upgrade(cell.position))
				print("We upgraded ({}, {})".format(cell.position.x, cell.position.y))
				me.gold   -= cell.building.upgrade_gold
				me.energy -= cell.building.upgrade_energy

		
		# Send the command list to the server
		result = game.send_cmd(cmd_list)
		print(result)
		print("energy: ", me.energy)
		print("gold: ", me.gold)
