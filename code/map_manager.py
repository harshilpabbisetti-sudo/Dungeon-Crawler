import pygame
from settings import *
from support import get_abs_path

class MapManager:
	def __init__(self, all_sprites):
		self.all_sprites = all_sprites
		self.load_floor_graphics()

	def load_floor_graphics(self):
		self.floor_graphics = {}
		keys = ['t', 'b', 'l', 'r', 'tl', 'tr', 'bl', 'br', 'white', 'blue', 'exit']
		for key in keys:
			path = get_abs_path(f'graphics/map/{key}.png')
			surf = pygame.image.load(path).convert_alpha()
			self.floor_graphics[key] = pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))

	def create_map(self, grid, dungeon):
		grid_width = len(grid[0])
		grid_height = len(grid)
		
		# 1. Create one huge surface for the entire floor
		full_width = grid_width * TILE_SIZE
		full_height = grid_height * TILE_SIZE
		floor_surface = pygame.Surface((full_width, full_height))
		floor_surface = pygame.Surface((full_width, full_height), pygame.SRCALPHA)
		
		# 2. Blit all floor tiles onto the huge surface
		for row_index, row in enumerate(grid):
			for col_index, cell in enumerate(row):
				if cell == 0: # Floor
					x = col_index * TILE_SIZE
					y = row_index * TILE_SIZE
					
					# Determine which graphic to use based on neighbors
					# 1: top, 2: right, 4: bottom, 8: left
					mask = 0
					if row_index > 0 and grid[row_index - 1][col_index] == 1: mask += 1
					if col_index < grid_width - 1 and grid[row_index][col_index + 1] == 1: mask += 2
					if row_index < grid_height - 1 and grid[row_index + 1][col_index] == 1: mask += 4
					if col_index > 0 and grid[row_index][col_index - 1] == 1: mask += 8

					mapping = {
						0: 'white', # Inner floor
						1: 't', 
						2: 'r',
						4: 'b',
						8: 'l',
						3: 'tr',
						6: 'br',
						12: 'bl',
						9: 'tl'
					}
					
					# Default to white if complex corner or isolated tile
					graphic_key = mapping.get(mask, 'white')
					floor_surface.blit(self.floor_graphics[graphic_key], (x, y))

					if dungeon.rooms[-1]['center'] == (col_index, row_index):
						floor_surface.blit(self.floor_graphics['exit'], (x, y))

		return floor_surface
