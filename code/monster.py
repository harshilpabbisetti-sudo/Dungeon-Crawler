import pygame
import random
from settings import *
from support import load_and_scale_sprite_sheet
from timer import Timer
from entity import Entity
from astar import get_path

class Monster(Entity):
    def __init__(self, pos, group, grid, monster_type):
        super().__init__(pos, group, grid)
        
        self.monster_type = monster_type

        # state
        self.state = 'ROAM'
        self.path = []
        self.path_index = 0
        
        # Graphics
        self.status = 'Walk'
        self.import_assets()
        self.image = self.animations[f'{self.facing}_{self.status}'][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(0, 0, 30, 50)
        self.hitbox.center = self.rect.center
        
        # Movement
        self.speed = 100

        # Timers
        self.timers = {
            'action': Timer(random.randint(1000, 3000), self.change_action),
            'hear_cooldown': Timer(2000)
        }
        self.timers['action'].activate()

    def import_assets(self):
        self.animations = {}
        # Mapping from file prefix to Entity direction
        directions = {'D': 'Down', 'U': 'Up', 'L': 'Left', 'R': 'Right'}
        states = ['Walk', 'Attack', 'Death']
        
        for prefix, direction in directions.items():
            for state in states:
                full_path = f'graphics/Monsters/{self.monster_type}/{prefix}_{state}.png'
                self.animations[f'{direction}_{state}'] = load_and_scale_sprite_sheet(full_path, 48, 48, 2)
            
    def change_action(self):
        if self.state != 'ROAM': return

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
        if self.direction.magnitude() == 0:
            pass # Keep last facing
        elif abs(self.direction.x) > abs(self.direction.y):
            # Moving more horizontally
            if self.direction.x > 0: self.facing = 'Right'
            else: self.facing = 'Left'
        else:
            # Moving more vertically
            if self.direction.y > 0: self.facing = 'Down'
            else: self.facing = 'Up'

    def hear_sound(self, sound_pos):
        if self.timers['hear_cooldown'].active: return

        # Convert pixel pos to grid pos
        start_grid = (int(self.rect.centerx // TILE_SIZE), int(self.rect.centery // TILE_SIZE))
        end_grid = (int(sound_pos[0] // TILE_SIZE), int(sound_pos[1] // TILE_SIZE))

        # Calculate path
        new_path = get_path(self.grid, start_grid, end_grid)
        if new_path:
            self.state = 'INSPECT'
            self.path = new_path
            self.path_index = 0
            self.timers['action'].deactivate()
            self.timers['hear_cooldown'].activate()

    def follow_path(self):
        if not self.path or self.path_index >= len(self.path):
            self.state = 'ROAM'
            self.path = []
            self.direction = pygame.math.Vector2() # Force stop when reaching target
            self.timers['action'].activate()
            return

        target_grid = self.path[self.path_index]
        target_pixel = pygame.math.Vector2(target_grid[0] * TILE_SIZE + TILE_SIZE / 2,
                                           target_grid[1] * TILE_SIZE + TILE_SIZE / 2)

        # Direction to next path node
        self.direction = target_pixel - self.pos
        if self.direction.magnitude() > 5:
            self.direction = self.direction.normalize()
        else:
            self.path_index += 1

    def update(self, dt):
        for timer in self.timers.values():
            timer.update()

        if self.state == 'INSPECT':
            self.follow_path()

        self.get_status()
        self.animate(dt)
        self.move(dt)
