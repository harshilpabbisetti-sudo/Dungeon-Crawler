import pygame
import random
from settings import *
from support import load_and_scale_sprite_sheet
from timer import Timer

class Monster(pygame.sprite.Sprite):
    def __init__(self, pos, group, grid, monster_type):
        super().__init__(group)
        
        self.monster_type = monster_type
        self.grid = grid
        
        # Graphics setup
        self.facing = 'D'
        self.status = 'Walk'
        self.import_assets()
        self.frame_index = 0
        
        self.image = self.animations[f'{self.facing}_{self.status}'][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(0, 0, 30, 50)
        self.hitbox.center = self.rect.center
        
        # Movement
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 100

        # Timers
        self.timers = {
            'action': Timer(random.randint(1000, 3000), self.change_action)
        }
        self.timers['action'].activate()
        
    def import_assets(self):
        self.animations = {}
        directions = ['D', 'U', 'L', 'R']
        states = ['Walk', 'Attack', 'Death']
        
        for direction in directions:
            for state in states:
                full_path = f'graphics/Monsters/{self.monster_type}/{direction}_{state}.png'
                # Frames are 48x48 according to earlier check
                self.animations[f'{direction}_{state}'] = load_and_scale_sprite_sheet(full_path, 48, 48, 2)
            
    def change_action(self):
        # 30% chance to stand still, 70% chance to pick a random direction
        if random.random() < 0.3:
            self.direction.x = 0
            self.direction.y = 0
        else:
            self.direction.x = random.choice([-1, 0, 1])
            self.direction.y = random.choice([-1, 0, 1])
            
        # Reset the timer with a new random duration
        self.timers['action'].duration = random.randint(1000, 3000)
        self.timers['action'].activate()

    def get_status(self):
        if self.direction.x > 0: self.facing = 'R'
        elif self.direction.x < 0: self.facing = 'L'
        elif self.direction.y > 0: self.facing = 'D'
        elif self.direction.y < 0: self.facing = 'U'

        # Note: status could be changed to 'Attack' or 'Death' later by game logic
        # For now we only have movement logic

    def animate(self, dt):
        animation_key = f'{self.facing}_{self.status}'
        
        # If moving, animate. If stationary, stay on frame 0
        if self.direction.magnitude() > 0:
            self.frame_index += 6 * dt
            if self.frame_index >= len(self.animations[animation_key]):
                self.frame_index = 0
        else:
            self.frame_index = 0
            
        self.image = self.animations[animation_key][int(self.frame_index)]

    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

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
                            if self.direction.x > 0: self.hitbox.right = tile_rect.left
                            if self.direction.x < 0: self.hitbox.left = tile_rect.right
                            self.rect.centerx = self.hitbox.centerx
                            self.pos.x = self.hitbox.centerx
                        if direction == 'vertical':
                            if self.direction.y > 0: self.hitbox.bottom = tile_rect.top
                            if self.direction.y < 0: self.hitbox.top = tile_rect.bottom
                            self.rect.centery = self.hitbox.centery
                            self.pos.y = self.hitbox.centery

    def update(self, dt):
        for timer in self.timers.values():
            timer.update()

        self.get_status()
        self.animate(dt)
        self.move(dt)
