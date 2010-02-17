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
- GRAPHICS     -

Provides an OpenGL-based graphics adaptor.
Pygame is required for text rendering. This may change in the future.

"""


import os, pygame
from OpenGL.GL import *
from pygame.locals import *

from myrmidon import MyrmidonGame, MyrmidonProcess

class MyrmidonGfxOpengl(object):

	clear_colour = (0.0, 0.0, 0.0, 1.0)
	prev_blend = False
	
	draw_layers = {	}
	
	def __init__(self):

		glClearColor(*self.clear_colour)
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		glOrtho(0, MyrmidonGame.screen_resolution[0], MyrmidonGame.screen_resolution[1], 0, -100, 100)
		glMatrixMode(GL_MODELVIEW)

		glEnable(GL_TEXTURE_2D)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
 
		glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
		glEnable(GL_LINE_SMOOTH)

		pygame.display.flip()


	def update_screen_pre(self):
		glClear(GL_COLOR_BUFFER_BIT)

	
	def update_screen_post(self):
		pygame.display.flip()


	def draw_processes(self, process_list):
		
		for process in process_list:

			if hasattr(process, "draw"):
				process.draw()
				continue
			
			if not process.image:
				continue

			glLoadIdentity()

			glTranslatef(process.x, process.y, 0)

			if process.rotation is not 0.0:
				glRotatef(process.rotation, 0, 0, 1)

			if not process.blend == self.prev_blend:
				if process.blend:
					glBlendFunc(GL_SRC_ALPHA, GL_ONE)
				else:
					glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

				self.prev_blend = process.blend
			
			glCallList(process._texture_list)


	current_bound_tex = 0
	
	def create_texture_list(self, process, image):
		new_list = glGenLists(1)
		glNewList(new_list, GL_COMPILE);

		glColor4f(1.0, 1.0, 1.0, process.alpha)

		glEnable(GL_TEXTURE_2D)
		
		if not image.surface == self.current_bound_tex:
			glBindTexture(GL_TEXTURE_2D, image.surface)
			self.current_bound_tex = image.surface
			
		glBegin(GL_QUADS)

		# bottom left
		glTexCoord2f(0.0, 0.0)
		glVertex3f(0.0, 0.0, 0.0)

		# top left
		glTexCoord2f(0.0, 1.0)
		glVertex3f(0.0, image.height, 0.0)

		# top right
		glTexCoord2f(1.0, 1.0)
		glVertex3f(image.width, image.height, 0.0)

		# bottom right
		glTexCoord2f(1.0, 0.0)
		glVertex3f(image.width, 0.0, 0.0)		
		
		glEnd()
		
		glEndList()

		return new_list


	def register_process(self, process):
		if not process.image:
			return
		
		process._texture_list = self.create_texture_list(process, process.image)
			

	def alter_x(self, process, x):
		pass

	def alter_y(self, process, y):
		pass

	def alter_z(self, process, z):
		pass

	def alter_image(self, process, image):
		if not process.image:
			return

		process._texture_list = self.create_texture_list(process, process.image)


	def draw_line(self, start, finish, colour = (1.0,1.0,1.0,1.0), width = 5.0):
		glLoadIdentity()
		glColor4f(*colour)
		glLineWidth(width)
		
		glDisable(GL_TEXTURE_2D)
		
		glBegin(GL_LINES)
		glVertex2f(start[0], start[1])
		glVertex2f(finish[0], finish[1])
		glEnd()
		

	class Image(object):
		
		surface = None
		width = 0
		height = 0
		
		def __init__(self, image = None):

			if image == None:
				return
			
			if isinstance(image, str):
				try:
					raw_surface = pygame.image.load(image)
				except:
					raise MyrmidonError("Couldn't load image from " + image)
			else:
				raw_surface = image

			self.width = raw_surface.get_width()
			self.height = raw_surface.get_height()

			data = pygame.image.tostring(raw_surface, "RGBA", 0)
 
			self.surface = glGenTextures(1)
			glBindTexture(GL_TEXTURE_2D, self.surface)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
				

	class Text(MyrmidonProcess):
		""" this is the class for all text handling """

		_text = ""
		_font = None
		_antialias = True
		
		def __init__(self, font, x, y, alignment, text):
			MyrmidonProcess.__init__(self)
			self.font = font
			self.x = x
			self.y = y
			self.z = -512.0
			self.alignment = alignment
			self.text = text
			self.antialias = True
			self._is_text = True
			self.rotation = 0.0

			self.generate_text_image()


		def generate_text_image(self):
			if self.text == "" or self.font == None:
				self.image = None
				return
				
			# Generate a Pygame image based on the current font and settings
			colour = (255 * self.colour[0], 255 * self.colour[1], 255 * self.colour[2])
			font_image = self.font.render(self.text, self.antialias, colour)

			# We need to work out the nearest power of 2 to appease opengl
			# there must be a better way of doing this
			width = font_image.get_width()
			height = font_image.get_height()

			h = 16
			while(h < height):
				h = h * 2
			w = 16
			while(w < width):
				w = w * 2

			new_surface = pygame.Surface((w, h))
			new_surface.blit(font_image, (0, 0))

			# Create an image from it
			self.image = MyrmidonGfxOpengl.Image(new_surface)
			

		# text
		@property
		def text(self):
			return self._text

		@text.setter
		def text(self, value):
			if not self._text == value:
				self._text = str(value)
				self.generate_text_image()
				
				
		@text.deleter
		def text(self):
			self._text = ""
			self.generate_text_image()

		# antialias
		@property
		def antialias(self):
			return self._antialias

		@antialias.setter
		def antialias(self, value):
			if not self._antialias == value:
				self._antialias = value
				self.generate_text_image()

		@antialias.deleter
		def antialias(self):
			self._antialias = True
			self.generate_text_image()

		# font
		@property
		def font(self):
			return self._font

		@font.setter
		def font(self, value):
			if not self._font == value:
				self._font = value
				self.generate_text_image()

		@font.deleter
		def font(self):
			self._font = None
			self.generate_text_image()
