import pygame
import random
import math
from settings import *
from support import load_and_scale_sprite_sheet
from timer import Timer
from entity import Entity
from astar import get_path

class VisionCone:
    def __init__(self, owner, radius, angle, static_edges):
        self.owner = owner
        self.radius = radius
        self.angle = angle
        self.static_edges = static_edges

    def get_edges(self):
        cx, cy = self.owner.rect.center
        r = self.radius + 10 # Buffer
        
        relevant_edges = []
        for p1, p2 in self.static_edges:
            # 1. Simple check: Are endpoints inside the bounding box?
            if (cx - r < p1[0] < cx + r and cy - r < p1[1] < cy + r) or (cx - r < p2[0] < cx + r and cy - r < p2[1] < cy + r):
                relevant_edges.append((p1, p2))
                continue
                
            # 2. Advanced check: Does the segment pass THROUGH the vision circle?
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            if dx == 0 and dy == 0: continue
            
            t = ((cx - p1[0]) * dx + (cy - p1[1]) * dy) / (dx*dx + dy*dy)
            t = max(0, min(1, t))
            
            closest_x = p1[0] + t * dx
            closest_y = p1[1] + t * dy
            
            dist_sq = (cx - closest_x)**2 + (cy - closest_y)**2
            if dist_sq <= r**2:
                relevant_edges.append((p1, p2))
        return relevant_edges

    def cast_ray(self, angle, edges):
        # Ray direction
        dx = math.cos(angle)
        dy = math.sin(angle)
        
        closest_dist = self.radius
        ox, oy = self.owner.rect.center
        
        # Check intersection with each edge
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
        
        # Collect angles to cast rays at
        angles = set()
        
        # Always add rays along the arc for smoothness
        arc_steps = 20
        for i in range(arc_steps + 1):
            angles.add(base_angle - half_fov + (half_fov * 2) * (i / arc_steps))
        
        for p1, p2 in edges:
            for p in [p1, p2]:
                # OPTIMIZATION: Only fire rays at corners that are actually within the radius
                dist_sq = (p[0] - cx)**2 + (p[1] - cy)**2
                if dist_sq > r_sq + 100: continue # Small buffer

                angle = math.atan2(p[1] - cy, p[0] - cx)
                # Only cast if within FOV
                diff = (angle - base_angle + math.pi) % (2 * math.pi) - math.pi
                if abs(diff) <= half_fov:
                    angles.add(angle)
                    angles.add(angle - 0.0001)
                    angles.add(angle + 0.0001)

        # Cast rays and sort points by angle
        points = []
        for angle in angles:
            points.append(self.cast_ray(angle, edges))

        def sort_by_relative_angle(p):
            # Get the raw angle
            angle = math.atan2(p[1] - self.owner.rect.centery, p[0] - self.owner.rect.centerx)
            # Normalize it so it doesn't jump at the -180/180 boundary
            diff = (angle - base_angle + math.pi) % (2 * math.pi) - math.pi
            return diff

        points.sort(key=sort_by_relative_angle)

        # Screen relative points
        screen_points = [pygame.math.Vector2(self.owner.rect.center) - offset]
        for p in points:
            angle = math.atan2(p[1] - self.owner.rect.centery, p[0] - self.owner.rect.centerx)
            diff = (angle - base_angle + math.pi) % (2 * math.pi) - math.pi
            if abs(diff) <= half_fov + 0.01: # Small buffer for float math
                screen_points.append(pygame.math.Vector2(p) - offset)

        if len(screen_points) > 2:
            pygame.draw.polygon(surface, (255, 255, 100, 40), screen_points)


class Monster(Entity):
    def __init__(self, pos, group, grid, monster_type, static_edges):
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
            'hear_cooldown': Timer(1000)
        }
        self.timers['action'].activate()

        # Vision
        self.vision = VisionCone(self, VISION_RADIUS, VISION_ANGLE, static_edges)
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
        if self.state == 'CHASE': return
        if self.timers['hear_cooldown'].active: return

        # Convert pixel pos to grid pos
        start_grid = (int(self.rect.centerx // TILE_SIZE), int(self.rect.centery // TILE_SIZE))
        end_grid = (int(sound_pos[0] // TILE_SIZE), int(sound_pos[1] // TILE_SIZE))

        # Calculate path
        new_path = get_path(self.grid, start_grid, end_grid)
        if new_path or len(new_path) > 20:
            self.state = 'INSPECT'
            self.path = new_path
            self.path_index = 0
            self.timers['action'].deactivate()
            self.timers['hear_cooldown'].activate()

    def follow_path(self):
        if not self.path or self.path_index >= len(self.path):
            self.state = 'ROAM'
            self.path = []
            self.direction = pygame.math.Vector2() 
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
        # Note: CHASE state direction is updated via check_vision in Level

        self.get_status()
        self.animate(dt)
        self.move(dt)
