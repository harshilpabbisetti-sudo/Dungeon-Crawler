from entity import Entity
from settings import *
from support import *
from timer import Timer

Vector = pygame.math.Vector2


class Player(Entity):
	def __init__(self, pos, group, dungeon, hideable_sprites, level):
		super().__init__(pos, group, dungeon.grid)

		self._import_assets()
		self.status = "Idle"
		self.facing = "Down"

		# general setup
		self.image = self.animations[f'{self.facing}_{self.status}'][self.frame_index]
		self.rect = self.image.get_rect(center=pos)
		self.hitbox = pygame.Rect(0, 0, PLAYER_HITBOX_SIZE[0], PLAYER_HITBOX_SIZE[1])
		self.hitbox.center = self.rect.center
		self.hideable_sprites = hideable_sprites
		self.level = level

		# Combat attributes
		self.sound_radius = 0
		self.dying = False

		# exit
		exit_pos = dungeon.rooms[-1]['center']
		self.exit_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
		self.exit_rect.center = (exit_pos[0] * TILE_SIZE, exit_pos[1] * TILE_SIZE)

		# end
		self.end_status = None

		# hiding
		self.hid = False
		self.hidable_sprite = None

		# timers
		self.timers = {'key_timer': Timer(500), 'hiding_sound_timer': Timer(200)}

		# sound
		self.hiding_sound = pygame.mixer.Sound(get_abs_path('audio/hide.wav'))

	def update(self, dt):
		keys = pygame.key.get_pressed()
		self._input(keys)
		self._get_status()

		if not self.dying:
			self._move(dt)

		self._animate(dt)
		for i in self.timers.keys():
			self.timers[i].update()
		self._update_sound_radius()
		self._game_end()

	def _import_assets(self):
		self.animations = {}
		directions = ['Down', 'Up', 'Left', 'Right']
		states = ['Idle', 'Run', 'Death']

		player_config = PLAYER_SET_CONFIG[PLAYER_SET]
		player_scale = player_config['scale']
		player_size = player_config['size']

		for direction in directions:
			for state in states:
				full_path = f'graphics/{PLAYER_SET}/{direction}_{state}.png'
				self.animations[f'{direction}_{state}'] = load_and_scale_sprite_sheet(full_path, player_size, player_size, player_scale)


	def _input(self, keys):
		# hiding
		if keys[pygame.K_f] and not self.timers['key_timer'].active:
			self._hiding()
			self.timers['key_timer'].activate()

		# movement
		if not self.hid and not self.dying:
			self.speed = PLAYER_SPEED

			# Movement input
			if keys[pygame.K_UP] or keys[pygame.K_w]:
				self.direction.y = -1
				self.facing = 'Up'
			elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
				self.direction.y = 1
				self.facing = 'Down'
			else:
				self.direction.y = 0

			if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				self.direction.x = 1
				self.facing = 'Right'
			elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
				self.direction.x = -1
				self.facing = 'Left'
			else:
				self.direction.x = 0

			if keys[pygame.K_LALT]:
				self.speed = PLAYER_RUN_SPEED

	def _get_status(self):
		if self.dying:
			self.status = 'Death'
		elif self.direction.magnitude() == 0:
			self.status = 'Idle'
		else:
			self.status = 'Run'

	def _animate(self, dt):
		animation_key = f'{self.facing}_{self.status}'

		# Animation loop
		self.frame_index += PLAYER_ANIMATION_SPEED * dt
		if self.frame_index >= len(self.animations[animation_key]):
			if self.dying:
				self.frame_index = len(self.animations[animation_key]) - 1
				animation_key = f'{self.facing}_Death'
				self.end_status = 'lost'
			else:
				self.frame_index = 0

		self.image = self.animations[animation_key][int(self.frame_index)]

	def _update_sound_radius(self):
		if self.timers['hiding_sound_timer'].active:
			self.sound_radius = SOUND_RADIUS['hiding']
			return

		if self.status == 'Run':
			if self.speed == PLAYER_RUN_SPEED:  # Running with LALT
				self.sound_radius = SOUND_RADIUS['run']
			else:  # Normal walking
				self.sound_radius = SOUND_RADIUS['walk']
		else:
			self.sound_radius = 0

	def _game_end(self):
		if self.exit_rect.colliderect(self.hitbox):
			self.end_status = 'win'
		# lost decided in self._animate()

	def _hiding(self):
		collided_sprite = pygame.sprite.spritecollideany(self, self.hideable_sprites)
		if collided_sprite:
			# Check if anyone sees us (Entering OR Exiting)
			self.level.notify_monsters_of_hiding(self.pos)

			self.hid = not self.hid
			if not self.hidable_sprite:
				self.hidable_sprite = collided_sprite
			else:
				self.hidable_sprite = None
			collided_sprite.has_player = not collided_sprite.has_player
			self.pos = Vector(collided_sprite.rect.center)
			self.direction = Vector(0, 0)

			# Trigger hiding sound
			self.sound_radius = SOUND_RADIUS['hiding']
			self.timers['hiding_sound_timer'].activate()

			self.hiding_sound.play()
