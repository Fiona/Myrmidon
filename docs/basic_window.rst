============
Basic Window
============

Unlike most game engines, you do not need to explicitly create the window and start the game loop. Instead Myrmidon will create it's window as soon as the first Entity object is created.

Game objects are created by subclassing the Entity class. They can have images, positions, rotations etc. Additionally they have one or more generator method that contain the code which governs the behaviour of the Entity.

The following piece of code creates a single Entity, running it will cause a window to open. (You will need to manually quit the process.)

.. code-block:: python

    from myrmidon import Entity, Game
    from myrmidon.consts import *

    class Screen(Entity):
        def execute(self):
            while True:
                yield

    Screen()
    
"execute" is always the name of the generator that is created and run when an Entity is created. Every entity's active generator (typically, execute) will be iterated every frame up to a yield statement.

If the end of an entity's active generator is reached (when StopIteration is thrown) then the Entity will be deleted. This is why most persistent Entities will have a loop like above.

To check for the state of keyboard keys you should use the Game.keyboard_key_down or Game.keyboard_key_release during the execution of an entity. You passing in a keycode to specify which key to check for.

.. note:: The keycodes are currently provided by the **pygame.locals** and this is due to change in the future. See: `Issue 63 <https://github.com/Fiona/Myrmidon/issues/63>`_

It can be used, as so to close the application on exit.
          
.. code-block:: python

    import sys
    from myrmidon import Entity, Game
    from myrmidon.consts import *
    from pygame.locals import *
    
    class Screen(Entity):
        def execute(self):
            while True:
                if Game.keyboard_key_released(K_ESCAPE):
                    sys.exit()
                yield

    Screen()
          
