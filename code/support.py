import os.path
from os import walk
import pygame
import sys


def join(path_list):
	return os.path.join(*path_list)


def clean_path(path):
	# making path platform/os independent
	return os.path.normpath(path.replace('/', os.sep).replace('\\', os.sep))


def get_abs_path(path):
	path = clean_path(path)
	# 1. Check if the game is running as a bundled executable
	if getattr(sys, 'frozen', False):
		# Support PyInstaller's _MEIPASS for self-contained builds
		if hasattr(sys, '_MEIPASS'):
			game_folder_path = sys._MEIPASS
		else:
			game_folder_path = os.path.dirname(sys.executable)
	else:
		# The root is one level up from this script (development mode)
		game_folder_path = os.path.dirname(clean_path(os.path.dirname(os.path.abspath(__file__))))

	# 2. Use os.path.join instead of + to avoid slash errors between Windows/Mac
	return os.path.join(game_folder_path, path)


def import_scaled_folder(path, scale=1):
	surface_list = []

	for _, __, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			orig_width, orig_height = image_surf.get_size()

			image_surf = pygame.transform.scale(image_surf, (orig_width * scale, orig_height * scale))
			surface_list.append(image_surf)

	return surface_list


def load_and_upscale_sprite(path, scale_factor=4):
	path = get_abs_path(path)

	# Load the original tiny sheet
	original_sheet = pygame.image.load(path).convert_alpha()

	# Calculate the new massive dimensions
	orig_width, orig_height = original_sheet.get_size()
	new_width = orig_width * scale_factor
	new_height = orig_height * scale_factor

	# Scale the entire sheet up at once using nearest neighbor
	upscaled_sheet = pygame.transform.scale(original_sheet, (new_width, new_height))

	return upscaled_sheet


def load_and_scale_sprite_sheet(path, orig_width, orig_height, scale=1):
	path = get_abs_path(path)

	# Load the big image
	sheet = pygame.image.load(path).convert()
	sheet.set_colorkey((0, 0, 0))
	frames = []

	sheet_width, sheet_height = sheet.get_size()

	for y in range(0, sheet_height, orig_height):
		for x in range(0, sheet_width, orig_width):
			# Create a new surface for each frame to preserve transparency
			frame_surf = pygame.Surface((orig_width, orig_height))
			frame_surf.set_colorkey((0, 0, 0))
			
			rect = pygame.Rect(x, y, orig_width, orig_height)
			frame_surf.blit(sheet, (0, 0), rect)

			scaled_frame = pygame.transform.scale(frame_surf, (orig_width * scale, orig_height * scale))
			frames.append(scaled_frame.convert_alpha())

	return frames
