"""
Myrmidon
Copyright (c) 2010 Fiona Burrows
 
Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:
 
The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
 
---------------------
 
An open source, actor based framework for fast game development for Python.

This file contains the Entity object that represents displayable and interactable
game objects.
"""

import sys, os, math
from consts import *
from Game import Game


class Entity(object):

    _x = 0.0
    _y = 0.0
    _z = 0.0
    _priority = 0
    _image = None
    _image_seq = 0
    _colour = (1.0, 1.0, 1.0)
    _alpha = 1.0
    
    scale = 1.0
    rotation = 0.0
    blend = False
    clip = None
    scale_point = [0.0, 0.0]
    disable_draw = False
    normal_draw = True
    status = 0

    parent = None
    child = None
    prev_sibling = None
    next_sibling = None

    _is_text = False
    _generator = None
    
    def __init__(self, *args, **kargs):
        if not Game.started:
            Game.start_game()

        Game.entity_register(self)

        self.z = 0.0
        self.x = 0.0
        self.y = 0.0
        self.priority = 0

        Game.remember_current_entity_executing.append(Game.current_entity_executing)
        Game.current_entity_executing = self
        self._generator = self.execute(*args, **kargs)
        self._iterate_generator()
        Game.current_entity_executing = Game.remember_current_entity_executing.pop()
        
        if not Game.started:
            Game.started = True             
            Game.run_game()
            

    def execute(self):
        """
        This is where the main code for the entity lives
        """
        while True:
            yield

    def on_exit(self):
        """
        Called automatically when a entity has finished executing for whatever reason.
        Is also called when a entity is killed using signal S_KILL.
        """
        pass
        
    def _iterate_generator(self):
        if not Game.started:
            return
        try:
            self._generator.next()
        except StopIteration:
            return
            #self.signal(S_KILL)


    def draw(self):
        """
        Override this to add custom drawing routines to your entity.
        """
        pass


    def move_forward(self, distance, angle = None):
        self.x, self.y = Game.move_forward((self.x, self.y), distance, self.rotation if angle == None else angle)

        
    def get_distance(self, pos):
        return Game.get_distance((self.x, self.y), pos)
    
        
    def signal(self, signal_code, tree=False):
        """ Signal will let you kill the entity or put it to sleep.
            The 'tree' parameter can be used to signal to an entity and all its
            descendant entities (provided an unbroken tree exists)
        
            Signal types-
            S_KILL - Permanently removes the entity
            S_SLEEP - Entity will disappear and will stop executing code
            S_FREEZE - Entity will stop executing code but will still appear
                and will still be able to be checked for collisions.
            S_WAKEUP - Wakes up or unfreezes the entity """
        Game.signal(self, signal_code, tree)


    def get_screen_draw_position(self):
        """ At draw time this function is called to determine exactly where
        the entity will be drawn. Override this if you need to programatically
        constantly change the position of entity.
        Returns a tuple (x,y)"""
        return self.x, self.y
        

    ##############################################
    # Special properties
    ##############################################
    # X
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        Game.engine['gfx'].alter_x(self, self._x)

    @x.deleter
    def x(self):
        self._x = 0.0
        
    # Y
    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        Game.engine['gfx'].alter_y(self, self._y)

    @y.deleter
    def y(self):
        self._y = 0.0

    # depth
    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        if not self._z == value:
            self._z = value
            Game.engine['gfx'].alter_z(self, self._z)

    @z.deleter
    def z(self):
        self._z = 0.0

    # rity
    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if not self._priority == value:
            Game.entity_priority_dirty = True
            self._priority = value

    @priority.deleter
    def priority(self):
        Game.entity_priority_dirty = True
        self._priority = 0

    # texture image
    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        #if not self._image == value:
        self._image = value
        Game.engine['gfx'].alter_image(self, self._image)

    @image.deleter
    def image(self):
        self._image = None

    # image sequence number
    @property
    def image_seq(self):
        return self._image_seq

    @image_seq.setter
    def image_seq(self, value):
        self._image_seq = value
        Game.engine['gfx'].alter_image(self, self._image)

    @image_seq.deleter
    def image_seq(self):
        self._image_seq = None

    # Colour
    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        if not self._colour == value:
            self._colour = value
            Game.engine['gfx'].alter_colour(self, self._colour)

    @colour.deleter
    def colour(self):
        self._colour = None


    # Alpha
    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        if not self._alpha == value:
            self._alpha = value
            Game.engine['gfx'].alter_alpha(self, self._alpha)

    @alpha.deleter
    def alpha(self):
        self._alpha = None

