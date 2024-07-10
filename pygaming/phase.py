"""A phase is one step of the game."""
import pygame
from .frame import Frame
from .inputs import Inputs

class Phase():
    """
    A Phase is a step in these. Each game should have a few phases.
    Exemple of phases: menus, lobby, stages, ...
    A phase is composed by a set of frames
    """

    def __init__(self, inputs: Inputs) -> None:
        self.frames: list[Frame] = []
        self.inputs = inputs
    
    def add_frame(self, frame: Frame):
        """Add a new frame to the phase."""
        self.frames.append(frame)
    
    def update_focus(self):
        """Update the focus of all the frames."""
        clicks = self.inputs.get_clicks()
        if 1 in clicks and not clicks[1].up:
            x = clicks[1].x
            y = clicks[1].y
            for frame in self.frames:
                if frame.x < x < frame.x + frame.width and frame.y < y < frame.y + frame.height:
                    frame.update_focus(x, y)
                else:
                    frame.remove_focus()
        actions = self.inputs.get_actions()
        if "next widget focus" in actions and actions["next widget focus"]:
            for frame in self.frames:
                if frame.focus:
                    frame.next_widget_focus()