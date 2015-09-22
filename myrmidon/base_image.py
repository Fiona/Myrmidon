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

All gfx engine implementations should define their own version of
the Image class as a member of themselves, and should derive from
this base object.
"""

class BaseImage(object):
    # Should be set to the image width and height of each frame, in pixels when loaded.
    # This is not necessarily the size of the entire image.
    width = 0
    height = 0
    
    # Should be set to the image filename if applicable. None indicates that
    # image data was given directly in lieu of a filename.
    filename = None

    # If this Image is a sequence of images and contains a number of frames.
    is_sequence_image = False

    def __init__(self, image = None, sequence = False, width = None, height = None):
        """
        Image objects need to implement this init method. It is perfectly acceptable to
        add any additional keyword arguments that any engine specific image loaders may
        require.
        """
        pass
