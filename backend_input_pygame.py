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

class MyrmidonInputPygame(object):

	keys_pressed = []
	last_keys_pressed = []

	def __init__(self):
		pygame.mouse.set_visible(True)
		pygame.key.set_repeat(10, 0)
		self.process_input()
		
	def process_input(self):
		self.last_keys_pressed  = self.keys_pressed
		pygame.event.pump()
		self.keys_pressed  = pygame.key.get_pressed()

	def keyboard_key_down(self, key_code):
		if self.keys_pressed[key_code]:
			return True
		return False

	def keyboard_key_released(self, key_code):
		if self.last_keys_pressed[key_code] and not cls.keys_pressed[key_code]:
			return True
		return False
