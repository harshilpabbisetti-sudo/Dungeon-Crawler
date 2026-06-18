import pygame
import os
from settings import *
from support import load_and_upscale_sprite, get_abs_path

class MapManager:
	def __init__(self):
		self.scale = TILE_SET_CONFIG[TILE_SET]['scale']
		self._load_assets()

	def _load_assets(self):
		# 0: Floor tiles, 1: Wall tiles
		self.graphics = {0: {}, 1: {}} 
		
		# Use the TILE_SET from settings.py to determine the base path
		base_path = os.path.join('graphics', TILE_SET)
		
		# Load from both subdirectories
		for cell_type, folder in [(0, 'floor'), (1, 'wall')]:
			path = os.path.join(base_path, folder)
			abs_path = get_abs_path(path)
			
			# Fallback for walls: if 'wall' folder doesn't exist, look in theme root
			if cell_type == 1 and not os.path.exists(abs_path):
				path = base_path
				abs_path = get_abs_path(path)

			if os.path.exists(abs_path):
				for filename in os.listdir(abs_path):
					if filename.endswith('.png') and filename[:-4].isdigit():
						key = int(filename[:-4])
						self.graphics[cell_type][key] = load_and_upscale_sprite(os.path.join(path, filename), self.scale)

		# Specialty/Fallbacks
		# 1. Exit Tile: Current Theme -> map1 -> Global Map
		exit_path = os.path.join(base_path, 'exit.png')
		if not os.path.exists(get_abs_path(exit_path)):
			exit_path = 'graphics/map1/exit.png'
		if not os.path.exists(get_abs_path(exit_path)):
			exit_path = 'graphics/map/exit.png'

		if os.path.exists(get_abs_path(exit_path)):
			self.graphics[0]['exit'] = load_and_upscale_sprite(exit_path, self.scale)

		# 2. Base Tile (0) Fallback: Current Theme Root -> map1 -> Global Map
		for cell_type in [0, 1]:
			if 0 not in self.graphics[cell_type]:
				fallback_path = os.path.join(base_path, '0.png')
				if not os.path.exists(get_abs_path(fallback_path)):
					fallback_path = 'graphics/map1/0.png'
				if not os.path.exists(get_abs_path(fallback_path)):
					fallback_path = 'graphics/map/0.png'

				if os.path.exists(get_abs_path(fallback_path)):
					self.graphics[cell_type][0] = load_and_upscale_sprite(fallback_path, self.scale)

	def _get_mask(self, grid, col, row, target_type):
		mask = 0
		grid_width = len(grid[0])
		grid_height = len(grid)

		# 1. Cardinal checks: 1=Top, 2=Right, 4=Bottom, 8=Left
		t = row > 0 and grid[row - 1][col] == target_type
		r = col < grid_width - 1 and grid[row][col + 1] == target_type
		b = row < grid_height - 1 and grid[row + 1][col] == target_type
		l = col > 0 and grid[row][col - 1] == target_type

		if t: mask += 1
		if r: mask += 2
		if b: mask += 4
		if l: mask += 8
		
		# 2. Diagonal checks: 16=Top-Right, 32=Bottom-Right, 64=Bottom-Left, 128=Top-Left
		if row > 0 and col < grid_width - 1 and grid[row - 1][col + 1] == target_type: mask += 16
		if row < grid_height - 1 and col < grid_width - 1 and grid[row + 1][col + 1] == target_type: mask += 32
		if row < grid_height - 1 and col > 0 and grid[row + 1][col - 1] == target_type: mask += 64
		if row > 0 and col > 0 and grid[row - 1][col - 1] == target_type: mask += 128
		
		return mask

	def create_map(self, grid, dungeon):
		grid_width = len(grid[0])
		grid_height = len(grid)

		full_width = grid_width * TILE_SIZE
		full_height = grid_height * TILE_SIZE
		map_surface = pygame.Surface((full_width, full_height), pygame.SRCALPHA)

		for row_index, row in enumerate(grid):
			for col_index, cell in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				
				# target_type is the opposite of the current cell
				target_type = 1 if cell == 0 else 0
				full_mask = self._get_mask(grid, col_index, row_index, target_type)

				# Try full 8-bit mask, then fallback to 4-bit cardinal mask, then to 0
				surf = self.graphics[cell].get(full_mask)
				if surf is None:
					cardinal_mask = full_mask & 15
					surf = self.graphics[cell].get(cardinal_mask)
					if surf is None:
						# Special legacy overrides for floors if needed
						if cell == 0:
							if cardinal_mask == 4: cardinal_mask = 0
							if cardinal_mask == 6: cardinal_mask = 2
							if cardinal_mask == 12: cardinal_mask = 8
						surf = self.graphics[cell].get(cardinal_mask, self.graphics[cell].get(0))

				if surf:
					map_surface.blit(surf, (x, y))

				# Exit tile
				if cell == 0 and dungeon.rooms[-1]['center'] == (col_index, row_index):
					map_surface.blit(self.graphics[0]['exit'], (x, y))

		return map_surface
