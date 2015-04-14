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

This file contains the Entity object that represents displayable and interactable
game objects.
"""

import sys, os, math
from collections import namedtuple
from myrmidon.consts import *
from myrmidon.Game import Game
from myrmidon.BaseEntity import BaseEntity
from myrmidon.ModuleLoader import ModuleLoader

EntityCollisionResult = namedtuple('EntityCollisionResult', ['result', 'entity'])

@ModuleLoader
class Entity(BaseEntity):

    # Basic entity properties
    _x = 0.0
    _y = 0.0
    _z = 0
    _priority = 0
    _image = None
    _image_seq = 0
    _colour = (1.0, 1.0, 1.0)
    _alpha = 1.0
    _scale = 1.0
    _rotation = 0.0
    _centre_point = [-1, -1]
    _drawing = True

    # Other properties (document)
    blend = False
    clip = None
    normal_draw = True
    flip_vertical = False
    flip_horizontal = False
    sleep_counter = 0
    
    # Entity relationships
    parent = None
    child = None
    prev_sibling = None
    next_sibling = None

    # Module list
    _module_list = []

    # Collision related

    # If set to False this Entity will never collide with
    # any other. It will silently fail to do so rather than error.
    collision_on = False

    # The shape that this entity will be collided as.
    # COLLISION_TYPE_RECTANGLE, COLLISION_TYPE_CIRCLE and COLLISION_TYPE_POINT
    # are currently the acceptable types.
    collision_type = COLLISION_TYPE_RECTANGLE

    # This is the offset of where all collisions will be checked from.
    # It is an optional offset from the x/y position of the Entity. Provided
    # as a two part tuple.
    collision_offset = None

    # Width and height of the collision rectangle if that type is used.
    # Specifying None will just take the size from the size of the image.
    collision_rectangle_width = None
    collision_rectangle_height = None

    # The size of the bounding circle when using that as the collision type.
    # Specifying None will just take the radius from the width of the image.
    collision_circle_radius = None

    # We use this to know if it's worth recalculating the corners for this
    # Entity as this can be a fairly costly procedure.
    _collision_rectangle_recalculate_corners = True

    # Contains our precalculated corners for collision detection. Should be
    # recalculated once per frame if necessary but no more.
    _collision_rectangle_calculated_corners = {'ul' : (0.0, 0.0), 'ur' : (0.0, 0.0), 'll' : (0.0, 0.0), 'lr' : (0.0, 0.0)}

    # Internal private properties
    _current_state = "execute"
    _previous_state = None
    _state_list = {}
    _state_generators = {}
    _is_text = False
    _executing = True

    def __init__(self, *args, **kwargs):
        if not Game.started:
            Game.first_registered_entity = self
            Game.start_game()
        else:
            Game.entity_register(self)

        self._collision_rectangle_calculated_corners = {'ul' : (0.0, 0.0), 'ur' : (0.0, 0.0), 'll' : (0.0, 0.0), 'lr' : (0.0, 0.0)}
        self._state_list = {}
        self._state_generators = {}

        self.add_state(self.execute, *args, **kwargs)

        Game.remember_current_entity_executing.append(Game.current_entity_executing)
        Game.current_entity_executing = self
        self._executing = True
        self._iterate_generator()
        Game.current_entity_executing = Game.remember_current_entity_executing.pop()

        for x in self._module_list:
            x._module_setup(self)

        if not Game.started:
            Game.started = True
            Game.run_game()

    def execute(self):
        """
        The default state method and where, typically, the main logic will sit.
        """
        while True:
            yield

    def on_exit(self):
        """
        Called automatically when a entity has finished executing for whatever reason.
        Is also called when a entity is killed using the destroy method.
        """
        pass

    def _iterate_generator(self):
        if not Game.started or not self._executing:
            return
        if self.sleep_counter:
            self.sleep_counter -= 1
            return
        return_val = None
        try:
            return_val = next(self._state_generators[self._current_state])
            if isinstance(return_val, int):
                self.sleep_counter = return_val
        except StopIteration:
            if not return_val in self._state_generators:
                self.destroy()
                return

    def add_state(self, state_method, *args, **kwargs):
        """Adds a new generator method to the list of states the entity can have.
        Pass in the method to register it. Any additional arguments or
        keyword arguments are passed to the generator."""
        self._state_list[state_method.__name__ ] = state_method
        self._state_generators[state_method.__name__] = state_method(*args, **kwargs)

    def check_state_started(self, state_name, *args, **kwargs):
        """Used to switch and resume methods to initialise a state
        generator. This is so we don't have to add them manually."""
        if not state_name in self._state_list:
            self.add_state(getattr(self, state_name), *args, **kwargs)

    def switch_state(self, state_name, *args, **kwargs):
        """Will switch to a different start, restarting it if previously
        started and passing in arguments and keyword arguments.
        It returns the started state generator. If you return a state from another state
        then it will automatically started."""
        self._previous_state = self._current_state
        self.check_state_started(state_name, *args, **kwargs)
        self.resume_state(state_name)
        self._state_generators[state_name] = self._state_list[state_name](*args, **kwargs)
        return self._state_generators[state_name]

    def resume_state(self, state_name):
        """Starts executing a completely different state. If called from anywhere
        other than the switch_state method it will not restart it.
        It returns the started state generator. If you return a state from another state
        then it will automatically resumed."""
        self._previous_state = self._current_state
        self.check_state_started(state_name)
        self._current_state = state_name
        return self._state_generators[state_name]

    def get_current_state(self):
        """Returns the name of the state that is currently running on this entity as string"""
        return self._current_state

    def resume_previous_state(self):
        """The state immediately preceeding the current one is remembered
        and you can hop-back to it with this. This allows for one-level easy
        sub-states."""
        return self.resume_state(self._previous_state)

    def switch_previous_state(self):
        """Same as resume_previous_state but for the odd situations where you want
        the return state to be restarted."""
        return self.switch_state(self._previous_state)

    def draw(self):
        """
        Override this to add custom drawing routines to your entity.
        """
        pass

    def get_screen_draw_position(self):
        """ At draw time this function is called to determine exactly where
        the entity will be drawn. Override this if you need to programatically
        constantly change the position of entity.
        Returns a tuple (x,y)"""
        if Game.centre_point_compatability_mode:
            return self.x, self.y
        centre = self.get_centre_point()
        return self.x - (centre[0] * self.scale), self.y - (centre[1] * self.scale)

    def get_centre_point(self):
        """Returns the centre of the current image if the centre_point member
        has not been explicitly set."""
        if -1 in self.centre_point and self.image is not None:
            return self.image.width / 2, self.image.height / 2
        else:
            return self.centre_point

    def is_alive(self):
        """Returns a boolean if the Entity is not destroyed yet."""
        return self in Game.entity_list and self not in Game.entities_to_remove

    def destroy(self, tree = False):
        """Kills this Entity, stopping it from executing and displaying and
        irreversibly destroying it.

        Keyword arguments:
        -- tree: If True then all children of this Entity (and their children
          etc) will be destroyed too. (default False)
        """
        Game.destroy_entities(self, tree = tree)


    def stop_executing(self, tree = False):
        """Stops this Entity executing code. Can be woke up again with start_executing
        or toggle_executing.

        Keyword arguments:
        -- tree: If True then all children of this Entity (and their children
          etc) will be stopped too. (default False)
        """
        Game.stop_entities_executing(self, tree = tree)


    def start_executing(self, tree = False):
        """Start this Entity executing code if previously stopped.

        Keyword arguments:
        -- tree: If True then all children of this Entity (and their children
          etc) will be started too. (default False)
        """
        Game.start_entities_executing(self, tree = tree)


    def toggle_executing(self, tree = False):
        """Toggle the execution of this Entity. If started it will be stopped
        and vise-versa.

        Keyword arguments:
        -- tree: If True then all children of this Entity (and their children
          etc) will be toggled too. (default False)
        """
        Game.toggle_entities_executing(self, tree = tree)


    def hide(self, tree = False):
        """Stops this Entity rendering. Can be set to draw again with show or
        toggle_display.

        Keyword arguments:
        -- tree: If True then all children of this Entity (and their children
          etc) will be hidden too. (default False)
        """
        Game.hide_entities(self, tree = tree)


    def show(self, tree = False):
        """Start this Entity rendering again if previously stopped.

        Keyword arguments:
        -- tree: If True then all children of this Entity (and their children
          etc) will be shown too. (default False)
        """
        Game.show_entities(self, tree = tree)


    def toggle_display(self, tree = False):
        """Toggle the rendering of this Entity. If hidden it will be shown
        and vise-versa.

        Keyword arguments:
        -- tree: If True then all children of this Entity (and their children
          etc) will be toggled too. (default False)
        """
        Game.toggle_entities_display(self, tree = tree)


    def sleep(self, num_frames):
        """yield from this to sleep for a certain number of frames.
        Sleeping entities will still execute."""
        return int(num_frames)
    

    ##############################################
    # Collision model related methods
    ##############################################


    def collision_rectangle_calculate_corners(self):
        """This method is used as an optimisation for recangle collisions.
        We store the location of corners and only do it either once per frame
        or if a relevant value has changed. (x/y/rotation/scale/centre_point)

        Returns a dictionary containing four tuples, 'ul', 'ur', 'll', 'lr'.
        The tuples are coordinates pointing to the four corners of the rotated and
        scaled rectangle (upper left, upper right, lower left and lower right)"""
        if not self._collision_rectangle_recalculate_corners:
            return self._collision_rectangle_calculated_corners

        # Determine the size of the rectangle to use
        width, height = self.collision_rectangle_size()

        # Get the real x/y
        centre = self.get_centre_point()
        x = self.x - centre[0]
        y = self.y - centre[1]

        if not self.collision_offset is None:
            x += self.collision_offset[0]
            y += self.collision_offset[1]

        # Rotate each point of the rectangle as the Entitiy is to calculate
        # it's true position.
        rot = Game.rotate_point(0, 0, self.rotation)
        self._collision_rectangle_calculated_corners['ul'] = float(x + rot[0]), float(y + rot[1])
        rot = Game.rotate_point(width, 0, self.rotation)
        self._collision_rectangle_calculated_corners['ur'] = float(x + rot[0]), float(y + rot[1])
        rot = Game.rotate_point(0, height, self.rotation)
        self._collision_rectangle_calculated_corners['ll'] = float(x + rot[0]), float(y + rot[1])
        rot = Game.rotate_point(width, height, self.rotation)
        self._collision_rectangle_calculated_corners['lr'] = float(x + rot[0]), float(y + rot[1])

        # Flag so we don't do this more than we need to.
        self._collision_rectangle_recalculate_corners = False

        return self._collision_rectangle_calculated_corners


    def collision_rectangle_size(self):
        """Returns the width and height of the collision rectangle as a two-part tuple.
        By default this is based on the image size, but can be overriden by setting
        collision_rectangle_width and collision_rectangle_height.
        """
        width = 0.0
        height = 0.0
        if self.collision_rectangle_width is None and not self.image is None:
            width = self.image.width
        else:
            width = self.collision_rectangle_width
        if self.collision_rectangle_height is None and not self.image is None:
            height = self.image.height
        else:
            height = self.collision_rectangle_height
        return (float(width * self.scale), float(height * self.scale))


    def collision_circle_calculate_radius(self):
        """Returns the radius of the collision circle used in collision calucations.
        By default this uses the image width. Can be overriden by setting collision_circle_radius.
        """
        radius = 0.0
        if self.collision_circle_radius is None:
            if not self.image is None:
                radius = (self.image.width * self.scale) / 2
        else:
            radius = self.collision_circle_radius * self.scale
        return radius


    def collision_point_calculate_point(self):
        """Returns the coordinates of the collision point to use, taking into account
        any offset assigned to collision_point_offset.
        """
        point = (self.x, self.y)
        if not self.collision_offset is None:
            rot = Game.rotate_point(self.collision_offset[0], self.collision_offset[1], self.rotation)
            point = (point[0] + rot[0], point[1] + rot[1])
        return point


    def collide_with(self, entities_colliding):
        """
        Checks collisions with an arbitrary list of Entities (or a single Entity)
        using the relevant algorithms depending on collision types specified.
        Returns a EntityCollisionResult, a namedtuple containing 'result' as a bool
        and 'entity' - If there was a found collision and which of the passed entities
        was hit.

        Keyword arguments:
        -- entities_colliding: List of Entities to check collisons against."""
        if not self.collision_on:
            return EntityCollisionResult(result = False, entity = None)

        # If we haven't passed in an iterator we assume it's a single Entity object
        # and turn it into a list
        try:
            iter(entities_colliding)
        except TypeError:
            entities_colliding = [entities_colliding]

        # Myrmidon needs to be told we're doing a collision for optimisation reasons
        Game.did_collision_check = True

        # Check collisions against every entity we've passed
        for check_object in entities_colliding:
            # Skip anything for that which has collisioned turned off
            # or ourself.
            if not check_object.collision_on or check_object == self:
                continue

            # We dynamically call the correct method, passing the entities
            # in as keyword arguments so the order does not matter. The argument
            # names are the only thing we are bothered about.
            if self.collision_type == check_object.collision_type:
                params = {self.collision_type + '_a' : self, check_object.collision_type + '_b' : check_object}
            else:
                params = {self.collision_type : self, check_object.collision_type : check_object}
            collision_result = Game.collision_methods[(self.collision_type, check_object.collision_type)](**params)

            if collision_result:
                return EntityCollisionResult(result = True, entity = check_object)

        # No collision
        return EntityCollisionResult(result = False, entity = None)


    def reset_collision_model(self):
        """ During checking of collisions we may set some temporary values to
        avoid repeating calculations. This is called if we did any collision
        checks to reset those."""
        self._collision_rectangle_recalculate_corners = True



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
        Game.engine['gfx'].alter_x(self, self._x)
        self._collision_rectangle_recalculate_corners = True

    @x.deleter
    def x(self):
        self._x = 0.0
        self._collision_rectangle_recalculate_corners = True

    # Y
    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        Game.engine['gfx'].alter_y(self, self._y)
        self._collision_rectangle_recalculate_corners = True

    @y.deleter
    def y(self):
        self._y = 0.0
        self._collision_rectangle_recalculate_corners = True

    # depth
    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        if not self._z == value:
            self._z = value
            Game.engine['gfx'].alter_z(self, self._z)

    @z.deleter
    def z(self):
        self._z = 0

    # priority
    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if not self._priority == value:
            Game.entity_priority_dirty = True
            self._priority = value

    @priority.deleter
    def priority(self):
        Game.entity_priority_dirty = True
        self._priority = 0

    # texture image
    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        #if not self._image == value:
        self._image = value
        Game.engine['gfx'].alter_image(self, self._image)
        self._collision_rectangle_recalculate_corners = True

    @image.deleter
    def image(self):
        self._image = None
        self._collision_rectangle_recalculate_corners = True

    # image sequence number
    @property
    def image_seq(self):
        return self._image_seq

    @image_seq.setter
    def image_seq(self, value):
        self._image_seq = value
        Game.engine['gfx'].alter_image(self, self._image)

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
            Game.engine['gfx'].alter_colour(self, self._colour)

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
            Game.engine['gfx'].alter_alpha(self, self._alpha)

    @alpha.deleter
    def alpha(self):
        self._alpha = None


    # Scale
    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        if not self._scale == value:
            self._scale = value
            Game.engine['gfx'].alter_scale(self, self._scale)
            self._collision_rectangle_recalculate_corners = True

    @scale.deleter
    def scale(self):
        self._scale = None
        self._collision_rectangle_recalculate_corners = True

    # Rotation
    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if not self._rotation == value:
            self._rotation = value
            Game.engine['gfx'].alter_rotation(self, self._rotation)
            self._collision_rectangle_recalculate_corners = True

    @rotation.deleter
    def rotation(self):
        self._rotation = None
        self._collision_rectangle_recalculate_corners = True

    # Centre point of graphic
    @property
    def centre_point(self):
        return self._centre_point

    @centre_point.setter
    def centre_point(self, value):
        self._centre_point = value
        self._collision_rectangle_recalculate_corners = True

    @centre_point.deleter
    def centre_point(self):
        self._centre_point = None
        self._collision_rectangle_recalculate_corners = True

    # Drawing internal thing
    @property
    def drawing(self):
        return self._drawing

    @drawing.setter
    def drawing(self, value):
        self._drawing = value
        Game.engine['gfx'].alter_display(self, self._drawing)
