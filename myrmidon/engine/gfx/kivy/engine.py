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

import copy

from myrmidon import Game, Entity, BaseImage, MyrmidonError
from myrmidon.consts import *

from kivy.core.image import Image as Kivy_Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Scale, Rotate, PushMatrix, PopMatrix, Translate, Quad
from kivy.core.window import Window
from kivy.graphics.opengl import glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA


class Myrmidon_Backend(Entity):
    clear_colour = (0.0, 0.0, 0.0, 1.0)
    z_index_dirty = True
    entity_list_draw_order = []

    def __init__(self):
        # Try hiding soft keys on certain ondroid phones
        self.get_device_size_metrics()
        self.entity_draws = {}
        self.widget = None

    def get_device_size_metrics(self):
        self.device_resolution = Window.width, Window.height
        Game.device_scale = float(Window.height) / Game.screen_resolution[1]
        # If any x position adjustment is necessary cos aspect ratio is lower than ideal
        Game.global_x_pos_adjust = 0.0
        if float(self.device_resolution[0]) / self.device_resolution[1] < float(Game.screen_resolution[0]) / Game.screen_resolution[1]:
            Game.global_x_pos_adjust = float((Game.screen_resolution[0] * Game.device_scale) - self.device_resolution[0]) / 2

    def change_resolution(self, resolution):
        pass


    def update_screen_pre(self):
        pass


    def update_screen_post(self):
        pass


    def draw_entities(self, entity_list):
        self.get_device_size_metrics()

        # Create our canvas to draw to if we hadn't got one yet
        if self.widget is None:
            self.widget = Widget()
            Game.engine['window'].kivy_app.widget.add_widget(self.widget)
        self.widget.width = Window.width
        self.widget.height = Window.height

        # If our z order is potentially dirty then we need to completely redraw
        # everything, se we clear the canvas and draw list, then get the proper order.
        if self.z_index_dirty:
            self.widget.canvas.clear()
            self.entity_draws = {}

            #self.entity_list_draw_order = copy.copy(entity_list)
            self.entity_list_draw_order = entity_list
            self.entity_list_draw_order.sort(
                key=lambda object:
                object.z if hasattr(object, "z") else 0,
                reverse = True
                )
            self.z_index_dirty = False

        # Now render for each entity
        for entity in self.entity_list_draw_order:
            if not entity.image is None and hasattr(entity.image, "image") and not entity.image.image is None:
                # Work out the real width/height and screen position of the entity
                size = ((entity.image.width) * (entity.scale * Game.device_scale), (entity.image.height) * (entity.scale * Game.device_scale))
                x, y = entity.get_screen_draw_position()
                y = Game.screen_resolution[1] - (entity.image.height * entity.scale) - y
                pos = ((x * Game.device_scale) - Game.global_x_pos_adjust, y * Game.device_scale)
                # If this entity hasn't yet been attached to the canvas then do so
                if not entity in self.entity_draws:
                    self.entity_draws[entity] = dict()
                    with self.widget.canvas:
                        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                        self.entity_draws[entity]['color'] = Color()
                        self.entity_draws[entity]['color'].rgb = entity.colour
                        self.entity_draws[entity]['color'].a = entity.alpha
                        PushMatrix()
                        self.entity_draws[entity]['translate'] = Translate()
                        self.entity_draws[entity]['rotate'] = Rotate()
                        self.entity_draws[entity]['rotate'].set(entity.rotation, 0, 0, 1)
                        self.entity_draws[entity]['rect'] = Quad(
                            texture = entity.image.image.texture,
                            points = (0.0, 0.0, size[0], 0.0, size[0], size[1], 0.0, size[1])
                            )
                        self.entity_draws[entity]['translate'].xy = pos
                        PopMatrix()
                    # Otherwise just update values
                else:
                    self.entity_draws[entity]['rotate'].angle = entity.rotation
                    self.entity_draws[entity]['translate'].xy = pos
                    self.entity_draws[entity]['color'].rgb = entity.colour
                    self.entity_draws[entity]['color'].a = entity.alpha
                    self.entity_draws[entity]['rect'].texture = entity.image.image.texture
                    self.entity_draws[entity]['rect'].points = (0.0, 0.0, size[0], 0.0, size[0], size[1], 0.0, size[1])

            entity.draw()


    def draw_single_entity(self, entity):
        pass


    def create_texture_list(self, entity, image):
        return None


    def draw_textured_quad(self, width, height, repeat = None):
        pass


    def register_entity(self, entity):
        self.z_index_dirty = True


    def remove_entity(self, entity):
        self.z_index_dirty = True


    def alter_x(self, entity, x):
        pass


    def alter_y(self, entity, y):
        pass


    def alter_z(self, entity, z):
        self.z_index_dirty = True


    def alter_image(self, entity, image):
        pass


    def alter_alpha(self, entity, alpha):
        pass


    def alter_colour(self, entity, colour):
        pass


    def alter_scale(self, entity, scale):
        pass


    def alter_rotation(self, entity, rotation):
        pass


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
        def __init__(self, image = None, sequence = False, width = None, height = None, mipmap = True):
            if image is None:
                return
            loaded_image = None
            if isinstance(image, str):
                self.filename = image
                try:
                    loaded_image = Kivy_Image(image, mipmap = mipmap)
                except:
                    raise MyrmidonError("Couldn't load image from " + image)
            else:
                loaded_image = Kivy_Image(image)
            self.image = loaded_image
            self.width = self.image.width
            self.height = self.image.height

        def destroy(self):
            """
            Explicitly removes this image from the video memory and
            Kivy's cache.
            This functionality requires the custom kivy version at
            http://github.com/arcticshores/kivy
            """
            if self.image is None:
                return

            from kivy.cache import Cache
            from kivy.graphics.opengl import glBindTexture, glDeleteTextures
            from kivy.logger import Logger

            Logger.debug("MyrmidonGFX: Destroying <{0}>".format(self.filename))

            # Remove from cache
            self.image.remove_from_cache()

            # Convert the ID to the right byte format for the GL method
            a1 = (self.image.texture.id >>  0) & 0xFF
            a2 = (self.image.texture.id >>  8) & 0xFF
            a3 = (self.image.texture.id >> 16) & 0xFF
            a4 = (self.image.texture.id >> 24) & 0xFF

            # Remove texture completely
            glBindTexture(self.image.texture.target, 0)
            glDeleteTextures(1, str.encode(chr(a1) + chr(a2) + chr(a3) + chr(a4)))

            # Since we've done a manual removal kivy shouldn't do it's own removal later
            self.image.texture.nofree = 1

            # Stop this image from being used as a texture now
            self.image = None


    class Text(Entity):
        alignment = ALIGN_CENTER
        label = None
        _text = ""
        _font = None
        _antialias = True

        text_image_size = (0,0)

        _shadow = None

        def __init__(self, font, x, y, alignment, text, antialias = True):
            Entity.__init__(self)
            if font is not None:
                self.label = Label(font_name = font.filename, font_size = font.size, mipmap = True)
            else:
                self.label = Label(font_size = "30", mipmap = True)
            self.font = font
            self.x = x
            self.y = y
            self.z = -500.0
            self.alignment = alignment
            self.text = text
            self.antialias = antialias
            self._is_text = True
            self.rotation = 0.0
            self.normal_draw = False


        def generate_text_image(self):
            # When set to a blank text, for some reason kivy wanted the texture update to happen
            # twice otherwise it wouldn't set the text to be empty. WHO KNOWS. KIVY BE CRAZY.
            self.label.text = " "
            self.label.texture_update()
            self.label.text = self._text
            self.label.texture_update()
            self.text_image_size = self.label.texture_size
            self.image = Myrmidon_Backend.Image(self.label._label.texture)


        def get_screen_draw_position(self):
            """ Overriding entity method to account for text alignment. """
            draw_x, draw_y = self.x, self.y

            if self.alignment == ALIGN_TOP:
                draw_x -= (self.text_image_size[0]/2)
            elif self.alignment == ALIGN_TOP_RIGHT:
                draw_x -= self.text_image_size[0]
            elif self.alignment == ALIGN_CENTER_LEFT:
                draw_y -= (self.text_image_size[1]/2)
            elif self.alignment == ALIGN_CENTER:
                draw_x -= (self.text_image_size[0]/2)
                draw_y -= (self.text_image_size[1]/2)
            elif self.alignment == ALIGN_CENTER_RIGHT:
                draw_x -= self.text_image_size[0]
                draw_y -= (self.text_image_size[1]/2)
            elif self.alignment == ALIGN_BOTTOM_LEFT:
                draw_y -= self.text_image_size[1]
            elif self.alignment == ALIGN_BOTTOM:
                draw_x -= (self.text_image_size[0]/2)
                draw_y -= self.text_image_size[1]
            elif self.alignment == ALIGN_BOTTOM_RIGHT:
                draw_x -= self.text_image_size[0]
                draw_y -= self.text_image_size[1]

            return draw_x, draw_y


        # text
        @property
        def text(self):
             return self._text

        @text.setter
        def text(self, value):
            #if not self._text == value:
            self._text = value#str(value)
            self.generate_text_image()


        @text.deleter
        def text(self):
            self._text = ""
            self.generate_text_image()
