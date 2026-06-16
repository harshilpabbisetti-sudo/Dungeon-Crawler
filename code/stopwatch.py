import pygame
from support import get_abs_path
from settings import *


class Stopwatch:
	def __init__(self):
		self.elapsed_time = 0
		self.start_time = 0
		self.active = False

	def activate(self):
		if not self.active:
			self.active = True
			self.start_time = pygame.time.get_ticks()

	def deactivate(self):
		if self.active:
			self.elapsed_time += pygame.time.get_ticks() - self.start_time
			self.active = False

	def get_total_ms(self):
		if self.active:
			return self.elapsed_time + (pygame.time.get_ticks() - self.start_time)
		return self.elapsed_time

	def calculate_time(self):
		total_ms = self.get_total_ms()
		total_seconds = total_ms // 1000
		minutes = total_seconds // 60
		seconds = total_seconds % 60
		return f'{minutes:02}:{seconds:02}'


class Clock:
	def __init__(self):
		# general setup
		self.font = pygame.font.Font(get_abs_path('font/Pixeltype.ttf'), 50)
		self.display_surf = pygame.display.get_surface()

		# stopwatch
		self.stopwatch = Stopwatch()
		self.stopwatch.activate()

		# text setup
		self.last_time_str = ""
		self.text = None
		self.text_rect = None

	def display(self):
		current_time_str = self.stopwatch.calculate_time()
		
		# Only re-render if the string has changed
		if current_time_str != self.last_time_str:
			self.last_time_str = current_time_str
			self.text = self.font.render(current_time_str, False, 'White')
			self.text_rect = self.text.get_rect(center=CLOCK_POS)

		if self.text:
			self.display_surf.blit(self.text, self.text_rect)
