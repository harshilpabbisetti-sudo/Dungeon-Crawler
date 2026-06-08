import pygame
from settings import *
from support import *
from entity import Entity
from timer import Timer

Vector = pygame.math.Vector2


class Player(Entity):
    def __init__(self, pos, group, dungeon, hideable_sprites):
        super().__init__(pos, group, dungeon.grid)

        self.import_assets()
        self.status = "Idle"
        self.facing = "Down"

        # general setup
        self.image = self.animations[f'{self.facing}_{self.status}'][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(0, 0, 25, 50)
        self.hitbox.center = self.rect.center
        self.hideable_sprites = hideable_sprites

        # combat attributes
        self.attacking = False
        self.sound_radius = 0

        # exit
        exit_pos = dungeon.rooms[-1]['center']
        self.exit_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        self.exit_rect.center = (exit_pos[0] * TILE_SIZE, exit_pos[1] * TILE_SIZE)

        # end
        self.end_status = None

        # hiding
        self.hid = False

        # timer
        self.key_timer = Timer(500)

    def import_assets(self):
        self.animations = {}
        directions = ['Down', 'Up', 'Left', 'Right']
        states = ['Idle', 'Run', 'Slice', 'Pierce', 'Death']

        for direction in directions:
            for state in states:
                full_path = f'graphics/Player/{direction}_{state}.png'
                # Frames are likely 64x64 based on earlier check
                self.animations[f'{direction}_{state}'] = load_and_scale_sprite_sheet(full_path, 64, 64, 2)

    def hiding(self):
        collided_sprite = pygame.sprite.spritecollideany(self, self.hideable_sprites)
        if collided_sprite:
            self.hid = not self.hid
            collided_sprite.has_player = not collided_sprite.has_player
            self.pos = Vector(collided_sprite.rect.center)
            self.direction = Vector(0, 0)


    def input(self, keys):
        # hiding
        if keys[pygame.K_f] and not self.key_timer.active:
            self.hiding()
            self.key_timer.activate()
        self.key_timer.update()

        # movement
        if not self.attacking and not self.hid:
            self.speed = 200
            
            # Movement input
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.facing = 'Up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.facing = 'Down'
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.facing = 'Right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.facing = 'Left'
            else:
                self.direction.x = 0

            # Attack input
            if keys[pygame.K_q]:
                self.attacking = True
                self.direction = pygame.math.Vector2() # Stop moving
                self.frame_index = 0
                self.status = 'Slice'
            elif keys[pygame.K_e]:
                self.attacking = True
                self.direction = pygame.math.Vector2() # Stop moving
                self.frame_index = 0
                self.status = 'Pierce'
        
    def get_status(self, keys):
        if self.attacking:
            return # Status is handled by input/animation logic
            
        if self.direction.magnitude() == 0:
            self.status = 'Idle'
        elif keys[pygame.K_LALT]:
            self.speed = 300
            self.status = 'Run'
        else:
            self.status = 'Run'

    def animate(self, dt):
        animation_key = f'{self.facing}_{self.status}'
        
        # Animation loop
        self.frame_index += 7 * dt
        if self.frame_index >= len(self.animations[animation_key]):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
                self.status = 'Idle'

        self.image = self.animations[animation_key][int(self.frame_index)]

    def update_sound_radius(self):
        if self.attacking:
            self.sound_radius = SOUND_RADIUS['attack']
        elif self.status == 'Run':
            if self.speed == 300: # Running with LALT
                self.sound_radius = SOUND_RADIUS['run']
            else: # Normal walking
                self.sound_radius = 100
        else:
            self.sound_radius = 0

    def game_end(self):
        if self.exit_rect.colliderect(self.hitbox):
            self.end_status = 'win'

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.input(keys)
        self.get_status(keys)

        if not self.attacking:
            self.move(dt)
        
        self.animate(dt)
        self.update_sound_radius()
        self.game_end()