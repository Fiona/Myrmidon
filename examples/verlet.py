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

shots = []

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
        while True:            
            if Game.keyboard_key_down(K_ESCAPE):
                sys.exit()
            if random.random()>.9:
                self.pattern_vortex(300.0, 300.0, 1)
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



class Shot(Entity):
    def execute(self, game, x, y, angle_to = 0.0):
        self.image = game.graphics['shot']
        self.x = x
        self.y = y
        self.ox = x+random.random()
        self.oy = y+random.random()
        self.z = 512
        self.collision_circle_radius = self.image.width/2
        self.age=0
        while True:
            self.age+=1
            xv = self.x-self.ox
            yv = self.y-self.oy
            self.ox = self.x
            self.oy = self.y
            self.x+=xv*.98
            self.y+=yv*.98+.1
            shots = Game.get_entities(Shot)
            slen = len(shots)
            for ai in range(slen-1):
                a=shots[ai]
                for bi in range(ai+1, slen):
                    b=shots[bi]
                    dvx = a.x-b.x
                    dvy = a.y-b.y
                    dist_sqr = dvx**2+dvy**2
                    rads = a.collision_circle_radius+b.collision_circle_radius
                    #if Game.collision_circle_to_circle(a,b):
                    if dist_sqr < rads**2:
                        td = math.sqrt(dist_sqr)
                        if td==0:td=0.0001
                        nx=dvx/td
                        ny=dvy/td
                        diffd = td-rads
                        fx = nx*diffd
                        fy = ny*diffd
                        a.x -= fx*.5
                        a.y -= fy*.5
                        b.x += fx*.5
                        b.y += fy*.5
                        #b.x -= fx
                        #b.y -= fy
            #if self.x < 0 or self.x > Game.screen_resolution[0]-0 or self.y < 0 or self.y > Game.screen_resolution[1]:
            if self.y > Game.screen_resolution[1]*.7:
                self.y=Game.screen_resolution[1]*.7
            if self.x > Game.screen_resolution[0]*.4:
                self.x=Game.screen_resolution[0]*.4
            if self.x < 20:
                self.x=20
            if self.age>600:
                self.destroy()
            yield
                        

# Start game
Game.screen_resolution = (1024, 768)
Game.full_screen = False
Game.modules_enabled = ('Entity_Helper',)
Window()
