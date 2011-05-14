import sys
from myrmidon.myrmidon import MyrmidonProcess, MyrmidonGame
from myrmidon.consts import *
from pygame.locals import *

# ----------------------------------------
# ----------------------------------------
# TEST TEST TEST
# ----------------------------------------
# ----------------------------------------


class Game(MyrmidonProcess):

	cur = 0.0
	cur2 = 0.0
	amount = 0
	fps_text = None

	font = None
	
	def execute(self):

		MyrmidonGame.current_fps = 60
		
		self.graphics = {
			"ship" : MyrmidonGame.engine['gfx'].Image("ship.png"),
			"shot" : MyrmidonGame.engine['gfx'].Image("shot.png")
			}

                MyrmidonGame.engine['gfx'].plugins['lighting'].add_light(x = 500.0, y = 500.0, colour = (1.0, 0.0, 0.0, .7), radius = 200.0, intensity = 10.0)
                MyrmidonGame.engine['gfx'].plugins['lighting'].add_light(x = 500.0, y = 300.0, colour = (0.0, 1.0, 0.0, .7), radius = 200.0, intensity = 10.0)

		self.font = MyrmidonGame.engine['window'].load_font(size = 50)
		Ship(self)

		self.fps_text = MyrmidonGame.write_text(0.0, 0.0, font = self.font, text = 0)
		self.process_text = MyrmidonGame.write_text(0.0, 40.0, font = self.font, text = 0)
		
		while True:
			#MyrmidonGame.engine['gfx'].draw_line((50.0, 50.0), (100.0, 100.0), colour = (1.0, 0.0, 0.0, 0.5))
			if MyrmidonGame.keyboard_key_down(K_ESCAPE):
				sys.exit()

			self.pattern_vortex(300.0, 300.0, 1)
			self.pattern_vortex(700.0, 300.0)

			#self.pattern_vortex(500.0, 400.0)

			self.fps_text.text = "FPS " + str(MyrmidonGame.fps)
			self.process_text.text = str(len(MyrmidonGame.process_list)) + " processes"

			yield
			

	def pattern_vortex(self, x, y, type = 0):

		_range = 1
		amount = 3.0
		if MyrmidonGame.keyboard_key_down(K_SPACE):
			_range = 4
			amount = 20.0
			
		for c in range(_range):
			if type:
				self.cur2 -= amount
			else:
				self.cur += amount
			

			if type:
				if self.cur2 < -360.0:
					self.cur2 = 0.0
			else:
				if self.cur > 360.0:
					self.cur = 0.0
				
			Shot(self, x, y, self.cur2 if type else self.cur)
			self.amount += 1
			

class Ship(MyrmidonProcess):
	def execute(self, game):
		self.image = game.graphics['ship']
		self.x, self.y = 500.0, 300.0
		self.rotation = 0.0
                self.z = -512
                self.alpha = 1.0
		while True:
			if MyrmidonGame.keyboard_key_down(K_LEFT):
				self.x -= 10.0
			if MyrmidonGame.keyboard_key_down(K_RIGHT):
				self.x += 10.0
			if MyrmidonGame.keyboard_key_down(K_UP):
				self.y -= 10.0
			if MyrmidonGame.keyboard_key_down(K_DOWN):
				self.y += 10.0
			if MyrmidonGame.keyboard_key_down(K_q):
				self.rotation += 1.0
			yield


class Shot(MyrmidonProcess):

	def execute(self, game, x, y, angle_to = 0.0):

		self.image = game.graphics['shot']
		self.x = x
		self.y = y
                self.z = 512
                self.scale = 1.0
		self.alpha = 1.0
		#self.blend = True

		#self.colour = (1.0, 0.5, 0.5)
		
		while True:
			self.move_forward(3.0, angle = angle_to)

			if self.x < 200 or self.x > MyrmidonGame.screen_resolution[0]-200 or self.y < 0 or self.y > MyrmidonGame.screen_resolution[1]:
				self.signal(S_KILL)
			
			yield

                        
# Start game
MyrmidonGame.screen_resolution = (1024, 768)
MyrmidonGame.full_screen = False
MyrmidonGame.define_engine(gfx = "modern_opengl")
MyrmidonGame.define_engine_plugins(gfx = ["lighting"])
#import cProfile
#cProfile.run('Game()', 'profile')
Game()
