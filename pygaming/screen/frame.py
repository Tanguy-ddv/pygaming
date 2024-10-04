"""The frame module contain the Frame class, base of all displayed object."""
from __future__ import annotations
from typing import Optional
import pygame
from .animated_surface import AnimatedSurface
from ..phase import GamePhase
from ..error import PygamingException
from .element import Element, TOP_LEFT, SurfaceLike

class Frame(Element):
    """
    The Frame represent a fraction of the screen.
    It has backgrounds and can contain many elements, including other frames, widgets and actors.
    """

    def __init__(
        self,
        master: GamePhase | Frame, # Frame or phase, no direct typing to avoid circular import
        window: pygame.Rect,
        background: SurfaceLike,
        focused_background: Optional[SurfaceLike] = None,
        background_window: Optional[pygame.Rect] = None,
        layer: int = 0,
        continue_animation: bool = False
    ) -> None:
        """
        Create the frame.

        Params:
        ----
        - master: Another Frame or a phase.
        - window: pygame.Rect, the rectangle in which show the frame in the master
        - background: The AnimatedSurface or Surface representing the background of the Frame.
        - focused_background: The AnimatedSurface or Surface representing the background of the Frame when it is focused.
        If None, copy the background
        - background_window: pygame.Rect, the rectangle of the background to get the image from. Use if you have a big background
        If None, the top left is 0,0 and the dimensions are the window dimensions.
        - layer: the layer of the frame on its master. Objects having the same master are blitted on it by increasing layer.
        - continue_animation: bool. If set to False, switching from focused to unfocused will reset the animations.
        """
        self.children: list[Element] = []
        x = window.left
        y = window.top
        self.window = window

        Element.__init__(
            self,
            master,
            background,
            x,
            y,
            TOP_LEFT,
            layer,
            None,
            None,
            can_be_disabled=False,
            can_be_focused=True
        )
        self._continue_animation = continue_animation

        if background_window is None:
            background_window = pygame.Rect(0, 0, self.window.width, self.window.height)
        if self.window.size != background_window.size:
            raise PygamingException(f"window and background window must have the same dimension, got {self.window.size} and {background_window.size}")
        self.background_window = background_window

        self.focused = False
        self._current_object_focus = None
        if focused_background is None:
            self.focused_background = self.surface.copy()
        elif isinstance(focused_background, pygame.Surface):
            self.focused_background = AnimatedSurface([focused_background], 4, 0)
        else:
            self.focused_background = focused_background

    def add_child(self, child: Element):
        """Add a new element to the child list."""
        self.children.append(child)

    def update_hover(self) -> tuple[bool, pygame.Surface | None]:
        """Update the hovering."""
        surf, cursor = None, None
        hover_x, hover_y = self.game.mouse.get_position()
        for child in self.visible_children:
            if child.absolute_rect.collidepoint(hover_x, hover_y):
                surf, cursor = child.update_hover()
        return surf, cursor

    def update_focus(self, click_x, click_y):
        """Update the focus of all the children in the frame."""
        click_x -= self._x
        click_y -= self._y
        self.focused = True
        self.surface.reset()
        one_is_clicked = False
        for (i,child) in enumerate(self.children):
            if child.visible and child.can_be_focused:
                if child.relative_rect.collidepoint(click_x, click_y):
                    child.focus()
                    self._current_object_focus = i
                    one_is_clicked = True
                else:
                    child.unfocus()
            else:
                child.unfocus()
        if not one_is_clicked:
            self._current_object_focus = None

    def switch_background(self):
        """Switch to the focused background or the normal background."""
        if not self._continue_animation:
            if not self.focused:
                self.focused_background.reset()
            else:
                self.surface.reset()

    def next_object_focus(self):
        """Change the focused object."""
        if self._current_object_focus is None:
            self._current_object_focus = 0

        for element in self.children:
            if element.can_be_focused:
                element.unfocus()

        for i in range(1, len(self.children)):
            j = (i + self._current_object_focus)%len(self.children)
            if self.children[j].can_be_focused:
                self.children[j].focus()
                self._current_object_focus = j
                break

    def remove_focus(self):
        """Remove the focus of all the children."""
        self.focused = False
        self.focused_background.reset()
        for child in self.children:
            child.unfocus()
        self.switch_background()

    def loop(self, loop_duration: int):
        """Update the frame every loop iteration."""
        if not self._continue_animation:
            if not self.focused:
                self.surface.update_animation(loop_duration)
            else:
                self.focused_background.update_animation(loop_duration)
        else:
            self.surface.update_animation(loop_duration)
            self.focused_background.update_animation(loop_duration)
        self.update(loop_duration)

    def update(self, loop_duration: int):
        """Update all the children of the frame."""
        for element in self.children:
            element.loop(loop_duration)

    @property
    def visible_children(self):
        """Return the list of visible children sorted by increasing layer."""
        return sorted(filter(lambda ch: ch.visible, self.children), key= lambda w: w.layer)

    def get_surface(self):
        """Return the surface of the frame as a pygame.Surface"""
        if self.focused:
            background = self.focused_background.get()
        else:
            background = self.surface.get()
        for child in self.visible_children:
            x = child.relative_left
            y = child.relative_top
            surface = child.get_surface()
            background.blit(surface, (x,y))
        return background.subsurface(self.background_window)

    def move_background(self, dx, dy):
        """Move the background in the window."""
        self.background_window.move(dx, dy)
    
    def set_background_position(self, new_x, new_y):
        """Reset the background position in the window with a new value."""
        self.background_window = pygame.Rect(new_x, new_y, *self.background_window.size)