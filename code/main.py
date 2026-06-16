import pygame
import sys
from settings import *
from level import Level
from end import End


class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption('Dungeon Crawler')
		self.clock = pygame.time.Clock()
		
		# state management
		self.state = 'PLAY'
		self.level = Level()
		self.end_screen = None

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				
				# restart logic
				if event.type == pygame.KEYDOWN and self.state != 'PLAY':
					if event.key == pygame.K_SPACE:
						self.level = Level()
						self.state = 'PLAY'
						self.end_screen = None

			dt = self.clock.tick() / 1000
			
			if self.state == 'PLAY':
				self.level.run(dt)
				# transition check
				if self.level.player.end_status:
					final_time = self.level.clock.stopwatch.calculate_time()
					self.end_screen = End(self.level.player.end_status, final_time)
					self.state = self.level.player.end_status.upper()
			
			else:
				if self.end_screen:
					self.end_screen.run(dt)

			pygame.display.update()


if __name__ == '__main__':
	game = Game()
	game.run()
