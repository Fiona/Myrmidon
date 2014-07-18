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
- AUDIO        -

A Kivy driven backend for handling and playing audio.

"""

from myrmidon import BaseAudio
from kivy.core.audio import SoundLoader


class Myrmidon_Backend(object):
    class Audio(BaseAudio):
        sound = None
        def __init__(self, audio = None):
            if audio is None:
                return
            if isinstance(audio, str):
                self.sound = SoundLoader.load(audio)
            else:
                self.sound = audio

        def play(self):
            self.sound.loop = False
            self.sound.play()

        def play_and_loop(self):
            self.sound.loop = True
            self.sound.play()

        def stop(self):
            self.sound.stop()
