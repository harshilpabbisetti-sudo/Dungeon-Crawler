import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
	def __init__(self, pos, groups, surface):
		super().__init__(groups)
		self.image = surface
		self.rect = self.image.get_rect(topleft = pos)

class MapManager:
	def __init__(self, all_sprites, obstacle_sprites):
		self.all_sprites = all_sprites
		self.obstacle_sprites = obstacle_sprites

	def create_map(self, grid):
		grid_width = len(grid[0])
		grid_height = len(grid)
		
		# 1. Create one huge surface for the entire floor
		full_width = grid_width * TILE_SIZE
		full_height = grid_height * TILE_SIZE
		floor_surface = pygame.Surface((full_width, full_height))
		floor_surface.set_colorkey('black') # Make parts without floor transparent
		
		# 2. Create a base tile surface to blit repeatedly
		base_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
		base_tile.fill('gray20')
		# Add a subtle border to see the grid (optional)
		pygame.draw.rect(base_tile, 'gray15', (0, 0, TILE_SIZE, TILE_SIZE), 1)

		# 3. Blit all floor tiles onto the huge surface
		for row_index, row in enumerate(grid):
			for col_index, cell in enumerate(row):
				if cell == 0: # Floor
					x = col_index * TILE_SIZE
					y = row_index * TILE_SIZE
					floor_surface.blit(base_tile, (x, y))

		# 4. Create a single sprite for the entire floor
		# We add it at (0,0) and make sure it's the first in the group so it draws under everything
		Tile((0, 0), [self.all_sprites], floor_surface)
