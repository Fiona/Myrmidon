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
 
An open source, actor based framework for fast game development for Python.

This is the main file, it have the main MyrmidonGame and MyrmidonProcess objects.
"""


import sys, os, math

from consts import *

class MyrmidonGame(object):

    # Engine related
    started = False

    # Set to true at run-time and Myrmidon will not create a screen,
    # nor will it accept input or execute any processes in a loop.
    # No backend engines are initialised.
    # Any process objects you create will not interate their generator
    # unless you run MyrmidonProcess._iterate_generator manually.
    test_mode = False
    
    engine_def = {
        "window" : "pygame",
        "gfx" : "opengl",
        "input" : "pygame",
        "audio" : "pygame"
        }
    engine_plugin_def = {
        "window" : [],
        "gfx" : [],
        "input" : [],
        "audio" : []
        }
    engine = {
        "window" : None,
        "gfx" : None,
        "input" : None,
        "audio" : None
        }

    current_fps = 30
    fps = 0

    # Display related
    screen_resolution = 1024,768
    lowest_resolution = 800,600
    full_screen = False

    # Process related
    process_list = []
    processes_to_remove = []
    remember_current_process_executing = []
    current_process_executing = None
    process_priority_dirty = True


    @classmethod
    def define_engine(cls, window = None, gfx = None, input = None, audio = None):
        """
        Use this before creating any processes to redefine which engine backends to use.
        """
        if window:
            cls.engine_def['window'] = window
        if gfx:
            cls.engine_def['gfx'] = gfx
        if input:
            cls.engine_def['input'] = input
        if audio:
            cls.engine_def['audio'] = audio

            
    @classmethod
    def define_engine_plugins(cls, window = [], gfx = [], input = [], audio = []):
        """
        Use this before creating any processes to specify which engine plugins you require,
        if any.
        Pass in lists of strings of plugin names.
        """
        cls.engine_plugin_def['window'] = window
        cls.engine_plugin_def['gfx'] = gfx
        cls.engine_plugin_def['input'] = input
        cls.engine_plugin_def['audio'] = audio
            

    @classmethod
    def init_engines(cls):
        # Attempt to dynamically import the required engines 
        try:
            for backend_name in ['window', 'gfx', 'input', 'audio']:
                backend_module = __import__(
                    "engine.%s.%s.engine" % (backend_name, cls.engine_def[backend_name]),
                    globals(),
                    locals(),
                    ['Myrmidon_Backend'],
                    -1
                    )
                cls.engine[backend_name] = backend_module.Myrmidon_Backend()
                
        except ImportError as detail:
            print "Error importing a backend engine.", detail
            sys.exit()
            
        # Test mode uses dummy engines
        if cls.test_mode:
            from backend_dummy import MyrmidonWindowDummy, MyrmidonGfxDummy, MyrmidonInputDummy, MyrmidonAudioDummy
            cls.engine['window'] = MyrmidonWindowDummy()
            cls.engine['gfx'] = MyrmidonGfxDummy()
            cls.engine['input'] = MyrmidonInputDummy()
            cls.engine['audio'] = MyrmidonAudioDummy()
            return
        

    @classmethod
    def load_engine_plugins(cls, engine_object, backend_name):
        # Import plugin modules and create them
        try:
            engine_object.plugins = {}
            if len(cls.engine_plugin_def[backend_name]):
                for plugin_name in  cls.engine_plugin_def[backend_name]:
                    plugin_module = __import__(
                        "engine.%s.%s.plugins.%s" % (backend_name, cls.engine_def[backend_name], plugin_name),
                        globals(),
                        locals(),
                        ['Myrmidon_Backend'],
                        -1
                        )
                    engine_object.plugins[plugin_name] = plugin_module.Myrmidon_Engine_Plugin(engine_object)
                
        except ImportError as detail:
            print "Error importing a backend engine plugin.", detail
            sys.exit()

            
    @classmethod
    def start_game(cls):
        """
        Called by processes if a game is not yet started.
        It initialises engines.
        """
        # Start up the backends
        cls.init_engines()
        cls.clock = cls.engine['window'].Clock()


    @classmethod
    def run_game(cls):
        """
        Called by processes if a game is not yet started.
        Is responsible for the main loop.
        """
        # No execution of anything if in test mode.
        if cls.test_mode:
            return
        
        while cls.started:

            if cls.process_priority_dirty == True:
                cls.process_list.sort(
                    reverse=True,
                    key=lambda object:
                    object.priority if hasattr(object, "priority") else 0
                    )
                cls.process_priority_dirty = False

            if cls.engine['input']:
                cls.engine['input'].process_input()

            cls.processes_to_remove = []
            
            for process in cls.process_list:
                if process.status == 0:
                    cls.current_process_executing = process
                    process._iterate_generator()

            for x in cls.processes_to_remove:
                cls.process_list.remove(x)
                
            cls.engine['gfx'].update_screen_pre()
            cls.engine['gfx'].draw_processes(cls.process_list)              
            cls.engine['gfx'].update_screen_post()

            cls.fps = int(cls.clock.get_fps())
            cls.clock.tick(cls.current_fps)


    @classmethod
    def change_resolution(cls, resolution):
        cls.screen_resolution = resolution
        cls.engine['window'].change_resolution(resolution)
        cls.engine['gfx'].change_resolution(resolution)

        

    ##############################################
    # PROCESSES
    ##############################################
    @classmethod
    def process_register(cls, process):
        """
        Registers a process with Myrmidon so it will be executed.
        """
        cls.process_list.append(process)
        cls.engine['gfx'].register_process(process)
        cls.process_priority_dirty = True

        # Handle relationships
        if cls.current_process_executing != None:
            process.parent = cls.current_process_executing
                
            if not process.parent.child == None:
                process.parent.child.prev_sibling = process
                    
            process.next_sibling = process.parent.child
            process.parent.child = process


    @classmethod        
    def signal(cls, process, signal_code, tree=False):
        """ Signal will let you kill a process or put it to sleep
        
            Will accept a process instance or an ID number to check against one,
            or a process type as a string to check for all of a specific type
        
            The tree parameter can be used to recursively signal all the 
            processes(es) descendants
        
            Signal types-
            S_KILL - Permanently removes the process
            S_SLEEP - Process will disappear and will stop executing code
            S_FREEZE - Process will stop executing code but will still appear
                and will still be able to be checked for collisions.
            S_WAKEUP - Wakes up or unfreezes the process """
        
        # We've entered a specific type as a string
        if type(process) == type(""):
            
            import copy
            process_iter = copy.copy(cls.process_list)
            
            for obj in process_iter:
                if obj.__class__.__name__ == process:
                    cls.single_object_signal(obj, signal_code, tree)
        
        # Passed in an object directly    
        else:
            cls.single_object_signal(process, signal_code, tree)
            return


    @classmethod
    def single_object_signal(cls, process, signal_code, tree = False):
        """ Used by signal as a shortcut """
        
        # do children
        if tree:
            next_child = process.child
            while next_child != None:
                cls.single_object_signal(next_child, signal_code, True)
                next_child = next_child.next_sibling
        
        # do this one
        if signal_code == S_KILL:
            cls.process_destroy(process)
        elif signal_code == S_WAKEUP:
            process.status = 0
        elif signal_code == S_SLEEP:
            process.status = S_SLEEP
        elif signal_code == S_FREEZE:
            process.status = S_FREEZE


    @classmethod
    def process_destroy(cls, process):
        """ Removes a process """
        if not process in MyrmidonGame.process_list:
            return
        process.on_exit()
        cls.engine['gfx'].remove_process(process)
        MyrmidonGame.processes_to_remove.append(process)

        
    ##############################################
    # INPUT
    ##############################################
    @classmethod        
    def keyboard_key_down(cls, key_code):
        """
        Ask if a key is currently being pressed.
        Pass in key codes that is relevant to your chosen input backend.
        """
        if not cls.engine['input']:
            raise MyrmidonError("Input backend not initialised.")
        return cls.engine['input'].keyboard_key_down(key_code)


    @classmethod        
    def keyboard_key_released(cls, key_code):
        """
        Ask if a key has just been released last frame.
        Pass in key codes that is relevant to your chosen input backend.
        """
        if not cls.engine['input']:
            raise MyrmidonError("Input backend not initialised.")
        return cls.engine['input'].keyboard_key_released(key_code)


    ##############################################
    # TEXT HANDLING
    ##############################################
    @classmethod    
    def write_text(cls, x, y, font, alignment = 0, text = "", antialias = True):
        return cls.engine['gfx'].Text(font, x, y, alignment, text, antialias = True)

    @classmethod    
    def delete_text(cls, text):
        if text in MyrmidonGame.process_list:
            MyrmidonGame.process_destroy(text)


    ##############################################
    # HELPFUL MATH
    ##############################################
    @classmethod    
    def get_distance(cls, pointa, pointb):
        return math.sqrt((math.pow((pointb[1] - pointa[1]), 2) + math.pow((pointb[0] - pointa[0]), 2)))

    @classmethod    
    def move_forward(cls, pos, distance, angle):
        pos2 = [0.0,0.0]
        
        pos2[0] = pos[0] + distance * math.cos(math.radians(angle))
        pos2[1] = pos[1] + distance * math.sin(math.radians(angle))             

        return pos2

    @classmethod    
    def angle_between_points(cls, pointa, pointb):
        """
        Take two tuples each containing coordinates between two points and
        returns the angle between those in degrees
        """
        return math.degrees(math.atan2(pointb[1] - pointa[1], pointb[0] - pointa[0]))

    @classmethod 
    def normalise_angle(cls, angle):
        """
        Returns an equivalent angle value between 0 and 360
        """
        """
        while angle < 0.0:
            angle += 360.0
        while angle >= 360.0:
            angle -= 360.0
        return angle
        """
        return angle % 360.0
    
    @classmethod
    def angle_difference(cls, start_angle, end_angle, skip_normalise = False):
        """
        Returns the angle to turn by to get from start_angle to end_angle.
        The sign of the result indicates the direction in which to turn.
        """
        if not skip_normalise:
            start_angle = cls.normalise_angle(start_angle)
            end_angle = cls.normalise_angle(end_angle)
        
        difference = end_angle - start_angle
        if difference > 180.0:
            difference -= 360.0
        if difference < -180.0:
            difference += 360.0
            
        return difference
    
    @classmethod
    def near_angle(cls, curr_angle, targ_angle, increment, leeway = 0):
        """ 
        Returns an angle which has been moved from 'curr_angle' closer to 
        'targ_angle' by 'increment'. increment should always be positive, as 
        angle will be rotated in the direction resulting in the shortest 
        distance to the target angle.
        leeway specifies an acceptable distance from the target to accept,
        allowing you to specify a cone rather than a specific point.
        """
        # Normalise curr_angle
        curr_angle = cls.normalise_angle(curr_angle)
            
        # Normalise targ_angle
        targ_angle = cls.normalise_angle(targ_angle)
            
        # calculate difference
        difference = cls.angle_difference(curr_angle, targ_angle, skip_normalise = True)
            
        # do increment
        if math.fabs(difference) <= leeway:
            return curr_angle
        elif math.fabs(difference) < increment:
            return targ_angle
        else:
            dir = difference / math.fabs(difference)
            return curr_angle + (increment * dir)



class MyrmidonError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)



class MyrmidonProcess(object):

    _x = 0.0
    _y = 0.0
    _z = 0.0
    _priority = 0
    _image = None
    _image_seq = 0
    _colour = (1.0, 1.0, 1.0)
    _alpha = 1.0
    
    scale = 1.0
    rotation = 0.0
    blend = False
    clip = None
    scale_point = [0.0, 0.0]
    disable_draw = False
    normal_draw = True
    status = 0

    parent = None
    child = None
    prev_sibling = None
    next_sibling = None

    _is_text = False
    _generator = None
    
    def __init__(self, *args, **kargs):
        if not MyrmidonGame.started:
            MyrmidonGame.start_game()

        MyrmidonGame.process_register(self)

        self.z = 0.0
        self.x = 0.0
        self.y = 0.0
        self.priority = 0

        MyrmidonGame.remember_current_process_executing.append(MyrmidonGame.current_process_executing)
        MyrmidonGame.current_process_executing = self
        self._generator = self.execute(*args, **kargs)
        self._iterate_generator()
        MyrmidonGame.current_process_executing = MyrmidonGame.remember_current_process_executing.pop()
        
        if not MyrmidonGame.started:
            MyrmidonGame.started = True             
            MyrmidonGame.run_game()
            

    def execute(self):
        """
        This is where the main code for the process lives
        """
        while True:
            yield

    def on_exit(self):
        """
        Called automatically when a process has finished executing for whatever reason.
        Is also called when a process is killed using signal S_KILL.
        """
        pass
        
    def _iterate_generator(self):
        if not MyrmidonGame.started:
            return
        try:
            self._generator.next()
        except StopIteration:
            return
            #self.signal(S_KILL)


    def draw(self):
        """
        Override this to add custom drawing routines to your process.
        """
        pass


    def move_forward(self, distance, angle = None):
        self.x, self.y = MyrmidonGame.move_forward((self.x, self.y), distance, self.rotation if angle == None else angle)

        
    def get_distance(self, pos):
        return MyrmidonGame.get_distance((self.x, self.y), pos)
    
        
    def signal(self, signal_code, tree=False):
        """ Signal will let you kill the process or put it to sleep.
            The 'tree' parameter can be used to signal to a process and all its
            descendant processes (provided an unbroken tree exists)
        
            Signal types-
            S_KILL - Permanently removes the process
            S_SLEEP - Process will disappear and will stop executing code
            S_FREEZE - Process will stop executing code but will still appear
                and will still be able to be checked for collisions.
            S_WAKEUP - Wakes up or unfreezes the process """
        MyrmidonGame.signal(self, signal_code, tree)


    def get_screen_draw_position(self):
        """ At draw time this function is called to determine exactly where
        the process will be drawn. Override this if you need to programatically
        constantly change the position of process.
        Returns a tuple (x,y)"""
        return self.x, self.y
        

    ##############################################
    # Special properties
    ##############################################
    # X
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        MyrmidonGame.engine['gfx'].alter_x(self, self._x)

    @x.deleter
    def x(self):
        self._x = 0.0
        
    # Y
    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        MyrmidonGame.engine['gfx'].alter_y(self, self._y)

    @y.deleter
    def y(self):
        self._y = 0.0

    # depth
    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        if not self._z == value:
            self._z = value
            MyrmidonGame.engine['gfx'].alter_z(self, self._z)

    @z.deleter
    def z(self):
        self._z = 0.0

    # rity
    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if not self._priority == value:
            self._priority = value

    @priority.deleter
    def priority(self):
        self._priority = 0

    # texture image
    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        #if not self._image == value:
        self._image = value
        MyrmidonGame.engine['gfx'].alter_image(self, self._image)

    @image.deleter
    def image(self):
        self._image = None

    # image sequence number
    @property
    def image_seq(self):
        return self._image_seq

    @image_seq.setter
    def image_seq(self, value):
        self._image_seq = value
        MyrmidonGame.engine['gfx'].alter_image(self, self._image)

    @image_seq.deleter
    def image_seq(self):
        self._image_seq = None

    # Colour
    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        if not self._colour == value:
            self._colour = value
            MyrmidonGame.engine['gfx'].alter_colour(self, self._colour)

    @colour.deleter
    def colour(self):
        self._colour = None


    # Alpha
    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        if not self._alpha == value:
            self._alpha = value
            MyrmidonGame.engine['gfx'].alter_alpha(self, self._alpha)

    @alpha.deleter
    def alpha(self):
        self._alpha = None

