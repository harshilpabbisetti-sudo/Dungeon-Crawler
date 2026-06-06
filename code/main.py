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
		self.win_screen = End('win')
		self.lose_screen = End('lost')

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

			dt = self.clock.tick() / 1000
			
			if self.state == 'PLAY':
				self.level.run(dt)
				# transition check
				if self.level.player.end_status == 'win':
					self.state = 'WIN'
				elif self.level.player.end_status == 'lost':
					self.state = 'LOST'
			
			elif self.state == 'WIN':
				self.win_screen.play()
			
			elif self.state == 'LOST':
				self.lose_screen.play()

			pygame.display.update()


if __name__ == '__main__':
	game = Game()
	game.run()
