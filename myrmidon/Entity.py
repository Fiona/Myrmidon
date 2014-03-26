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
from myrmidon.consts import *
from myrmidon.Game import Game
from myrmidon.BaseEntity import BaseEntity


class Entity(BaseEntity):

    # Basic entity properties
    _x = 0.0
    _y = 0.0
    _z = 0.0
    _priority = 0
    _image = None
    _image_seq = 0
    _colour = (1.0, 1.0, 1.0)
    _alpha = 1.0
    _scale = 1.0
    _rotation = 0.0

    # Other properties (document)
    blend = False
    clip = None
    scale_point = [0.0, 0.0]
    normal_draw = True

    # Entity relationships
    parent = None
    child = None
    prev_sibling = None
    next_sibling = None

    # Collision related
    
    # If set to False this Entity will never collide with
    # any other. It will silently fail to do so rather than error.
    collision_on = False

    # The shape that this entity will be collided as.
    # COLLISION_TYPE_RECTANGLE, COLLISION_TYPE_CIRCLE and COLLISION_TYPE_POINT
    # are currently the acceptable types.
    collision_type = COLLISION_TYPE_RECTANGLE

    # Width and height of the collision rectangle if that type is used.
    # Specifying None will just take the size from the size of the image.
    collision_rectangle_width = None
    collision_rectangle_height = None

    # The size of the bounding circle when using that as the collision type.
    # Specifying None will just take the radius from the width of the image.
    collision_circle_radius = None

    # This is the offset of the point when using that as the collision type.
    # It is an optional offset from the x/y position of the Entity. Provided
    # as a two part tuple.
    collision_point_offset = None

    # We use this to know if it's worth recalculating the corners for this
    # Entity as this can be a fairly costly procedure.
    _collision_rectangle_recalculate_corners = True

    # Contains our precalculated corners for collision detection. Should be
    # recalculated once per frame if necessary but no more.
    _collision_rectangle_calculated_corners = {'ul' : (0.0, 0.0), 'ur' : (0.0, 0.0), 'll' : (0.0, 0.0), 'lr' : (0.0, 0.0)}


    # Internal private properties
    _is_text = False
    _generator = None
    _executing = True
    _drawing = True
    
    
    def __init__(self, *args, **kargs):
        if not Game.started:
            Game.start_game()

        Game.entity_register(self)

        self.z = 0.0
        self.x = 0.0
        self.y = 0.0
        self.priority = 0
        self._collision_rectangle_calculated_corners = {'ul' : (0.0, 0.0), 'ur' : (0.0, 0.0), 'll' : (0.0, 0.0), 'lr' : (0.0, 0.0)}

        Game.remember_current_entity_executing.append(Game.current_entity_executing)
        Game.current_entity_executing = self
        self._executing = True
        self._drawing = True        
        self._generator = self.execute(*args, **kargs)
        self._iterate_generator()
        Game.current_entity_executing = Game.remember_current_entity_executing.pop()
        
        if not Game.started:
            Game.started = True             
            Game.run_game()
            

    def execute(self):
        """
        This is where the main code for the entity lives
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
        try:
            next(self._generator)
        except StopIteration:
            return


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
        return self.x, self.y


    def move_forward(self, distance, angle = None):
        self.x, self.y = Game.move_forward((self.x, self.y), distance, self.rotation if angle == None else angle)

        
    def get_distance(self, pos):
        return Game.get_distance((self.x, self.y), pos)


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


    ##############################################
    # Collision model related methods 
    ##############################################


    def collision_rectangle_calculate_corners(self):
        """This method is used as an optimisation for recangle collisions.
        We store the location of corners and only do it either once per frame
        or if a relevant value has changed. (x/y/rotation/scale)

        Returns a dictionary containing four tuples, 'ul', 'ur', 'll', 'lr'.
        The tuples are coordinates pointing to the four corners of the rotated and
        scaled rectangle (upper left, upper right, lower left and lower right)"""
        if not self._collision_rectangle_recalculate_corners:
            return self._collision_rectangle_calculated_corners

        # Determine the size of the rectangle to use
        width, height = self.collision_rectangle_size()

        # Rotate each point of the rectangle as the Entitiy is to calculate
        # it's true position.
        rot = Game.rotate_point(0, 0, self.rotation)
        self._collision_rectangle_calculated_corners['ul'] = float(self.x + rot[0]), float(self.y + rot[1])
        rot = Game.rotate_point(width, 0, self.rotation)
        self._collision_rectangle_calculated_corners['ur'] = float(self.x + rot[0]), float(self.y + rot[1])
        rot = Game.rotate_point(0, height, self.rotation)
        self._collision_rectangle_calculated_corners['ll'] = float(self.x + rot[0]), float(self.y + rot[1])
        rot = Game.rotate_point(width, height, self.rotation)
        self._collision_rectangle_calculated_corners['lr'] = float(self.x + rot[0]), float(self.y + rot[1])

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
        if not self.collision_point_offset is None:
            rot = Game.rotate_point(self.collision_point_offset[0], self.collision_point_offset[1], self.rotation)
            point = (point[0] + rot[0], point[1] + rot[1])
        return point


    def collide_with(self, entities_colliding):
        """
        Checks collisions with an arbitrary list of Entities using the relevant
        algorithms depending on collision types specified.
        Returns a two-part tuple containing True/False and the first Entity we detected
        a collision with, if indeed we did.

        Keyword arguments:
        -- entities_colliding: List of Entities to check collisons against."""
        if not self.collision_on:
            return (False, None)
        
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
                return (True, check_object)

        # No collision
        return (False, None)
    

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
        _collision_rectangle_recalculate_corners = True

    @x.deleter
    def x(self):
        self._x = 0.0
        _collision_rectangle_recalculate_corners = True
        
    # Y
    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        Game.engine['gfx'].alter_y(self, self._y)
        _collision_rectangle_recalculate_corners = True

    @y.deleter
    def y(self):
        self._y = 0.0
        _collision_rectangle_recalculate_corners = True

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
        self._z = 0.0

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
        _collision_rectangle_recalculate_corners = True

    @image.deleter
    def image(self):
        self._image = None
        _collision_rectangle_recalculate_corners = True

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
            _collision_rectangle_recalculate_corners = True

    @scale.deleter
    def scale(self):
        self._scale = None
        _collision_rectangle_recalculate_corners = True

    # Rotation
    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if not self._rotation == value:
            self._rotation = value
            Game.engine['gfx'].alter_rotation(self, self._rotation)
            _collision_rectangle_recalculate_corners = True

    @rotation.deleter
    def rotation(self):
        self._rotation = None
        _collision_rectangle_recalculate_corners = True


