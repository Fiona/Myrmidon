"""
This example shows a large number of entities at once.
Would like to expand this into a complete shoot 'em up game.
"""
import os, sys
from OpenGL.GL import *
from myrmidon import Game, Entity
from myrmidon.consts import *
from pygame.locals import *
import math, random
from cymunk import *

shots = []
# create the main space
space = Space()
#space.set_default_collision_handler(begin=mycollide)
space.iterations = 30
space.gravity = (0, 100)
space.sleep_time_threshold = 0.5
space.collision_slop = 0.5





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
        #Ship(self)
        self.fps_text = Game.write_text(0.0, 0.0, font = self.font, text = 0)
        self.entity_text = Game.write_text(0.0, 40.0, font = self.font, text = 0)
        Game.write_text(
            512.0, 730.0,
            font = self.font,
            text = "Hold space to produce more entities",
            alignment = ALIGN_CENTRE
            )
        # add bounds
        sx = Game.screen_resolution[0]
        sy = Game.screen_resolution[1]
        seg1 = Segment(space.static_body, Vec2d(0, 0), Vec2d(0, sy), 0)
        seg1.elasticity = 1.0
        seg1.friction = 1.0

        seg2 = Segment(space.static_body, Vec2d(0, sy), Vec2d(sx, sy), 0)
        seg2.elasticity = 1.0
        seg2.friction = 1.0

        seg3 = Segment(space.static_body, Vec2d(sx, sx), Vec2d(sx, 0), 0)
        seg3.elasticity = 1.0
        seg3.friction = 1.0

        # add everything into space
        space.add_static(seg1, seg2, seg3)
        while True:            
            if Game.keyboard_key_down(K_ESCAPE):
                sys.exit()
            space.step(.1)#TODO - use actual time delta
            self.pattern_vortex(300.0, 300.0, 1)
            self.fps_text.text = "FPS " + str(Game.current_fps)
            self.entity_text.text = str(len(Game.entity_list)) + " entities"            
            yield
           
    def pattern_vortex(self, x, y, type = 0):
        _range = 0
        if Game.keyboard_key_down(K_SPACE):
            _range = 10
        if random.random()>.9:
            _range=1
        for c in range(_range):
            Shot(self, x, y)



class Shot(Entity):
    def execute(self, game, x, y, angle_to = 0.0):
        self.image = game.graphics['shot']
        self.x = x
        self.y = y
        self.z = 512
        self.body = Body(100, 1e9)#TODO calc moment using cymunk function
        self.body.position = (x+random.random()*10.,y)
        self.circle = Circle(self.body, self.image.width/2)
        self.circle.elasticity = .10
        self.circle.friction = .50
        self.collision_circle_radius = self.image.width/2
        space.add(self.circle, self.body)
        self.age=0
        while True:
            self.age+=1
            self.x=self.body.position.x
            self.y=self.body.position.y
            #if self.age>60:
            #    self.destroy()#TODO remove/destroy body/shape
            yield


# Start game
Game.screen_resolution = (1024, 768)
Game.full_screen = False
Game.modules_enabled = ('Entity_Helper',)
Window()
