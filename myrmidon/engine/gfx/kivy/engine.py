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

Provides a Kviy-based graphics adaptor.
"""


from myrmidon import Game, Entity, BaseImage, MyrmidonError
from myrmidon.consts import *

from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Scale, Rotate


class Entity_Widget(Widget):
    rect = None
    rotation = None
    colour = None
    def __init__(self, **kwargs):
        self.kivy_app = kwargs['kivy_app']
        super(Entity_Widget, self).__init__(**kwargs)
        with self.canvas:
            self.colour = Color(1.0, 1.0, 1.0, 1.0, mode = 'rgba')
            self.rotation = Rotate(angle = 0)
            self.rect = Rectangle(pos = (0, 0), size = (0, 0))


class Myrmidon_Backend(object):
    clear_colour = (0.0, 0.0, 0.0, 1.0)
    entity_widgets = {}

    def __init__(self):
        self.entity_widgets = {}
    

    def change_resolution(self, resolution):
        pass


    def update_screen_pre(self):
        pass
    
	
    def update_screen_post(self):
        pass


    def draw_entities(self, entity_list):
        pass
    

    def draw_single_entity(self, entity):
        pass
    
	
    def create_texture_list(self, entity, image):
        return None


    def draw_textured_quad(self, width, height, repeat = None):
        pass


    def register_entity(self, entity):
        if entity in self.entity_widgets:
            return
        self.entity_widgets[entity] = Entity_Widget(kivy_app = Game.engine['window'].kivy_app)
        Game.engine['window'].kivy_app.widget.add_widget(self.entity_widgets[entity])
    

    def remove_entity(self, entity):
        if not entity in self.entity_widgets:
            return
        Game.engine['window'].kivy_app.widget.remove_widget(self.entity_widgets[entity])
        del(self.entity_widgets[entity])

    
    def alter_x(self, entity, x):
        y = entity.y if entity.image is None else Game.screen_resolution[1] - entity.image.height - entity.y
        self.entity_widgets[entity].rect.pos = (x, y)
        self.entity_widgets[entity].rotation.origin = (x + (self.entity_widgets[entity].rect.size[0]/2), y + (self.entity_widgets[entity].rect.size[1]/2))


    def alter_y(self, entity, y):
        y = y if entity.image is None else Game.screen_resolution[1] - entity.image.height - y
        self.entity_widgets[entity].rect.pos = (entity.x, y)
        self.entity_widgets[entity].rotation.origin = (entity.x + (self.entity_widgets[entity].rect.size[0]/2), y + (self.entity_widgets[entity].rect.size[1]/2))


    def alter_z(self, entity, z):
        #Game.engine['window'].kivy_app.widget.remove_widget(self.entity_widgets[entity])
        #Game.engine['window'].kivy_app.widget.add_widget(self.entity_widgets[entity], entity.z)
        pass

	
    def alter_image(self, entity, image):
        if image is None:
            self.entity_widgets[entity].rect.texture = None
        else:
            self.entity_widgets[entity].rect.texture = image.image.texture
            self.entity_widgets[entity].rect.size = (image.width * entity.scale, image.height * entity.scale)
            self.entity_widgets[entity].rect.pos = (entity.x, Game.screen_resolution[1] - entity.image.height - entity.y)
        

    def alter_colour(self, entity, colour):
        self.entity_widgets[entity].colour.rgb = colour


    def alter_alpha(self, entity, alpha):
        self.entity_widgets[entity].colour.a = alpha


    def alter_scale(self, entity, scale):
        if entity.image is None:
            return
        self.entity_widgets[entity].rect.size = (entity.image.width * scale, entity.image.height * scale)


    def alter_rotation(self, entity, rotation):
        self.entity_widgets[entity].rotation.angle = rotation
        

    def new_image(self, width, height, colour = None):
        return Myrmidon_Backend.Image()

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
            if image is None:
                return
            loaded_image = None
            if isinstance(image, str):
                self.filename = image
                try:
                    loaded_image = Image(image)
                except:
                    raise MyrmidonError("Couldn't load image from " + image)
            else:
                loaded_image = image
            self.image = loaded_image
            self.width = self.image.height
            self.height = self.image.height
            

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

