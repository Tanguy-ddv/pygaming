"""A phase is one step of the game."""
from abc import ABC, abstractmethod
import gc
import pygame
from .error import PygamingException
from .game import Game
from ._base import BaseRunnable, STAY
from .server import Server
from .cursor import Cursor
from .screen._visual import Visual
from .screen.art import Rectangle

_TOOLTIP_DELAY = 500 # [ms]

class _BasePhase(ABC):
    """
    A Phase is a step in the game. Each game should have a few phases.
    Exemple of phases: menus, lobby, stages, ...
    Create a subclass of phase to do whatever you need by
    rewriting the start, the __init__, update, end, next and apply_transition methods.
    If the game is online, you will need twice as much frames. One half for the Server and the other half for the game.
    For the server, don't use any frame, but use only the inputs from the players by using self..gnetwork.get_last_receptions()
    and send data based on them to the players via self.network.send() (or .send_all()).
    """

    def __init__(self, name: str, runnable: BaseRunnable) -> None:
        """
        Create the phase. Each game/server have several phases

        Params:
        ----
        - name: The name of the phase
        - runnable: the game or server instance
        """
        ABC.__init__(self)
        self._name = name
        self.runnable = runnable
        self.runnable.set_phase(name, self)

    @property
    def database(self):
        """Alias for self.game.database or self.server.database"""
        return self.runnable.database

    @property
    def logger(self):
        """Alias for self.game.database or self.server.logger"""
        return self.runnable.logger

    @property
    def config(self):
        """Alias for self.game.config or self.server.config"""
        return self.runnable.config

    @property
    def debug(self):
        """Alias for self.game.debug or self.server.debug"""
        return self.runnable.debug

    def begin(self, **kwargs):
        """This method is called at the beginning of the phase."""
        self.start(**kwargs)

    @abstractmethod
    def start(self, **kwargs):
        """This method is called at the start of the phase and might need several arguments."""
        raise NotImplementedError()

    @abstractmethod
    def loop(self, loop_duration: int):
        """This method is called at every loop iteration."""
        raise NotImplementedError()

    def next(self):
        """
        If the phase is over, return the name of the next phase, if the phase is not, return an empty string.
        If it is the end of the game, return 'NO_NEXT'
        """
        return STAY

    # pylint: disable=unused-argument
    def apply_transition(self, next_phase: str):
        """
        This method is called if the method next returns a new phase. Its argument is the name of the next phase.
        For each new phase possible, it should return a dict, whose keys are the name of the argument of the
        start method of the next phase, and the values are the values given to these arguments.
        """
        return {}

    @abstractmethod
    def update(self, loop_duration: int):
        """
        Update the phase based on loop duration, inputs and network (via the game instance)
        This method is called at every loop iteration.
        """
        raise NotImplementedError()

    def finish(self):
        """This method is called at the end of the phase and is used to clear some data"""
        self.end()
        gc.collect()

    def end(self):
        """Action to do when the phase is ended."""
        return

class ServerPhase(_BasePhase, ABC):
    """
    The ServerPhase is a phase to be added to the server only.
    Each SeverPhase must implements the `start`, `update`, `end`, `next` and `apply_transition` emthods.
    - The `start` method is called at the beginning of the phase and is used to initialiez it. It can have several arguments
    - The `update` method is called every loop iteration and contains the game's logic.
    - The `end` method is called at the end of the game and is used to save results and free resources.
    - The `next` method is called every loop iteration and is used to know if the phase is over.
    It should return pygaming.NO_NEXT if the whole game is over, pygaming.STAY if the phase is not over
    or the name of another phase if we have to switch phase.
    - The `apply_transition` method is called if the `next` method returns a phase name. It return the argument
    for the start method of the next phase as a dict.
    
    ---
    You can access to the network via `self.network` to send data to the players or receive data.
    You can acces to the logger via `self.logger`, to the config via `self.config` and to the database via `self.database`.
    """

    def __init__(self, name, server: Server) -> None:
        ABC.__init__(self)
        _BasePhase.__init__(self, name, server)

    @property
    def server(self) -> Server:
        """Alias for the server."""
        return self.runnable

    @property
    def network(self):
        """Alias for self.server.network"""
        return self.server.network

    def loop(self, loop_duration: int):
        """Update the phase every loop iteraton."""
        self.update(loop_duration)

class GamePhase(_BasePhase, Visual):
    """
    The GamePhase is a phase to be added to the game only.
    Each SeverPhase must implements the `start`, `update`, `end`, `next` and `apply_transition` emthods.
    - The `start` method is called at the beginning of the phase and is used to initialiez it. It can have several arguments
    - The `update` method is called every loop iteration and contains the game's logic.
    - The `end` method is called at the end of the game and is used to save results and free resources.
    - The `next` method is called every loop iteration and is used to know if the phase is over.
    It should return pygaming.LEAVE if the whole game is over, pygaming.STAY if the phase is not over
    or the name of another phase if we have to switch phase.
    - The `apply_transition` method is called if the `next` method returns a phase name. It return the argument
    for the start method of the next phase as a dict. 
    
    ---
    You can access to the network via `self.network` to send data to the server or receive data.
    You can acces to the logger via `self.logger`, to the config via `self.config`, to the settings with `self.settings`,
    to the database via `self.database`, to the input via `self.keyboard` and `self.mouse`,
    to the texts and speeches via `self.texts` and `self.speeches`, and
    to the soundbox and jukebox via `self.soundbox` and `self.jukebox`.
    """

    def __init__(self, name, game: Game) -> None:
        _BasePhase.__init__(self, name, game)
        background = Rectangle((0, 0, 0, 0), *self.config.dimension)
        Visual.__init__(self, background, False)

        self.frames = [] # list[Frame]

        self.absolute_left = 0
        self.absolute_top = 0
        self.camera = self.window = self.absolute_rect = pygame.Rect((0, 0, *self.config.dimension))
        self.wc_ratio = (1, 1)

        # Data about the hovering
        self.current_tooltip = None 
        self._default_cursor = Cursor(self.config.default_cursor)
        self.current_cursor = self._default_cursor
        self._tooltip_x, self._tooltip_y = None, None
        self._tooltip_delay = _TOOLTIP_DELAY # [ms], the delay waited before showing the tooltip

    def add_child(self, frame):
        """Add a new frame to the phase."""
        self.frames.append(frame)

    def begin(self, **kwargs):
        """This method is called at the beginning of the phase."""
        # Update the game settings
        Visual.begin(self, self.settings)
        self.game.keyboard.load_controls(self.settings, self.config, self._name)
        self.game.update_settings()

        # Start the frames
        for frame in self.frames:
            frame.begin()
        # Change to default cursor
        self.current_cursor = self._default_cursor
        pygame.mouse.set_cursor(self._default_cursor.get(self.settings))
        # Start the phase
        self.notify_change_all()
        self.start(**kwargs)

    def finish(self):
        """This method is called at the end of the phase."""
        self.end()
        for frame in self.frames:
            frame.end() # Unload
        Visual.finish(self)
        gc.collect()

    def is_child_on_me(self, child):
        """Return whether the child is visible on the phase or not."""
        return self.absolute_rect.colliderect(child.relative_rect)

    @property
    def game(self) -> Game:
        """Alias for the game."""
        return self.runnable

    @property
    def typewriter(self):
        """Alias for self.game.typewriter"""
        return self.game.typewriter

    @property
    def settings(self):
        """Alias for self.game.settings"""
        return self.game.settings

    @property
    def soundbox(self):
        """Alias for self.game.soundbox"""
        return self.game.soundbox

    @property
    def jukebox(self):
        """Alias for self.game.jukebox"""
        return self.game.jukebox

    @property
    def keyboard(self):
        """Alias for self.game.keyboard"""
        return self.game.keyboard

    @property
    def mouse(self):
        """Alias for self.game.mouse"""
        return self.game.mouse

    @property
    def network(self):
        """Alias for self.game.network"""
        if self.game.online:
            return self.game.client
        raise PygamingException("The game is not connected yet, there is no network to reach.")

    def notify_change_all(self):
        """Notify the change to everyone."""
        self.notify_change()
        for frame in self.frames:
            frame.notify_change_all()

    def is_visible(self):
        """Return always True as the phase itself can't be hidden. Used for the recursive is_visible method of elements."""
        return True

    def loop(self, loop_duration: int):
        """Update the phase."""
        Visual.loop(self, loop_duration)
        self._update_focus()
        self.update(loop_duration)
        for frame in self.frames:
            frame.loop(loop_duration)

    def _update_focus(self):
        """Update the focus of all the frames."""
        ck1 = self.mouse.get_click(1)
        if ck1:
            for frame in self.frames:
                if frame.is_contact(ck1):
                    frame.update_focus(ck1)
                else:
                    frame.remove_focus()

        if "tab" in self.keyboard.actions_down and self.keyboard.actions_down["tab"]:
            for frame in self.frames:
                frame.next_object_focus()

    def update_hover(self, loop_duration):
        """Update the cursor and the over hover surface based on whether we are above one element or not."""
        x, y = self.mouse.get_position()
        cursor, tooltip = None, None
        for frame in self.visible_frames:
            
            if frame.is_contact((x,y)):
                tooltip, cursor = frame.get_hover()

        if tooltip is None: # We are not on a widget requiring a tooltip
            if self.current_tooltip is not None:
                self.current_tooltip = None
                self.notify_change()
        else: # We are on a widget requiring a tooltip
            if tooltip is self.current_tooltip: # It is the same as the current tooltip
                self._tooltip_delay -= loop_duration
                if self._tooltip_delay < 0:
                    self.notify_change() # We ask to remake the screen only if the delay is exceeded
            else: # We have a new tooltip
                self.current_tooltip = tooltip
                self._tooltip_delay = _TOOLTIP_DELAY
                self._tooltip_x, self._tooltip_y = None, None
                self.current_tooltip.notify_change() # We force its change because the language might have changed.
                
            self.current_tooltip.loop(loop_duration)

        if cursor is None:
            cursor = self._default_cursor

        if cursor is self.current_cursor:
            has_changed = self.current_cursor.update(loop_duration)
            if has_changed:
                pygame.mouse.set_cursor(self.current_cursor.get(self.settings))
                # Trigger the update of the cursor.
                pygame.mouse.set_pos(x, y)
        else:
            self.current_cursor.reset()
            self.current_cursor = cursor
            pygame.mouse.set_cursor(self.current_cursor.get(self.settings))
            # Trigger the update of the cursor.
            pygame.mouse.set_pos(x, y)

    @property
    def visible_frames(self):
        """Return all the visible frames sorted by increasing layer."""
        return sorted(filter(lambda f: f.visible, self.frames), key= lambda w: w.layer)

    def make_surface(self) -> pygame.Surface:
        """Make the new surface to be returned to his parent."""
        bg = self.background.get(None, **self.settings)
        for frame in self.visible_frames:
            surf = frame.get_surface()
            bg.blit(surf, (frame.relative_left, frame.relative_top))

        if self.current_tooltip is not None and self._tooltip_delay < 0:
            if self._tooltip_x is None:
                x, y = self.mouse.get_position() # We set the position of the tooltip with the position of the mouse.
                self._tooltip_x, self._tooltip_y = x, y
            bg.blit(self.current_tooltip.get_surface(), (self._tooltip_x, self._tooltip_y - self.current_tooltip.height))
        return bg
