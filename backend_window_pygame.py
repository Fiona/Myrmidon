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
- WINDOW       -

A pygame-based window creation and handling backend.

"""

import os, pygame
from myrmidon import MyrmidonGame, MyrmidonError

class MyrmidonWindowPygame(object):
	opengl = False
	screen = None
	flags = 0
	
	def __init__(self):
		if MyrmidonGame.engine_def['gfx'] == "opengl":
			self.opengl = True
		
		os.environ['SDL_VIDEO_CENTERED'] = '1'

		pygame.mixer.pre_init(44100,-16,2, 1024 * 3)
		
		pygame.init()

		if self.opengl:
			pygame.display.gl_set_attribute(pygame.locals.GL_MULTISAMPLEBUFFERS, 1)
			pygame.display.gl_set_attribute(pygame.locals.GL_MULTISAMPLESAMPLES, 4)
			pygame.display.gl_set_attribute(pygame.locals.GL_SWAP_CONTROL, 0)
			self.flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE

		if MyrmidonGame.full_screen:
			self.flags |= pygame.FULLSCREEN

		# Check we can set the resolution at this mode
		try:
			self.screen = pygame.display.set_mode(MyrmidonGame.screen_resolution, self.flags)
		except Exception, e:
			# Video mode can't be set, fall back
			if "video mode" in str(e):
				self.resolution_fallback()
			elif self.opengl:
				# Try to fix "Couldn't find matching GLX visual" error with unsupported samplebuffers
				self.disable_multisamples()
				

	def resolution_fallback(self):
		""" Reset resolution down to the lowest supported and windowed. """
		if MyrmidonGame.full_screen:
			self.flags ^= pygame.FULLSCREEN
			MyrmidonGame.full_screen = False
		try:
			MyrmidonGame.screen_resolution = MyrmidonGame.lowest_resolution
			self.screen = pygame.display.set_mode(MyrmidonGame.lowest_resolution, self.flags)
		except Exception, e:
			if self.opengl:
				self.disable_multisamples()
			else:
				raise MyrmidonError("Couldn't find a supported video mode.")
			
			
	def disable_multisamples(self):
		""" If this system doesn't support samplebuffers and also as a last ditch to get
		    a working video mode we'll try disabling them. """
		pygame.display.gl_set_attribute(pygame.locals.GL_MULTISAMPLEBUFFERS, 0)
		pygame.display.gl_set_attribute(pygame.locals.GL_MULTISAMPLESAMPLES, 0)

		try:
			MyrmidonGame.screen_resolution = MyrmidonGame.screen_resolution
			self.screen = pygame.display.set_mode(MyrmidonGame.screen_resolution, self.flags)
		except Exception, e:
			if "video mode" in str(e):
				self.resolution_fallback()
			else:
				raise MyrmidonError("Couldn't find a supported video mode.")
			

	def Clock(self):
		return pygame.time.Clock()
	

	def change_resolution(self, resolution):
		pygame.display.quit()
		self.__init__()
		

	# TEXT HANDLING
	@classmethod	
	def load_font(cls, filename = None, size = 20):
		return pygame.font.Font(filename, size)
	 
