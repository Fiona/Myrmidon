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


import os, pygame, math

from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from myrmidon.myrmidon import MyrmidonGame, MyrmidonProcess, MyrmidonError
from myrmidon.consts import *

class Myrmidon_Backend(object):

        clear_colour = (0.0, 0.0, 0.0, 1.0)

        z_order_dirty = True
        processes_z_order_list = []
        last_image = None
        
        def __init__(self):
                glClearColor(*self.clear_colour)
                glClear(GL_COLOR_BUFFER_BIT)

                glViewport(0, 0, MyrmidonGame.screen_resolution[0], MyrmidonGame.screen_resolution[1])

                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()

                glOrtho(0, MyrmidonGame.screen_resolution[0], MyrmidonGame.screen_resolution[1], 0, -1, 1)
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
                

        def draw_processes(self, process_list):
                if self.z_order_dirty == True:
                        self.processes_z_order_list.sort(
                                reverse=True,
                                key=lambda object:
                                object.z if hasattr(object, "z") else 0
                                )
                        self.z_order_dirty = False

                self.last_image = None
                
                for process in self.processes_z_order_list:

                        if process.disable_draw:
                                continue
                        
                        dont_draw = False
                                
                        if process.normal_draw == False:
                                dont_draw = True
                        
                        if not process.image or process.alpha <= 0.0 or process.status == S_SLEEP:
                                dont_draw = True

                        if not dont_draw:
                                glPushMatrix()

                                # get actual place to draw
                                draw_x, draw_y = process.get_screen_draw_position()

                                # Clip the process if necessary
                # glScissor assumes origin as bottom-left rather than top-left which explains the fudging with the second param
                                if not process.clip is None:
                                        glEnable(GL_SCISSOR_TEST)
                                        glScissor(int(process.clip[0][0]), MyrmidonGame.screen_resolution[1] - int(process.clip[0][1]) - int(process.clip[1][1]), int(process.clip[1][0]), int(process.clip[1][1]))

                                # glrotate works by you translating to the point around which you wish to rotate
                                # and applying the rotation you can translate back to apply the real translation
                                # position
                                if process.rotation <> 0.0:
                                        x = draw_x + (process.image.width/2) * process.scale
                                        y = draw_y + (process.image.height/2) * process.scale
                                        glTranslatef(x, y, 0)
                                        glRotatef(process.rotation, 0, 0, 1)
                                        glTranslatef(-x, -y, 0)
                                
                                # move to correct draw pos
                                glTranslatef(draw_x, draw_y, 0.0)

                                # scale if necessary
                                if not process.scale == 1.0:
                                        glTranslatef(process.scale_point[0], process.scale_point[1], 0) 
                                        glScalef(process.scale, process.scale, 1.0)             
                                        glTranslatef(-process.scale_point[0], -process.scale_point[1], 0)
                                        
                                # bending function
                                if process.blend:
                                        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                                
                                # draw the triangle strip
                                glEnable(GL_TEXTURE_2D)
                                if not self.last_image == process.image.surfaces[process.image_seq]:
                                        glBindTexture(GL_TEXTURE_2D, process.image.surfaces[process.image_seq])
                                        self.last_image = process.image.surfaces[process.image_seq]
                                glColor4f(process.colour[0], process.colour[1], process.colour[2], process.alpha)
                                glCallList(process.image.surfaces_draw_lists[process.image_seq])

                                # Set blending back to default
                                if process.blend:
                                        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

                                # Stop clipping
                                if not process.clip == None:
                                        glDisable(GL_SCISSOR_TEST)
                                
                                glPopMatrix()

                        process.draw()


        
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


        def register_process(self, process):
                self.processes_z_order_list.append(process)
                self.z_order_dirty = True
                if not process.image:
                        return


        def remove_process(self, process):
                self.processes_z_order_list.remove(process)             
                

        def alter_x(self, process, x):
                pass

        def alter_y(self, process, y):
                pass

        def alter_z(self, process, z):
                self.z_order_dirty = True

        def alter_image(self, process, image):
                if not process.image:
                        return
                process.image.surface = process.image.surfaces[process.image_seq]

        def alter_colour(self, process, colour):
                pass
        
        def alter_alpha(self, process, alpha):
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

                        for surf in self.surfaces:
                                self.surfaces_draw_lists.append(self.create_draw_list(surf))


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
                        MyrmidonGame.engine['gfx'].draw_textured_quad(self.width, self.height)
                        glEndList()
                        return new_list


                def __del__(self):
                        for list in self.surfaces_draw_lists:
                                glDeleteLists(list, 1)
                        for surf in self.surfaces:
                                glDeleteTextures(surf)
                

        class Text(MyrmidonProcess):
                """ this is the class for all text handling """

                _text = ""
                _font = None
                _antialias = True

                text_image_size = (0,0)
                
                def __init__(self, font, x, y, alignment, text, antialias = True):
                        MyrmidonProcess.__init__(self)
                        self.font = font
                        self.x = x
                        self.y = y
                        self.z = -500.0
                        self.alignment = alignment
                        self.text = text
                        self.antialias = antialias
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

                        self.text_image_size = (width, height)

                        h = 16
                        while(h < height):
                                h = h * 2
                        w = 16
                        while(w < width):
                                w = w * 2

                        new_surface = pygame.Surface((w, h), SRCALPHA, 32)
                        new_surface.blit(font_image, (0, 0))

                        # Create an image from it
                        self.image = Myrmidon_Backend.Image(new_surface)
                        

                def get_screen_draw_position(self):
                        """ Overriding process method to account for text alignment. """
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
