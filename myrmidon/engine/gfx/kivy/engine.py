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
import math

from myrmidon import Game, Entity, BaseImage, MyrmidonError
from myrmidon.consts import *

import kivy
from kivy.core.image import Image as Kivy_Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Scale, Rotate, PushMatrix, PopMatrix, Translate, Quad, Ellipse, Line
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.graphics.opengl import glBlendFunc, glBlendFuncSeparate, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE


class Myrmidon_Backend(Entity):

    clear_colour = (0.0, 0.0, 0.0, 1.0)
    letter_box_border_colour = (0.0, 0.0, 0.0, 1.0)
    draw_list_dirty = True
    entity_list_draw_order = []
    letter_boxes = []
    device_resolution = None
    
    def __init__(self):
        # Try hiding soft keys on certain android phones
        self.get_device_size_metrics()
        self.entity_draws = {}
        self.widget = None

    def get_device_size_metrics(self):
        self.device_resolution = Window.width, Window.height
        if Game.screen_size_adjustment_compatability_mode:
            Game.device_scale = float(Window.height) / Game.screen_resolution[1]
        else:
            Game.device_scale = float(Window.width) / Game.screen_resolution[0]
        # If any y position adjustment is necessary cos aspect ratio is lower than ideal
        Game.global_x_pos_adjust = 0.0
        Game.global_y_pos_adjust = 0.0
        if float(self.device_resolution[0]) / self.device_resolution[1] < float(Game.screen_resolution[0]) / Game.screen_resolution[1]:
            if Game.screen_size_adjustment_compatability_mode:
                Game.global_x_pos_adjust = float((Game.screen_resolution[0] * Game.device_scale) - self.device_resolution[0]) / 2
            else:
                Game.global_y_pos_adjust = float((Game.screen_resolution[1] * Game.device_scale) - self.device_resolution[1]) / 2

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
        if self.draw_list_dirty:
            self.widget.canvas.clear()
            self.entity_draws = {}
            self.letter_boxes = []

            #self.entity_list_draw_order = copy.copy(entity_list)
            self.entity_list_draw_order = entity_list
            self.entity_list_draw_order.sort(
                key=lambda object:
                object.z if hasattr(object, "z") else 0,
                reverse = True
                )
            self.draw_list_dirty = False

        # Now render for each entity
        for entity in self.entity_list_draw_order:
            if not entity.drawing:
                continue

            if entity.image and getattr(entity.image, "image", None) and entity.image.width and entity.image.height:
                platform.glBlendFunc()
                # Work out the real width/height and screen position of the entity
                size = ((entity.image.width) * (entity.scale * Game.device_scale), (entity.image.height) * (entity.scale * Game.device_scale))
                x, y = entity.get_screen_draw_position()
                y = Game.screen_resolution[1] - (entity.image.height * entity.scale) - y
                if Game.screen_size_adjustment_compatability_mode:
                    pos = ((x * Game.device_scale) - Game.global_x_pos_adjust, y * Game.device_scale)
                else:
                    pos = ((x * Game.device_scale) - Game.global_x_pos_adjust, (y * Game.device_scale) - Game.global_y_pos_adjust)
                cen = entity.get_centre_point()

                # Figure out how the textures are drawn to accommodate for image flippery
                w, h = self.get_dimensions_for_texture_coords(entity.image.width, entity.image.height)
                tex_coords = (0, h, w, h, w, 0, 0, 0)
                if entity.flip_vertical and entity.flip_horizontal:
                    tex_coords = (w, 0, 0, 0, 0, h, w, h)
                elif entity.flip_vertical:
                    tex_coords = (0, 0, w, 0, w, h, 0, h)
                elif entity.flip_horizontal:
                    tex_coords = (w, h, 0, h, 0, 0, w, 0)

                # If this entity hasn't yet been attached to the canvas then do so
                if entity not in self.entity_draws:
                    self.entity_draws[entity] = dict()
                    with self.widget.canvas:
                        self.entity_draws[entity]['color'] = color = Color()
                        platform.apply_rgb(entity, color)
                        color.a = entity.alpha
                        PushMatrix()
                        self.entity_draws[entity]['translate'] = Translate()
                        self.entity_draws[entity]['translate'].xy = pos
                        self.entity_draws[entity]['rotate'] = Rotate()
                        self.entity_draws[entity]['rotate'].angle = entity.rotation
                        self.entity_draws[entity]['rotate'].axis = (0, 0, -1)
                        self.entity_draws[entity]['rotate'].origin = (cen[0] * entity.scale * Game.device_scale, size[1] - (cen[1] * entity.scale * Game.device_scale))
                        self.entity_draws[entity]['rect'] = Quad(
                            texture = entity.image.image.texture,
                            points = (0.0, 0.0, size[0], 0.0, size[0], size[1], 0.0, size[1]),
                            tex_coords = tex_coords,
                            )
                        PopMatrix()
                    # Otherwise just update values
                else:
                    self.entity_draws[entity]['rotate'].angle = entity.rotation
                    self.entity_draws[entity]['rotate'].origin = (cen[0] * entity.scale * Game.device_scale, size[1] - (cen[1] * entity.scale * Game.device_scale))                    
                    self.entity_draws[entity]['translate'].xy = pos
                    color = self.entity_draws[entity]['color']
                    platform.apply_rgb(entity, color)
                    color.a = entity.alpha
                    self.entity_draws[entity]['rect'].texture = entity.image.image.texture
                    self.entity_draws[entity]['rect'].points = (0.0, 0.0, size[0], 0.0, size[0], size[1], 0.0, size[1])
                    self.entity_draws[entity]['rect'].tex_coords = tex_coords

            entity.draw()

        # Draw letterbox squares over the top and bottom
        if not len(self.letter_boxes):
            for i in range(2):
                if Game.screen_size_adjustment_compatability_mode:
                    continue
                self.letter_boxes.append(dict())
                with Game.engine['gfx'].widget.canvas:
                    self.letter_boxes[i]['color'] = Color()
                    self.letter_boxes[i]['color'].rgba = self.letter_box_border_colour
                    PushMatrix()
                    self.letter_boxes[i]['translate'] = Translate()
                    if i:
                        self.letter_boxes[i]['translate'].xy = (0, self.device_resolution[1] - abs(Game.global_y_pos_adjust))
                    else:
                        self.letter_boxes[i]['translate'].xy = (0, 0)                        
                    self.letter_boxes[i]['rect'] = Quad(
                        points = (0.0, 0.0, self.device_resolution[0], 0.0, self.device_resolution[0], abs(Game.global_y_pos_adjust), 0.0, abs(Game.global_y_pos_adjust))
                        )
                    PopMatrix()                

    def get_dimensions_for_texture_coords(self, o_width, o_height):
        """Returns two values between 0 and 1 representing the width and height of
        an image ready to use for texture coords. It takes into account the padding
        added by raising a texture to power of 2."""
        # Get the real texture coords (we work this out as the value is hidden by kivy)
        texture_dimensions = [0, 0]
        for k,val in enumerate((o_width, o_height)):
            if self.is_pot(val):
                texture_dimensions[k] = val
            else:
                texture_dimensions[k] = self.raise_to_next_pot(val)
        return (float(o_width) / texture_dimensions[0], float(o_height) / texture_dimensions[1])
        
    def is_pot(self, val):
        """Returns a boolean indicating if the passed number of a power of two."""
        is_pot = True
        while(val != 1 and val > 0):
            if(val % 2):
                return False
            val = val / 2
        return is_pot and (val > 0)

    def raise_to_next_pot(self, val):
        """Raises the past value to the next power of 2 in sequence."""
        return int(math.pow(2, math.ceil(math.log(val, 2))))

    def draw_single_entity(self, entity):
        pass

    def create_texture_list(self, entity, image):
        return None

    def draw_textured_quad(self, width, height, repeat = None):
        pass

    def register_entity(self, entity):
        self.draw_list_dirty = True

    def remove_entity(self, entity):
        self.draw_list_dirty = True

    def alter_x(self, entity, x):
        pass

    def alter_y(self, entity, y):
        pass

    def alter_z(self, entity, z):
        self.draw_list_dirty = True

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

    def alter_display(self, entity, display):
        self.draw_list_dirty = True

    def new_image(self, width, height, colour = None):
        return Myrmidon_Backend.Image()

    def draw_line(self, start, finish, colour = (1.0,1.0,1.0,1.0), width = 5.0, noloadidentity = False):
        pass

    def draw_circle(self, position, radius, colour = (1.0,1.0,1.0,1.0), width = 5.0, filled = False, accuracy = 24, noloadidentity = False):
        pass

    def draw_rectangle(self, top_left, bottom_right, colour = (1.0,1.0,1.0,1.0), filled = True, width = 2.0, noloadidentity = False):
        pass

    def rgb_to_colour(self, colour):
        colour = list(colour)
        if kivy.platform in ['ios', 'macosx'] and len(colour) > 3:
            pre_multiply = colour[3] / 255.0
        else:
            pre_multiply = 1.0
        for k,a in enumerate(colour):
            colour[k] = ((a/255.0) * (pre_multiply if k < 3 else 1.0))
        return colour

    class Image(object):
        EMPTY_IMAGE = Kivy_Image(Texture.create(size=(0, 0)), nocache=True)

        width = 0
        height = 0
        filename = None
        is_sequence_image = False

        def __init__(self, image = None, sequence = False, width = None, height = None, mipmap = True):
            if image is None:
                self.image = self.EMPTY_IMAGE
                self.width = 0
                self.height = 0
                return
            if isinstance(image, str):
                self.filename = image
                try:
                    self.image = Kivy_Image(image, mipmap = mipmap)
                except:
                    raise MyrmidonError("Couldn't load image from " + image)
            else:
                self.image = Kivy_Image(image, nocache=True)
            self.width = self.image.width
            self.height = self.image.height

        def destroy(self):
            """
            Explicitly removes this image from the video memory and
            Kivy's cache.
            This functionality requires the custom kivy version at
            http://github.com/arcticshores/kivy
            """
            if self.image is None or self.image is self.EMPTY_IMAGE:
                return

            from kivy.graphics.opengl import glBindTexture, glDeleteTextures
            from kivy.logger import Logger

            Logger.debug("MyrmidonGFX: Destroying {0}".format(self.filename if self.filename else self.image))

            # Remove from cache
            if not self.image.nocache:
                self.image.remove_from_cache()

            # Convert the ID to the right byte format for the GL method
            a1 = (self.image.texture.id >>  0) & 0xFF
            a2 = (self.image.texture.id >>  8) & 0xFF
            a3 = (self.image.texture.id >> 16) & 0xFF
            a4 = (self.image.texture.id >> 24) & 0xFF

            # Remove texture completely
            glBindTexture(self.image.texture.target, 0)
            glDeleteTextures(1, bytes(bytearray([a1, a2, a3, a4])))

            # Since we've done a manual removal kivy shouldn't do it's own removal later
            self.image.texture.nofree = 1

            # Stop this image from being used as a texture now
            self.image = None

    class _Polygon(Entity):
        """ This class encapsulates a primitive shape entity """

        @property
        def line_width(self):
            return self._line_width

        @line_width.setter
        def line_width(self, line_width):
            # if shape switches from filled to non-filled or vice-versa, the shape object must be replaced in the draw
            # list, so mark it for clearing
            if (line_width <= 0) != (self._line_width <= 0):
                Game.engine['gfx'].draw_list_dirty = True
            self._line_width = line_width

        def __init__(self, x, y, line_width=0):
            Entity.__init__(self)
            self.x = x
            self.y = y
            self._line_width = line_width
            self.status = S_FREEZE
            self._width = 0
            self._height = 0

        def draw(self):

            engine = Game.engine['gfx']

            platform.glBlendFunc()
            # Work out the real width/height and screen position of the entity
            size = (self._width * (self.scale * Game.device_scale),
                    self._height * (self.scale * Game.device_scale))
            x, y = self.get_screen_draw_position()
            y = Game.screen_resolution[1] - (self._height * self.scale) - y
            if Game.screen_size_adjustment_compatability_mode:
                pos = ((x * Game.device_scale) - Game.global_x_pos_adjust,
                        y * Game.device_scale)
            else:
                pos = ((x * Game.device_scale) - Game.global_x_pos_adjust,
                       (y * Game.device_scale) - Game.global_y_pos_adjust)
            cen = self.get_centre_point()

            # If this entity hasn't yet been attached to the canvas then do so
            if self not in engine.entity_draws:
                engine.entity_draws[self] = dict()
                with engine.widget.canvas:
                    engine.entity_draws[self]['color'] = color = Color()
                    PushMatrix()
                    engine.entity_draws[self]['translate'] = Translate()
                    engine.entity_draws[self]['rotate'] = Rotate()
                    engine.entity_draws[self]['rotate'].axis = (0, 0, -1)
                    engine.entity_draws[self]['scale'] = Scale()
                    engine.entity_draws[self]['rect'] = self._create_shape()
                    PopMatrix()

            # update values
            color = engine.entity_draws[self]['color']
            platform.apply_rgb(self, color)
            color.a = self.alpha
            engine.entity_draws[self]['translate'].xy = pos
            engine.entity_draws[self]['rotate'].angle = self.rotation
            engine.entity_draws[self]['rotate'].origin = (cen[0] * self.scale * Game.device_scale,
                                                          size[1] - (cen[1] * self.scale * Game.device_scale))
            engine.entity_draws[self]['scale'].xyz = (self.scale * (-1 if self.flip_horizontal else 1),
                                                      self.scale * (-1 if self.flip_vertical else 1),
                                                      1.0)
            self._update_shape(engine.entity_draws[self]['rect'], cen, size)

        def _create_shape(self):
            pass

        def _update_shape(self, shape, cen, size):
            pass

        def get_centre_point(self):
            """overridden to return centre of polygon if not set"""
            if -1 in self.centre_point:
                return self._width / 2, self._height / 2
            else:
                return self.centre_point

    class Rectangle(_Polygon):

        @property
        def width(self):
            return self._width

        @width.setter
        def width(self, width):
            self._width = width
            self._points_dirty = True

        @property
        def height(self):
            return self._height

        @height.setter
        def height(self, height):
            self._height = height
            self._points_dirty = True

        def __init__(self, x, y, width, height, colour=(1.0, 1.0, 1.0), line_width=0):
            self._points_dirty = True
            Myrmidon_Backend._Polygon.__init__(self, x, y, line_width)
            self._width = width
            self._height = height
            self.colour = colour

        def _create_shape(self):
            if self._line_width <= 0:
                return Rectangle()
            else:
                self._points_dirty = True
                return Line()

        def _update_shape(self, shape, cen, size):
            if self._line_width <= 0:
                # rectangle object for filled shape
                shape.size = self._width*Game.device_scale, self._height*Game.device_scale
            else:
                # line obejct for non-filled shape
                if self._points_dirty:
                    shape.rectangle = (0, 0, self._width*Game.device_scale, self._height*Game.device_scale)
                    self._points_dirty = False
                shape.width = self.line_width

    class Ellipse(_Polygon):

        @property
        def width(self):
            return self._width

        @width.setter
        def width(self, width):
            self._width = width
            self._points_dirty = True

        @property
        def height(self):
            return self._height

        @height.setter
        def height(self, height):
            self._height = height
            self._points_dirty = True

        @property
        def start_angle(self):
            return self._start_angle

        @start_angle.setter
        def start_angle(self, start_angle):
            self._start_angle = start_angle
            self._points_dirty = True

        @property
        def end_angle(self):
            return self._end_angle

        @end_angle.setter
        def end_angle(self, end_angle):
            self._end_angle = end_angle
            self._points_dirty = True

        def __init__(self, x, y, width, height, colour=(1.0, 1.0, 1.0), line_width=0, start_angle=0, end_angle=360):
            self._points_dirty = True
            self._start_angle = start_angle
            self._end_angle = end_angle
            Myrmidon_Backend._Polygon.__init__(self, x, y, line_width)
            self._width = width
            self._height = height
            self.colour = colour

        def _create_shape(self):
            if self._line_width <= 0:
                return Ellipse(segments=32)
            else:
                self._points_dirty = True
                return Line()

        def _update_shape(self, shape, cen, size):
            # kivy's ellipse angles appear to start at the top of the ellipse rather than to the right, so add 90
            # degrees. Also it doesn't seem to work unless the end angle is greater than the start, so add 360 to end
            # angle if necessary
            ang_start = self._start_angle + 90
            ang_end = self._end_angle + 90 + (360 if self._end_angle+90 < self._start_angle+90 else 0)
            if self._line_width <= 0:
                # ellipse object for filled shape
                shape.size = self._width*Game.device_scale, self._height*Game.device_scale
                shape.angle_start = ang_start
                shape.angle_end = ang_end
            else:
                # line object for non-filled shape
                if self._points_dirty:
                    shape.ellipse = (0, 0, self._width*Game.device_scale, self._height*Game.device_scale,
                                     ang_start, ang_end, 32)
                    self._points_dirty = False
                shape.width = self.line_width

    class Line(_Polygon):

        @property
        def points(self):
            return self._points

        @points.setter
        def points(self, points):
            self._points = points
            min_x = min([p[0] for p in points])
            max_x = max([p[0] for p in points])
            min_y = min([p[1] for p in points])
            max_y = max([p[1] for p in points])
            self._width = max_x - min_x
            self._height = max_y - min_y
            self._points_dirty = True

        def __init__(self, x, y, points, colour=(1.0, 1.0, 1.0), line_width=1, closed=False):
            self._points_dirty = True
            self.closed = closed
            Myrmidon_Backend._Polygon.__init__(self, x, y, line_width)
            self.points = points
            self.colour = colour

        def _create_shape(self):
            self._points_dirty = True
            return Line()

        def _update_shape(self, shape, cen, size):
            if self._points_dirty:
                # only reassign the points list if it has changed
                shape.points = sum([[p[0]*Game.device_scale,
                                     (self._height-p[1])*Game.device_scale] for p in self._points], [])
                self._points_dirty = False
            shape.close = self.closed
            shape.width = self.line_width

    class _Text(Entity):
        _alignment = ALIGN_CENTER
        label = None
        _text = ""
        _font = None
        _antialias = True

        text_image_size = (0,0)

        _shadow = None

        def generate_label(self):
            if not self.label:
                if self.font is not None:
                    self.label = Label(font_name=self.font.filename, font_size=self.font.size, mipmap=True)
                else:
                    self.label = Label(font_size="30", mipmap=True)
            return self.label

        def __init__(self, font, x, y, alignment, text, antialias=True):
            Entity.__init__(self)
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

        def _update_centre_point(self, alignment):
            w, h = self.text_image_size
            if alignment == ALIGN_TOP_LEFT:
                self.centre_point = 0, 0
            elif alignment == ALIGN_TOP:
                self.centre_point = w/2, 0
            elif alignment == ALIGN_TOP_RIGHT:
                self.centre_point = w, 0
            elif alignment == ALIGN_CENTRE_LEFT:
                self.centre_point = 0, h/2
            elif alignment == ALIGN_CENTRE:
                self.centre_point = w/2, h/2
            elif alignment == ALIGN_CENTRE_RIGHT:
                self.centre_point = w, h/2
            elif alignment == ALIGN_BOTTOM_LEFT:
                self.centre_point = 0, h
            elif alignment == ALIGN_BOTTOM:
                self.centre_point = w/2, h
            elif alignment == ALIGN_BOTTOM_RIGHT:
                self.centre_point = w, h

        @property
        def alignment(self):
            return self._alignment

        @alignment.setter
        def alignment(self, alignment):
            self._alignment = alignment
            self._update_centre_point(alignment)

        # text
        @property
        def text(self):
             return self._text

        @text.setter
        def text(self, value):
            if self._text == value:
                return
            self._text = value
            self.destroy_text_image()
            self.generate_text_image()

        @text.deleter
        def text(self):
            self._text = ""
            self.destroy_text_image()
            self.generate_text_image()

        def on_exit(self):
            self.destroy_text_image()

        def destroy_text_image(self):
            """Destroy the underlying image."""
            if self.image:
                self.image.destroy()
                self.image = None

    class DefaultText(_Text):
        def generate_text_image(self):
            label = self.generate_label()
            label.text = " " if self._text == "" else self._text
            label.texture_update()
            if not label.texture:
                self.text_image_size = (0, 0)
                self.image = Myrmidon_Backend.Image()
                return

            self.text_image_size = label.texture_size
            self.image = Myrmidon_Backend.Image(label.texture)
            self._update_centre_point(self.alignment)

    class AppleText(_Text):
        def generate_text_image(self):
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            label = self.generate_label()
            label.text = " " if self._text == "" else self._text
            label.texture_update()
            if not label.texture:
                self.text_image_size = (0, 0)
                self.image = Myrmidon_Backend.Image()
                return

            self.text_image_size = label.texture_size
            tex = Texture.create(size=label.texture.size, mipmap=True)
            tex.blit_buffer(label.texture.pixels, colorfmt='rgba', bufferfmt='ubyte')
            tex.flip_vertical()
            self.image = Myrmidon_Backend.Image(tex)
            self._update_centre_point(self.alignment)

    Text = DefaultText
    #Text = {
    #    'ios': AppleText,
    #    'macosx': AppleText,
    #}.get(kivy.platform, DefaultText)


# Platform specific functions
class DefaultPlatform(object):
    @staticmethod
    def glBlendFunc():
        """Blend function for blending images onscreen."""
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    @staticmethod
    def apply_rgb(entity, color):
        """Apply an entity's colour and alpha to a Kivy Colour object."""
        color.rgb = entity.colour


class ApplePlatform(object):
    @staticmethod
    def glBlendFunc():
        glBlendFuncSeparate(GL_ONE, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    @staticmethod
    def apply_rgb(entity, color):
        color.rgb = entity.alpha, entity.alpha, entity.alpha


platform = DefaultPlatform
#platform = {
#    'ios': ApplePlatform,
#    'macosx': ApplePlatform,
#}.get(kivy.platform, DefaultPlatform)
