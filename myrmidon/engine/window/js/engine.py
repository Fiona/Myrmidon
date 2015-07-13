"""
Myrmidon
Copyright (c) 2015 Fiona Burrows

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

A pypyjs-based window creation and handling backend.

"""

import js

class Myrmidon_Backend(object):

    callback_wrapper = None
    target_fps = 30

    def set_window_loop(self, callback, target_fps = 30):
        # When you use browser callbacks you have to tell pypyjs specifically
        # to keep references to things around or they are cleaned up
        # by the garbage collector. So we wrap the callback in this decorator.
        self.callback = js.Method(callback)
        self.target_fps = target_fps

    def open_window(self):
        js.globals.setInterval(self.callback, 1000/self.target_fps)

    def app_loop_tick(self):
        """Runs once every frame before any entity code or rendering."""
        pass
        
    class Clock(object):
        def get_fps(self):
            return 0
        
        def tick(self, fps_rate):
            pass

    def change_resolution(self, resolution):
        pass

    class Font(object):
        pass

    @classmethod	
    def load_font(cls, filename = None, size = 20):
        return cls.Font
    
