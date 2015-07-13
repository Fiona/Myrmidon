"""
Myrmidon
Copyright (c) 2015 Fiona Burrows

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

Provides a pypyjs based graphics backend
"""

class Myrmidon_Backend(object):

    clear_colour = (0.0, 0.0, 0.0, 1.0)
    prev_blend = False
    entities_z_order_list = []
    device_resolution = (0, 0)

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

    def alter_scale(self, entity, scale):
        pass

    def alter_rotation(self, entity, rotation):
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

        def destroy(self):
            return
                 
