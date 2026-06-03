import pygame
import random
from settings import *
from dungeon_gen import DungeonGenerator
from map_manager import MapManager
from player import Player
from monster import Monster

class Level:
	def __init__(self):
		# get the display surface
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()

		# setup
		self.dungeon = DungeonGenerator(50, 50)
		self.grid = self.dungeon.generate()
		self.map_manager = MapManager(self.all_sprites, self.obstacle_sprites)
		
		# create the ground
		self.all_sprites.floor_surface = self.map_manager.create_map(self.grid)

		# spawn player in the center of the first room
		if self.dungeon.rooms:
			spawn_x, spawn_y = self.dungeon.rooms[0]['center']
			self.player = Player((spawn_x * TILE_SIZE, spawn_y * TILE_SIZE), self.all_sprites, self.grid)

	def run(self, dt):
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		self.all_sprites.update(dt)

		# debugging
		# for sprite in self.all_sprites.sprites():
		# 	pygame.draw.rect(self.display_surface, 'red', sprite.rect, 3)
		# 	pygame.draw.rect(self.display_surface, 'blue', sprite.image.get_bounding_rect(), 5)

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()
		self.floor_surface = None

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

		# Define the screen rect in world coordinates for culling
		screen_rect = pygame.Rect(self.offset.x, self.offset.y, SCREEN_WIDTH, SCREEN_HEIGHT)

		# 1. Draw the floor (only the visible part)
		if self.floor_surface:
			self.display_surface.blit(self.floor_surface, (0, 0), screen_rect)

		# 2. Draw all other sprites (Monsters, etc.) with offset
		for sprite in self.sprites():
			if sprite != player:
				if sprite.rect.colliderect(screen_rect):
					offset_rect = sprite.rect.copy()
					offset_rect.topleft -= self.offset
					self.display_surface.blit(sprite.image, offset_rect)
		
		# 3. Draw player last (on top)
		offset_rect = player.rect.copy()
		offset_rect.topleft -= self.offset
		self.display_surface.blit(player.image, offset_rect)
