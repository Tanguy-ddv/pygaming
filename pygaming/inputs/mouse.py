"""The mouse module contains the mouse and click classes to know what is the player doing with the mouse."""

from dataclasses import dataclass
import pygame
from ..settings import Settings


class Mouse:
    """The Mouse class is used to manage mouse inputs."""

    def __init__(self, settings: Settings) -> None:

        self._x, self._y = pygame.mouse.get_pos()
        self.v_x = 0
        self.v_y = 0
        self._settings = settings
        self.event_list: list[pygame.event.Event] = []
        self.clicks: list[Click | None] = [None, None, None, None, None]

    def update(self, loop_duration: int, event_list: list[pygame.event.Event]):
        """Update the mouse at every loop iteration."""
        self._x, self._y = pygame.mouse.get_pos()
        dx, dy = pygame.mouse.get_rel()
        self.v_x = dx/loop_duration
        self.v_y = dy/loop_duration
        pressed = pygame.mouse.get_pressed(5)
        for button, button_pressed in enumerate(pressed):
            if button_pressed:
                if self.clicks[button] is None:
                    self.clicks[button] = Click(self._x, self._y)
                else:
                    self.clicks[button].update_pos(self._x, self._y, loop_duration)
            else:
                self.clicks[button] = None
        self.event_list = event_list

    def get_velocity(self):
        """Return the velocity corrected by the sensibility settings."""
        return self.v_x*self._settings.get("sensibility")*2, self.v_y*self._settings.get("sensibility")*2

    def get_position(self):
        """Return the current mouse position."""
        return self._x, self._y

    def get_click(self, button: int):
        """Return the click."""
        return self.clicks[button - 1]

    def get_wheel(self):
        """Return +1 is the player is turning the wheel up, -1 if the player is turning the wheel down, 0 otherwise."""
        for event in self.event_list:
            if event.type == pygame.MOUSEWHEEL:
                return event.y
        return 0

@dataclass(init=False)
class Click:
    """A click represent the fact that the player is clicking with one of the 5 buttons."""

    def __init__(self: int, x: int, y: int) -> None:
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.duration = 0

    def update_pos(self, x: int, y: int, loop_duration: int):
        """Update the position of the click at every loop iteration."""
        self.x = x
        self.y = y
        self.duration += loop_duration
