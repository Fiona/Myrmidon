"""
This is a very simple example demonstrating the bare minimum required
to create a Myrmidon window.
It does nothing except allow it to be closed with the escape key.
"""

# sys is used simply to destroy the window. It is not necessarily required
# by myrmidon (but you would have to manually kill the process otherwise.)
import sys

# These are the core Myrmidon objects. The Game object is what you use to
# interact with your application and manage interaction with it.
# The Entity object is what all game objects are derived from, the second one
# is created the application will start.
from myrmidon import Game, Entity
from myrmidon.consts import *

# This example uses Pygame locals for it's input routines
from pygame.locals import *

# An Entity object must be running before the application will open, in this case
# we will have an Entity to represent our screen that will be responsible for
# quitting the application upon hitting the escape key.
class Screen(Entity):

    # Each Entity will at least have this method, which contains the behaviour of it.
    # Rather than being a typical method it is instead a Python generator, allowing
    # entities to essentially be mini-program loops themselves.
    def execute(self):
        # We want this entity to check for the escape key every frame, so we use a loop.
        while True:
            # Check for the escape key being pressed.
            if Game.keyboard_key_down(K_ESCAPE):
                # We can safely use the typical Python system method for quitting.
                sys.exit()
            # Each tick we leave the entity at the yield statement and will return here
            # in the next tick. If we returned instead of yielded our Entity would be
            # considered finished and would be destroyed.
            yield

# We create our Entity object and start executing from it's code. As soon as an Entity
# is made the application will start.
Screen()
