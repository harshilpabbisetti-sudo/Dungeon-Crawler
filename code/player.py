import pygame
from settings import *
from support import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, grid):
        super().__init__(group)

        self.import_assets()
        self.status = "Down_Idle"
        self.frame_index = 0

        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(0, 0, 25, 50)
        self.hitbox.center = self.rect.center

        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # collision
        self.grid = grid

    def import_assets(self):
        self.animations = {"Down": [], "Up": [], "Right": [], "Left": [],
                           "Down_Idle": [], "Up_Idle": [], "Right_Idle": [], "Left_Idle": [],
                           "Down_Run": [], "Up_Run": [], "Right_Run": [], "Left_Run": []}

        for animation in self.animations.keys():
            full_path = f'graphics/Player/{animation}.png'
            self.animations[animation] = load_and_scale_sprite_sheet(full_path, 64, 64, 2)

    def input(self, keys):
        self.speed = 200

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
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def collision(self, direction):
        start_col = max(0, int(self.hitbox.left // TILE_SIZE))
        end_col = min(len(self.grid[0]), int(self.hitbox.right // TILE_SIZE) + 1)
        start_row = max(0, int(self.hitbox.top // TILE_SIZE))
        end_row = min(len(self.grid), int(self.hitbox.bottom // TILE_SIZE) + 1)

        for row_index in range(start_row, end_row):
            for col_index in range(start_col, end_col):
                if self.grid[row_index][col_index] == 1:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

                    if self.hitbox.colliderect(tile_rect):
                        if direction == 'horizontal':
                            if self.direction.x > 0:  # Moving right
                                self.hitbox.right = tile_rect.left
                            if self.direction.x < 0:  # Moving left
                                self.hitbox.left = tile_rect.right
                            self.rect.centerx = self.hitbox.centerx
                            self.pos.x = self.hitbox.centerx

                        if direction == 'vertical':
                            if self.direction.y > 0:  # Moving down
                                self.hitbox.bottom = tile_rect.top
                            if self.direction.y < 0:  # Moving up
                                self.hitbox.top = tile_rect.bottom
                            self.rect.centery = self.hitbox.centery
                            self.pos.y = self.hitbox.centery

    def get_status(self, keys):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_Idle'
        elif keys[pygame.K_LALT]:
            self.speed = 300
            self.status = self.status.split('_')[0] + '_Run'

    def animate(self, dt):
        self.frame_index += 6 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.input(keys)
        self.get_status(keys)

        self.move(dt)
        self.animate(dt)
