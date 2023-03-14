import pygame 
from settings import *

class Tile(pygame.sprite.Sprite):
	def __init__(self, pos, groups, sprite_type, surface = pygame.Surface((TILESIZE, TILESIZE))):
		super().__init__(groups) # call constructor on Sprite
		self.sprite_type = sprite_type
		self.y_offset = HITBOX_OFFSET[sprite_type]
		self.image = surface
		if sprite_type == 'object': # object is bigger then 64 by 64 so we have to adjust where they go
			# do an offset
			# larger objects are twice as high as TILESIZE
			self.rect = self.image.get_rect(topleft = (pos[0], pos[1] - TILESIZE))
		else:
			self.rect = self.image.get_rect(topleft = pos)

		# inflate takes a rectangle and changes it's size, but keeps it same centr
		# takes x and y as parameters, we want to squish our y a bit
		# -10 will shrink on y axis by 5 on each side
		self.hitbox = self.rect.inflate(0, self.y_offset) 