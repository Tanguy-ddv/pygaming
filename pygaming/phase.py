"""A phase is one step of the game."""
import pygame
from abc import ABC, abstractmethod
from .screen.frame import Frame
from .inputs import Inputs
from .config import Config
from .game import Game

class Phase(ABC):
    """
    A Phase is a step in the game. Each game should have a few phases.
    Exemple of phases: menus, lobby, stages, ...
    Create a subclass of phase to do whatever you need by
    rewriting the _init, the __init__, _update and/or _end method.
    """

    def __init__(self, game: Game) -> None:
        """
        Create the phase.

        Game: the game instance
        """
        ABC.__init__(self)
        self.game = game
        self.frames: list[Frame] = []
        self.absolute_x = 0
        self.absolute_y = 0
        self.current_hover_surface = None
        self._init()
    
    def add_child(self, frame: Frame):
        """Add a new frame to the phase."""
        self.frames.append(frame)
    
    def _init(self):
        pass
    
    def __update_focus(self, inputs: Inputs):
        """Update the focus of all the frames."""
        clicks = inputs.get_clicks()
        if 1 in clicks and not clicks[1].up:
            x = clicks[1].x
            y = clicks[1].y
            for frame in self.frames:
                if frame.x < x < frame.x + frame.width and frame.y < y < frame.y + frame.height:
                    frame.update_focus(x, y)
                else:
                    frame.remove_focus()
        
        actions = inputs.get_actions()
        if "next widget focus" in actions and actions["next widget focus"]:
            for frame in self.frames:
                if frame.focused:
                    frame.next_object_focus()
                
    def __update_hover(self, inputs: Inputs, config: Config):
        """Update the cursor and the over hover surface based on whether we are above one element or not."""
        clicks = inputs.get_clicks()
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

        if not is_one_hovered:
            pygame.mouse.set_cursor(config.get_cursor())
    
    def update(self, inputs: Inputs, loop_duration: int):
        """Update the phase."""
        self._update(inputs, loop_duration)
        self.__update_focus(inputs)
        self.__update_hover(inputs, )
        for frame in self.frames:
            frame.update(inputs, loop_duration)

    def _update(self, inputs: Inputs, loop_duration: int):
        """Update the phase."""

    @property
    def visible_frames(self):
        return sorted(filter(lambda f: f.visible, self.frames), key= lambda w: w.layer)
    
    def get_surface(self, width, height):
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        for frame in self.visible_frames:
            surf = frame.get_surface()
            bg.blit(surf, (frame.x, frame.y))
        return bg
    
    def end(self, **kwargs):
        """Execute this when you change the frame for another one."""
        self._end(**kwargs)

    def _end(self, **kwargs):
        """Action to do when the phase is ended."""