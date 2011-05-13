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

Provides an OpenGL-based graphics adaptor, using modern shader
based OpenGL rather than intemediary mode.
Pygame is required for text rendering.

"""


import sys, os, pygame, math

from OpenGL.GL import *
from OpenGL.GL.shaders import *
from OpenGL.arrays import *
from OpenGL.arrays.vbo import *
from OpenGL.GLU import *
from pygame.locals import *
from numpy import array
from collections import defaultdict

from myrmidon.myrmidon import MyrmidonGame, MyrmidonProcess, MyrmidonError
from myrmidon.consts import *


class Myrmidon_Backend(object):

    clear_colour = (0.0, 0.0, 0.0, 1.0)
    processes_z_order_list = []

    max_textures = 2

    vertex_shader = None
    fragment_shader = None
    shader_program = None

    uniforms = {}
    attributes = {}
    vertex_buffer = None

    textures = []

    def __init__(self):
        self.max_textures = glGetInteger(GL_MAX_TEXTURE_IMAGE_UNITS)

        #
        self.init_shaders()
        
        # Set up screen and reset viewport
        glClearColor(*self.clear_colour)
        glClear(GL_COLOR_BUFFER_BIT)
        glViewport(0, 0, MyrmidonGame.screen_resolution[0], MyrmidonGame.screen_resolution[1])

        glMatrixMode(GL_MODELVIEW)	

        # set up depth buffer
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Blending setup
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_CULL_FACE)        
        
        # Get uniform pointer list
        self.uniforms = {}
        for uni in ["screen_resolution"] + ["textures[%d]" % x for x in range(self.max_textures)]:
            self.uniforms[uni] = glGetUniformLocation(self.shader_program, uni)

        # Initialise all vertex attributes
        self.attributes = {}
        for att in ("position","color","texcoord"):
            self.attributes[att] = glGetAttribLocation(self.shader_program, att)	

        # Create global VBO
        self.vertex_buffer = VBO(array([]), target=GL_ARRAY_BUFFER, usage=GL_STREAM_DRAW)


    def init_shaders(self):
        self.vertex_shader = compileShader(self.generate_vertex_shader_glsl(), GL_VERTEX_SHADER)
        self.fragment_shader = compileShader(self.generate_fragment_shader_glsl(), GL_FRAGMENT_SHADER)
        self.shader_program = compileProgram(self.vertex_shader, self.fragment_shader)

    def change_resolution(self, resolution):
        self.__init__()


    def update_screen_pre(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    def update_screen_post(self):
        pygame.display.flip()


    def draw_processes(self, process_list):
        """
        if self.z_order_dirty == True:
        self.processes_z_order_list.sort(
            reverse=True,
            key=lambda object:
            object.z if hasattr(object, "z") else 0
            )
        self.z_order_dirty = False
        """
        #glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # organise processes by graphic
        process_by_image = defaultdict(list)
        for g in process_list:
            if g.image:
                process_by_image[g.image.surfaces[g.image_seq]].append(g)		

        # set active shader program
        glUseProgram(self.shader_program)

        try:
            glUniform2f(self.uniforms["screen_resolution"], MyrmidonGame.screen_resolution[0], MyrmidonGame.screen_resolution[1])

            # render in batches grouped by texture
            pass_processes = {}	
            for img in process_by_image:

                pass_processes[img] = process_by_image[img]			

                if len(pass_processes) >= self.max_textures:
                    self.render_batch(pass_processes)
                    pass_processes = {}				

            if len(pass_processes) > 0:
                self.render_batch(pass_processes)
                
        finally:
            glUseProgram(0)


    def render_batch(self, processes):
        # Give each image a number for OpenGL to reference them by
        # and bind them
        texture_lookup = {}
        for i,t in enumerate(processes):
            texture_lookup[t] = i
            # Programatically accessing the GL_TEXTURE* globals and activating them
            glActiveTexture(globals()["GL_TEXTURE%d" % i])
            glBindTexture(GL_TEXTURE_2D, t)
            glUniform1i(self.uniforms["textures[%d]" % i], i)

        # OpenGL requires all image slots to be filled, so we throw
        # any old shit in to fill it all up.
        for i in range(len(processes), self.max_textures):
            glActiveTexture(globals()["GL_TEXTURE%d" % i])
            glBindTexture(GL_TEXTURE_2D, self.textures[0])
            glUniform1i(self.uniforms["textures[%d]" % i], i)		

        # Sum all the objects into one giant list and prepare the vertex buffer
        master_process_list = sum(processes.values(),[])
        self.prepare_vertex_buffers(master_process_list, texture_lookup)		
        self.vertex_buffer.bind()

        try:
            # tell GL to process vertex data			
            glEnableVertexAttribArray(self.attributes["position"])
            glVertexAttribPointer(
                self.attributes["position"],
                4,
                GL_FLOAT,
                False,
                4*4*3,
                self.vertex_buffer
                )
            
            glEnableVertexAttribArray(self.attributes["color"])
            glVertexAttribPointer(
                self.attributes["color"],
                4,
                GL_FLOAT,
                False,
                4*4*3,
                self.vertex_buffer + (4 * 4)
                )

            glEnableVertexAttribArray(self.attributes["texcoord"])
            glVertexAttribPointer(
                self.attributes["texcoord"],
                4,
                GL_FLOAT,
                False,
                4*4*3,
                self.vertex_buffer + (8 * 4)
                )

            glDrawArrays(GL_QUADS, 0, 4*len(master_process_list))

        finally:
            self.vertex_buffer.unbind()        
            glDisableVertexAttribArray(self.attributes["position"])
            glDisableVertexAttribArray(self.attributes["color"])
            glDisableVertexAttribArray(self.attributes["texcoord"])


    def prepare_vertex_buffers(self, processes, texture_lookup):
        vertex_array = []

        for i,g in enumerate(processes):	
            cosr = math.cos(g.rotation)
            sinr = math.sin(g.rotation)

            process_width = g.image.width
            process_height = g.image.height

            vertex_array.append(
                self.coordinate_transform(-1.0, 1.0, process_width * g.scale, process_height * g.scale, cosr, sinr, g.x, g.y)
                + (g.z, 1.0)
                + g.colour
                + (g.alpha,)
                + (0.0, 1.0, texture_lookup[g.image.surfaces[g.image_seq]], 1.0)
                )			
            vertex_array.append(
                self.coordinate_transform(1.0, 1.0, process_width * g.scale, process_height * g.scale, cosr, sinr, g.x, g.y)
                + (g.z, 1.0)
                + g.colour
                + (g.alpha,)
                + (1.0, 1.0, texture_lookup[g.image.surfaces[g.image_seq]], 1.0)
                )			
            vertex_array.append(				
                self.coordinate_transform(1.0, -1.0, process_width * g.scale, process_height * g.scale, cosr, sinr, g.x, g.y)
                + (g.z, 1.0)
                + g.colour
                + (g.alpha,)
                + (1.0, 0.0, texture_lookup[g.image.surfaces[g.image_seq]], 1.0)
            )		
            vertex_array.append(
                self.coordinate_transform(-1.0, -1.0, process_width * g.scale, process_height * g.scale, cosr, sinr, g.x, g.y)
                + (g.z, 1.0)
                + g.colour
                + (g.alpha,)
                + (0.0, 0.0, texture_lookup[g.image.surfaces[g.image_seq]], 1.0)
                )

        self.vertex_buffer.set_array(array(vertex_array, 'f'))        


    def coordinate_transform(self, qx, qy, w, h, cosr, sinr, px, py):
        x0 = qx * w / 2
        y0 = qy * h / 2
        x1 = x0 * cosr - y0 * sinr
        y1 = x0 * sinr + y0 * cosr
        x2 = x1 + px + w / 2
        y2 = y1 + py + h / 2
        return (x2, y2)


    def register_process(self, process):
        self.processes_z_order_list.append(process)
        self.z_order_dirty = True


    def remove_process(self, process):
        self.processes_z_order_list.remove(process)


    def alter_x(self, process, x):
        pass


    def alter_y(self, process, y):
        pass


    def alter_z(self, process, z):
        self.z_order_dirty = True


    def alter_image(self, process, image):
        pass


    def alter_colour(self, process, colour):
        pass


    def alter_alpha(self, process, alpha):
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
        surfaces = []
        surface = None
        width = 0
        height = 0

        def __init__(self, image = None, sequence = False, width = None, height = None):
            self.surfaces = []

            if image == None:
                return

            if isinstance(image, str):
                try:
                    raw_surface = pygame.image.load(image)#.convert_alpha()
                except:
                    raise MyrmidonError("Couldn't load image from " + image)
            else:
                raw_surface = image

            self.width = (width if not width == None else raw_surface.get_width())
            self.height = (height if not height == None else raw_surface.get_height())
            self.surface = self.gl_image_from_surface(raw_surface, self.width, self.height)
            self.surfaces.append(self.surface)
            MyrmidonGame.engine['gfx'].textures.append(self.surface)
            

        def gl_image_from_surface(self, raw_surface, width, height):
            data = pygame.image.tostring(raw_surface, "RGBA")

            tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, data)
            return tex

        
        def __del__(self):
            for surf in self.surfaces:
                glDeleteTextures(surf)
                MyrmidonGame.engine['gfx'].textures.remove(surf)
                
        
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
            self.z = 0
            self.alignment = alignment
            self.text = text
            self.antialias = antialias
            self._is_text = True
            self.rotation = 0.0

            self.generate_text_image()


        def generate_text_image(self):
            if self.image:
                del self.image
                
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
            
            

    ##################################
    ############ WARNING #############
    ######## HERE BE DRAGONS #########
    ##################################


    def generate_vertex_shader_glsl(self):
        shader_code = """	
uniform vec2 screen_resolution;
	
in vec4 position;
in vec4 color;
in vec4 texcoord;
	
mat4 screen_scale = mat4(
  vec4( 2.0/screen_resolution.x, 0.0, 0.0, 0.0),
  vec4( 0.0, -2.0/screen_resolution.y, 0.0, 0.0),
  vec4( 0.0, 0.0, 1.0, 0.0),
  vec4( 0.0, 0.0, 0.0, 1.0)
);
	
mat4 screen_translate = mat4(
  vec4( 1.0, 0.0, 0.0, 0.0),
  vec4( 0.0, 1.0, 0.0, 0.0),
  vec4( 0.0, 0.0, 1.0, 0.0),
  vec4(-1.0, 1.0, 0.0, 1.0)
);
	
void main()
{
  gl_Position = screen_translate * screen_scale * position;
  gl_TexCoord[0] = texcoord;
  gl_FrontColor = color;						
}
"""

        return shader_code

    
    def generate_fragment_shader_glsl(self):
        shader_code = """
uniform sampler2D textures[%d];
""" % self.max_textures
        
        shader_code += """
void main()
{
"""

        texture_check_if = """
  if(int(gl_TexCoord[0].z) == %d)
  {
    gl_FragColor = texture(textures[%d],gl_TexCoord[0].xy) * gl_Color;
  }"""
        shader_code += " else ".join([texture_check_if % (x,x) for x in range(self.max_textures)])
        
        shader_code += """
  else
  {
    gl_FragColor = vec4(1.0,0.0,0.0,1.0);
  }

}
"""

        return shader_code
