"""A phase is one step of the game."""
from abc import ABC, abstractmethod
import pygame
import gc
from .error import PygamingException
from .game import Game
from .base import BaseRunnable
from .server import Server
from .database import SoundBox, TypeWriter



class BasePhase(ABC):
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

    @abstractmethod
    def next(self):
        """
        If the phase is over, return the name of the next phase, if the phase is not, return an empty string.
        If it is the end of the game, return 'NO_NEXT'
        """
        raise NotImplementedError()

    @abstractmethod
    def apply_transition(self, next_phase: str):
        """
        This method is called if the method next returns a new phase. Its argument is the name of the next phase.
        For each new phase possible, it should return a dict, whose keys are the name of the argument of the
        start method of the next phase, and the values are the values given to these arguments.
        """
        raise NotImplementedError()

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

    @abstractmethod
    def end(self):
        """Action to do when the phase is ended."""
        raise NotImplementedError()

class ServerPhase(BasePhase, ABC):
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
        BasePhase.__init__(self, name, server)

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

class GamePhase(BasePhase, ABC):
    """
    The GamePhase is a phase to be added to the game only.
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
    You can access to the network via `self.network` to send data to the server or receive data.
    You can acces to the logger via `self.logger`, to the config via `self.config`, to the settings with `self.settings`,
    to the database via `self.database`, to the input via `self.keyboard` and `self.mouse`,
    to the texts and speeches via `self.texts` and `self.speeches`, and
    to the soundbox and jukebox via `self.soundbox` and `self.jukebox`.
    """

    def __init__(self, name, game: Game) -> None:
        ABC.__init__(self)
        BasePhase.__init__(self, name, game)
        self.frames = [] # list[Frame]

        self.absolute_left = 0
        self.absolute_top = 0
        self.current_hover_surface = None
        self._surface_changed = True

    def add_child(self, frame):
        """Add a new frame to the phase."""
        self.frames.append(frame)

    def begin(self, **kwargs):
        """This method is called at the beginning of the phase."""
        self.game.keyboard.load_controls(self.settings, self.config, self._name)
        self.game.update_settings()
        self.game.soundbox = SoundBox(self.settings, self._name, self.database)
        self.game.typewriter = TypeWriter(self.database, self.settings, self._name)
        for frame in self.frames:
            frame.start()
        # Start the phase
        self.start(**kwargs)
    
    def finish(self):
        """This method is called at the end of the phase."""
        self.game.soundbox = None # Unload all the sounds
        self.game.typewriter = None # Unload all the fonts
        for frame in self.frames: # Unload 
            frame.end()
        self.end()
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

    def loop(self, loop_duration: int):
        """Update the phase."""
        self.__update_focus()
        self.__update_hover()
        self.update(loop_duration)
        for frame in self.frames:
            frame.loop(loop_duration)

    def __update_focus(self):
        """Update the focus of all the frames."""
        ck1 = self.mouse.get_click(1)
        if ck1:
            x = ck1.x
            y = ck1.y
            for frame in self.frames:
                if frame.is_contact((x,y)):
                    frame.update_focus(x, y)
                else:
                    frame.remove_focus()

        if "tab" in self.keyboard.actions_down and self.keyboard.actions_down["tab"]:
            for frame in self.frames:
                frame.next_object_focus()

    def __update_hover(self):
        """Update the cursor and the over hover surface based on whether we are above one element or not."""
        x,y = self.mouse.get_position()
        cursor, surf = None, None
        for frame in self.frames:
            if frame.is_contact((x,y)):
                surf, cursor = frame.update_hover()
                if surf is not None:
                    self.current_hover_surface: pygame.Surface = surf
                    break

        if surf is None:
            self.current_hover_surface = None

        if cursor is None:
            cursor = self.config.default_cursor
            if hasattr(pygame, cursor):
                cursor = getattr(pygame, cursor)
            pygame.mouse.set_cursor(cursor)
        else:
            pygame.mouse.set_cursor(cursor)

    @property
    def visible_frames(self):
        """Return all the visible frames sorted by increasing layer."""
        return sorted(filter(lambda f: f.visible, self.frames), key= lambda w: w.layer)
    
    def make_surface(self) -> pygame.Surface:
        """Make the new surface to be returned to his parent."""
        bg = pygame.Surface(self.config.dimension, pygame.SRCALPHA)
        for frame in self.visible_frames:
            surf = frame.get_surface()
            bg.blit(surf, (frame.relative_left, frame.relative_top))

        if self.current_hover_surface is not None:
            x, y = self.mouse.get_position()
            bg.blit(self.current_hover_surface, (x, y - self.current_hover_surface.get_height()))
        return bg

    def notify_change(self):
        """Notify the need to remake the last surface."""
        self._surface_changed = True

    def get_surface(self) -> pygame.Surface:
        """Return the surface to his parent."""
        if self._surface_changed:
            self._last_surface = self.make_surface()
            self._surface_changed = False
        return self._last_surface