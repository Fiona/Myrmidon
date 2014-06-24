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
- WINDOW       -

A Kivy-based window creation and handling backend.

"""

from myrmidon import Game, MyrmidonError, BaseFont

import kivy
kivy.require('1.8.0')
from kivy import platform as kivy_platform
if kivy_platform in ['ios', 'android']:
    Game.is_phone = True

# THIS IS HORRIBLE
# KIVY IS HORRIBLE
if not Game.is_phone:
    from kivy.config import Config
    Config.set('graphics', 'resizable', 0)
    Config.set('graphics', 'fullscreen', '1' if Game.full_screen else '0')

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window


class KivyApp(App):
    
    built = False
    
    def build(self):
        self.built = True
        self.widget = KivyApp.App_Widget()
        return self.widget
        
    class App_Widget(Widget):
        def __init__(self, **kwargs):
            super(KivyApp.App_Widget, self).__init__(**kwargs)
            self.size = Game.screen_resolution
        
        def on_touch_down(self, touch):
            if not Game.engine['input'].map_touch_to_mouse:
                return
            Game.engine['input'].mouse.left = True            
            Game.engine['input'].mouse.pos = (
                ((touch.pos[0] + Game.global_x_pos_adjust) / Game.device_scale),
                (Game.engine['gfx'].device_resolution[1]  - touch.pos[1]) / Game.device_scale
                )
            Game.engine['input'].mouse.x = Game.engine['input'].mouse.pos[0]
            Game.engine['input'].mouse.y = Game.engine['input'].mouse.pos[1]

        def on_touch_move(self, touch):
            if not Game.engine['input'].map_touch_to_mouse:
                return
            Game.engine['input'].mouse.pos = (
                ((touch.pos[0] + Game.global_x_pos_adjust) / Game.device_scale),
                (Game.engine['gfx'].device_resolution[1]  - touch.pos[1]) / Game.device_scale
                )
            Game.engine['input'].mouse.x = Game.engine['input'].mouse.pos[0]
            Game.engine['input'].mouse.y = Game.engine['input'].mouse.pos[1]

        def on_touch_up(self, touch):
            if not Game.engine['input'].map_touch_to_mouse:
                return
            Game.engine['input'].mouse.left = False

    
    
class Myrmidon_Backend(object):

    kivy_app = None
    
    def __init__(self):
        self.kivy_app = KivyApp()


    def set_window_loop(self, callback, target_fps = 30):
        Clock.schedule_interval(callback, 1.0 / target_fps)


    def open_window(self):
        self.kivy_app.run()

        
    def Clock(self):            
        return Myrmidon_Backend.Kivy_Clock()
    

    def change_resolution(self, resolution):
        pass
    
                
    def set_title(self, title):
        pass


    class Kivy_Clock(object):
        def get_fps(self):
            return 0
        
        def tick(self, fps_target):
            pass


    class Font(BaseFont):
        loaded_font = None
        
        def __init__(self, font = None, size = 20):
            self.size = size
            self.filename = font
