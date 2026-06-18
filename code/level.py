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
from timer import *
from stopwatch import *
import os

Vector = pygame.math.Vector2


class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()
		self.hideable_sprite = pygame.sprite.Group()

		# setup
		self.dungeon = DungeonGenerator(GRID_WIDTH, GRID_HEIGHT)
		self.grid = self.dungeon.generate()
		self.static_edges = self.dungeon.get_static_edges()
		self.map_manager = MapManager()

		# create the ground
		self.all_sprites.floor_surface = self.map_manager.create_map(self.grid, self.dungeon)

		# Fade-in setup
		self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.fade_surface.fill('black')
		self.fade_alpha = 255.0
		self.fade_speed = FADE_SPEED

		# spawn player in the center of the first room
		if self.dungeon.rooms:
			# spawn player
			spawn_x, spawn_y = self.dungeon.rooms[0]['center']
			self.player = Player((spawn_x * TILE_SIZE, spawn_y * TILE_SIZE), self.all_sprites, self.dungeon, self.hideable_sprite, self)

			# spawn monsters and sprites to hide into in other rooms
			monster_types = ['wolf', 'goblin']
			
			# Dynamically discover hideable types from the current TILE_SET
			hiding_path = get_abs_path(f'graphics/{TILE_SET}/hiding')
			
			# Function to get subdirs
			get_types = lambda p: [d for d in os.listdir(p) if os.path.isdir(os.path.join(p, d))] if os.path.exists(p) else []
			
			hideable_types = get_types(hiding_path)
			
			# Fallback to type1 if current theme has no hideables
			if not hideable_types:
				hideable_types = get_types(get_abs_path('graphics/type1/hiding'))

			for room in self.dungeon.rooms[1:]:
				# find valid border positions for hiding objects
				if hideable_types and random.choice([True, False]):  # need hidables or not
					hideable_type = random.choice(hideable_types)

					for _ in range(2):
						if random.choice([True, False]):  # true for top/bottom borders
							pos = (random.randint(room['x'], room['x'] + room['w'] - 1), random.choice([room['y'], room['y'] + room['h'] - 1]))

						else:
							pos = (random.choice([room['x'], room['x'] + room['w'] - 1]), random.randint(room['y'], room['y'] + room['h'] - 1))

						if self.grid[pos[1]+1][pos[0]] or self.grid[pos[1]-1][pos[0]] or self.grid[pos[1]][pos[0]+1] or self.grid[pos[1]][pos[0]-1]:
							Hiding_Obj(hideable_type, (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE), [self.all_sprites, self.hideable_sprite])

				# monsters
				if random.choice([True, False]):
					monster_type = random.choice(monster_types)
					for _ in range(random.randint(2, 6)):
						center_x, center_y = room['center']
						dx = random.randint(-1, 1)
						dy = random.randint(-1, 1)
						grid_x = center_x + dx
						grid_y = center_y + dy
						if 0 <= grid_x < len(self.grid[0]) and 0 <= grid_y < len(self.grid):
							if self.grid[grid_y][grid_x] == 0:
								monster_pos = (grid_x * TILE_SIZE, grid_y * TILE_SIZE)
								Monster(monster_pos, self.all_sprites, self.grid, monster_type, self.static_edges, self.player, self.hideable_sprite)

		# Clock
		self.clock = Clock()

	def run(self, dt):
		self.display_surface.fill(TILE_SET_CONFIG[TILE_SET]['bg color'])
		self.all_sprites.update(dt)

		# # Update fog based on mode (room_based=True reveals whole rooms)
		# self.all_sprites.update_fog(self.player, self.dungeon.rooms, room_based=True)

		self.all_sprites.custom_draw(self.player)

		# Draw and update fade-in overlay
		if self.fade_alpha > 0:
			self.fade_alpha -= self.fade_speed * dt
			if self.fade_alpha < 0: self.fade_alpha = 0
			self.fade_surface.set_alpha(int(self.fade_alpha))
			self.display_surface.blit(self.fade_surface, (0, 0))

		self.clock.display()

	def notify_monsters_of_hiding(self, player_pos):
		for sprite in self.all_sprites:
			if isinstance(sprite, Monster):
				if sprite.vision.check_detection(player_pos):
					sprite.notify_player_hiding()


class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()
		self.floor_surface = None
		self.vision_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
		self.display_rect = self.display_surface.get_rect()

		# Fog of War setup
		self.fog_unexplored = None
		self.fog_dynamic = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

		# Vision mask (Dynamic flashlight)
		self.light_radius = LIGHT_RADIUS
		self.light_mask = pygame.Surface((self.light_radius * 2, self.light_radius * 2), pygame.SRCALPHA)
		self.light_mask.fill((255, 255, 255, 255))
		pygame.draw.circle(self.light_mask, (255, 255, 255, 0), (self.light_radius, self.light_radius), self.light_radius)

	def update_fog(self, player, rooms, room_based=False):
		# Initialize fog map and discovery_radius once floor is ready
		if self.floor_surface and self.fog_unexplored is None:
			self.fog_unexplored = pygame.Surface(self.floor_surface.get_size(), pygame.SRCALPHA)
			self.fog_unexplored.fill((0, 0, 0, 255))

			# Discovery mask (Persistent map reveal)
			# Smaller to prevent bleeding into adjacent rooms through walls
			self.discovery_radius = DISCOVERY_RADIUS_ROOM if room_based else DISCOVERY_RADIUS_FREE
			self.discovery_mask = pygame.Surface((self.discovery_radius * 2, self.discovery_radius * 2), pygame.SRCALPHA)
			self.discovery_mask.fill((255, 255, 255, 255))
			pygame.draw.circle(self.discovery_mask, (255, 255, 255, 0), (self.discovery_radius, self.discovery_radius), self.discovery_radius)

		if self.fog_unexplored:
			if room_based:
				# Find which room the player is in
				player_grid_x = int(player.rect.centerx // TILE_SIZE)
				player_grid_y = int(player.rect.centery // TILE_SIZE)

				for room in rooms:
					if (room['x'] <= player_grid_x < room['x'] + room['w'] and
						room['y'] <= player_grid_y < room['y'] + room['h']):
						# Reveal the entire room (including walls slightly for better visuals)
						room_rect = pygame.Rect(
							(room['x'] - 1) * TILE_SIZE,
							(room['y'] - 1) * TILE_SIZE,
							(room['w'] + 2) * TILE_SIZE,
							(room['h'] + 2) * TILE_SIZE
						)
						pygame.draw.rect(self.fog_unexplored, (255, 255, 255, 0), room_rect)

			# 1. Update persistent map using the SMALLER discovery mask
			# This prevents the map from revealing neighboring rooms through walls
			self.fog_unexplored.blit(self.discovery_mask, (player.rect.centerx - self.discovery_radius, player.rect.centery - self.discovery_radius), special_flags=pygame.BLEND_RGBA_MIN)

			# 2. Update dynamic flashlight (dim visited areas)
			self.fog_dynamic.fill((0, 0, 0, DYNAMIC_FOG_ALPHA))
			self.fog_dynamic.blit(self.light_mask, (player.rect.centerx - self.offset.x - self.light_radius, player.rect.centery - self.offset.y - self.light_radius), special_flags=pygame.BLEND_RGBA_MIN)

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

		screen_rect = pygame.Rect(self.offset.x, self.offset.y, SCREEN_WIDTH, SCREEN_HEIGHT)

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
					elif sprite.state == 'CHASE':
						# chase sign
						pygame.draw.circle(self.display_surface, 'red', (offset_rect.centerx, offset_rect.top - 10), 5)

					# # for path visualization
					# path_visualization(sprite, self.display_surface, self.offset, True)

				# for player
				if isinstance(sprite, Player) and sprite.hid:
					continue
				self.display_surface.blit(sprite.image, offset_rect)

				# # analysis
				# debug_values(player.key_timer.active, True)
				# debug_rect(sprite, player, offset_rect)

		self.display_surface.blit(self.vision_surf, (0, 0))

		# Fog of War Rendering
		if self.fog_unexplored:
			self.display_surface.blit(self.fog_dynamic, (0, 0))
			self.display_surface.blit(self.fog_unexplored, (0, 0), screen_rect)
