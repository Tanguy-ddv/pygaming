"""A phase is one step of the game."""
from abc import ABC, abstractmethod
import pygame
from .screen.frame import Frame
from .error import PygamingException
from .game import Game
from .base import BaseRunnable
from .server import Server

class BasePhase(ABC):
    """
    A Phase is a step in the game. Each game should have a few phases.
    Exemple of phases: menus, lobby, stages, ...
    Create a subclass of phase to do whatever you need by
    rewriting the start, the __init__, _update and/or end method.
    If the game is online, you will need twice as much frames. One half for the Server and the other half for the game.
    For the server, don't use any frame, but use only the inputs from the players by using self.game.server.get_last_reception()
    and send data based on them to the players via self.game.server.send() (or .send_all()).
    """

    def __init__(self, name, runnable: BaseRunnable) -> None:
        """
        Create the phase.

        Runnable: the game or server instance
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
    def update(self, loop_duration: int):
        """
        Update the phase based on loop duration, inputs and network (via the game instance)
        This method is called at every loop iteration.
        """
        raise NotImplementedError()

    @abstractmethod
    def end(self):
        """Action to do when the phase is ended."""
        raise NotImplementedError()

class ServerPhase(BasePhase, ABC):
    """The ServerPhase is a game phase to be add to the server only."""

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
    """The ServerPhase is a game phase to be add to the game only."""

    def __init__(self, name, game: Game) -> None:
        ABC.__init__(self)
        BasePhase.__init__(self, name, game)
        self.frames: list[Frame] = []

        self.absolute_x = 0
        self.absolute_y = 0
        self.current_hover_surface = None

    def add_child(self, frame: Frame):
        """Add a new frame to the phase."""
        self.frames.append(frame)

    @property
    def game(self) -> Game:
        """Alias for the game."""
        return self.runnable

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
        self.update(loop_duration)
        self.__update_focus()
        self.__update_hover()
        for frame in self.frames:
            frame.loop(loop_duration)

    def __update_focus(self):
        """Update the focus of all the frames."""
        ck1 = self.mouse.get_click(1)
        if ck1:
            x = ck1.x
            y = ck1.y
            for frame in self.frames:
                if frame.absolute_left < x < frame.absolute_right and frame.absolute_top < y < frame.absolute_bottom:
                    frame.update_focus(x, y)
                else:
                    frame.remove_focus()

        actions = self.keyboard.get_actions()
        if "tab" in actions and actions["tab"]:
            for frame in self.frames:
                if frame.focused:
                    frame.next_object_focus()

    def __update_hover(self):
        """Update the cursor and the over hover surface based on whether we are above one element or not."""
        x,y = self.mouse.get_position()
        is_one_hovered = False
        for frame in self.frames:
            if frame.absolute_left < x < frame.absolute_right and frame.absolute_top < y < frame.absolute_bottom:
                is_frame_hovered, surf = frame.update_hover(x, y)
                if is_frame_hovered:
                    is_one_hovered = True
                    self.current_hover_surface = surf
                    break

        if not is_one_hovered:
            cursor = self.config.default_cursor
            if hasattr(pygame, cursor):
                cursor = getattr(pygame, cursor)
            pygame.mouse.set_cursor(cursor)

    @property
    def visible_frames(self):
        """Return all the visible frames sorted by increasing layer."""
        return sorted(filter(lambda f: f.visible, self.frames), key= lambda w: w.layer)

    def get_surface(self, width, height):
        """Return the surface to be displayed by the phase."""
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        for frame in self.visible_frames:
            surf = frame.get_surface()
            bg.blit(surf, (frame.x, frame.y))
        return bg
