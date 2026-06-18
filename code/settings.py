# screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64

# grid
GRID_WIDTH, GRID_HEIGHT = (50, 50)

# player
PLAYER_SPEED = 150
PLAYER_RUN_SPEED = 275
PLAYER_ANIMATION_SPEED = 7
PLAYER_HITBOX_SIZE = (25, 50)

# monster
MONSTER_SPEED = 100
MONSTER_CHASE_SPEED = 180
MONSTER_ANIMATION_SPEED = 6
MONSTER_ATTACK_ANIMATION_SPEED = 10
MONSTER_HITBOX_SIZE = (30, 50)
MONSTER_PATH_THRESHOLD = 15
MONSTER_DETECTION_BUFFER = 5
MONSTER_LOS_BUFFER = 10
MONSTER_THICK_RAY_OFFSET = 26

# physics
BLOCKED_THRESHOLD = 0.1

# stealth & vision
SOUND_RADIUS = {
	'walk': 100,
	'run': 250,
	'attack': 500,
	'hiding': 200
}

VISION_RADIUS = 200
VISION_ANGLE = 90

# levels & fog
FADE_SPEED = 200.0
LIGHT_RADIUS = 300
DISCOVERY_RADIUS_ROOM = 120
DISCOVERY_RADIUS_FREE = 260
DYNAMIC_FOG_ALPHA = 180

# layers
Z_LAYER = {
	'floor': 0,
	'sound/state': 1,
	'main': 2
}

# UI
CLOCK_POS = (SCREEN_WIDTH / 2, 30)

# map
TILE_SET = 'map2'  # Options: 'map1', 'map2'
TILE_SET_CONFIG = {
	'map1': {'scale': 2, 'bg color': (0, 0, 0)},
	'map2': {'scale': 4, 'bg color': (89, 78, 63)}
}
# player
PLAYER_SET = 'player2'  # Options: 'player1', 'player2'
PLAYER_SET_CONFIG = {
	'player1': {'scale': 2, 'size': 64},
	'player2': {'scale': 3, 'size': 40}
}
