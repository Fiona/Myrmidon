#!/usr/bin/env python3

"""
Hooks for pygame and kivy backends which delegate to the IPython event loop.
This allows the user to start a Myrmidon application from within IPython whilst
having full access to inspect and change entities within the application, for
example, the position of entities may be directly inspected and updated in the REPL.

To install and activate the hook then run the app::

    In [1]: from myrmidon import Game, ipython_hook
    In [2]: ipython_hook.register()
    In [3]: %gui myrmidon_kivy  # Or %gui myrmidon_pygame
    In [4]: run kivy_test.py
    In [5]: print(window.test_entity.x)
    In [6]: Game.mouse().pos = 500, 500  # Move entity position immediately

The above example assumes that a Myrmidon window has been assigned to a module level
variable called `window` which can then be accessed in the REPL.

Note 1: You may find that the position of an entity which has been programmed to follow the
mouse position in the `execute()` method refuses to be updated. This is because the
mouse position continually overrides any change made in the REPL. To overcome this,
update the mouse position directly with, for example, `Game.mouse().pos = 500, 500`
which will then update the position of the entity in turn. See the example above.

Note 2: The kivy ipython hook assumes that the SDL2 provider is being used.

Requires IPython >3.0.0.

"""

from IPython.lib import inputhook

from myrmidon import Game


def inputhook_myrmidon_pygame():
    """The pygame eventloop hook."""
    engine_window = Game.engine['window']
    if not engine_window:
        return 0

    for x in Game._module_list:
        x._module_setup(cls)

    if Game.started:
        Game.app_loop_callback(0)

    return 0


def inputhook_myrmidon_kivy():
    """The kivy eventloop hook."""
    from kivy.base import EventLoop
    from kivy.utils import platform

    engine_window = Game.engine['window']
    if not engine_window or not engine_window.kivy_app:
        return 0

    kivy_app = engine_window.kivy_app
    if not kivy_app.built:
        from kivy.uix.widget import Widget
        from kivy.core.window import Window
        from kivy.base import runTouchApp

        for x in Game._module_list:
            x._module_setup(cls)

        kivy_app.load_config()
        kivy_app.load_kv(filename=kivy_app.kv_file)
        kivy_app.root = kivy_app.build()
        if not isinstance(kivy_app.root, Widget):
            raise Exception('Invalid instance in App.root')
        Window.add_widget(kivy_app.root)

        # Check if the window is already created
        window = EventLoop.window
        if window:
            kivy_app._app_window = window
            window.set_title(kivy_app.get_application_name())
            icon = kivy_app.get_application_icon()
            if icon:
                window.set_icon(icon)
            kivy_app._install_settings_keys(window)
        else:
            raise Exception("Application: No window is created."
                            " Terminating application run.")

        kivy_app.dispatch('on_start')
        runTouchApp(kivy_app.root, slave=True)

    # Tick forward the Myrmidon event loop one frame
    Game.app_loop_callback(0)

    # Tick forward kivy to reflect events and changes from Myrmidon.
    # This has been directly lifted from `kivy.core.window.window_sdl2`.
    EventLoop.idle()

    window = EventLoop.window
    event = window._win.poll()
    if event is False or event is None:
        return 0

    action, args = event[0], event[1:]
    if action == 'quit':
        EventLoop.quit = True
        window.close()
        return 0

    elif action in ('fingermotion', 'fingerdown', 'fingerup'):
        # for finger, pass the raw event to SDL motion event provider
        # XXX this is problematic. On OSX, it generates touches with 0,
        # 0 coordinates, at the same times as mouse. But it works.
        # We have a conflict of using either the mouse or the finger.
        # Right now, we have no mechanism that we could use to know
        # which is the preferred one for the application.
        if platform == "ios":
            SDL2MotionEventProvider.q.appendleft(event)
        pass

    elif action == 'mousemotion':
        x, y = args
        x, y = window._fix_mouse_pos(x, y)
        window._mouse_x = x
        window._mouse_y = y
        # don't dispatch motion if no button are pressed
        if len(window._mouse_buttons_down) == 0:
            return 0
        window._mouse_meta = window.modifiers
        window.dispatch('on_mouse_move', x, y, window.modifiers)

    elif action in ('mousebuttondown', 'mousebuttonup'):
        x, y, button = args
        x, y = window._fix_mouse_pos(x, y)
        btn = 'left'
        if button == 3:
            btn = 'right'
        elif button == 2:
            btn = 'middle'
        eventname = 'on_mouse_down'
        window._mouse_buttons_down.add(button)
        if action == 'mousebuttonup':
            eventname = 'on_mouse_up'
            window._mouse_buttons_down.remove(button)
        window._mouse_x = x
        window._mouse_y = y
        window.dispatch(eventname, x, y, btn, window.modifiers)
    elif action.startswith('mousewheel'):
        window._update_modifiers()
        x, y, button = args
        btn = 'scrolldown'
        if action.endswith('up'):
            btn = 'scrollup'
        elif action.endswith('right'):
            btn = 'scrollright'
        elif action.endswith('left'):
            btn = 'scrollleft'

        window._mouse_meta = window.modifiers
        window._mouse_btn = btn
        #times = x if y == 0 else y
        #times = min(abs(times), 100)
        #for k in range(times):
        window._mouse_down = True
        window.dispatch('on_mouse_down',
            window._mouse_x, window._mouse_y, btn, window.modifiers)
        window._mouse_down = False
        window.dispatch('on_mouse_up',
            window._mouse_x, window._mouse_y, btn, window.modifiers)

    elif action == 'dropfile':
        dropfile = args
        window.dispatch('on_dropfile', dropfile[0])
    # video resize
    elif action == 'windowresized':
        window._size = window._win.window_size
        # don't use trigger here, we want to delay the resize event
        cb = window._do_resize
        from kivy.clock import Clock
        Clock.unschedule(cb)
        Clock.schedule_once(cb, .1)

    elif action == 'windowresized':
        window.canvas.ask_update()

    elif action == 'windowrestored':
        window.canvas.ask_update()

    elif action == 'windowexposed':
        window.canvas.ask_update()

    elif action == 'windowminimized':
        if Config.getboolean('kivy', 'pause_on_minimize'):
            window.do_pause()

    elif action == 'joyaxismotion':
        stickid, axisid, value = args
        window.dispatch('on_joy_axis', stickid, axisid, value)
    elif action == 'joyhatmotion':
        stickid, hatid, value = args
        window.dispatch('on_joy_hat', stickid, hatid, value)
    elif action == 'joyballmotion':
        stickid, ballid, xrel, yrel = args
        window.dispatch('on_joy_ball', stickid, ballid, xrel, yrel)
    elif action == 'joybuttondown':
        stickid, buttonid = args
        window.dispatch('on_joy_button_down', stickid, buttonid)
    elif action == 'joybuttonup':
        stickid, buttonid = args
        window.dispatch('on_joy_button_up', stickid, buttonid)

    elif action in ('keydown', 'keyup'):
        mod, key, scancode, kstr = args

        from kivy.core.window import window_sdl2
        key_swap = {
            window_sdl2.SDLK_LEFT: 276, window_sdl2.SDLK_RIGHT: 275, window_sdl2.SDLK_UP: 273,
            window_sdl2.SDLK_DOWN: 274, window_sdl2.SDLK_HOME: 278, window_sdl2.SDLK_END: 279,
            window_sdl2.SDLK_PAGEDOWN: 281, window_sdl2.SDLK_PAGEUP: 280, window_sdl2.SDLK_SHIFTR: 303,
            window_sdl2.SDLK_SHIFTL: 304, window_sdl2.SDLK_SUPER: 309, window_sdl2.SDLK_LCTRL: 305,
            window_sdl2.SDLK_RCTRL: 306, window_sdl2.SDLK_LALT: 308, window_sdl2.SDLK_RALT: 307,
            window_sdl2.SDLK_CAPS: 301, window_sdl2.SDLK_INSERT: 277, window_sdl2.SDLK_F1: 282,
            window_sdl2.SDLK_F2: 283, window_sdl2.SDLK_F3: 284, window_sdl2.SDLK_F4: 285, window_sdl2.SDLK_F5: 286,
            window_sdl2.SDLK_F6: 287, window_sdl2.SDLK_F7: 288, window_sdl2.SDLK_F8: 289, window_sdl2.SDLK_F9: 290,
            window_sdl2.SDLK_F10: 291, window_sdl2.SDLK_F11: 292, window_sdl2.SDLK_F12: 293, window_sdl2.SDLK_F13: 294,
            window_sdl2.SDLK_F14: 295, window_sdl2.SDLK_F15: 296, window_sdl2.SDLK_KEYPADNUM: 300}

        if platform == 'ios':
            # XXX ios keyboard suck, when backspace is hit, the delete
            # keycode is sent. fix it.
            key_swap[127] = 8  # back

        try:
            key = key_swap[key]
        except KeyError:
            pass

        if action == 'keydown':
            window._update_modifiers(mod, key)
        else:
            window._update_modifiers(mod)  # ignore the key, it
                                         # has been released

        # if mod in window._meta_keys:
        if (key not in window._modifiers and
            key not in window.command_keys.keys()):
            try:
                kstr = chr(key)
            except ValueError:
                pass
        #if 'shift' in window._modifiers and key\
        #        not in window.command_keys.keys():
        #    return

        if action == 'keyup':
            window.dispatch('on_key_up', key, scancode)
            return 0

        # don't dispatch more key if down event is accepted
        if window.dispatch('on_key_down', key,
                         scancode, kstr,
                         window.modifiers):
            return 0
        window.dispatch('on_keyboard', key,
                      scancode, kstr,
                      window.modifiers)

    elif action == 'textinput':
        text = args[0]
        window.dispatch('on_textinput', text)
        # XXX on IOS, keydown/up don't send unicode anymore.
        # With latest sdl, the text is sent over textinput
        # Right now, redo keydown/up, but we need to seperate both call
        # too. (and adapt on_key_* API.)
        #window.dispatch()
        #window.dispatch('on_key_down', key, None, args[0],
        #              window.modifiers)
        #window.dispatch('on_keyboard', None, None, args[0],
        #              window.modifiers)
        #window.dispatch('on_key_up', key, None, args[0],
        #              window.modifiers)

    # unhandled event !
    else:
        from kivy.logger import Logger
        Logger.trace('WindowSDL: Unhandled event %s' % str(event))

    return 0


def register():
    """Register hooks for IPython.

    This activates the use of `%gui myrmidon_pygame` and `%gui myrmidon_kivy`.

    """
    @inputhook.register('myrmidon_pygame')
    class MyrmidonPygameInputHook(inputhook.InputHookBase):
        def enable(self, app=None):
            # Prevent autostart of Myrmidon loop on creation of first entity
            Game.run_game = lambda: None
            self.manager.set_inputhook(inputhook_myrmidon_pygame)

    @inputhook.register('myrmidon_kivy')
    class MyrmidonKivyInputHook(inputhook.InputHookBase):
        def enable(self, app=None):
            # Prevent autostart of Myrmidon loop on creation of first entity
            Game.run_game = lambda: None
            # Monkey patch kivy app startup to force "slave" mode to take control of event loop
            from kivy import base
            _runTouchApp = base.runTouchApp
            base.runTouchApp = lambda widget=None, slave=False: _runTouchApp(widget, slave=True)
            self.manager.set_inputhook(inputhook_myrmidon_kivy)
