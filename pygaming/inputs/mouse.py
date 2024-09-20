"""The mouse module contains the mouse and click classes to know what is the player doing with the mouse."""

from dataclasses import dataclass
import pygame


class Mouse:

    def __init__(self, settings) -> None:
        
        self._x = 0
        self._y = 0
        self.v_x = 0
        self.v_y = 0
        self._settings = settings
        self.update()
        self.clicks: list[Click | None] = [None, None, None, None, None]
        
    def update(self, loop_duration: int):
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

    
    def get_velocity(self):
        return self.v_x*self._settings.get("sensibility")*2, self.v_y*self._settings.get("sensibility")*2

    def get_position(self):
        return self._x, self._y

    def get_click(self, button: int):
        return self.clicks[button - 1]

@dataclass(init=False)
class Click:

    def __init__(self: int, x: int, y: int) -> None:
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.duration = 0
    
    def update_pos(self, x: int, y: int, loop_duration: int):
        self.x = x
        self.y = y
        self.duration += loop_duration
