import pygame
from settings import *

pygame.init()
font = pygame.font.Font(None, 30)


def debug_rect(sprite, player, offset_rect, layers=Z_LAYER.values()):
    if sprite.z in layers:
        display_surface = pygame.display.get_surface()
        pygame.draw.rect(display_surface, 'red', offset_rect, 5)
        hitbox_rect = player.hitbox.copy()
        hitbox_rect.center = offset_rect.center
        pygame.draw.rect(display_surface, 'green', hitbox_rect, 5)


def debug_values(info, bg=False, y=10, x=10):
    display_surf = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, 'black')
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    if bg:
        pygame.draw.rect(display_surf, 'white', debug_rect)
    display_surf.blit(debug_surf, debug_rect)
