"""
This example shows a large number of entities at once.
Would like to expand this into a complete shoot 'em up game.
"""
import os, sys
from OpenGL.GL import *
from myrmidon import Game, Entity
from myrmidon.consts import *
from pygame.locals import *


class Window(Entity):

    cur = 0.0
    cur2 = 0.0
    amount = 0
    fps_text = None
    font = None

    def execute(self):
        self.graphics = {
            "ship" : Game.load_image(os.path.join("media", "ship.png")),
            "shot" : Game.load_image(os.path.join("media", "shot.png"))
            }
        self.font = Game.load_font(size = 50)
        self.ship = Ship(self)
        self.fps_text = Game.write_text(0.0, 0.0, font = self.font, text = 0)
        self.entity_text = Game.write_text(0.0, 40.0, font = self.font, text = 0)
        Game.write_text(
            512.0, 730.0,
            font = self.font,
            text = "Hold space to produce more entities",
            alignment = ALIGN_CENTRE
            )
        while True:
            if Game.keyboard_key_down(K_ESCAPE):
                sys.exit()
            self.pattern_vortex(300.0, 300.0, 1)
            self.pattern_vortex(700.0, 300.0)
            self.fps_text.text = "FPS " + str(Game.current_fps)
            self.entity_text.text = str(len(Game.entity_list)) + " entities"
            yield

    def pattern_vortex(self, x, y, type = 0):
        _range = 1
        amount = 10.0
        if Game.keyboard_key_down(K_SPACE):
            _range = 10
            amount = 5.0
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


class Ship(Entity):
    def execute(self, game):
        self.image = game.graphics['ship']
        self.x, self.y = 500.0, 300.0
        self.z = -512
        while True:
            if Game.keyboard_key_down(K_LEFT):
                self.x -= 10.0
            if Game.keyboard_key_down(K_RIGHT):
                self.x += 10.0
            if Game.keyboard_key_down(K_UP):
                self.y -= 10.0
            if Game.keyboard_key_down(K_DOWN):
                self.y += 10.0
            yield


class Shot(Entity):
    def execute(self, game, x, y, angle_to = 0.0):
        self.image = game.graphics['shot']
        self.x = x
        self.y = y
        self.z = 512
        while True:
            self.move_forward(4.5, angle = angle_to)
            if self.x < 200 or self.x > Game.screen_resolution[0]-200 or self.y < 0 or self.y > Game.screen_resolution[1]:
                self.destroy()
            yield


# Start game
Game.screen_resolution = (1024, 768)
Game.full_screen = False
Game.modules_enabled = ('Entity_Helper',)
window = Window()
