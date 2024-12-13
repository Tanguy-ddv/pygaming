"""The keyboard class is used to manage the inputs."""

import pygame

from .mouse import Mouse
from .keyboard import Keyboard

class Inputs:
    """
    The keyboard class is used to manage the inputs.
    check if the user clicked somewhere or if a key have been pressed by using this class.
    """

    def __init__(self, mouse: Mouse, keyboard: Keyboard) -> None:
        self.event_list: list[pygame.event.Event] = []
        self.mouse = mouse
        self.keyboard = keyboard

    def update(self, loop_duration: int):
        """Get the current events and update the mouse and the keyboard."""
        self.event_list = pygame.event.get()
        self.keyboard.update(self.event_list)
        self.mouse.update(loop_duration, self.event_list)

    @property
    def quit(self):
        """Return True if the user quited the pygame window."""
        return any(event.type == pygame.QUIT for event in self.event_list)
