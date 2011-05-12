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

A Pygame (and conversely, SDL) driven backend for user input.

"""

import pygame
from pygame.locals import *

from myrmidon.myrmidon import MyrmidonProcess


class Myrmidon_Backend(object):

        keys_pressed = []
        last_keys_pressed = []

        event_store = []
        mouse_buttons_pressed = [False, False, False]
        last_mouse_buttons_pressed = [False, False, False]

        mouse = None

        clear_events = True
        disable_input = False
        
        def __init__(self):
                pygame.key.set_repeat(10, 0)
                self.keys_pressed  = pygame.key.get_pressed()
                self.last_keys_pressed  = self.keys_pressed

                
        def process_input(self):

                if not self.mouse:
                        self.mouse = self.Mouse()
                        self.mouse.z = -512
                        self.mouse.visible = True               
                        self.mouse.pos = (0, 0)
                        self.mouse.rel = (0, 0)
                        self.mouse.left = False
                        self.mouse.middle = False
                        self.mouse.right = False
                        self.mouse.left_up = False
                        self.mouse.middle_up = False
                        self.mouse.right_up = False
                        self.mouse.wheel_up = False
                        self.mouse.wheel_down = False      

                if self.disable_input:
                        return
                
                self.last_keys_pressed  = self.keys_pressed
                pygame.event.pump()
                self.keys_pressed  = pygame.key.get_pressed()

                self.mouse.pos = pygame.mouse.get_pos()
                self.mouse.rel = pygame.mouse.get_rel()
                self.mouse.x = self.mouse.pos[0]
                self.mouse.y = self.mouse.pos[1]
                
                self.mouse.wheel_up = False
                self.mouse.wheel_down = False

                self.event_store = []
                
                for event in pygame.event.get(MOUSEBUTTONDOWN):
                        self.event_store.append(event)
                        if event.type == MOUSEBUTTONDOWN:
                                if event.button == 4:
                                        self.mouse.wheel_up = True
                                if event.button == 5:
                                        self.mouse.wheel_down = True
                                        
                self.last_mouse_buttons_pressed  = self.mouse_buttons_pressed
                self.mouse_buttons_pressed = pygame.mouse.get_pressed()

                self.mouse.left = True if self.mouse_buttons_pressed[0] else False
                self.mouse.left_up = True if self.last_mouse_buttons_pressed[0] and not self.mouse_buttons_pressed[0] else False
                
                self.mouse.middle = True if self.mouse_buttons_pressed[1] else False
                self.mouse.middle_up = True if self.last_mouse_buttons_pressed[1] and not self.mouse_buttons_pressed[1] else False
                
                self.mouse.right = True if self.mouse_buttons_pressed[2] else False
                self.mouse.right_up = True if self.last_mouse_buttons_pressed[2] and not self.mouse_buttons_pressed[2] else False

                if self.clear_events:
                        pygame.event.clear()


        def keyboard_key_down(self, key_code):
                if self.keys_pressed[key_code]:
                        return True
                return False
        

        def keyboard_key_released(self, key_code):
                if self.last_keys_pressed[key_code] and not self.keys_pressed[key_code]:
                        return True
                return False


        
        class Mouse(MyrmidonProcess):
                """ Record for holding mouse info """

                _visible = True
                @property
                def visible(self):
                        return self._visible

                @visible.setter
                def visible(self, value):
                        self._visible = value
                        pygame.mouse.set_visible(value)

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
                        pygame.mouse.set_pos(new_pos)
