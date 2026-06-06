import pygame
from settings import *
from support import get_abs_path


class End:
    def __init__(self, message):

        # setup
        self.display_surf = pygame.display.get_surface()

        # overlay image
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

        # text
        self.font = pygame.font.Font(get_abs_path('font/Pixeltype.ttf'), 300)
        if message == 'win':
            self.text = self.font.render('You Won', False, 'Green')
        elif message == 'lost':
            self.text = self.font.render('You Lost', False, 'Green')
        else:
            self.text = self.font.render('error message', False, 'Green')

        self.text_rect = self.text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT/2))

    def play(self):
        self.image.fill((self.color, self.color, self.color))
        self.display_surf.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        self.color += self.speed
        if self.color <= 0:
            self.color = 0
            self.display_surf.blit(self.text, self.text_rect)
