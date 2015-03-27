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

- BACKEND FILE -
- INPUT        -

A Kivy driven backend for user input.

"""

from myrmidon import Entity, Game
from myrmidon.consts import *

from kivy.core.window import Window

class Myrmidon_Backend(object):
    keys_pressed = []
    last_keys_pressed = []
    mouse = None
    disable_input = False
    map_touch_to_mouse = True
    mouse_left_state = [False, False]

    def __init__(self):
        pass

    def process_input(self):
        if not self.mouse:
            self.mouse = self.Mouse()
            self.mouse.z = -512
            self.mouse.visible = True
            self.initialise_mouse_state()
        if self.disable_input:
            self.initialise_mouse_state()
            return

        self.last_keys_pressed  = self.keys_pressed        
        self.mouse.x = self.mouse.pos[0]
        self.mouse.y = self.mouse.pos[1]
        self.mouse.y -= abs(Game.global_y_pos_adjust) / Game.device_scale
        self.mouse.wheel_up = False
        self.mouse.wheel_down = False
        self.mouse.left_down, self.mouse.left_up = self.mouse_left_state
        self.mouse_left_state = [False, False]

    def keyboard_key_down(self, key_code):
        if self.keys_pressed[key_code]:
            return True
        return False

    def keyboard_key_released(self, key_code):
         if self.last_keys_pressed[key_code] and not self.keys_pressed[key_code]:
              return True
         return False

    def initialise_mouse_state(self):
        self.mouse.pos = (0, 0)
        self.mouse.rel = (0, 0)
        self.mouse.left = False
        self.mouse.middle = False
        self.mouse.right = False
        self.mouse.left_down = False
        self.mouse.left_up = False
        self.mouse.middle_down = False
        self.mouse.middle_up = False
        self.mouse.right_down = False
        self.mouse.right_up = False
        self.mouse.wheel_up = False
        self.mouse.wheel_down = False

    class Mouse(Entity):
        """ Record for holding mouse info """
        collision_type = COLLISION_TYPE_POINT
        collision_on = True
        _visible = True
        @property
        def visible(self):
            return self._visible

        @visible.setter
        def visible(self, value):
            self._visible = value

        @visible.deleter
        def visible(self):
            self._visible = False

        def set_pos(self, new_pos):
            """
            Pass in a tuple corrisponding to the screen position we want
            the mouse to sit at.
            """
            self.pos = new_pos
            self.x, self.y = self.pos
