import pygame
from settings import *
from support import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        self.import_assets()
        self.status = "Down_Idle"
        self.frame_index = 0

        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

    def import_assets(self):
        self.animations = {"Down": [], "Up": [], "Right": [], "Left": [],
                           "Down_Idle": [], "Up_Idle": [], "Right_Idle": [], "Left_Idle": [],
                           "Down_Run": [], "Up_Run": [], "Right_Run": [], "Left_Run": []}

        for animation in self.animations.keys():
            full_path = f'graphics/Player/{animation}.png'
            self.animations[animation] = load_and_scale_sprite_sheet(full_path, 64, 64, 2)

    def input(self):
        self.speed = 200
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'Up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'Down'
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'Right'
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'Left'
        else:
            self.direction.x = 0

    def move(self, dt):
        # normalizing a vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y

    def get_status(self):
        keys = pygame.key.get_pressed()
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_Idle'
        elif keys[pygame.K_LALT]:
            self.speed = 300
            self.status = self.status.split('_')[0] + '_Run'

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def update(self, dt):
        self.input()
        self.get_status()

        self.move(dt)
        self.animate(dt)
