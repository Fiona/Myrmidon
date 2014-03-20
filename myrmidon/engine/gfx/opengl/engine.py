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

from myrmidon import Game, Entity, MyrmidonError
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

        pygame.display.flip()
        

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
        if entity.disable_draw or entity.status == S_SLEEP:
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
            if not entity.rotation == 0.0:
                x = draw_x + (entity.image.width/2) * entity.scale
                y = draw_y + (entity.image.height/2) * entity.scale
                glTranslatef(x, y, 0)
                glRotatef(entity.rotation, 0, 0, 1)
                glTranslatef(-x, -y, 0)
                                
            # move to correct draw pos
            glTranslatef(draw_x, draw_y, 0.0)

            # scale if necessary
            if not entity.scale == 1.0:
                glTranslatef(entity.scale_point[0], entity.scale_point[1], 0) 
                glScalef(entity.scale, entity.scale, 1.0)             
                glTranslatef(-entity.scale_point[0], -entity.scale_point[1], 0)
                                        
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

        
    def draw_textured_quad(self, width, height, repeat = None, tex_offset = None):
        if repeat == None:
            tex_coords = (1.0, 1.0)
            tex_offset = (0.0, 0.0)
        else:
            tex_coords = (width / repeat.width, height / repeat.height)
            if not tex_offset == None:
                tex_offset = ((tex_offset[0] / repeat.width) * .1, (tex_offset[1] / repeat.height) * .1)
            else:
                tex_offset = (0.0, 0.0)
                                
        glBegin(GL_TRIANGLE_STRIP)

        # top right
        glTexCoord2f(tex_coords[0] + tex_offset[0], tex_coords[1] + tex_offset[1])
        glVertex3f(width, height, 0.0)

        # top left
        glTexCoord2f(0.0 + tex_offset[0], tex_coords[1] + tex_offset[1])
        glVertex3f(0.0, height, 0.0)

        # bottom right
        glTexCoord2f(tex_coords[0] + tex_offset[0], 0.0 + tex_offset[1])
        glVertex3f(width, 0.0, 0.0)             

        # bottom left
        glTexCoord2f(0.0 + tex_offset[0], 0.0 + tex_offset[1])
        glVertex3f(0.0, 0.0, 0.0)
                
        glEnd()


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

                        
    def draw_line(self, start, finish, colour = (1.0,1.0,1.0,1.0), width = 5.0, noloadidentity = False):
        gradient = True if hasattr(colour[0], "__iter__") else False

        if not noloadidentity:
            glPushMatrix()
                        
        glLineWidth(width)
                
        glDisable(GL_TEXTURE_2D)
                
        glBegin(GL_LINES)
        glColor4f(*(colour if not gradient else colour[0]))
        glVertex2f(start[0], start[1])
        if gradient:
            glColor4f(*colour[1])
        glVertex2f(finish[0], finish[1])
        glEnd()

        if not noloadidentity:
            glPopMatrix()


    def draw_circle(self, position, radius, colour = (1.0,1.0,1.0,1.0), width = 5.0, filled = False, accuracy = 24, noloadidentity = False):
        if not noloadidentity:
            glPushMatrix()
                        
        glDisable(GL_TEXTURE_2D)

        glColor4f(*colour)

        if filled:
            glBegin(GL_TRIANGLE_FAN)
        else:
            glLineWidth(width)
            glBegin(GL_LINE_LOOP)

        for angle in frange(0, math.pi*2, (math.pi*2)/accuracy):
            glVertex2f(position[0] + radius * math.sin(angle), position[1] + radius * math.cos(angle))
        glEnd()
                                          
        glEnable(GL_TEXTURE_2D)

        if not noloadidentity:
            glPopMatrix()


    def draw_rectangle(self, top_left, bottom_right, colour = (1.0,1.0,1.0,1.0), filled = True, width = 2.0, noloadidentity = False):
        four_colours = True if hasattr(colour[0], "__iter__") else False
                
        if not noloadidentity:
            glPushMatrix()
                
        glDisable(GL_TEXTURE_2D)
                
        if filled:
            glBegin(GL_QUADS)
        else:
            glLineWidth(width)
            glBegin(GL_LINE_LOOP)
                        
        glColor4f(*(colour[0] if four_colours else colour))
        glVertex2f(top_left[0], top_left[1])

        if four_colours:                
            glColor4f(*colour[1])
                        
        glVertex2f(bottom_right[0], top_left[1])

        if four_colours:                
            glColor4f(*colour[2])
        glVertex2f(bottom_right[0], bottom_right[1])

        if four_colours:                
            glColor4f(*colour[3])
                        
        glVertex2f(top_left[0], bottom_right[1])
        glEnd()
                                          
        glEnable(GL_TEXTURE_2D)

        if not noloadidentity:
            glPopMatrix()


    def rgb_to_colour(self, colour):
        col = []
        for a in colour:
            col.append(a/255.0)
        return tuple(col)
        

    class Image(object):
                
        surfaces = []
        surfaces_draw_lists = []
        surface = None
        width = 0
        height = 0

        vertex_data = []
                
        def __init__(self, image = None, sequence = False, width = None, height = None, for_repeat = False):
            self.surfaces = []
            self.surfaces_draw_lists = []
                        
            if image == None:
                return
                        
            if isinstance(image, str):
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

                for a in range(0, rh/self.height):
                    for b in range(rw/self.width):
                        surf = pygame.Surface((self.width, self.height), SRCALPHA, 32)
                        surf.blit(raw_surface, (0,0), pygame.Rect((b*self.width, a*self.height), (self.width, self.height)))
                        self.surfaces.append(self.gl_image_from_surface(surf, self.width, self.height, for_repeat))
                        
                self.surface = self.surfaces[:1]
                                
            else:
                self.height = (height if not height == None else raw_surface.get_height())
                self.surface = self.gl_image_from_surface(raw_surface, self.width, self.height, for_repeat)
                self.surfaces.append(self.surface)

            self.generate_vertex_data()
                        
            for surf in self.surfaces:
                self.surfaces_draw_lists.append(self.create_draw_list(surf))


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


        def create_draw_list(self, surface):
            new_list = glGenLists(1)
            glNewList(new_list, GL_COMPILE)
            Game.engine['gfx'].draw_textured_quad(self.width, self.height)
            glEndList()
            return new_list


        def __del__(self):
            for list in self.surfaces_draw_lists:
                glDeleteLists(list, 1)
            for surf in self.surfaces:
                glDeleteTextures(surf)                                


    text_texture_cache = {}
        

    class Text(Entity):
        """ this is the class for all text handling """

        _text = ""
        _font = None
        _antialias = True

        text_image_size = (0,0)

        _shadow = None
        
        def __init__(self, font, x, y, alignment, text, antialias = True):
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
            draw_x, draw_y = self.get_screen_draw_position()

            # Clip the entity if necessary
            if not self.clip is None:
                glEnable(GL_SCISSOR_TEST)
                glScissor(int(self.clip[0][0]), Game.screen_resolution[1] - int(self.clip[0][1]) - int(self.clip[1][1]), int(self.clip[1][0]), int(self.clip[1][1]))

            # Rotate
            if self.rotation != 0.0:
                x = draw_x + (self.image.width/2) * self.scale
                y = draw_y + (entity.image.height/2) * self.scale
                glTranslatef(x, y, 0)
                glRotatef(self.rotation, 0, 0, 1)
                glTranslatef(-x, -y, 0)
                                
            # move to correct draw pos
            glTranslatef(draw_x, draw_y, 0.0)

            # scale if necessary
            if not self.scale == 1.0:
                glTranslatef(self.scale_point[0], self.scale_point[1], 0) 
                glScalef(self.scale, self.scale, 1.0)             
                glTranslatef(-self.scale_point[0], -self.scale_point[1], 0)
                                        
            # bending function
            if self.blend:
                glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                                
            # Shadow draw
            glEnable(GL_TEXTURE_2D)
            if not Game.engine['gfx'].last_image == self.image.surfaces[self.image_seq]:
                glBindTexture(GL_TEXTURE_2D, self.image.surfaces[self.image_seq])
                Game.engine['gfx'].last_image = self.image.surfaces[self.image_seq]
                glVertexPointer(3, GL_FLOAT, 0, self.image.vertex_data)
                       
            if not self.shadow is None:
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
            if not self.clip == None:
                glDisable(GL_SCISSOR_TEST)
                                
            glPopMatrix()

                                
        def generate_text_image(self):
            self.image = self.make_texture()
                        
                        
        def make_texture(self):
            if self.text == "" or self.font == None:
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
            font_image = self.font.render(self.text, self.antialias, colour)

            # We need to work out the nearest power of 2 to appease opengl
            # there must be a better way of doing this
            width = font_image.get_width()
            height = font_image.get_height()
                        
            self.text_image_size = (width, height)
                        
            h = 16
            while(h < height):
                h = h * 2
            w = 16
            while(w < width):
                w = w * 2
                                
            new_surface = pygame.Surface((w, h), SRCALPHA, 32)
            new_surface.blit(font_image, (0, 0))

            Game.engine['gfx'].text_texture_cache[self.font][self.text][1] = Myrmidon_Backend.Image(new_surface)
            self.image = Game.engine['gfx'].text_texture_cache[self.font][self.text][1]
            self.image.text_image_size = self.text_image_size
            return Game.engine['gfx'].text_texture_cache[self.font][self.text][1]
                        

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


        def un_assign_text(self, text):
            if self.font in Game.engine['gfx'].text_texture_cache and text in Game.engine['gfx'].text_texture_cache[self.font]:
                Game.engine['gfx'].text_texture_cache[self.font][text][0] -= 1
                if Game.engine['gfx'].text_texture_cache[self.font][text][0] == 0:
                    del(Game.engine['gfx'].text_texture_cache[self.font][text][1])
                    del(Game.engine['gfx'].text_texture_cache[self.font][text])

                        
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
    "A range function, that does accept float increments..."

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
