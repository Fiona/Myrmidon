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

The module loader adds functionality to other classes by way of mixins.
"""

import itertools

def ModuleLoader(decorated_class):
    """The module loader is responsible for injecting functionality to existing
    classes, it does this using a mixin class dynamically imported from another loacation.
    """
    class Mixedin(decorated_class):
        def __new__(cls, *args, **kwargs):
            from myrmidon.game import Game
            class_name = decorated_class.__name__
            if not class_name in Game.modules_loaded_for:
                Game.modules_loaded_for.append(class_name)
                for module_name in Game.modules_enabled:
                    # dynamically load the module
                    module_component_name = module_name + "_" + class_name
                    mixin_module = __import__(
                        "myrmidon.Modules.%s.%s" % (module_name, module_component_name),
                        globals(),
                        locals(),
                        [module_component_name],
                        0
                        )
                    mixin_class = getattr(mixin_module, module_component_name)
                    # Add the found mixin to the base classes 
                    if not mixin_class in decorated_class.__bases__:
                        decorated_class.__bases__ = tuple(itertools.chain(decorated_class.__bases__, (mixin_class,)))
                        # Also add to list of modules so we can play with them later
                        if not hasattr(decorated_class, '_module_list'):
                            decorated_class._module_list = []
                        decorated_class._module_list.append(mixin_class)                    
            return super(Mixedin, cls).__new__(cls)
    return Mixedin
