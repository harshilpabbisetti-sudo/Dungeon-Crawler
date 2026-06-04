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
		self.map_manager = MapManager(self.all_sprites)
		
		# create the ground
		self.all_sprites.floor_surface = self.map_manager.create_map(self.grid)

		# spawn player in the center of the first room
		if self.dungeon.rooms:
			spawn_x, spawn_y = self.dungeon.rooms[0]['center']
			self.player = Player((spawn_x * TILE_SIZE, spawn_y * TILE_SIZE), self.all_sprites, self.grid)

			# spawn monsters in other rooms
			monster_types = ['wolf', 'goblin']
			for room in self.dungeon.rooms[1:]:
				if random.choice([True, False]):
					monster_type = random.choice(monster_types)
					for _ in range(random.randint(2, 6)):
						center_x, center_y = room['center']
						dx = random.randint(-2, 2)
						dy = random.randint(-2, 2)
						grid_x = center_x + dx
						grid_y = center_y + dy
						if 0 <= grid_x < len(self.grid[0]) and 0 <= grid_y < len(self.grid):
							if self.grid[grid_y][grid_x] == 0:
								monster_pos = (grid_x * TILE_SIZE, grid_y * TILE_SIZE)
								Monster(monster_pos, self.all_sprites, self.grid, monster_type)

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

		# 2. Draw sound radius (faint circle)
		if player.sound_radius > 0:
			# Subtract offset to draw it in world space relative to camera
			pygame.draw.circle(self.display_surface, 'gray50', player.rect.center - self.offset, player.sound_radius, 1)

		# 3. Draw all other sprites (Monsters, etc.) with offset
		for sprite in self.sprites():
			if sprite != player:
				if sprite.rect.colliderect(screen_rect):
					offset_rect = sprite.rect.copy()
					offset_rect.topleft -= self.offset
					self.display_surface.blit(sprite.image, offset_rect)

					# Visual alert for monsters
					if isinstance(sprite, Monster) and sprite.state == 'INSPECT':
						pygame.draw.circle(self.display_surface, 'yellow', (offset_rect.centerx, offset_rect.top - 10), 5)
		
		# 3. Draw player last (on top)
		offset_rect = player.rect.copy()
		offset_rect.topleft -= self.offset
		self.display_surface.blit(player.image, offset_rect)
