"""
Myrmidon
Copyright (c) 2014 Fiona Burrows
 
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

This is a special Entity that is typically used for fading the
screen in and out, but essentially is a coloured rectangle that
gradually changes from one colour to another.
"""


from myrmidon.Entity import Entity
from myrmidon.Game import Game

class ScreenOverlay(Entity):

    fading = False
    fade_speed = None
    current_colour = (0.0, 0.0, 0.0, 0.0)
    current_colour_from = (0.0, 0.0, 0.0, 0.0)
    current_colour_to = (0.0, 0.0, 0.0, 0.0)
    kill_after_fade = False
    callback = None
    
    def execute(self, colour_from, colour_to, blocking, pos, size, z, callback):
        self.colour_from = colour_from
        self.colour_to = colour_to
        self.blocking = blocking
        self.x, self.y = pos
        self.width, self.height = size
        self.z = z
        self.callback = callback
            
        while True:
            if self.fading:
                for frame,total in self.fade_speed:
                    self.current_colour = (
                        Game.lerp(self.current_colour_from[0], self.current_colour_to[0], frame / total),
                        Game.lerp(self.current_colour_from[1], self.current_colour_to[1], frame / total),
                        Game.lerp(self.current_colour_from[2], self.current_colour_to[2], frame / total),
                        Game.lerp(self.current_colour_from[3], self.current_colour_to[3], frame / total)
                        )
                    yield
                if self.blocking:                        
                    Game.disable_entity_execution = False
                if not self.callback is None:
                    self.callback()
                    self.callback = None
                if self.kill_after_fade:
                    Game.screen_overlay = None
                    self.destroy()
                self.fading = False
            yield


    def fade_from_to(self, fade_speed):
        self.fade_speed = fade_speed
        self.current_colour_from = self.colour_from
        self.current_colour_to = self.colour_to
        self.fading = True
        

    def fade_to_from(self, fade_speed):
        self.fade_speed = fade_speed
        self.current_colour_from = self.colour_to
        self.current_colour_to = self.colour_from
        self.kill_after_fade = True
        self.fading = True
        

    def draw(self):
        Game.engine['gfx'].draw_rectangle(
            (self.x, self.y),
            (self.width, self.height),
            self.current_colour
            )

        # Kivy is special so we make sure that our attached widget is the right colour and size
        # to get the overlay to appear
        if Game.engine_def['gfx'] == "kivy":
            Game.engine['gfx'].entity_widgets[self].rect.pos = (self.x, self.y)
            Game.engine['gfx'].entity_widgets[self].rect.size = (self.width, self.height)
            Game.engine['gfx'].entity_widgets[self].colour.rgba = self.current_colour
        
        
    
