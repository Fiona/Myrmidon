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
- INPUT        -

A pypyjs driven backend for user input.

"""

class Myrmidon_Backend(object):

    keys_pressed = []
    last_keys_pressed = []
    event_store = []
    mouse_buttons_pressed = [False, False, False]
    last_mouse_buttons_pressed = [False, False, False]
    mouse = None
    clear_events = True
    disable_input = False

    def __init__(self):
        self.process_input()

    def process_input(self):
        if not self.mouse:
            self.mouse = self.Mouse()

    def keyboard_key_down(self, key_code):
        return False

    def keyboard_key_released(self, key_code):
        return False

    class Mouse(object):
        x = 0.0
        y = 0.0
        z = -512
        visible = True		
        pos = (0, 0)
        left = False
        middle = False
        right = False
        left_up = False
        middle_up = False
        right_up = False
        wheel_up = False
        wheel_down = False	   
