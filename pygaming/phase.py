"""A phase is one step of the game."""
import pygame
from abc import ABC, abstractmethod
from .screen.frame import Frame
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

        Game: the game instance
        """
        ABC.__init__(self)
        self._name = name
        self.runnable = runnable
        self.runnable.set_phase(name, self)
    
    @abstractmethod
    def start(self, **kwargs):
        """This method is called at the start of the phase and might need several arguments."""
        raise NotImplementedError()
    
    @abstractmethod
    def update(self):
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
    def _update(self, loop_duration: int):
        """Update the phase based on the inputs, network communications and the loop_duration. This method is called at every loop iteration."""
        raise NotImplementedError()
    
    @abstractmethod
    def end(self):
        """Action to do when the phase is ended."""
        raise NotImplementedError()

class ServerPhase(BasePhase, ABC):

    def __init__(self, name, server: Server) -> None:
        ABC.__init__(self)
        GamePhase.__init__(self, name, server)

    @property
    def server(self) -> Server:
        return self.runnable
    
    def update(self, loop_duration: int):
        self._update(loop_duration)

class GamePhase(BasePhase, ABC):
    
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
        return self.runnable
        
    def update(self, loop_duration: int):
        """Update the phase."""
        self._update(loop_duration)
        self.__update_focus()
        self.__update_hover()
        for frame in self.frames:
            frame.update(loop_duration)    
    
    def __update_focus(self):
        """Update the focus of all the frames."""
        clicks = self.game.inputs.get_clicks()
        if 1 in clicks and not clicks[1].up:
            x = clicks[1].x
            y = clicks[1].y
            for frame in self.frames:
                if frame.x < x < frame.x + frame.width and frame.y < y < frame.y + frame.height:
                    frame.update_focus(x, y)
                else:
                    frame.remove_focus()
        
        actions = self.game.inputs.get_actions()
        if "next widget focus" in actions and actions["next widget focus"]:
            for frame in self.frames:
                if frame.focused:
                    frame.next_object_focus()
                
    def __update_hover(self):
        """Update the cursor and the over hover surface based on whether we are above one element or not."""
        clicks = self.game.inputs.get_clicks()
        is_one_hovered = False
        if 0 in clicks:
            x = clicks[0].x
            y = clicks[0].y
            for frame in self.frames:
                if frame.x < x < frame.x + frame.width and frame.y < y < frame.y + frame.height:
                    is_frame_hovered, surf = frame.update_hover(x, y)
                    if is_frame_hovered:
                        is_one_hovered = True
                        self.current_hover_surface = surf
                        break

        if not is_one_hovered:
            cursor = self.game.config.get_cursor()
            if hasattr(pygame, cursor):
                cursor = getattr(pygame, cursor)
            pygame.mouse.set_cursor(cursor)
    
    @property
    def visible_frames(self):
        return sorted(filter(lambda f: f.visible, self.frames), key= lambda w: w.layer)
    
    def get_surface(self, width, height):
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        for frame in self.visible_frames:
            surf = frame.get_surface()
            bg.blit(surf, (frame.x, frame.y))
        return bg