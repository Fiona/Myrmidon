"""
This is a very simple example demonstrating the bare minimum required
to create a Myrmidon window.
It does nothing except allow it to be closed with the escape key.
"""

# sys is used simply to destroy the window. It is not necessarily required
# by myrmidon (but you would have to manually kill the process otherwise.)
import sys

#
from myrmidon import Entity, Game
from myrmidon.consts import *


class Screen(Entity):
    def execute(self):
        while True:
            if Game.keyboard_key_down(K_ESCAPE):
                sys.exit()
            yield

Screen()
            
