import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade

class Level:
	def __init__(self):
		# get display surface from anywhere in our code
		self.display_surface = pygame.display.get_surface()
		self.game_paused = False

		# Sprite Group Setup
		#self.visible_sprites = pygame.sprite.Group()
		self.visible_sprites = YSortCameraGroup()
		self.obstacles_sprites = pygame.sprite.Group()

		# attack sprites
		self.current_attack = None
		# weapons will go into attack srpites, enemies in attackable sprites
		# then we can check for collisions between the two
		self.attack_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()

		# sprite setup
		self.create_map()

		# User Interface
		self.ui = UI()
		self.upgrade = Upgrade(self.player)

		# Particles
		self.animation_player = AnimationPlayer()
		self.magic_player = MagicPlayer(self.animation_player)

	def create_map(self):
		layout = {
			'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
			'grass': import_csv_layout('../map/map_Grass.csv'),
			'object': import_csv_layout('../map/map_LargeObjects.csv'),
			'entities': import_csv_layout('../map/map_Entities.csv')
		}

		graphics = {
			'grass': import_folder('../graphics/grass'),
			'objects': import_folder('../graphics/objects')
		}

		for style, layout in layout.items():
			for row_index, row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x, y), [self.obstacles_sprites], 'invisible')
						if style == 'grass':
							random_grass_image = choice(graphics['grass']) # randomly pick one of the grass images
							Tile(
								(x, y), 
								[self.visible_sprites, self.obstacles_sprites, self.attackable_sprites], 
								'grass', 
								random_grass_image
							)
						if style == 'object':
							# graphics['objects] returns a list so we can get the index of that list using col as the index
							surf = graphics['objects'][int(col)] # col is a string, so convert to an integer
							Tile((x, y), [self.visible_sprites, self.obstacles_sprites], 'object', surf)
						if style == 'entities':
							if col == '394':
								self.player = Player(
									(x, y), 
									[self.visible_sprites], 
									self.obstacles_sprites, 
									self.create_attack, 
									self.destroy_attack,
									self.create_magic
								)
							else:
								if col == '390':
									monster_name = 'bamboo'
								elif col == '391':
									monster_name = 'spirit'
								elif col == '392':
									monster_name = 'raccoon'
								else:
									monster_name = 'squid'
								Enemy(
									monster_name, 
									(x, y), 
									[self.visible_sprites, self.attackable_sprites], 
									self.obstacles_sprites,
									self.damage_player,
									self.trigger_death_particles,
									self.add_xp
								)

	def create_attack(self):
		self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

	def create_magic(self, style, strength, cost):
		if style == 'heal':
			self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

		if style == 'flame':
			self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				# Third argument is boolean to let pygame know if collision should kill sprite or not
				collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if target_sprite.sprite_type == 'grass':
							pos = target_sprite.rect.center
							offset = pygame.math.Vector2(0, 75)
							for leaf in range(randint(3, 6)):
								self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
							target_sprite.kill()
						else:
							target_sprite.get_damage(self.player, attack_sprite.sprite_type)

	def damage_player(self, amount, attack_type):
		if self.player.vulnerable:
			self.player.health -= amount
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
			self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

	def trigger_death_particles(self, pos, particle_type):
		self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])

	def add_xp(self, amount):
		self.player.exp += amount

	def toggle_menu(self):
		self.game_paused = not self.game_paused

	def run(self):
		# Update and draw the game
		#self.visible_sprites.draw(self.display_surface)
		self.visible_sprites.custom_draw(self.player)
		self.ui.display(self.player)

		if self.game_paused:
			self.upgrade.display()
		else:
			self.visible_sprites.update()
			self.visible_sprites.enemy_update(self.player)
			self.player_attack_logic()

# Making this class to make a custom group and change functionality of the groups
class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):
		# general setup
		super().__init__()
		self.display_surface = pygame.display.get_surface()

		# get middle of screen, [0] is x, [1] is y...  and // 2 means floor by 2 to get an integer
		self.half_width = self.display_surface.get_size()[0]  // 2
		self.half_height = self.display_surface.get_size()[1]  // 2

		# offset is used to move world so we can move to parts not visible on screen
		self.offset = pygame.math.Vector2() # default if x: 0, y: 0, is offset of entire screen

		# Creating the floor
		self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0, 0))

	# we want player in middle of screen and screen moves instead of player
	def custom_draw(self, player):
		# getting the offset
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		# Drawing the floor
		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf, floor_offset_pos)
		
		#for sprite in self.sprites():
		# want player to be behind rock when on top, and the rock to be behind player when player is below
		# sort sprites by y position and loop through those sorted sprites
		# so we are basically drawing to the screen in order of y position
		for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_pos)

	def enemy_update(self, player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)