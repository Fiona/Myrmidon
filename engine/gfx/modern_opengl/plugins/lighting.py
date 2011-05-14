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

- BACKEND FILE   -
- GRAPHICS PLUGN -

Adds lighting shaders to modern OpenGL rendering.

"""

from OpenGL.GL import *
from OpenGL.GL.shaders import *


class Myrmidon_Engine_Plugin(object):

    # Backend object
    backend = None

    # shader uniform locs
    uniforms = None

    # Max number of lights
    max_light_num = 64

    # Lights list
    lights = []
    
    def __init__(self, backend):
        """
        Plugin is initialised after all backends have been.
        The object for the relevant backend is passed in. (Although it
        can be accessed normally via MyrmidonGame.engine['x']
        """
        self.backend = backend


    def backend_init(self):
        """
        This is called during the backend initialisation when appropriate.
        """
        # Create our shader
        self.backend.shaders.append(
            [self.generate_fragment_shader_glsl(), GL_FRAGMENT_SHADER]
            )

        
    def pre_render(self):
        """
        Called before every render is done. (But after update_screen_pre())
        """
        pass
    

    def pre_during_render(self):
        """
        Called before all the render passes, but the shader has been enabled
        """    
        # Get uniform locations if we don't have them
        if self.uniforms is None:
            self.uniforms = {}
            for light_num in range(self.max_light_num):
                for uniform_name in ["light_x[%d]", "light_y[%d]", "light_radius[%d]", "light_r[%d]", "light_g[%d]", "light_b[%d]", "light_a[%d]", "light_intensity[%d]"]:
                    uniform_name = uniform_name % light_num
                    self.uniforms[uniform_name] = glGetUniformLocation(self.backend.shader_program, uniform_name)
            self.uniforms["lights_count"] = glGetUniformLocation(self.backend.shader_program, "lights_count")

        # Set all the uniform data
        for num in range(self.max_light_num):
            if num >= len(self.lights):
                light = Light()
            else:
                light = self.lights[num]
            glUniform1f(self.uniforms["light_x[%d]" % num], light.x)
            glUniform1f(self.uniforms["light_y[%d]" % num], light.y)
            glUniform1f(self.uniforms["light_r[%d]" % num], light.colour[0])
            glUniform1f(self.uniforms["light_g[%d]" % num], light.colour[1])
            glUniform1f(self.uniforms["light_b[%d]" % num], light.colour[2])
            glUniform1f(self.uniforms["light_a[%d]" % num], light.colour[3])
            glUniform1f(self.uniforms["light_intensity[%d]" % num], light.intensity)
            glUniform1f(self.uniforms["light_radius[%d]" % num], light.radius)

        glUniform1i(self.uniforms["lights_count"], len(self.lights))

    
    def post_render(self):
        """
        Called after every render is done. (But just before update_screen_post())
        """
        pass


    def add_light(self, x = 0.0, y = 1.0, colour = (1.0, 1.0, 1.0, .7), radius = 50.0, intensity = 10.0):
        """
        Use this method to add a new light to the scene.
        """
        if len(self.lights) > self.max_light_num:
            return
        
        new_light = Light()
        new_light.x = x
        new_light.y = y
        new_light.intensity = intensity
        new_light.colour = colour
        new_light.radius = radius
        self.lights.append(new_light)

        
    def remove_light(self, light):
        """
        Kill a light.
        """
        self.lights.remove(light)
        
        
    def generate_fragment_shader_glsl(self):
        return """
uniform float light_x[%(max_light_num)d];
uniform float light_y[%(max_light_num)d];
uniform float light_r[%(max_light_num)d];
uniform float light_g[%(max_light_num)d];
uniform float light_b[%(max_light_num)d];
uniform float light_a[%(max_light_num)d];
uniform float light_intensity[%(max_light_num)d];
uniform float light_radius[%(max_light_num)d];
uniform int lights_count;

vec4 apply_lighting(vec4 pixel, vec2 texcoord)
{

  float distance_to_light;
  int light_num;
  vec3 final_light;
  vec4 colour;

  final_light = vec3(1.0, 1.0, 1.0);
  colour = pixel;
  if(colour.a == 0.0)
    return colour;

  for(light_num = 0; light_num < lights_count; light_num ++)
  {


    distance_to_light = sqrt(
      (
         pow((texcoord.y - light_y[light_num]), 2.0) +
         pow((texcoord.x - light_x[light_num]), 2.0)
      )
    );

    if(distance_to_light < light_radius[light_num])
    {
      float amount = 1.0 - (((distance_to_light / light_radius[light_num]) * 100.0) / 100.0);

      for(int intensity = 0; intensity < light_intensity[light_num]; intensity++)
      {
        final_light.r += light_r[light_num] * amount;
        final_light.g += light_g[light_num] * amount;
        final_light.b += light_b[light_num] * amount;
      }
    }

  }

  colour.r *= final_light.r;
  colour.g *= final_light.g;
  colour.b *= final_light.b;

  return colour;

}
""" % {'max_light_num' : self.max_light_num}


    
class Light(object):
    x = 0.0
    y = 0.0
    colour = (1.0, 1.0, 1.0, .7)
    radius = 50.0
    intensity = 10.0
