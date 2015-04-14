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


import os, pygame, math, numpy

from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from myrmidon import Game, Entity, BaseImage, MyrmidonError
from myrmidon.consts import *


class Myrmidon_Backend(object):

    clear_colour = (0.0, 0.0, 0.0, 1.0)

    z_order_dirty = True
    entities_z_order_list = []
    last_image = None
    text_coords = numpy.array([1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0])
        
    def __init__(self):
        glClearColor(*self.clear_colour)
        glClear(GL_COLOR_BUFFER_BIT)

        glViewport(0, 0, Game.screen_resolution[0], Game.screen_resolution[1])

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(0, Game.screen_resolution[0], Game.screen_resolution[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LINE_SMOOTH)

        #pygame.display.flip()

    def change_resolution(self, resolution):
        self.__init__()

    def update_screen_pre(self):
        glClear(GL_COLOR_BUFFER_BIT)

    def update_screen_post(self):
        pygame.display.flip()

    def draw_entities(self, entity_list):
        if self.z_order_dirty == True:
            self.entities_z_order_list.sort(
                    reverse=True,
                    key=lambda object:
                    object.z if hasattr(object, "z") else 0
                    )
            self.z_order_dirty = False

        self.last_image = None

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, 0, self.text_coords)

        list(map(self.draw_single_entity, self.entities_z_order_list))

        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

    def draw_single_entity(self, entity):
        if not entity.drawing:
            return
                        
        dont_draw = False
                        
        if entity.normal_draw == False or not entity.image or entity.alpha <= 0.0:
            dont_draw = True
                        
        if not dont_draw:
            glPushMatrix()

            # get actual place to draw
            draw_x, draw_y = entity.get_screen_draw_position()

            # Clip the entity if necessary
            # glScissor assumes origin as bottom-left rather than top-left which explains the fudging with the second param
            if not entity.clip is None:
                glEnable(GL_SCISSOR_TEST)
                glScissor(int(entity.clip[0][0]), Game.screen_resolution[1] - int(entity.clip[0][1]) - int(entity.clip[1][1]), int(entity.clip[1][0]), int(entity.clip[1][1]))

            # glrotate works by you translating to the point around which you wish to rotate
            # and applying the rotation you can translate back to apply the real translation
            # position
            # Flipping is also done here.
            if not entity.rotation == 0.0 or entity.flip_vertical or entity.flip_horizontal:
                cen = entity.get_centre_point()
                x = draw_x + (cen[0] * entity.scale)
                y = draw_y + (cen[1] * entity.scale)
                glTranslatef(x, y, 0)
                if not entity.rotation == 0.0:
                    glRotatef(entity.rotation, 0, 0, 1)
                if entity.flip_vertical:
                    glScalef(1.0, -1.0, 1.0)
                if entity.flip_horizontal:
                    glScalef(-1.0, 1.0, 1.0)
                glTranslatef(-x, -y, 0)
                                
            # move to correct draw pos
            glTranslatef(draw_x, draw_y, 0.0)

            # scale if necessary
            if not entity.scale == 1.0:
                glScalef(entity.scale, entity.scale, 1.0)
                                        
            # bending function
            if entity.blend:
                glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                                
            # draw the triangle strip
            glEnable(GL_TEXTURE_2D)
            if not self.last_image == entity.image.surfaces[entity.image_seq]:
                glBindTexture(GL_TEXTURE_2D, entity.image.surfaces[entity.image_seq])
                glVertexPointer(3, GL_FLOAT, 0, entity.image.vertex_data)
                self.last_image = entity.image.surfaces[entity.image_seq]
                                
            glColor4f(entity.colour[0], entity.colour[1], entity.colour[2], entity.alpha)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

            # Set blending back to default
            if entity.blend:
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # Stop clipping
            if not entity.clip == None:
                glDisable(GL_SCISSOR_TEST)
                                
            glPopMatrix()

        entity.draw()

    def register_entity(self, entity):
        self.entities_z_order_list.append(entity)
        self.z_order_dirty = True
        if not entity.image:
            return

    def remove_entity(self, entity):
        self.entities_z_order_list.remove(entity)             

    def alter_x(self, entity, x):
        pass

    def alter_y(self, entity, y):
        pass

    def alter_z(self, entity, z):
        self.z_order_dirty = True

    def alter_image(self, entity, image):
        if not entity.image:
            return
        entity.image.surface = entity.image.surfaces[entity.image_seq]

    def alter_colour(self, entity, colour):
        pass

    def alter_alpha(self, entity, alpha):
        pass

    def alter_scale(self, entity, scale):
        pass

    def alter_rotation(self, entity, rotation):
        pass

    def alter_display(self, entity, display):
        pass

    def new_image(self, width, height, colour = None):
        # We need to work out the nearest power of 2
        h = 16
        while(h < height):
            h = h * 2
        w = 16
        while(w < width):
            w = w * 2

        new_surface = pygame.Surface((w, h), SRCALPHA, 32)
        if not colour == None:
            new_surface.fill((colour[0]*255, colour[1]*255, colour[2]*255), rect = Rect((0,0), (width, height)))
                                
        # Create an image from it
        return MyrmidonGfxOpengl.Image(new_surface)

    def rgb_to_colour(self, colour):
        col = []
        for a in colour:
            col.append(a/255.0)
        return tuple(col)

    class Image(BaseImage):
                
        surfaces = []
        surfaces_draw_lists = []
        surface = None

        vertex_data = []
                
        def __init__(self, image = None, sequence = False, width = None, height = None, for_repeat = False):
            self.is_sequence_image = sequence
            self.surfaces = []
            self.surfaces_draw_lists = []
                        
            if image is None:
                return
                        
            if isinstance(image, str):
                self.filename = image
                try:
                    raw_surface = pygame.image.load(image).convert_alpha()
                except:
                    raise MyrmidonError("Couldn't load image from " + image)
            else:
                raw_surface = image

            self.width = (width if not width == None else raw_surface.get_width())

            if sequence:
                self.height = (width if height == None else height)
                rw = raw_surface.get_width()
                rh = raw_surface.get_height()

                for a in range(0, rh//self.height):
                    for b in range(rw//self.width):
                        surf = pygame.Surface((self.width, self.height), SRCALPHA, 32)
                        surf.blit(raw_surface, (0,0), pygame.Rect((b*self.width, a*self.height), (self.width, self.height)))
                        self.surfaces.append(self.gl_image_from_surface(surf, self.width, self.height, for_repeat))
                        
                self.surface = self.surfaces[:1]
                                
            else:
                self.height = (height if not height == None else raw_surface.get_height())
                self.surface = self.gl_image_from_surface(raw_surface, self.width, self.height, for_repeat)
                self.surfaces.append(self.surface)

            self.generate_vertex_data()

        def generate_vertex_data(self):
            self.vertex_data = numpy.array([float(self.width), float(self.height), 0.0,
                                            0.0, float(self.height), 0.0,
                                            float(self.width), 0.0, 0.0,
                                            0.0, 0.0, 0.0])
                        
        def gl_image_from_surface(self, raw_surface, width, height, for_repeat):
            data = pygame.image.tostring(raw_surface, "RGBA", 0)

            tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex)
            glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )
            if for_repeat:
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            else:
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
            gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, data)             
                                
            return tex

    text_texture_cache = {}


    class _Polygon(Entity):
        """ This class encapsulates a primitive shape entity """

        def __init__(self, x, y, points, closed=True, line_width=0):
            """
            :param x: starting x coordinate
            :param y: starting y coordinate
            :param points: list of 2-tuples containing vertex coordinates of a convex polygon.
                           0,0 is the top-left of the shape. Points should wind clockwise.
            :param closed: if False, and line_width is set, the last line is not connected to the first.
            :param line_width: if greater than 0, polygon is drawn un-filled with the given line width, otherwise
                               polygon is filled. Defaults to 0 (filled)
            """
            Entity.__init__(self)
            self.x = x
            self.y = y
            self._points = points
            self._closed = closed
            self.line_width = line_width
            self.status = S_FREEZE
            self._update_points(points)

        def _update_points(self, points):
            self._points = points
            min_x = min([p[0] for p in points])
            min_y = min([p[1] for p in points])
            max_x = max([p[0] for p in points])
            max_y = max([p[1] for p in points])
            self._width = max_x - min_x
            self._height = max_y - min_y

        def draw(self):

            glPushMatrix()

            # get actual place to draw
            draw_x, draw_y = self.get_screen_draw_position()

            # Clip the entity if necessary
            if not self.clip is None:
                glEnable(GL_SCISSOR_TEST)
                glScissor(int(self.clip[0][0]), Game.screen_resolution[1] - int(self.clip[0][1]) - int(self.clip[1][1]),
                          int(self.clip[1][0]), int(self.clip[1][1]))

            if not self.rotation == 0.0 or self.flip_vertical or self.flip_horizontal:
                cen = self.get_centre_point()
                x = draw_x + (cen[0] * self.scale)
                y = draw_y + (cen[1] * self.scale)
                glTranslatef(x, y, 0)
                if not self.rotation == 0.0:
                    glRotatef(self.rotation, 0, 0, 1)
                if self.flip_vertical:
                    glScalef(1.0, -1.0, 1.0)
                if self.flip_horizontal:
                    glScalef(-1.0, 1.0, 1.0)
                glTranslatef(-x, -y, 0)

            # move to correct draw pos
            glTranslatef(draw_x, draw_y, 0.0)

            # scale if necessary
            if not self.scale == 1.0:
                glScalef(self.scale, self.scale, 1.0)

            # blending function
            if self.blend:
                glBlendFunc(GL_SRC_ALPHA, GL_ONE)

            glDisable(GL_TEXTURE_2D)
            glColor4f(*(list(self.colour)+[self.alpha]))

            if self.line_width <= 0:
                glBegin(GL_TRIANGLE_FAN)
            else:
                glLineWidth(self.line_width)
                glBegin(GL_LINE_LOOP if self._closed else GL_LINE_STRIP)

            for p in self._points:
                glVertex2f(p[0], p[1])

            glEnd()

            glEnable(GL_TEXTURE_2D)

            # Set blending back to default
            if self.blend:
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # Stop clipping
            if self.clip is not None:
                glDisable(GL_SCISSOR_TEST)

            glPopMatrix()

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
            self._update_points(self._calculate_points(width, self._height))

        @property
        def height(self):
            return self._height

        @height.setter
        def height(self, height):
            self._update_points(self._calculate_points(self._width, height))

        def __init__(self, x, y, width, height, colour=(1.0, 1.0, 1.0), line_width=0):
            Myrmidon_Backend._Polygon.__init__(self, x, y, self._calculate_points(width, height), True, line_width)
            self.colour = colour

        def _calculate_points(self, width, height):
            return [(0, 0), (width, 0), (width, height), (0, height)]

    class Ellipse(_Polygon):

        @property
        def width(self):
            return self._width

        @width.setter
        def width(self, width):
            points, closed = self._calculate_points_and_closed(width, self._height, self._start_angle, self._end_angle,
                                                               self.line_width <= 0)
            self._update_points(points)
            self._closed = closed
            self._width = width

        @property
        def height(self):
            return self._height

        @height.setter
        def height(self, height):
            points, closed = self._calculate_points_and_closed(self._width, height, self._start_angle, self._end_angle,
                                                               self.line_width <= 0)
            self._update_points(points)
            self._closed = closed
            self._height = height

        @property
        def start_angle(self):
            return self._start_angle

        @start_angle.setter
        def start_angle(self, start_angle):
            self._start_angle = start_angle
            points, closed = self._calculate_points_and_closed(self._width, self._height, start_angle, self._end_angle,
                                                               self.line_width <= 0)
            self._update_points(points)
            self._closed = closed

        @property
        def end_angle(self):
            return self._end_angle

        @end_angle.setter
        def end_angle(self, end_angle):
            self._end_angle = end_angle
            points, closed = self._calculate_points_and_closed(self._width, self._height, self._start_angle, end_angle,
                                                               self.line_width <= 0)
            self._update_points(points)
            self._closed = closed

        def __init__(self, x, y, width, height, colour=(1.0, 1.0, 1.0), line_width=0, start_angle=0, end_angle=360):
            self._start_angle = start_angle
            self._end_angle = end_angle
            self._width = width
            self._height = height
            points, closed = self._calculate_points_and_closed(width, height, start_angle, end_angle, line_width <= 0)
            Myrmidon_Backend._Polygon.__init__(self, x, y, points, closed, line_width)
            self.colour = colour

        def _calculate_points_and_closed(self, width, height, start_angle, end_angle, filled):
            points = []
            closed = abs(end_angle - start_angle) >= 360
            if filled and not closed:
                points.append((width/2, height/2))
            angle = start_angle
            while angle >= end_angle and angle < 360:
                points.append((width/2 + math.cos(math.radians(angle)) * width/2,
                               height/2 + math.sin(math.radians(angle)) * height/2))
                angle += 360/32.0
            if angle >= 360:
                angle = 0.0
            while angle < end_angle and angle < 360:
                points.append((width/2 + math.cos(math.radians(angle)) * width/2,
                               height/2 + math.sin(math.radians(angle)) * height/2))
                angle += 360/32.0
            if not closed:
                points.append((width/2 + math.cos(math.radians(end_angle)) * width/2,
                               height/2 + math.sin(math.radians(end_angle)) * height/2))
            return points, closed

        def _update_points(self, points):
            self._points = points

    class Line(_Polygon):

        @property
        def points(self):
            return self._points

        @points.setter
        def points(self, points):
            self._update_points(points)

        def __init__(self, x, y, points, colour=(1.0, 1.0, 1.0), line_width=1.0, closed=False):
            Myrmidon_Backend._Polygon.__init__(self, x, y, points, closed, line_width)
            self.colour = colour

    class Text(Entity):
        """ this is the class for all text handling """

        _text = ""
        _font = None
        _antialias = True
        _alignment = ALIGN_CENTRE

        text_image_size = (0, 0)

        _shadow = None
        
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
            self.status = S_FREEZE

        def draw(self):
            if self.image is None:
                return
                        
            glPushMatrix()

            # get actual place to draw
            # get_screen_draw_position returns coordinate where top left corner of quad is intended to go, before
            # rotation but after scaling. Compensate for all this so draw_x and draw_y are were entity's centre should
            # go
            draw_x, draw_y = self.get_screen_draw_position()
            cp_x, cp_y = self.get_centre_point()  # the centre_point property doesnt apply the same logic as the getter
            draw_x += cp_x * self.scale
            draw_y += cp_y * self.scale

            # Clip the entity if necessary
            if not self.clip is None:
                glEnable(GL_SCISSOR_TEST)
                glScissor(int(self.clip[0][0]), Game.screen_resolution[1] - int(self.clip[0][1]) - int(self.clip[1][1]),
                          int(self.clip[1][0]), int(self.clip[1][1]))

            # move to correct pos
            glTranslatef(draw_x, draw_y, 0.0)

            # Rotate
            if self.rotation != 0.0:
                glRotatef(self.rotation, 0, 0, 1)

            # scale
            if self.scale != 1.0 or self.flip_horizontal or self.flip_vertical:
                glScalef(self.scale * (-1.0 if self.flip_horizontal else 1.0),
                         self.scale * (-1.0 if self.flip_vertical else 1.0), 1.0)

            # quad vertices are such that top-left corner is at origin, and centre_point is relative to top-left corner
            # also. translate by -centre_point to put quad's origin in the right place
            glTranslate(-cp_x, -cp_y, 0.0)

            # blending function
            if self.blend:
                glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                                
            # Shadow draw
            glEnable(GL_TEXTURE_2D)
            if not Game.engine['gfx'].last_image == self.image.surfaces[self.image_seq]:
                glBindTexture(GL_TEXTURE_2D, self.image.surfaces[self.image_seq])
                Game.engine['gfx'].last_image = self.image.surfaces[self.image_seq]
                glVertexPointer(3, GL_FLOAT, 0, self.image.vertex_data)
                       
            if self.shadow is not None:
                glTranslatef(2, 2, 0.0)
                glColor4f(self.shadow[0], self.shadow[1], self.shadow[2], self.alpha)
                glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
                glTranslatef(-2, -2, 0.0)
                               
            # draw the triangle strip
            glColor4f(self.colour[0], self.colour[1], self.colour[2], self.alpha)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

            # Set blending back to default
            if self.blend:
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # Stop clipping
            if self.clip is not None:
                glDisable(GL_SCISSOR_TEST)
                                
            glPopMatrix()

        def generate_text_image(self):
            self.image = self.make_texture()
            self._update_centre_point(self.alignment)

        def make_texture(self):
            if self.text == "" or self.font is None:
                self.image = None
                return                        

            if not self.font in Game.engine['gfx'].text_texture_cache:
                Game.engine['gfx'].text_texture_cache[self.font] = {}

            if self.text in Game.engine['gfx'].text_texture_cache[self.font]:
                Game.engine['gfx'].text_texture_cache[self.font][self.text][0] += 1
                self.image = Game.engine['gfx'].text_texture_cache[self.font][self.text][1]
                self.text_image_size = self.image.text_image_size
                return Game.engine['gfx'].text_texture_cache[self.font][self.text][1]
            else:
                Game.engine['gfx'].text_texture_cache[self.font][self.text] = [1, None]
                                
            # Generate a Pygame image based on the current font and settings
            colour = (255 * self.colour[0], 255 * self.colour[1], 255 * self.colour[2])
            font_image = self.font.loaded_font.render(self.text, self.antialias, colour)

            # We need to work out the nearest power of 2 to appease opengl
            # there must be a better way of doing this
            width = font_image.get_width()
            height = font_image.get_height()
                        
            self.text_image_size = (width, height)
                        
            h = 16
            while h < height:
                h *= 2
            w = 16
            while w < width:
                w *= 2
                                
            new_surface = pygame.Surface((w, h), SRCALPHA, 32)
            new_surface.blit(font_image, (0, 0))

            Game.engine['gfx'].text_texture_cache[self.font][self.text][1] = Myrmidon_Backend.Image(new_surface)
            self.image = Game.engine['gfx'].text_texture_cache[self.font][self.text][1]
            self.image.text_image_size = self.text_image_size
            return Game.engine['gfx'].text_texture_cache[self.font][self.text][1]

        def un_assign_text(self, text):
            if self.font in Game.engine['gfx'].text_texture_cache and text in Game.engine['gfx'].text_texture_cache[self.font]:
                Game.engine['gfx'].text_texture_cache[self.font][text][0] -= 1
                if Game.engine['gfx'].text_texture_cache[self.font][text][0] == 0:
                    del(Game.engine['gfx'].text_texture_cache[self.font][text][1])
                    del(Game.engine['gfx'].text_texture_cache[self.font][text])

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

        # alignment
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
            if not self._text == value:
                self.un_assign_text(self._text)
                self._text = str(value)
                self.generate_text_image()

        @text.deleter
        def text(self):
            self.un_assign_text(self._text)
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
                self.un_assign_text(self._text)
                self._font = value
                self.generate_text_image()

        @font.deleter
        def font(self):
            self._font = None
            self.generate_text_image()

        # shadow
        @property
        def shadow(self):
            return self._shadow

        @shadow.setter
        def shadow(self, value):
            if not self._shadow == value:
                self._shadow = value

        @shadow.deleter
        def shadow(self):
            self._shadow = None

        # Deleting
        def on_exit(self):
            self.un_assign_text(self._text)
                        

def frange(start, end=None, inc=None):
    """A range function, that does accept float increments..."""

    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
        
    return L
