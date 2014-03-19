Myrmidon - Python 2D game framework
===================================

Myrmidon is a framework for Python that aims to provide rapid development of 2D games.

Using a simple and easy to use API, Myrmidon allows developers to create interactive games and was designed to be perfectly suited for prototypes, proof-of-concepts and game jams.

Myrmidon's bottom-line is that the developer should only be concerned about behaviour of game objects and how the user interacts with them. Any low-level graphics, window or input handling should be the sole responsibility of Myrmidon. Hiding that as much as possible and allowing you to get on writing your game.


Examples
========

This example displays a window that the user can close using the escape key.

```python
import sys
from myrmidon import Entity, Game
from myrmidon.consts import *

class Screen(Entity):
    def execute(self):
        while True:
            if Game.keyboard_key_down(K_ESCAPE):
                sys.exit()
            yield

Screen()
```
