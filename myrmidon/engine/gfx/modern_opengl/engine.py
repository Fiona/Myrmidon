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
from numpy import array
from collections import defaultdict

from myrmidon import Game, Entity, MyrmidonError
from myrmidon.consts import *


class Myrmidon_Backend(object):
    plugins = {}
    
    clear_colour = (0.0, 0.0, 0.0, 1.0)
    entities_z_order_list = []

    max_textures = 2

    shaders = []
    shader_program = None

    uniforms = {}
    attributes = {}
    vertex_buffer = None

    textures = []

    def __init__(self):
        Game.load_engine_plugins(self, "gfx")
        
        self.max_textures = glGetInteger(GL_MAX_TEXTURE_IMAGE_UNITS)

        #
        self.init_shaders()
        
        # Set up screen and reset viewport
        glClearColor(*self.clear_colour)
        glClear(GL_COLOR_BUFFER_BIT)
        glViewport(0, 0, Game.screen_resolution[0], Game.screen_resolution[1])

        glMatrixMode(GL_MODELVIEW)	

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
        self.shaders.append([self.generate_vertex_shader_glsl(), GL_VERTEX_SHADER])
        self.shaders.append([self.generate_fragment_shader_glsl(), GL_FRAGMENT_SHADER])

        for x in self.plugins:
            self.plugins[x].backend_init()
        
        shader_objects = []

        for source,type in self.shaders:
            obj = glCreateShader(type)
            glShaderSource(obj, source)
            shader_objects.append(obj)
        try:            
            
            for obj in shader_objects:
                glCompileShader(obj)

            self.shader_program = glCreateProgram()

            for obj in shader_objects:
                glAttachShader(self.shader_program, obj)

            glLinkProgram(self.shader_program)
        except GLError as err:
            print "GLSL linking error", err
            print err.description[:2500]
            sys.exit()
        
        
    def change_resolution(self, resolution):
        self.__init__()


    def update_screen_pre(self):
        glClear(GL_COLOR_BUFFER_BIT)
        for x in self.plugins:
            self.plugins[x].pre_render()


    def update_screen_post(self):
        for x in self.plugins:
            self.plugins[x].post_render()
        pygame.display.flip()


    def draw_entities(self, entity_list):
        if self.z_order_dirty == True:
            self.entities_z_order_list.sort(
                reverse=True,
                key=lambda object:
                    object.z if hasattr(object, "z") else 0
                )
            self.z_order_dirty = False

        glLoadIdentity()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # organise entities by graphic
        entity_by_z = {}
        for g in self.entities_z_order_list:
            if g.image:
                if not g.z in entity_by_z:
                    entity_by_z[g.z] = {}
                
                if not g.image.surfaces[g.image_seq] in entity_by_z[g.z]:
                    entity_by_z[g.z][g.image.surfaces[g.image_seq]] = []
                    
                entity_by_z[g.z][g.image.surfaces[g.image_seq]].append(g)		

        # set active shader program
        glUseProgram(self.shader_program)
        
        try:
            for x in self.plugins:
                self.plugins[x].pre_during_render()
            
            glUniform2f(self.uniforms["screen_resolution"], Game.screen_resolution[0], Game.screen_resolution[1])
            
            # render in batches grouped by texture
            for z_value in entity_by_z:
                pass_entities = {}	

                for img in entity_by_z[z_value]:
                    pass_entities[img] = entity_by_z[z_value][img]			

                    if len(pass_entities) >= self.max_textures:
                        self.render_batch(pass_entities)
                        pass_entities = {}				

                if len(pass_entities) > 0:
                    self.render_batch(pass_entities)
                
        finally:
            glUseProgram(0)

        
    def render_batch(self, entities):
        # Give each image a number for OpenGL to reference them by
        # and bind them
        texture_lookup = {}
        for i,t in enumerate(entities):
            texture_lookup[t] = i
            # Programatically accessing the GL_TEXTURE* globals and activating them
            glActiveTexture(globals()["GL_TEXTURE%d" % i])
            glBindTexture(GL_TEXTURE_2D, t)
            glUniform1i(self.uniforms["textures[%d]" % i], i)

        # OpenGL requires all image slots to be filled, so we throw
        # any old shit in to fill it all up.
        for i in range(len(entities), self.max_textures):
            glActiveTexture(globals()["GL_TEXTURE%d" % i])
            glBindTexture(GL_TEXTURE_2D, self.textures[0])
            glUniform1i(self.uniforms["textures[%d]" % i], i)		

        # Sum all the objects into one giant list and prepare the vertex buffer
        master_entity_list = sum(entities.values(),[])
        self.prepare_vertex_buffers(master_entity_list, texture_lookup)		
        self.vertex_buffer.bind()

        try:
            # tell GL the entity vertex data			
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

            glDrawArrays(GL_QUADS, 0, 4*len(master_entity_list))

        finally:
            self.vertex_buffer.unbind()        
            glDisableVertexAttribArray(self.attributes["position"])
            glDisableVertexAttribArray(self.attributes["color"])
            glDisableVertexAttribArray(self.attributes["texcoord"])


    def prepare_vertex_buffers(self, entities, texture_lookup):
        vertex_array = []

        for i,g in enumerate(entities):	
            cosr = math.cos(g.rotation)
            sinr = math.sin(g.rotation)

            entity_width = g.image.width
            entity_height = g.image.height

            vertex_array.append(
                self.coordinate_transform(-1.0, 1.0, entity_width * g.scale, entity_height * g.scale, cosr, sinr, g.x, g.y)
                + (0.0, 1.0)
                + g.colour
                + (g.alpha,)
                + (0.0, 1.0, texture_lookup[g.image.surfaces[g.image_seq]], 1.0)
                )			
            vertex_array.append(
                self.coordinate_transform(1.0, 1.0, entity_width * g.scale, entity_height * g.scale, cosr, sinr, g.x, g.y)
                + (0.0, 1.0)
                + g.colour
                + (g.alpha,)
                + (1.0, 1.0, texture_lookup[g.image.surfaces[g.image_seq]], 1.0)
                )			
            vertex_array.append(				
                self.coordinate_transform(1.0, -1.0, entity_width * g.scale, entity_height * g.scale, cosr, sinr, g.x, g.y)
                + (0.0, 1.0)
                + g.colour
                + (g.alpha,)
                + (1.0, 0.0, texture_lookup[g.image.surfaces[g.image_seq]], 1.0)
            )		
            vertex_array.append(
                self.coordinate_transform(-1.0, -1.0, entity_width * g.scale, entity_height * g.scale, cosr, sinr, g.x, g.y)
                + (0.0, 1.0)
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


    def register_entity(self, entity):
        self.entities_z_order_list.append(entity)
        self.z_order_dirty = True


    def remove_entity(self, entity):
        self.entities_z_order_list.remove(entity)


    def alter_x(self, entity, x):
        pass


    def alter_y(self, entity, y):
        pass


    def alter_z(self, entity, z):
        self.z_order_dirty = True


    def alter_image(self, entity, image):
        pass


    def alter_colour(self, entity, colour):
        pass


    def alter_alpha(self, entity, alpha):
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
            Game.engine['gfx'].textures.append(self.surface)
            

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
                Game.engine['gfx'].textures.remove(surf)
                
        
    class Text(Entity):
        """ this is the class for all text handling """

        _text = ""
        _font = None
        _antialias = True

        text_image_size = (0,0)
                
        def __init__(self, font, x, y, alignment, text, antialias = True):
            Entity.__init__(self)
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
vec4 apply_lighting(vec4, vec2);

uniform sampler2D textures[%d];
""" % self.max_textures
        
        shader_code += """
void main()
{
"""

        texture_check_if = """
  if(int(gl_TexCoord[0].z) == %d)
  {
    gl_FragColor = apply_lighting((texture2D(textures[%d],gl_TexCoord[0].xy) * gl_Color), gl_FragCoord);
  }"""
        shader_code += " else ".join([texture_check_if % (x,x) for x in range(self.max_textures)])
        
        shader_code += """
  else
  {
    gl_FragColor = vec4(1.0,0.0,0.0,1.0);
  }

}
"""

        if not "lighting" in self.plugins:
            shader_code += """
vec4 apply_lighting(vec4 pixel, vec2, texcoord){ return pixel; }
"""
            
        return shader_code
