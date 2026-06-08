import pygame
from support import load_and_upscale_sprite
from settings import *

class Hiding_Obj(pygame.sprite.Sprite):
	def __init__(self, graphic_type, pos, groups):
		super().__init__(groups)
		self.graphic_type = graphic_type

		self.import_graphics()

		self.image = self.floor_graphics['open']
		self.rect = self.image.get_rect(topleft=pos)
		self.has_player = False
		self.z = Z_LAYER['main']

	def import_graphics(self):
		self.floor_graphics = {}
		keys = ['open', 'close']
		for key in keys:
			path = f'graphics/hiding/{self.graphic_type}/{key}.png'
			self.floor_graphics[key] = load_and_upscale_sprite(path, 4)

	def update(self, dt):
		if(self.has_player):
			self.image = self.floor_graphics['close']
		else:
			self.image = self.floor_graphics['open']