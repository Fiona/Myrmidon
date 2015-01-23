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

Constants
"""

S_KILL = 0
S_WAKEUP = 1
S_SLEEP = 2
S_FREEZE = 3			

ALIGN_TOP_LEFT = 0
ALIGN_TOP = 1
ALIGN_TOP_RIGHT = 2
ALIGN_CENTER_LEFT = 3
ALIGN_CENTER = 4
ALIGN_CENTER_RIGHT = 5
ALIGN_CENTRE_LEFT = 3
ALIGN_CENTRE = 4
ALIGN_CENTRE_RIGHT = 5
ALIGN_BOTTOM_LEFT = 6
ALIGN_BOTTOM = 7
ALIGN_BOTTOM_RIGHT = 8 

COLLISION_TYPE_RECTANGLE = 'rectangle'
COLLISION_TYPE_CIRCLE = 'circle'
COLLISION_TYPE_POINT = 'point'

# BEWARE - HERE BE HACKS
# This used to do this all the time, but it breaks when you're
# not using PyGame as the input. Unfortunately I liked only needing
# one import line. So we check for it instead.
# We're trying catch because it's the default value so it's likely
# that you will import consts before even setting it. Which is bloody
# marvelous.
try:
    from myrmidon.Game import Game
    if Game.engine_def['input'] == "pygame":
        from pygame.locals import *
except ImportError:
    pass
