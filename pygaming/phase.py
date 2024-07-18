"""A phase is one step of the game."""
import pygame
from abc import ABC, abstractmethod
from .screen.frame import Frame
from .inputs import Inputs

class Phase(ABC):
    """
    A Phase is a step in these. Each game should have a few phases.
    Exemple of phases: menus, lobby, stages, ...
    A phase is composed by a set of frames
    """

    def __init__(self) -> None:
        ABC.__init__(self)
        self.frames: list[Frame] = []
        self.absolute_x = 0
        self.absolute_y = 0
    
    def add_child(self, frame: Frame):
        """Add a new frame to the phase."""
        self.frames.append(frame)
    
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
    
    def update(self, inputs: Inputs, loop_duration: int):
        """Update the phase."""
        self._update(inputs, loop_duration)
        self.__update_focus()
        for frame in self.frames:
            frame.update()

    @abstractmethod
    def _update(self, inputs: Inputs, loop_duration: int):
        """Update the phase."""