# This is a game.

import sys
from random import randint
# From stackoverflow.
class textcolor:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
   
def teamcolor(civ, string):
	return str(civ.info.color + string + textcolor.END)

								## ASSIGNMENTS ##

class Civ:
	def __init__(self, info, name, units_List, cities_List):
		self.info = info
		self.name = name
		self.units_List = units_List
		self.cities_List = cities_List
		self.active = 1
		self.score = 0
		self.units_destroyed = 0
		self.cities_captured = 0

class CivInfo:
	def __init__(self, name, capital_Name, color):
		self.name = name
		self.capital_Name = capital_Name
		self.color = color
		
class MapObject:
	def __init__(self, position, name, owner, isterrain):
		self.position = position
		self.name = name
		self.owner = owner		
		self.isterrain = isterrain
		self.level = 1
		
class City(MapObject):
	def __init__(self, position, name, owner):
		super().__init__(position, name, owner,0)
		self.icon = teamcolor(owner, owner.name[0].upper())
	
	health = 200
	dmg = 0
	dmg_turn = 0

class Unit(MapObject):
	def __init__(self, position, name, owner):
		super().__init__(position, name.lower(), owner,0)
		self.level = 0
		self.icon = teamcolor(owner, owner.name[0].lower())
	health = 100
	dmg = 0
	dmg_turn = 0

class Position:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
class Terrain(MapObject):
	def __init__(self, position):
		super().__init__(position,"Terrain",None,1)
		self.icon = "."
		self.passable = 0
		
class Mountain(Terrain):
	def __init__(self, position):
		super().__init__(position)
		self.icon = "▲▲"
		

		
		
# Some civilizations with their capital. The capital is never really named
# in the game, so this is just for fun. 
c_Afghanistan = CivInfo("Afghanistan", "Kabul", '\033[95m')
c_Bolivia = CivInfo("Bolivia","La Paz", '\033[96m')	
c_CzechRepublic = CivInfo("Czech Republic", "Prague", '\033[36m')
c_Denmark = CivInfo("Denmark", "Copenhagen", '\033[94m')
c_Ecuador = CivInfo("Ecuador", "Quito", '\033[91m')
c_France = CivInfo("France", "Paris", '\033[92m')
c_Null = CivInfo("null", "null", '')

c_ListAll = [c_Afghanistan, c_Bolivia, c_CzechRepublic, c_Denmark, c_Ecuador,
c_France]

m_width = 10
m_height = 10

# default attack power and attack coefficient per level.
attack_power = 100
attacker_advantage = 5

# every level gained (or stolen) by units adds the following to damage:
level_bonus_default = 10

matrix = [[0] * m_width for i in range(m_height)]

# units per city, max 4 (i guess if you let them spawn at the corners
# the max would become 8 - but that isn't written in the spawn function)
default_unit_number = 3

# cities per civ, no max
default_city_number = 3

# civs per game, max 10, player-inclusive.
c_Number = 3

# Adjusts the amount of terrain (right now, just mountains)
terrain_scale = 1
default_terrain_number = int((m_width+m_height)/2)*terrain_scale

# A value of 10 means cities spawn units 1 out of 10 turns
# NB this is not per civ, this is per CITY. 
# Overwhelming the map with units is just annoying,
# especially as there is no overlapping allowed.
unit_spawn_rarity = 40

# I want this flag to mean that the AI never moves into another
# unit's area of attack. Especially as the attacker advantage
# is so high this will make the game exceedingly
# difficult.
AI_HARD = 1

turns = 0
turns_limit = (m_width*m_height)/2
score_threshold = 10

u_List = []	
c_List = []

c_Player = Civ(c_Null, "null", [], [])

p_Null = Position(0,0)



								## GAME FUNCTIONS ##
def debug(i):
	if i == "k":
		sys.exit("Bye bye ;_;")
	return 0
	
def setup():
	global c_Player
	i = 0
	global c_List
	c_List = []
	civs_picked = []
	civ_picked_player = None
	while i < c_Number:
		if civ_picked_player==None:
			civ_picked_player = randint(0,len(c_ListAll)-1)
			civs_picked.append(civ_picked_player)
			c_Player = Civ(c_ListAll[civ_picked_player],
				c_ListAll[civ_picked_player].name,[],[])
			c_List.append(c_Player)
			player_assigned = 1	
			print("The player has been assigned to "
				+c_Player.name+".")
		else:
			civ_picked_AI = randint(0,len(c_ListAll)-1)
			while civ_picked_AI in civs_picked:
				civ_picked_AI = randint(0,len(c_ListAll)-1)
			c_AI = Civ(c_ListAll[civ_picked_AI],
				c_ListAll[civ_picked_AI].name,[],[])
			civs_picked.append(civ_picked_AI)
			c_List.append(c_AI)
			print("AI has been assigned to "+c_AI.name+".")
		i += 1
	print()
	
	i = 0
	while i < default_terrain_number:
		createterrain(p_Null)
		i += 1
	
	for civ in c_List:
		i = 0
		while i < default_city_number:
			i += 1
			if i == 1:
				city=foundcity(p_Null, civ, civ.info.capital_Name)

			else:
				city=foundcity(p_Null, civ)
			print	
			j = 0
			while j < default_unit_number:
				j += 1
				spawnunit(civ, city)
	return 0
	
def foundcity(pos, civ, cityname="", hostile=0):
	while pos == p_Null:
		temp_pos = Position((randint(0,m_width-1)),
			(randint(0,m_height-1)))
		if matrix[temp_pos.y][temp_pos.x]==0:
			pos = temp_pos
		else:
			None
	cityname = "city"
	if hostile == 0:
		print(civ.name+" has founded a "+cityname+" at "+locstring(pos))
	else:
		print(civ.name+" has captured a "+cityname+" at "+locstring(pos)+"!")
		civ.cities_captured += 1
	city = City(pos, cityname, civ)
	civ.cities_List.append(city)	
	matrix[pos.y][pos.x] = city
	return city
	
def createterrain(pos, kind=0):
	while pos == p_Null:
		temp_pos = Position((randint(0,m_width-1)),
			(randint(0,m_height-1)))
		if matrix[temp_pos.y][temp_pos.x]==0:
			pos = temp_pos
		else:
			None
	if kind == 0:		
		print("	A mountain has formed at "+locstring(pos))
		newterrain = Mountain(pos)
	
	matrix[pos.y][pos.x] = newterrain
	return newterrain
	
	
def spawnunit(civ, city, random=0):
	pos = city.position
	spawned = 0
	debugcounter=0
	while spawned==0:
		debugcounter += 1
		rand = randint(0,3)
		if rand == 0:
			spawn = Position(pos.x, pos.y+1)
		if rand == 1:
			spawn = Position(pos.x+1, pos.y)
		if rand == 2:
			spawn = Position(pos.x, pos.y-1)
		if rand == 3:
			spawn = Position(pos.x-1, pos.y)
		try:	
			if matrix[spawn.y][spawn.x] == 0:
				if 0<=spawn.x<=m_width:
					if 0<=spawn.y<=m_height:
						unit = Unit(spawn, "Unit", civ)
						matrix[spawn.y][spawn.x] = unit
						civ.units_List.append(unit)               
						spawned = 1
						print("	"+civ.name+" has trained a unit at "+locstring(unit)+".")
		except IndexError as error:
			None
		if debugcounter == 20:
			print("	"+civ.name+" tried to train a unit but it wouldn't fit.")
			spawned = 1
			return 0
	
	
	
def move(unit, direction,verbose=1,AI=0):
	if direction==move_Words[4]:
		print(namestr(unit)+" is biding its time.")
		return 0
	horrible_error_counter = 0	
	origin_x = unit.position.x
	origin_y = unit.position.y
	origin = Position(origin_x, origin_y)
	aim = p_Null
	global matrix
	moved = 0
	if moved==0:
	# CHANGED TO AN IF STATEMENT because loop occurs in move function
	# Main move loop
		if direction==move_Words[0]:
			aim = Position(origin_x, origin_y-1)
		elif direction==move_Words[1]:
			aim = Position(origin_x+1, origin_y)
		elif direction==move_Words[2]:
			aim = Position(origin_x, origin_y+1)
		elif direction==move_Words[3]:
			aim = Position(origin_x-1, origin_y)
		else:
			print("Direction not parsed. Retry.")
			return 1
		
		try:
			if 0<=aim.x<=m_width and 0<=aim.y<=m_height:
				if matrix[aim.y][aim.x] == 0:
					# empty tile
					unit.position.x = aim.x
					unit.position.y = aim.y
					changemap(aim, origin, unit, 0)
					moved = 1
					print(namestr(unit) +" moved to "+locstring(unit)+".")
					return 0
					
				elif matrix[aim.y][aim.x].isterrain == 1:
					# mountain
					print("	Unit at "+locstring(unit)+" tried to climb a mountain.")
					return 1	

				elif matrix[aim.y][aim.x].owner == unit.owner:
					# friendly
					print("	Unit at "+locstring(unit)+" ran into a friendly.")
					return 1	
					
				elif matrix[aim.y][aim.x].owner is not unit.owner:
					# enemy
					combat(unit, matrix[aim.y][aim.x])
					return 0	
					
			else:
				print("	Unit at "+locstring(unit)+" tried to leave the AO.")
				return 1
				
					# enemy
		except IndexError as error:
			print("Not sure how you managed to get this error but well done.")
				
		

def geticon(obj):
	return str("["+obj.icon+"]")
	
def combat(red, blu):
	random_seed = randint(0,attack_power)
	level_bonus = red.level*level_bonus_default
	red.dmg_turn = int(random_seed/attacker_advantage)
	blu.dmg_turn = attack_power-random_seed + level_bonus
	
	if blu.__class__.__name__=="Unit":
		print(namestr(red)+" attacks "+namestr(blu)+" at "+locstring(blu)+"!")
	if blu.__class__.__name__=="City":
		combatcity(red, blu)
	
	if random_seed > 50:
		print("	The attack was unlucky!"+" ("+str(100-random_seed)+")")
	if 10 < random_seed <= 50:
		print("	The attack succeeds!"+" ("+str(100-random_seed)+")")
	if random_seed <= 10:
		print("	A critical hit! The defenders are routed!"+" ("+str(100-random_seed)+")")	
		
	bindex = 0	
	belligerents = [red, blu]
	for b in belligerents:
		other = belligerents[abs(belligerents.index(b)-1)]
		b.dmg += b.dmg_turn
		print("	"+namestr(b) + " took "+str(b.dmg_turn)+" damage.")
		other.level += 1
		if b.__class__.__name__=="Unit":
			if b.dmg >= b.health:
				print("	"+namestr(b)+" has died from its wounds.")
				saveloc = b.position
				killunit(b)		
				other.owner.units_destroyed += 1
				# This line makes stealing levels possible
				# Can result in huge snowballs but that could be fun:
				# other.level += b.level
		if b.__class__.__name__=="City":
			
			if b.dmg >= b.health:
				print("	"+namestr(b)+" has fallen.")
				saveloc = b.position
				killunit(b)
				foundcity(saveloc, red.owner, b.name,1)
				
			
			
		else:
			None
		bindex += 1	
		
	return 0
	

	
def combatcity(unit, city):
	unitname = namestr(unit)
	cityname = city.name+" ["+str(city.health-city.dmg)+"]"
	print(unitname+" attacks "+namestr(city)+" at "+locstring(city)+"!")	
	return cityname
	
def namestr(obj):
	return str(obj.owner.name + "'s "+obj.name+" ["+str(obj.health-obj.dmg)+"]")

def locstring(obj,literal=0):
	if obj.__class__.__name__=="Unit" or obj.__class__.__name__=="City":
		return "("+str(obj.position.x + 1)+", "+str(obj.position.y+1)+")"
	if obj.__class__.__name__=="Position":
		return "("+str(obj.x + 1)+", "+str(obj.y+1)+")"
	if literal:
		if obj.__class__.__name__=="Unit" or obj.__class__.__name__=="City":
			return "("+str(obj.position.x)+", "+str(obj.position.y)+")"
		if obj.__class__.__name__=="Position":
			return "("+str(obj.x)+", "+str(obj.y)+")"

def changemap(aim, origin, obj, verbose=1):
	# This should handle all cases.
	matrix[origin.y][origin.x] = 0
	if aim == p_Null:
		None
	else:	
		matrix[aim.y][aim.x] = obj
	obj.position = aim
	if verbose:
		printmap()
	
def killunit(unit):
	if unit.__class__.__name__ == "Unit":
		unit.owner.units_List.remove(unit)
	if unit.__class__.__name__ == "City":	
		unit.owner.cities_List.remove(unit)
	changemap(p_Null,unit.position,unit,0)	
	return 0
		
def initmessage():
	# Called once at the start of the game
	print("=================================================")
	print("Hello. Welcome to Alex's War Game.")
	print()
	print("In this game, you can win by four conditions:")
	print("Controlling every city (domination),")
	print("Being the last to control units (elimination),")
	print("Having "+str(score_threshold)+" times your closest competitor's score,")
	print("Or having the highest score at the end of "+str(turns_limit)+" turns.")
	print("Move using WASD: w, a, s, d, and enter.")
	print("To skip a unit's turn, use space or enter by itself.")
	print("Capital letters are cities, and lower case letters are units.")
	print("An exclamation point signifies the active unit.")
	print("Cities have the chance to spawn additional units.")
	print("Units will level up as they fight and do more damage.")
	print("Attackers have a significant advantage, so be cautious.")
	print("Consider your movements carefully and use diagonals to your advantage.")
	print("But, of course, you already knew that... General.")
	print()
	return 0
	
def printmap(unit, debug=""):
	if debug=="debug":
		return 0
	global matrix
	p = 0
	while p < m_width:
		p += 1
		if p < 10:
			print(" "+str(p)+"  ", end="")
		elif p < 100:
			print(" "+str(p)+" ", end="")
	print()
	p = 0
	while p < m_width:
		p += 1
		print(" |  ", end="")
	print()
	print()
	h = 0
	for a in matrix:
		h += 1
		for b in a:
			if b==0:
				print("    ", end="")
			elif b.isterrain:
				print(" "+str(b.icon)+" ",end="")
			elif b.__class__.__name__=="City":
				print(" "+str(b.icon)+"⚑ ",end="")
			elif b==unit:
				print(teamcolor(c_Player, "🁢🁢🁢🁢"), end="")
			else:
				if b.level == 0:
					print(" "+b.icon+"  ", end ="")
				elif b.level < 10:
					print(" "+b.icon+str(b.level)+" ", end ="")
				else:
					print(" "+b.icon+str(b.level)+"", end ="")
		print("--"+str(h))
		print()
	print()	
	
def requestinput(unit, prompt):
	printmap(unit)
	i = input(prompt+'\n>>> ')
	i = i.lower()
	if i in debug_Words:
		debug(i)
		return i
	if i == "":
		return " "
		
	else:
		return i
	
def AI():
	# For AI in civs list, performs a turn
	# Random for now but in theory should 'seek' player/other AI units.
	for civ in c_List:
		if civ == c_Player:
			None
		else:
			print()
			print("--------------------"+civ.name+"--------------------")
			for city in civ.cities_List:
				if randint(0, unit_spawn_rarity-1) == 0:
					spawnunit(civ, city, 1)
			for unit in civ.units_List:
				# For each unit, aims itself at the closest enemy.
				# If this move is blocked, it picks a new random direction.
				# If 10 consecutive moves fail, it is deemed to be stuck and rests.
				ai_aim = AIaim(unit)
				whoopsie_counter = 0
				while move(unit, ai_aim,1,1):
					ai_aim = move_Words[randint(0,len(move_Words)-2)]
					whoopsie_counter += 1
					print("AI did a whoopsie.")
					if whoopsie_counter > 10:
						ai_aim = move_Words[4]
	return 0
	
def AIaim(red):
	red_pos = red.position
	grid_distance = 100
	closest = p_Null
	for civ in c_List:
		if civ is not red.owner:
			for blu in (civ.units_List + civ.cities_List):
				candidate = get_target(red,blu)
				grid_distance_candidate = abs(candidate.x)+abs(candidate.y)
				if grid_distance_candidate <= grid_distance:
					grid_distance = grid_distance_candidate
					closest = candidate
	if closest == p_Null:
		return move_Words[4]	
	if closest.x == 0:
		# in x alignment
		if closest.y > 0:
			return move_Words[2]
		else:
			return move_Words[0]
	elif closest.y == 0:
		# in y alignment
		if closest.x > 0:
			return move_Words[1]
		else:
			return move_Words[3]
	if abs(closest.x) >= abs(closest.y):
	# if unit is farther laterally than longitudinally
		if closest.x > 0:
			return move_Words[1]
		else:
			return move_Words[3]
	else:
		if closest.y > 0:
			return move_Words[2]
		else:
			return move_Words[0]

		for blu in civ.cities_List:
			if blu.owner is not red.owner:
				blu_pos = blu.position
				print("City detected at "+locstring(blu))
	print("Nothing found. Something went wrong.")			
	return move_Words[4]
				
def get_target(red, blu):
	x_distance = blu.position.x - red.position.x
	rel_pos = Position(blu.position.x-red.position.x, blu.position.y-red.position.y)
	return rel_pos
	
def playerloop():
	# Cycles through player's units and cities and asks them to perform an
	# action.
	print()
	for civ in c_List:
		print(civ.name+"------ "+str(calculate_score(civ)[0])+"/"+str(calculate_score(civ)[1]))
		for unit in civ.units_List:
			print(" >   "+locstring(unit)+" - "+str(unit.health - unit.dmg)+" - "+unit.name)
		for city in civ.cities_List:
			print(" >>> "+locstring(city)+" - "+str(city.health - city.dmg)+" - "+city.name)
	print()	
	if turns == 1:
		initmessage()
	print("Turn "+str(turns)+"/"+str(int(turns_limit)))
	print("\nThe sun rises.\n")
	print("--------------------"+c_Player.name+"--------------------")
	if len(c_Player.units_List)==0:
		i = requestinput(None,"You have no more units. Press enter to wait for a new spawn.")
		if i == "t":
			return 0
	for city in c_Player.cities_List:
		if randint(0, unit_spawn_rarity-1) == 0:
			spawnunit(c_Player, city)	
		
	for unit in c_Player.units_List:
		print()
		i = requestinput(unit, namestr(unit)+" {"+str(unit.level)+"} "+locstring(unit) + " needs an order.").lower()
		if i == "t":
			return 0
		while move(unit, i):
			i = requestinput(unit,"Try again.")
	return 0
	
def mainloop():	
	# does a heckin turn. then announces it
	global turns
	turns += 1
	playerloop()
	if (matrixscan()):

		print()
		return 1
	AI()
	return 0
	
def calculate_score(civ):
	score = 0
	unit_points = 0
	city_points = 0
	for unit in civ.units_List:
		unit_points += (unit.health - unit.dmg)
		
	#if len(civ.units_List) == 0:
	#	unit_points = 0
	#else: 
	#	unit_points = unit_points/len(civ.units_List)
		
	for city in civ.cities_List:
		city_points += (city.health - city.dmg)	
		
	#if len(civ.cities_List) == 0:
	#	city_points = 0
	#else: 
	#	city_points = (city_points/len(civ.cities_List))/2
		
	civ.score = int(unit_points) + int(city_points)	
	return [int(unit_points), int(city_points)]
	
def matrixscan(debug=0):
	if debug=="debug":
		return 0
	winner = c_Player
	highscore = c_Player
	game_over = 0
	active_players = []
	landed_players = []
	global matrix
	for civ in c_List:
		civ.score = sum(calculate_score(civ))
		if civ.score <= 0:
			c_List.remove(civ)
		elif civ.score > highscore.score:
			highscore = civ
			
	score_list = []
	for civ in c_List:
		score_list.append(civ.score)
	score_list.sort(reverse = True)
	if score_list[0] >= score_threshold*score_list[1]*100:
		winner = highscore
		game_over = 1
		congratulations(winner, "score")
		return 1
	elif turns > turns_limit:
		winner = highscore
		game_over = 1
		congratulations(winner, "time")
		return 1
	
	unit_count = 0
	for civ in c_List:
		if len(civ.units_List) > 0:
			active_players.append(civ)
		else:
			if civ in active_players:
				active_players.remove(civ)
		if len(civ.cities_List) > 0:
			landed_players.append(civ)
		else:
			if civ in landed_players:
				landed_players.remove(civ)
		
	if len(landed_players) == 1:
		try:
			winner = landed_players[0]
		except IndexError as error:
			winner = highscore
		game_over = 1
		congratulations(winner, "domination")
		return 1
	
	if len(active_players) == 1:
		try:
			winner = active_players[0]
		except IndexError as error:
			winner = highscore
		game_over = 1
		congratulations(winner, "elimination")
		return 1
			
		
def congratulations(winner, reason):
	print()
	print("-----------------------=== Game over. ===------------------------")
	print("--------------------Your score was "+str(calculate_score(c_Player))+"--------------------")
	print("--------------------=== Hope you enjoyed! ===--------------------")
	print()
	print(str(winner.name)+" wins by "+reason+".")	
	if winner is not c_Player:
		print("Even the best leaders make mistakes sometimes.")
	print(winner.name+"'s total score was "+str(winner.score)+".")
	print(winner.name+" had "+str(len(winner.units_List))+" units remaining.")
	print(winner.name+" had "+str(len(winner.cities_List))+" cities remaining.")
	print(winner.name+" destroyed "+str(winner.units_destroyed)+" units.")
	print(winner.name+" captured "+str(winner.cities_captured)+" cities.")
	
	
		
debug_Words = ["k","t"]	
move_Words = ["w", "d", "s", "a", " "]
df = "Debug flag======================="

								## STACK BASE ##
								
def mainfunc():
	setup()
	while mainloop() == 0:
		None
	return 0
		
mainfunc()