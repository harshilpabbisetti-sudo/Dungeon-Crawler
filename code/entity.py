import pygame
from settings import *

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, grid):
        super().__init__(groups)
        
        # Graphics setup
        self.frame_index = 0
        self.facing = 'Down'
        self.status = 'Idle'
        self.animations = {}
        
        # Movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(pos)
        self.speed = 200
        
        # Collision
        self.grid = grid
        self.is_blocked = False

    def move(self, dt):
        # Normalizing vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Save old position to check for blocking
        old_pos = self.pos.copy()

        # Horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # Vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

        # Check if we are blocked (movement was negligible)
        # Using a tiny epsilon to handle float precision
        if (self.pos - old_pos).magnitude() < 0.1 and self.direction.magnitude() > 0:
            self.is_blocked = True
        else:
            self.is_blocked = False

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
                            if self.direction.x > 0: # Moving right
                                self.hitbox.right = tile_rect.left
                            if self.direction.x < 0: # Moving left
                                self.hitbox.left = tile_rect.right
                            self.rect.centerx = self.hitbox.centerx
                            self.pos.x = self.hitbox.centerx

                        if direction == 'vertical':
                            if self.direction.y > 0: # Moving down
                                self.hitbox.bottom = tile_rect.top
                            if self.direction.y < 0: # Moving up
                                self.hitbox.top = tile_rect.bottom
                            self.rect.centery = self.hitbox.centery
                            self.pos.y = self.hitbox.centery

    def animate(self, dt):
        animation_key = f'{self.facing}_{self.status}'
        if animation_key not in self.animations: return

        if self.direction.magnitude() > 0 and not self.is_blocked:
            self.frame_index += 6 * dt
            if self.frame_index >= len(self.animations[animation_key]):
                self.frame_index = 0
        else:
            self.frame_index = 0

        self.image = self.animations[animation_key][int(self.frame_index)]
