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

This contains the primary Game object from where you manipulate
and interact with the application.
"""


import sys, os, math
from myrmidon.consts import *

class Game(object):

    # Engine related
    started = False

    # Set to true at run-time and Myrmidon will not create a screen,
    # nor will it accept input or execute any entities in a loop.
    # No backend engines are initialised.
    # Any entity objects you create will not interate their generator
    # unless you run Entity._iterate_generator manually.
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

    # Entity related
    entity_list = []
    entities_to_remove = []
    remember_current_entity_executing = []
    current_entity_executing = None
    entity_priority_dirty = True


    @classmethod
    def define_engine(cls, window = None, gfx = None, input = None, audio = None):
        """
        Use this before creating any entities to redefine which engine backends to use.
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
        Use this before creating any entities to specify which engine plugins you require,
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
                    "myrmidon.engine.%s.%s.engine" % (backend_name, cls.engine_def[backend_name]),
                    globals(),
                    locals(),
                    ['Myrmidon_Backend'],
                    0
                    )
                cls.engine[backend_name] = backend_module.Myrmidon_Backend()
                
        except ImportError as detail:
            print("Error importing a backend engine.", detail)
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
            print("Error importing a backend engine plugin.", detail)
            sys.exit()

            
    @classmethod
    def start_game(cls):
        """
        Called by entities if a game is not yet started.
        It initialises engines.
        """
        # Start up the backends
        cls.init_engines()
        cls.clock = cls.engine['window'].Clock()


    @classmethod
    def run_game(cls):
        """
        Called by entities if a game is not yet started.
        Is responsible for the main loop.
        """
        # No execution of anything if in test mode.
        if cls.test_mode:
            return
        
        while cls.started:

            if cls.entity_priority_dirty == True:
                cls.entity_list.sort(
                    reverse=True,
                    key=lambda object:
                    object.priority if hasattr(object, "priority") else 0
                    )
                cls.entity_priority_dirty = False

            if cls.engine['input']:
                cls.engine['input'].process_input()

            cls.entities_to_remove = []
            
            for entity in cls.entity_list:
                if entity.status == 0:
                    cls.current_entity_executing = entity
                    entity._iterate_generator()

            for x in cls.entities_to_remove:
                if x in cls.entity_list:
                    cls.entity_list.remove(x)
                
            cls.engine['gfx'].update_screen_pre()
            cls.engine['gfx'].draw_entities(cls.entity_list)              
            cls.engine['gfx'].update_screen_post()

            cls.fps = int(cls.clock.get_fps())
            cls.clock.tick(cls.current_fps)


    @classmethod
    def change_resolution(cls, resolution):
        cls.screen_resolution = resolution
        cls.engine['window'].change_resolution(resolution)
        cls.engine['gfx'].change_resolution(resolution)

        

    ##############################################
    # ENTITIES
    ##############################################
    @classmethod
    def entity_register(cls, entity):
        """
        Registers an entity with Myrmidon so it will be executed.
        """
        cls.entity_list.append(entity)
        cls.engine['gfx'].register_entity(entity)
        cls.entity_priority_dirty = True

        # Handle relationships
        if cls.current_entity_executing != None:
            entity.parent = cls.current_entity_executing
                
            if not entity.parent.child == None:
                entity.parent.child.prev_sibling = entity
                    
            entity.next_sibling = entity.parent.child
            entity.parent.child = entity


    @classmethod        
    def signal(cls, entity, signal_code, tree=False):
        """ Signal will let you kill a entity or put it to sleep
        
            Will accept a entity object or an ID number to check against one,
            or a entity type as a string to check for all of a specific type
        
            The tree parameter can be used to recursively signal all the 
            entity's descendants
        
            Signal types-
            S_KILL - Permanently removes the entity
            S_SLEEP - Entity will disappear and will stop executing code
            S_FREEZE - Entity will stop executing code but will still appear
                and will still be able to be checked for collisions.
            S_WAKEUP - Wakes up or unfreezes the entity """
        
        # We've entered a specific type as a string
        if type(entity) == type(""):
            
            import copy
            entity_iter = copy.copy(cls.entity_list)
            
            for obj in entity_iter:
                if obj.__class__.__name__ == entity:
                    cls.single_object_signal(obj, signal_code, tree)
        
        # Passed in an object directly    
        else:
            cls.single_object_signal(entity, signal_code, tree)
            return


    @classmethod
    def single_object_signal(cls, entity, signal_code, tree = False):
        """ Used by signal as a shortcut """
        
        # do children
        if tree:
            next_child = entity.child
            while next_child != None:
                cls.single_object_signal(next_child, signal_code, True)
                next_child = next_child.next_sibling
        
        # do this one
        if signal_code == S_KILL:
            cls.entity_destroy(entity)
        elif signal_code == S_WAKEUP:
            entity.status = 0
        elif signal_code == S_SLEEP:
            entity.status = S_SLEEP
        elif signal_code == S_FREEZE:
            entity.status = S_FREEZE


    @classmethod
    def entity_destroy(cls, entity):
        """ Removes a entity """
        if not entity in Game.entity_list:
            return
        entity.on_exit()
        cls.engine['gfx'].remove_entity(entity)
        Game.entities_to_remove.append(entity)

        
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
    # MEDIA 
    ##############################################
    @classmethod
    def load_image(cls, image = None, sequence = False, width = None, height = None, **kwargs):
        """Creates and returns an Image object that we can then attach to an Entity's image member
        to display graphics.
        A particular graphics engine may also have their own specific arguments not documented here.

        Keyword arguments:
        image -- The filesystem path to the filename that the image is contained in. Typically this can
          also be a pointer to already loaded image data if the gfx in-use supports such behaviour. (for
          instance, engines using PyGame to load images can be given a PyGame surface directly.) (Required)
        sequence -- Denotes if the image being loaded contains a series of images as frames. (default False)
        width -- If we have a sequence of images, this denotes the width of each frame. (default None)
        height -- The height of a frame in a sequence image, if not supplied this will default to
          the width. (default None)
        """
        return cls.engine['gfx'].Image(image, sequence, width, height, **kwargs)


    @classmethod
    def load_font(cls, font = None, size = 20, **kwargs):
        """Creates and returns a Font object that we give to the write_text method to specify how to render
        text. You can also dynamically change the font attribute of Text objects.
        A particular window engine may also have their own specific arguments not documented here.

        Keyword arguments:
        font -- The filesystem path to the filename that the font is contained in. Typically this can
          also be a pointer to an already loaded font if the engine in-use supports this behaviour. (For
          instance, eungines using Pygame for font loading can be given a pygame.font.Font object directly.)
          If None is supplied then the default internal font will be used if applicable. (default None)
        size -- The size of the text that we want to display. What this value actually relates to is dependant
          on the font loading engine used. (default 20)
        """
        return cls.engine['window'].Font(font, size, **kwargs)


    @classmethod
    def load_audio(cls, filename):
        return cls.engine['audio'].load_audio_from_file(filename)
    
    
    ##############################################
    # TEXT HANDLING
    ##############################################
    @classmethod    
    def write_text(cls, x, y, font, alignment = 0, text = "", antialias = True):
        return cls.engine['gfx'].Text(font, x, y, alignment, text, antialias = True)

    @classmethod    
    def delete_text(cls, text):
        if text in Game.entity_list:
            Game.entity_destroy(text)


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


