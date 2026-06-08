import pygame
import random
import math
from settings import *
from dungeon_gen import DungeonGenerator
from map_manager import MapManager
from player import Player
from monster import Monster
from debug import *
from hiding_obj import Hiding_Obj

class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()
		self.hideable_sprite = pygame.sprite.Group()

		# setup
		self.dungeon = DungeonGenerator(50, 50)
		self.grid = self.dungeon.generate()
		self.static_edges = self.dungeon.get_static_edges()
		self.map_manager = MapManager(self.all_sprites)
		
		# create the ground
		self.all_sprites.floor_surface = self.map_manager.create_map(self.grid, self.dungeon)

		# spawn player in the center of the first room
		if self.dungeon.rooms:
			# spawn player
			spawn_x, spawn_y = self.dungeon.rooms[0]['center']
			self.player = Player((spawn_x * TILE_SIZE, spawn_y * TILE_SIZE), self.all_sprites, self.dungeon, self.hideable_sprite)

			# spawn monsters and sprites to hide into in other rooms
			monster_types = ['wolf', 'goblin']
			for room in self.dungeon.rooms[1:]:
				# hideable
				center_x, center_y = room['center']
				Hiding_Obj('barrel', (center_x * TILE_SIZE, center_y * TILE_SIZE), [self.all_sprites, self.hideable_sprite])

				# monsters
				if random.choice([True, False]):
					monster_type = random.choice(monster_types)
					for _ in range(random.randint(2, 6)):

						dx = random.randint(-1, 1)
						dy = random.randint(-1, 1)
						grid_x = center_x + dx
						grid_y = center_y + dy
						if 0 <= grid_x < len(self.grid[0]) and 0 <= grid_y < len(self.grid):
							if self.grid[grid_y][grid_x] == 0:
								monster_pos = (grid_x * TILE_SIZE, grid_y * TILE_SIZE)
								Monster(monster_pos, self.all_sprites, self.grid, monster_type, self.static_edges)

	def run(self, dt):
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		self.all_sprites.update(dt)
		self.check_sound_propagation()

	def check_sound_propagation(self):
		if self.player.sound_radius > 0:
			for sprite in self.all_sprites.sprites():
				if isinstance(sprite, Monster):
					dist = (pygame.math.Vector2(sprite.rect.center) - pygame.math.Vector2(self.player.rect.center)).magnitude()
					if dist <= self.player.sound_radius:
						sprite.hear_sound(self.player.pos)

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()
		self.floor_surface = None
		self.vision_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

		screen_rect = pygame.Rect(self.offset.x, self.offset.y, SCREEN_WIDTH, SCREEN_HEIGHT)
		self.display_rect = self.display_surface.get_rect()

		if self.floor_surface:
			self.display_surface.blit(self.floor_surface, (0, 0), screen_rect)
		
		self.vision_surf.fill((0, 0, 0, 0))
		if player.sound_radius > 0:
			pygame.draw.circle(self.display_surface, 'gray50', player.rect.center - self.offset, player.sound_radius, 1)

		for sprite in sorted(self.sprites(), key=lambda sprite: (sprite.z, sprite.rect.centery)):
			offset_rect = sprite.rect.copy()
			offset_rect.center -= self.offset
			if self.display_rect.colliderect(offset_rect):
				# for monsters
				if isinstance(sprite, Monster):
					# vision cone
					sprite.vision.draw(self.vision_surf, self.offset)
					if sprite.state == 'INSPECT':
						# inspect sign
						pygame.draw.circle(self.display_surface, 'yellow', (offset_rect.centerx, offset_rect.top - 10), 5)

				# for player
				if isinstance(sprite, Player) and sprite.hid:
					continue
				self.display_surface.blit(sprite.image, offset_rect)

				# # analysis
				# debug_values(player.key_timer.active, True)
		
		self.display_surface.blit(self.vision_surf, (0, 0))
