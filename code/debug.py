import pygame
from settings import *

pygame.init()
font = pygame.font.Font(None, 30)
Vector = pygame.math.Vector2


def debug_rect(sprite, offset, layers=Z_LAYER.values()):
	if sprite.z in layers:
		display_surface = pygame.display.get_surface()
		
		# Draw the image boundary (Rect) in Red
		image_rect = sprite.rect.copy()
		image_rect.center -= offset
		pygame.draw.rect(display_surface, 'red', image_rect, 2)
		
		# Draw the actual collision area (Hitbox) in Green
		if hasattr(sprite, 'hitbox'):
			hitbox_rect = sprite.hitbox.copy()
			hitbox_rect.center -= offset
			pygame.draw.rect(display_surface, 'green', hitbox_rect, 2)


def debug_values(info, bg=False, y=10, x=10):
	display_surf = pygame.display.get_surface()
	debug_surf = font.render(str(info), True, 'black')
	debug_rect = debug_surf.get_rect(topleft=(x, y))
	if bg:
		pygame.draw.rect(display_surf, 'white', debug_rect)
	display_surf.blit(debug_surf, debug_rect)


def path_visualization(sprite, display_surface, offset, show_path=False):
	# Path visualization
	if sprite.path and sprite.path_index < len(sprite.path):
		target_grid = sprite.path[sprite.path_index]
		target_pixel = Vector(target_grid[0] * TILE_SIZE + TILE_SIZE / 2, target_grid[1] * TILE_SIZE + TILE_SIZE / 2)
		pygame.draw.line(display_surface, 'red', sprite.rect.center - offset, target_pixel - offset, 2)
	# Optional: draw the full path points
	if show_path:
		for tg in sprite.path[sprite.path_index:]:
			p = Vector(tg[0] * TILE_SIZE + TILE_SIZE / 2, tg[1] * TILE_SIZE + TILE_SIZE / 2)
			pygame.draw.circle(display_surface, 'blue', p - offset, 3)
