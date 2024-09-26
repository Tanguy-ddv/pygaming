"""The frame module contain the Frame class, base of all displayed object."""
from __future__ import annotations
from typing import Optional
import pygame
from .animated_surface import AnimatedSurface
from ..phase import GamePhase
from .element import Element, TOP_LEFT, SurfaceLike

class Frame(Element):
    """
    The Frame represent a fraction of the screen.
    It has backgrounds and can contain many elements, including other frames, widgets and actors.
    """

    def __init__(
        self,
        master: GamePhase | Frame, # Frame or phase, no direct typing to avoid circular import
        x: int,
        y: int,
        background: SurfaceLike,
        focused_background: Optional[SurfaceLike] = None,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        layer: int = 0,
        hover_surface: Optional[pygame.Surface] = None,
        hover_cursor: Optional[pygame.Cursor] = None,
        continue_animation: bool = False
    ) -> None:
        """
        Create the frame.

        Params:
        ----
        - master: Another Frame or a phase.
        - x: the coordinate of the left of the frame, in its master.
        - y: the coordinate of the top of the frame, in its master.
        - background: The AnimatedSurface or Surface representing the background of the Frame.
        - focused_background: The AnimatedSurface or Surface representing the background of the Frame when it is focused.
        If None, copy the background
        - layer: the layer of the frame on its master. Objects having the same master are blitted on it by increasing layer.
        - hover_surface: Surface. If a surface is provided, it to be displayed at the mouse location when the
        frame is hovered by the mouse.
        - hover_cursor: Cursor. If a cursor is provided, it is the cursor of the mouse when the mouse is over the frame.
        - continue_animation: bool. If set to False, switching from focused to unfocused will reset the animations.
        """
        self.children: list[Element] = []

        Element.__init__(
            self,
            master,
            background,
            x,
            y,
            anchor,
            layer,
            hover_surface,
            hover_cursor,
            can_be_disabled=False,
            can_be_focused=True
        )
        self._continue_animation = continue_animation

        self.focused = False
        self._current_object_focus = None
        if focused_background is None:
            focused_background = self.surface.copy()
        elif isinstance(focused_background, pygame.Surface):
            self.focused_background = AnimatedSurface([focused_background], 4, 0)
        else:
            self.focused_background = focused_background
        self.current_hover_surface = None

    def add_child(self, child: Element):
        """Add a new element to the child list."""
        self.children.append(child)

    def update_hover(self, hover_x, hover_y) -> tuple[bool, pygame.Surface | None]:
        """Update the hovering."""
        hover_x -= self.x
        hover_y -= self.y
        is_one_hovered = False
        for child in self.children:
            if child.visible:
                if child.x < hover_x < child.x + child.width and child.y < hover_y < child.y + child.height:
                    is_child_hovered, surf = child.update_hover(hover_x, hover_y)
                    if is_child_hovered:
                        is_one_hovered = True
                        self.current_hover_surface = surf
        return is_one_hovered, self.current_hover_surface

    def update_focus(self, click_x, click_y):
        """Update the focus of all the children in the frame."""
        click_x -= self.x
        click_y -= self.y
        self.focused = True
        self.surface.reset()
        one_is_clicked = False
        for (i,child) in enumerate(self.children):
            if child.visible and child.can_be_focused:
                if child.x < click_x < child.x + child.width and child.y < click_y < child.y + child.height:
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
        return background
