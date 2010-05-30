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

This is the main file, it have the main MyrmidonGame and MyrmidonProcess objects.
"""


import sys, os, math

from consts import *

class MyrmidonGame(object):

	# Engine related
	started = False
	engine_def = {
		"window" : "pygame",
		"gfx" : "opengl",
		"input" : "pygame"
		}
	engine = {
		"window" : None,
		"gfx" : None,
		"input" : None
		}

	current_fps = 30
	fps = 0

	# Display related
	screen_resolution = 1024,768
	full_screen = False

	# Process related
	process_list = []
	current_process_executing = None


	@classmethod
	def define_engine(cls, window = None, gfx = None, input = None):
		"""
		Use this before creating any processes to redefine which engine backends to use.
		"""
		if window:
			cls.engine_def['window'] = window
		if gfx:
			cls.engine_def['gfx'] = gfx
		if input:
			cls.engine_def['input'] = input


	@classmethod
	def init_engines(cls):
		# Window
		if cls.engine_def['window'] == "pygame":
			from backend_window_pygame import MyrmidonWindowPygame
			cls.engine['window'] = MyrmidonWindowPygame()

		# gfx
		if cls.engine_def['gfx'] == "opengl":
			from backend_gfx_opengl import MyrmidonGfxOpengl
			cls.engine['gfx'] = MyrmidonGfxOpengl()

		# input
		if cls.engine_def['input'] == "pygame":
			from backend_input_pygame import MyrmidonInputPygame
			cls.engine['input'] = MyrmidonInputPygame()


	@classmethod
	def start_game(cls):
		"""
		Called by processes if a game is not yet started.
		It initialises engines.
		"""
		# Start up the backends
		cls.init_engines()
		cls.clock = cls.engine['window'].Clock()


	@classmethod
	def run_game(cls):
		"""
		Called by processes if a game is not yet started.
		Is responsible for the main loop.
		"""
		while cls.started:
			
			if cls.engine['input']:
				cls.engine['input'].process_input()

			cls.engine['gfx'].update_screen_pre()
				
			for process in cls.process_list:
				if hasattr(process, "execute"):
					cls.current_process_executing = process
					process._iterate_generator()

			cls.engine['gfx'].draw_processes(cls.process_list)
				
			cls.engine['gfx'].update_screen_post()

			cls.fps = int(cls.clock.get_fps())
			timerunning = cls.clock.tick(cls.current_fps)


	@classmethod
	def change_resolution(cls, resolution):
		cls.screen_resolution = resolution
		cls.engine['window'].change_resolution(resolution)
		cls.engine['gfx'].change_resolution(resolution)

		

	##############################################
	# PROCESSES
	##############################################
	@classmethod
	def process_register(cls, process):
		"""
		Registers a process with Myrmidon so it will be executed.
		"""
		cls.process_list.append(process)

		cls.engine['gfx'].register_process(process)
		
		"""
		cls.z_order_dirty = True
		
		if is_process == True:
			
			cls.priority_order_dirty = True
			
			# Handle relationships
			if cls.current_process_running != None:
				object.father = cls.current_process_running
				
				if not object.father.son == None:
					object.father.son.smallbro = object
					
				object.bigbro = object.father.son
				object.father.son = object
				"""

	@classmethod		
	def signal(cls, process, signal_code, tree=False):
		""" Signal will let you kill a process or put it to sleep
		
			Will accept a process instance or an ID number to check against one,
			or a process type as a string to check for all of a specific type
		
			The tree parameter can be used to recursively signal all the 
			processes(es) descendants
		
			Signal types-
			S_KILL - Permanently removes the process
			S_SLEEP - Process will disappear and will stop executing code
			S_FREEZE - Process will stop executing code but will still appear
				and will still be able to be checked for collisions.
			S_WAKEUP - Wakes up or unfreezes the process """
		
		# We've entered a specific type as a string
		if type(process) == type(""):
			
			import copy
			process_iter = copy.copy(cls.process_list)
			
			for obj in process_iter:
				if cls.process_list[obj].__class__.__name__ == process:
					cls.single_object_signal(cls.process_list[obj], signal_code, tree)
		
		# Passed in an object directly	  
		else:
			cls.single_object_signal(process, signal_code, tree)
			return


	@classmethod
	def single_object_signal(cls, process, signal_code, tree=False):
		""" Used by signal as a shortcut """
		
		# do children
		if tree:
			next_child = process.son
			while next_child != None:
				cls.single_object_signal(next_child, signal_code, True)
				next_child = next_child.bigbro
		
		# do this one
		if signal_code == S_KILL:
			cls.process_destroy(process)
		elif signal_code == S_WAKEUP:
			process.status = 0
		elif signal_code == S_SLEEP:
			process.status = S_SLEEP
		elif signal_code == S_FREEZE:
			process.status = S_FREEZE


	@classmethod
	def process_destroy(cls, process):
		""" Removes a process """
		if not process in MyrmidonGame.process_list:
			return
		process.on_exit()
		cls.engine['gfx'].remove_process(process)
		MyrmidonGame.process_list.remove(process)

		
	##############################################
	# INPUT
	##############################################
	@classmethod		
	def keyboard_key_down(cls, key_code):
		"""
		Ask if a key is currently being pressed.
		Pass in key codes that is relevant to your chosen input backend.
		"""
		if not cls.engine['input']:
			raise MyrmidonError("Input backend not initialised.")
		return cls.engine['input'].keyboard_key_down(key_code)


	@classmethod		
	def keyboard_key_released(cls, key_code):
		"""
		Ask if a key has just been released last frame.
		Pass in key codes that is relevant to your chosen input backend.
		"""
		if not cls.engine['input']:
			raise MyrmidonError("Input backend not initialised.")
		return cls.engine['input'].keyboard_key_released(key_code)


	##############################################
	# TEXT HANDLING
	##############################################
	@classmethod	
	def write_text(cls, x, y, font, alignment = 0, text = "", antialias = True):
		return cls.engine['gfx'].Text(font, x, y, alignment, text, antialias = True)

	@classmethod	
	def delete_text(cls, text):
		if text in MyrmidonGame.process_list:
			MyrmidonGame.process_destroy(text)


	##############################################
	# HELPFUL MATH
	##############################################
	@classmethod	
	def get_distance(cls, pointa, pointb):
		return math.sqrt((math.pow((pointb[1] - pointa[1]), 2) + math.pow((pointb[0] - pointa[0]), 2)))

	@classmethod	
	def move_forward(cls, pos, distance, angle):
		pos2 = [0.0,0.0]
		
		pos2[0] = pos[0] + distance * math.cos(math.radians(angle))
		pos2[1] = pos[1] + distance * math.sin(math.radians(angle))			

		return pos2
		

class MyrmidonError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)



class MyrmidonProcess(object):

	_x = 0.0
	_y = 0.0
	_z = 0.0
	_image = None
	_image_seq = 0
	_colour = (1.0, 1.0, 1.0)
	_alpha = 1.0
	
	scale = 1.0
	rotation = 0.0
	blend = False
	scale_point = [0.0, 0.0]
	disable_draw = False

	_is_text = False
	_generator = None
	
	_texture_list = None
	
	def __init__(self, *args, **kargs):
		if not MyrmidonGame.started:
			MyrmidonGame.start_game()

		MyrmidonGame.process_register(self)

		self.z = 0.0
		self.x = 0.0
		self.y = 0.0
		
		self._generator = self.execute(*args, **kargs)
		self._iterate_generator()
		
		if not MyrmidonGame.started:
			MyrmidonGame.started = True			
			MyrmidonGame.run_game()


	def execute(self):
		"""
		This is where the main code for the process lives
		"""
		while True:
			yield

	def on_exit(self):
		"""
		Called automatically when a process has finished executing for whatever reason.
		Is also called when a process is killed using signal S_KILL.
		"""
		pass
		
	def _iterate_generator(self):
		if not MyrmidonGame.started:
			return
		try:
			self._generator.next()
		except StopIteration:
			return
			#self.signal(S_KILL)


	def move_forward(self, distance, angle = None):
		self.x, self.y = MyrmidonGame.move_forward((self.x, self.y), distance, self.rotation if angle == None else angle)


	def signal(self, signal_code, tree=False):
		""" Signal will let you kill the process or put it to sleep.
			The 'tree' parameter can be used to signal to a process and all its
			descendant processes (provided an unbroken tree exists)
		
			Signal types-
			S_KILL - Permanently removes the process
			S_SLEEP - Process will disappear and will stop executing code
			S_FREEZE - Process will stop executing code but will still appear
				and will still be able to be checked for collisions.
			S_WAKEUP - Wakes up or unfreezes the process """
		MyrmidonGame.signal(self, signal_code, tree)
		

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
		MyrmidonGame.engine['gfx'].alter_x(self, self._x)

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
		MyrmidonGame.engine['gfx'].alter_y(self, self._y)

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
			MyrmidonGame.engine['gfx'].alter_z(self, self._z)

	@z.deleter
	def z(self):
		self._z = 0.0

	# texture image
	@property
	def image(self):
		return self._image

	@image.setter
	def image(self, value):
		#if not self._image == value:
		self._image = value
		MyrmidonGame.engine['gfx'].alter_image(self, self._image)

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
		MyrmidonGame.engine['gfx'].alter_image(self, self._image)

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
			MyrmidonGame.engine['gfx'].alter_colour(self, self._colour)

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
			MyrmidonGame.engine['gfx'].alter_alpha(self, self._alpha)

	@alpha.deleter
	def alpha(self):
		self._alpha = None

