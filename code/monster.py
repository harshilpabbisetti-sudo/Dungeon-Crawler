import pygame
import random
import math
from settings import *
from support import load_and_scale_sprite_sheet
from timer import Timer
from entity import Entity
from astar import get_path

class VisionCone:
    def __init__(self, owner, radius, angle, static_edges, hideable_sprites):
        self.owner = owner
        self.radius = radius
        self.angle = angle
        self.static_edges = static_edges
        self.hideable_sprites = hideable_sprites

    def get_edges(self):
        cx, cy = self.owner.rect.center
        r = self.radius + 10 # Buffer
        
        relevant_edges = []
        for p1, p2 in self.static_edges:
            if (cx - r < p1[0] < cx + r and cy - r < p1[1] < cy + r) or (cx - r < p2[0] < cx + r and cy - r < p2[1] < cy + r):
                relevant_edges.append((p1, p2))
                continue
                
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            if dx == 0 and dy == 0: continue
            
            t = ((cx - p1[0]) * dx + (cy - p1[1]) * dy) / (dx*dx + dy*dy)
            if not (0 <= t <= 1):
                continue
            closest_x = p1[0] + t * dx
            closest_y = p1[1] + t * dy

            dist_sq = (cx - closest_x)**2 + (cy - closest_y)**2
            if dist_sq <= r**2:
                relevant_edges.append((p1, p2))

        for sprite in self.hideable_sprites:
            if (pygame.math.Vector2(sprite.rect.center) - pygame.math.Vector2(cx, cy)).magnitude() < r + 100:
                rect = sprite.rect
                relevant_edges.append(((rect.left, rect.top), (rect.right, rect.top)))
                relevant_edges.append(((rect.right, rect.top), (rect.right, rect.bottom)))
                relevant_edges.append(((rect.right, rect.bottom), (rect.left, rect.bottom)))
                relevant_edges.append(((rect.left, rect.bottom), (rect.left, rect.top)))

        return relevant_edges

    def cast_ray(self, angle, edges):
        dx, dy = math.cos(angle), math.sin(angle)
        closest_dist = self.radius
        ox, oy = self.owner.rect.center
        
        for p1, p2 in edges:
            x1, y1 = p1
            x2, y2 = p2
            denominator = (dx * (y2 - y1) - dy * (x2 - x1))
            if abs(denominator) < 0.0001: continue
            t = ((x1 - ox) * (y2 - y1) - (y1 - oy) * (x2 - x1)) / denominator
            u = ((x1 - ox) * dy - (y1 - oy) * dx) / denominator
            if t > 0 and 0 <= u <= 1:
                if t < closest_dist:
                    closest_dist = t
        return ox + dx * closest_dist, oy + dy * closest_dist

    def draw(self, surface, offset):
        angle_map = {'Right': 0, 'Down': 90, 'Left': 180, 'Up': 270}
        base_angle = math.radians(angle_map[self.owner.facing])
        half_fov = math.radians(self.angle / 2)
        edges = self.get_edges()
        cx, cy = self.owner.rect.center
        r_sq = self.radius ** 2
        
        angles = set()
        arc_steps = 20
        for i in range(arc_steps):
            angles.add(base_angle - half_fov + (half_fov * 2 * i) / arc_steps)
        
        for p1, p2 in edges:
            for p in [p1, p2]:
                dist_sq = (p[0] - cx)**2 + (p[1] - cy)**2
                if dist_sq > r_sq + 100: continue
                angle = math.atan2(p[1] - cy, p[0] - cx)
                diff = (angle - base_angle + math.pi) % (2 * math.pi) - math.pi
                if abs(diff) <= half_fov:
                    angles.add(angle)
                    angles.add(angle - 0.0001)
                    angles.add(angle + 0.0001)

        points = []
        for angle in angles:
            points.append(self.cast_ray(angle, edges))

        def sort_by_relative_angle(p):
            angle = math.atan2(p[1] - self.owner.rect.centery, p[0] - self.owner.rect.centerx)
            diff = (angle - base_angle + math.pi) % (2 * math.pi) - math.pi
            return diff

        points.sort(key=sort_by_relative_angle)
        screen_points = [pygame.math.Vector2(self.owner.rect.center) - offset]
        for p in points:
            angle = math.atan2(p[1] - self.owner.rect.centery, p[0] - self.owner.rect.centerx)
            diff = (angle - base_angle + math.pi) % (2 * math.pi) - math.pi
            if abs(diff) <= half_fov + 0.01:
                screen_points.append(pygame.math.Vector2(p) - offset)

        if len(screen_points) > 2:
            if self.owner.state == 'ROAM':
                pygame.draw.polygon(surface, (255, 255, 255, 40), screen_points)
            elif self.owner.state == 'INSPECT':
                pygame.draw.polygon(surface, (241, 196, 15, 50), screen_points)
            else:
                pygame.draw.polygon(surface, (231, 76, 60, 60), screen_points)

    def check_detection(self, target_pos):
        dist_vec = pygame.math.Vector2(target_pos) - self.owner.rect.center
        dist = dist_vec.magnitude()
        if dist > self.radius: return False
            
        angle_map = {'Right': 0, 'Down': 90, 'Left': 180, 'Up': 270}
        base_angle = math.radians(angle_map[self.owner.facing])
        half_fov = math.radians(self.angle / 2)
        target_angle = math.atan2(dist_vec.y, dist_vec.x)
        diff = (target_angle - base_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(diff) > half_fov: return False
            
        dx, dy = math.cos(target_angle), math.sin(target_angle)
        ox, oy = self.owner.rect.center
        relevant_edges = self.get_edges()
        for p1, p2 in relevant_edges:
            x1, y1 = p1
            x2, y2 = p2
            denominator = (dx * (y2 - y1) - dy * (x2 - x1))
            if abs(denominator) < 0.0001: continue
            t = ((x1 - ox) * (y2 - y1) - (y1 - oy) * (x2 - x1)) / denominator
            u = ((x1 - ox) * dy - (y1 - oy) * dx) / denominator
            if t > 0 and 0 <= u <= 1:
                if t < dist - 5: return False
        return True


class Monster(Entity):
    def __init__(self, pos, group, grid, monster_type, static_edges, player, hideable_sprites):
        super().__init__(pos, group, grid)
        self.monster_type, self.player, self.hideable_sprites = monster_type, player, hideable_sprites
        self.state, self.path, self.path_index = 'ROAM', [], 0
        self.status = 'Walk'
        self.import_assets()
        self.image = self.animations[f'{self.facing}_{self.status}'][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(0, 0, 30, 50)
        self.hitbox.center = self.rect.center
        self.speed = 100
        self.player_last_grid_pos = None
        self.forcing_chase = False
        self.timers = {'action': Timer(random.randint(1000, 3000), self.change_action), 'hear_cooldown': Timer(1000)}
        self.timers['action'].activate()
        self.vision = VisionCone(self, VISION_RADIUS, VISION_ANGLE, static_edges, hideable_sprites)

    def import_assets(self):
        self.animations = {}
        directions = {'D': 'Down', 'U': 'Up', 'L': 'Left', 'R': 'Right'}
        states = ['Walk', 'Attack', 'Death']
        for prefix, direction in directions.items():
            for state in states:
                full_path = f'graphics/Monsters/{self.monster_type}/{prefix}_{state}.png'
                self.animations[f'{direction}_{state}'] = load_and_scale_sprite_sheet(full_path, 48, 48, 2)
            
    def change_action(self):
        if self.state == 'CHASE': return
        if random.random() < 0.3: self.direction = pygame.math.Vector2(0, 0)
        else: self.direction = pygame.math.Vector2(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        self.timers['action'].duration = random.randint(1000, 3000)
        self.timers['action'].activate()

    def get_status(self):
        if self.direction.magnitude() == 0: pass
        elif abs(self.direction.x) > abs(self.direction.y) + 0.1:
            self.facing = 'Right' if self.direction.x > 0 else 'Left'
        elif abs(self.direction.y) > abs(self.direction.x) + 0.1:
            self.facing = 'Down' if self.direction.y > 0 else 'Up'

    def follow_path(self):
        if not self.path or self.path_index >= len(self.path):
            self.direction = pygame.math.Vector2(0, 0)
            return True
        target_grid = self.path[self.path_index]
        target_pixel = pygame.math.Vector2(target_grid[0] * TILE_SIZE + TILE_SIZE / 2, target_grid[1] * TILE_SIZE + TILE_SIZE / 2)
        diff = target_pixel - self.pos
        if diff.magnitude() < 15:
            self.path_index += 1
            return self.follow_path()
        self.direction = diff.normalize()
        return False

    def notify_player_hiding(self):
        self.state = 'CHASE'
        self.forcing_chase = True
        self.timers['action'].deactivate()

    def chase_player(self):
        self.speed = 180
        target_grid = (int(self.player.rect.centerx // TILE_SIZE), int(self.player.rect.centery // TILE_SIZE))
        if target_grid != self.player_last_grid_pos:
            start_grid = (int(self.rect.centerx // TILE_SIZE), int(self.rect.centery // TILE_SIZE))
            new_path = get_path(self.grid, start_grid, target_grid)
            if new_path:
                self.path, self.path_index, self.player_last_grid_pos = new_path, 0, target_grid
        self.follow_path()

    def stop_chase(self):
        self.state, self.speed, self.forcing_chase = 'INSPECT', 100, False
        # Path is already pointing to player's last position
        self.timers['action'].deactivate()

    def check_vision(self, player):
        in_vision = self.vision.check_detection(player.pos)

        if not in_vision and not player.hid: 
            self.forcing_chase = False
            
        if in_vision and not player.hid:
            if self.state != 'CHASE':
                self.state = 'CHASE'
                self.timers['action'].deactivate()
        
        if self.state == 'CHASE' and not self.forcing_chase:
            if player.hid and not in_vision:
                self.stop_chase()

    def check_hearing(self, player):
        if self.state == 'CHASE': return
        if player.sound_radius > 0:
            dist = (pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(player.rect.center)).magnitude()
            if dist <= player.sound_radius: self.hear_sound(player.pos)

    def hear_sound(self, sound_pos):
        if self.state == 'CHASE' or self.timers['hear_cooldown'].active: return
        start_grid = (int(self.rect.centerx // TILE_SIZE), int(self.rect.centery // TILE_SIZE))
        end_grid = (int(sound_pos[0] // TILE_SIZE), int(sound_pos[1] // TILE_SIZE))
        new_path = get_path(self.grid, start_grid, end_grid)
        if new_path:
            self.state, self.path, self.path_index = 'INSPECT', new_path, 0
            self.timers['action'].deactivate()
            self.timers['hear_cooldown'].activate()

    def check_player_caught(self, player):
        if self.state == 'CHASE' and self.hitbox.colliderect(player.hitbox):
            if player.hid:
                player.hid = False
                player.hidable_sprite.has_player = False
        if self.hitbox.colliderect(player.hitbox) and not player.hid:
            player.end_status = 'lost'

    def animate(self, dt):
        animation_key = f'{self.facing}_{self.status}'
        if animation_key not in self.animations: return

        # Faster animation for attacking
        speed = 6
        
        if (self.direction.magnitude() > 0 and not self.is_blocked):
            self.frame_index += speed * dt
            if self.frame_index >= len(self.animations[animation_key]):
                self.frame_index = 0
        else:
            self.frame_index = 0

        self.image = self.animations[animation_key][int(self.frame_index)]

    def update(self, dt):
        for timer in self.timers.values(): timer.update()
        self.check_vision(self.player)
        self.check_hearing(self.player)
        self.check_player_caught(self.player)

        if self.state == 'INSPECT':
            if self.follow_path():
                self.state = 'ROAM'
                self.timers['action'].activate()
        elif self.state == 'CHASE':
            self.chase_player()

        self.get_status()
        self.animate(dt)
        self.move(dt)
