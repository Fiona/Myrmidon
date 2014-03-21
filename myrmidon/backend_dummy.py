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

Dummy backend file, used to define objects that look
like backend engines but actually do nothing
"""

class MyrmidonWindowDummy(object):
	class Clock(object):
		def tick(self, fps_rate):
			pass

	def change_resolution(self, resolution):
		pass

	class Font(object):
		pass

	@classmethod	
	def load_font(cls, filename = None, size = 20):
		return cls.Font


class MyrmidonGfxDummy(object):

	clear_colour = (0.0, 0.0, 0.0, 1.0)
	prev_blend = False
	entities_z_order_list = []
	
	def change_resolution(self, resolution):
		pass

	def update_screen_pre(self):
		pass
	
	def update_screen_post(self):
		pass

	def draw_entities(self, entity_list):
		pass	
	
	def create_texture_list(self, entity, image):
		return None

	def draw_textured_quad(self, width, height, repeat = None):
		pass

	def register_entity(self, entity):
		self.entities_z_order_list.append(entity)

	def remove_entity(self, entity):
		self.entities_z_order_list.remove(entity)

	def alter_x(self, entity, x):
		pass

	def alter_y(self, entity, y):
		pass

	def alter_z(self, entity, z):
		pass
	
	def alter_image(self, entity, image):
		pass

	def alter_colour(self, entity, colour):
		pass

	def alter_alpha(self, entity, alpha):
		pass

	def new_image(self, width, height, colour = None):
		return MyrmidonGfxDummy.Image()
			
	def draw_line(self, start, finish, colour = (1.0,1.0,1.0,1.0), width = 5.0, noloadidentity = False):
		pass
	
	def draw_circle(self, position, radius, colour = (1.0,1.0,1.0,1.0), width = 5.0, filled = False, accuracy = 24, noloadidentity = False):
		pass

	def draw_rectangle(self, top_left, bottom_right, colour = (1.0,1.0,1.0,1.0), filled = True, width = 2.0, noloadidentity = False):
		pass

	def rgb_to_colour(self, colour):
		col = []
		for a in colour:
			col.append(a/255.0)
		return tuple(col)
	

	class Image(object):
		width = 0
		height = 0
        filename = None
        is_sequence_image = False
		def __init__(self, image = None, sequence = False, width = None, height = None):
			pass
		

	class Text(object):
		font = None
		x = 0
		y = 0
		z = -500.0
		alignment = 0
		text = ""
		antialias = True
		rotation = 0.0
		text_image_size = (0,0)
		
		def __init__(self, font, x, y, alignment, text, antialias = True):
			self.font = font
			self.x = x
			self.y = y
			self.alignment = alignment
			self.text = text
			self.antialias = antialias

		def get_screen_draw_position(self):
			return self.x, self.y



class MyrmidonInputDummy(object):
	keys_pressed = []
	last_keys_pressed = []
	event_store = []
	mouse_buttons_pressed = [False, False, False]
	last_mouse_buttons_pressed = [False, False, False]
	mouse = None
	clear_events = True
	disable_input = False

	def __init__(self):
		self.process_input()
		
	def process_input(self):
		if not self.mouse:
			self.mouse = self.Mouse()

	def keyboard_key_down(self, key_code):
		return False

	def keyboard_key_released(self, key_code):
		return False

	class Mouse(object):
		x = 0.0
		y = 0.0
		z = -512
		visible = True		
		pos = (0, 0)
		left = False
		middle = False
		right = False
		left_up = False
		middle_up = False
		right_up = False
		wheel_up = False
		wheel_down = False	   


class MyrmidonAudioDummy(object):
	def load_audio_from_file(self, filename):
		return None
