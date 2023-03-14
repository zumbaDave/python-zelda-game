import pygame
from math import sin

class Entity(pygame.sprite.Sprite):

    def __init__(self, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.14
        self.direction = pygame.math.Vector2() # default is x: 0, y: 0

    def move(self, speed):
		# if moving diagnolly, speed is faster, but we don't want that
		#    this is because of trigonometry
		# so we have to normalize the direction
		# so if vector has a length, then we normalize it by setting it to 1
		# a vector of 0 cannot be normalized, so we have to check to make sure 
		#    that we don't try to normalize a vector of 0
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

            self.hitbox.x += self.direction.x * speed
            self.collision('horizontal')

            self.hitbox.y += self.direction.y * speed
            self.collision('vertical')
            self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # we are moving right
                        self.hitbox.right = sprite.hitbox.left # make the right side of player to be no further then left side of obstacle
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # moving down 
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0: 
            return 255
        else:
            return 0
