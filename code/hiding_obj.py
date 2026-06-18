import pygame
from support import load_and_upscale_sprite, get_abs_path
from settings import *
import os

class Hiding_Obj(pygame.sprite.Sprite):
	def __init__(self, graphic_type, pos, groups):
		super().__init__(groups)
		
		# graphics
		self.graphic_type = graphic_type
		self._import_graphics()

		# general setup
		self.image = self.floor_graphics['open']
		self.rect = self.image.get_rect(topleft=pos)
		self.has_player = False
		self.z = Z_LAYER['main']

	def update(self, dt):
		if(self.has_player):
			self.image = self.floor_graphics['close']
		else:
			self.image = self.floor_graphics['open']

	def _import_graphics(self):
		self.floor_graphics = {}
		keys = ['open', 'close']
		scale = TILE_SET_CONFIG[TILE_SET]['scale']
		for key in keys:
			path = f'graphics/{TILE_SET}/hiding/{self.graphic_type}/{key}.png'
			# Fallback to map1 if current theme doesn't have the graphic
			if not os.path.exists(get_abs_path(path)):
				path = f'graphics/map1/hiding/{self.graphic_type}/{key}.png'
			self.floor_graphics[key] = load_and_upscale_sprite(path, scale)
