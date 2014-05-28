"""
Writing a Kivy-based backend for myrmidon
"""
import os

from myrmidon import Game, Entity
from myrmidon.consts import *


class Test_entity(Entity):
    def execute(self, window):
        self.window = window
        self.image = self.window.test_image
        self.x, self.y = 0, 0
        #self.colour = (1.0, 0.0, 0.0)
        #self.alpha = 0.5
        while True:            
            self.x, self.y = Game.mouse().pos
            #self.rotation -= 1
            #self.scale += 0.005
            yield


class Window(Entity):
    def execute(self):
        self.test_image = Game.load_image(os.path.join("media", "ship.png"))
        Test_entity(self)
        while True:            
            yield

# Start game
Game.screen_resolution = (1024, 768)
Game.full_screen = False
Game.define_engine(*(["kivy"] * 4))
Window()
