import pygame
from player import Player
from settings import *


class Level:
	def __init__(self):
		# get the display surface
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()

		self.setup()

	def setup(self):
		self.player = Player((640,360), self.all_sprites)

	def run(self, dt):
		self.display_surface.fill('black')
		self.all_sprites.draw(self.display_surface)
		self.all_sprites.update(dt)

		# debugging
		# for sprite in self.all_sprites.sprites():
		# 	pygame.draw.rect(self.display_surface, 'red', sprite.rect, 3)
		# 	pygame.draw.rect(self.display_surface, 'blue', sprite.image.get_bounding_rect(), 5)

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()

	def custom_draw(self, player):
		for sprite in self.sprites():
			self.display_surface.blit(sprite.image, sprite.rect)
