"""A phase is one step of the game."""
from abc import ABC, abstractmethod
from functools import lru_cache
import gc
import pygame
from .error import PygamingException
from .game import Game
from ._base import BaseRunnable, STAY
from .server import Server
from .screen.hover import Cursor
from .screen.frame import Frame
from .screen._abstract import Master

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
        super().__init__()
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
    def loop(self, dt: int):
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
    def update(self, dt: int):
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
        super().__init__(name, server)

    @property
    def server(self) -> Server:
        """Alias for the server."""
        return self.runnable

    @property
    def network(self):
        """Alias for self.server.network"""
        return self.server.network

    def loop(self, dt: int):
        """Update the phase every loop iteraton."""
        self.update(dt)

class GamePhase(_BasePhase, Master):
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

    def __init__(self, name: str, game: Game) -> None:

        super().__init__(name, game)

        self.frame_children: set[Frame]
        self.absolute_rect = pygame.Rect((0, 0, *self.config.dimension))
        self.wc_ratio = (1, 1)
        self._width, self._height = self.config.dimension
        self.absolute_left = self.absolute_top = 0

        # Data about the hovering
        self.current_tooltip = None 
        self._default_cursor = Cursor(self.config.default_cursor)
        self.current_cursor = self._default_cursor
        self._tooltip_x, self._tooltip_y = None, None
        self._tooltip_delay = _TOOLTIP_DELAY # [ms], the delay waited before showing the tooltip
    
    def __hash__(self) -> int:
        return hash(self._name)

    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height

    def is_child_on_me(self, child):
        """Return whether the child is visible on the frame or not."""
        return child in self.placeable_children and self.absolute_rect.colliderect(child.relative_rect)

    def begin(self, **kwargs):
        """This method is called at the beginning of the phase."""
        # Update the game settings
        self.game.keyboard.load_controls(self.settings, self.config, self._name)
        self.game.update_settings()

        # Start the frames
        for frame in self.children:
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
        for frame in self.children:
            frame.end() # Unload
        Master.finish(self)
        gc.collect()

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
        for frame in self.children:
            frame.notify_change_all()

    def is_visible(self):
        """Return always True as the phase itself can't be hidden. Used for the recursive is_visible method of elements."""
        return True

    def loop(self, dt: int):
        """Update the phase."""
        Master.loop(self, dt)
        self._update_focus()
        self.update(dt)
        for frame in self.children:
            frame.loop(dt)

    def _update_focus(self):
        """Update the focus of all the frames."""
        ck1 = self.mouse.get_click(1)
        if ck1:
            for frame in self.frame_children:
                if frame.is_contact(ck1):
                    frame.update_focus(ck1)
                else:
                    frame.remove_focus()

        if "tab" in self.keyboard.actions_down and self.keyboard.actions_down["tab"]:
            for frame in self.children:
                frame.next_object_focus()

    def update_hover(self, dt):
        """Update the cursor and the over hover surface based on whether we are above one element or not."""
        pos = self.mouse.get_position()
        cursor, tooltip = None, None
        for frame in self.visible_children():
            frame_tooltip, frame_cursor = frame.get_hover(pos)
            if frame_tooltip is not None:
                tooltip = frame_tooltip
            if frame_cursor is not None:
                cursor = frame_cursor

        if tooltip is None: # We are not on a widget requiring a tooltip
            if self.current_tooltip is not None:
                self.current_tooltip = None
                self.notify_change()
        else: # We are on a widget requiring a tooltip
            if tooltip is self.current_tooltip: # It is the same as the current tooltip
                tooltip.loop(dt)
                if tooltip._surface_changed: # need to go like this as tooltip's internal notify change do not call the phase
                    self.notify_change()
                if self._tooltip_delay > 0:
                    self._tooltip_delay -= dt
                    if self._tooltip_delay < 0:
                        self.notify_change() # We ask to remake the screen only if the delay is exceeded
            else: # We have a new tooltip
                tooltip.begin(self.settings)
                self.current_tooltip = tooltip
                self._tooltip_delay = _TOOLTIP_DELAY
                self._tooltip_x, self._tooltip_y = None, None
                self.current_tooltip.notify_change() # We force its change because the language might have changed.
                
            self.current_tooltip.loop(dt)

        if cursor is None:
            cursor = self._default_cursor

        if cursor is self.current_cursor:
            has_changed = self.current_cursor.update(dt)
            if has_changed:
                pygame.mouse.set_cursor(self.current_cursor.get(self.settings))
                # Trigger the update of the cursor.
                pygame.mouse.set_pos(*pos)
        else:
            self.current_cursor.reset()
            self.current_cursor = cursor
            pygame.mouse.set_cursor(self.current_cursor.get(self.settings))
            # Trigger the update of the cursor.
            pygame.mouse.set_pos(*pos)
    
    @lru_cache()
    def visible_children(self) -> list[Frame]:
        return sorted(filter(lambda ch: (ch.is_visible() and ch._x is not None), self.frame_children), key=lambda ch: ch.layer)

    def draw(self, screen: pygame.Surface):
        """Draw the phase's surface on the screen."""
        for frame in self.visible_children():
            surf = frame.get_surface()
            screen.blit(surf, (frame.relative_left, frame.relative_top))

        if self.current_tooltip is not None and self._tooltip_delay < 0:
            if self._tooltip_x is None:
                x, y = self.mouse.get_position() # We set the position of the tooltip with the position of the mouse.
                self._tooltip_x, self._tooltip_y = x, y
            screen.blit(self.current_tooltip.get_surface(self), (self._tooltip_x, max(0, self._tooltip_y - self.current_tooltip.height)))

    def make_surface(self) -> pygame.Surface:
        pass
