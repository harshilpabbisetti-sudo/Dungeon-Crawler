import pygame
from settings import *
from support import get_abs_path


class End:
    def __init__(self, message, final_time=None):

        # setup
        self.display_surf = pygame.display.get_surface()

        # overlay image
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255.0
        self.fade_speed = 150.0

        # text setup
        self.font = pygame.font.Font(get_abs_path('font/Pixeltype.ttf'), 300)
        self.sub_font = pygame.font.Font(get_abs_path('font/Pixeltype.ttf'), 50)
        
        if message == 'win':
            self.text = self.font.render('You Won', False, 'Green')
        elif message == 'lost':
            self.text = self.font.render('You Lost', False, 'Red')
        else:
            self.text = self.font.render('error message', False, 'White')

        self.text_rect = self.text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        
        # Subtext
        self.restart_text = self.sub_font.render('Press SPACE to Restart', False, 'White')
        self.restart_rect = self.restart_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150))

        # Time Text
        self.time_text = None
        if final_time:
            self.time_text = self.sub_font.render(f'Time: {final_time}', False, 'White')
            self.time_rect = self.time_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 210))
        
        # Alpha for text fade-in
        self.text_alpha = 0
        self.text_fade_speed = 200.0

    def run(self, dt):
        # 1. Fade the screen to black
        if self.color > 0:
            self.color -= self.fade_speed * dt
            if self.color < 0: self.color = 0
        
        # Draw overlay
        c = int(self.color)
        self.image.fill((c, c, c))
        self.display_surf.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # 2. Fade in the text once screen is dark enough
        if self.color <= 100:
            if self.text_alpha < 255:
                self.text_alpha += self.text_fade_speed * dt
                if self.text_alpha > 255: self.text_alpha = 255
            
            # Create a copy of text to apply alpha
            self.text.set_alpha(int(self.text_alpha))
            self.restart_text.set_alpha(int(self.text_alpha))
            if self.time_text:
                self.time_text.set_alpha(int(self.text_alpha))
            
            self.display_surf.blit(self.text, self.text_rect)
            self.display_surf.blit(self.restart_text, self.restart_rect)
            if self.time_text:
                self.display_surf.blit(self.time_text, self.time_rect)

