"""The frame module contain the Frame class, base of all displayed object."""
from __future__ import annotations
from typing import Optional
import numpy as np
import pygame
from ._abstract import Master
from .element import Element
from .art.art import Art
from .camera import Camera
from .anchors import CENTER_CENTER, TOP_LEFT, Anchor, AnchorLike
from ..inputs import Click
class Frame(Element, Master):
    """
    The Frame represent a fraction of the screen.
    It has backgrounds and can contain many elements, including other frames, widgets and actors.
    """

    def __init__(
        self,
        master: Master,
        background: Art,
        size: Optional[tuple[int, int]] = None,
        focused_background: Optional[Art] = None,
        camera: Optional[Camera] = None,
        continue_animation: bool = False,
        update_if_invisible: bool = False
    ) -> None:
        """
        Create the frame.

        Params:
        ----
        - master: Another Frame or a GamePhase.
        - background: The AnimatedSurface or Surface representing the background of the Frame.
        - size: tuple[int, int]. The size of the Frame. If None, the size of the background is used instead.
        - focused_background: The AnimatedSurface or Surface representing the background of the Frame when it is focused.
        If None, copy the background
        - camera: Camera, the rectangle of the background to get the image from. Use if you have a big background
        If None, the top left is 0,0 and the dimensions are the window dimensions.
        - layer: the layer of the frame on its master. Objects having the same master are blitted on it by increasing layer.
        - continue_animation: bool. If set to False, switching from focused to unfocused will reset the animations.
        """
        window = pygame.Rect(0, 0, *(background.size if size is None else size))

        self.has_a_widget_focused = False

        if camera is None:
            camera = Camera(0, 0, *window.size)
        
        self.camera = camera

        Master.__init__(self, window)
        self._compute_wc_ratio(master=master)
        Element.__init__(
            self,
            master,
            background,
            None,
            None,
            False,
            True,
            None,
            update_if_invisible=update_if_invisible
        )
        self._continue_animation = continue_animation

        self.focused = False
        self._current_object_focus = None
        if focused_background is None:
            self.focused_background = self.background
        else:
            self.focused_background = focused_background
        
        self.width = self.window.width
        self.height = self.window.height

    def place(self, x: int, y: int, anchor: AnchorLike = TOP_LEFT, layer: int = 0):

        """Place the Frame. Its width and height have already been defined"""
        self.anchor = Anchor(anchor)
        self._x = self.window.left = x - self.anchor[0]*self.window.width
        self._y = self.window.top = y - self.anchor[1]*self.window.height
        self.layer = layer

        self.get_on_master()
        if self.on_master:
            self.master.notify_change()
        
        return self

    def _compute_wc_ratio(self, master: Master = None):
        """Recompute the ratio between the window and the camera dimensions."""
        if master is None:
            master = self.master
        self.wc_ratio = self.window.width/self.camera.width*master.wc_ratio[0], self.window.height/self.camera.height*master.wc_ratio[1]

    def get_hover(self) -> tuple[bool, pygame.Surface | None]:
        """Update the hovering."""
        surf, cursor = None, None
        mouse_pos = self.game.mouse.get_position()
        check_contact = True
        for child in self.visible_children:
            if check_contact and child.is_contact(mouse_pos):
                surf, cursor = child.get_hover()
                check_contact = False # This is a "smooth break" to avoid checking if there is a contact for every child once one is found.
            else:
                child.unset_hover()
        return surf, cursor

    def update_focus(self, click: Click | None):
        """Update the focus of all the children in the frame."""
        if not self.focused:
            self.switch_background()
        self.focused = True
        one_is_clicked = False

        for (i,child) in enumerate(self._widget_children):
            if child.is_contact(click) and not child.disabled:
                child.focus()
                self._current_object_focus = i
                one_is_clicked = True
                self.has_a_widget_focused = True
            else:
                if self.focused:
                    child.unfocus()

        for (i, child) in enumerate(self._frame_childern):
            if child.is_contact(click):
                child.update_focus(click)
        if not one_is_clicked:
            self._current_object_focus = None
            self.has_a_widget_focused = False

    def notify_change_all(self):
        """Force the change notification to remake every surface."""
        self.notify_change()

        for child in self.children:
            child.notify_change()

        for frame in self._all_frame_children:
            frame.notify_change_all()

    def unfocus(self):
        """Unfocus the Frame by unfocusing itself and its children"""
        super().unfocus()
        for child in self.children:
            child.unfocus()
        self.notify_change()

    def next_object_focus(self):
        """Change the focused object."""
        if self.focused and self.has_a_widget_focused:

            widget_children = [wc for wc in self._widget_children if not wc.disabled]
            if len(widget_children) > 1:

                for element in widget_children:
                    if element.focused:
                        element.unfocus()

                next_index = (1 + self._current_object_focus)%len(widget_children)
                widget_children[next_index].focus()
                self._current_object_focus = next_index

        else:
            for child in self._frame_childern:
                child.next_object_focus()

    def remove_focus(self):
        """Remove the focus of all the children."""
        self.focused = False
        self.has_a_widget_focused = False
        focused_children = list(child for child in self.children if child.focused)
        if focused_children:
            for child in focused_children:
                child.unfocus()
            self.switch_background()

    def switch_background(self):
        """Switch to the focused background or the normal background."""
        if not self._continue_animation:
            if not self.focused:
                self.focused_background.reset()
            else:
                self.background.reset()
        self.notify_change()

    def start(self):
        """Execute this method at the beginning of the phase."""
        for child in self.children:
            child.begin()
        self.focused_background.start(**self.game.settings)

    def end(self):
        """Execute this method at the end of the phase, unload all the arts."""
        for child in self.children:
            child.finish()
        self.focused_background.end()

    def loop(self, loop_duration: int):
        """Update the frame every loop iteration."""
        if not self._continue_animation:
            if not self.focused:
                has_changed = self.background.update(loop_duration)
            else:
                has_changed = self.focused_background.update(loop_duration)
            if has_changed:
                self.notify_change()
        else:
            has_changed = self.background.update(loop_duration)
            if has_changed:
                self.notify_change()
        self.update(loop_duration)

    def update(self, loop_duration: int):
        """Update all the children of the frame."""
        for element in self.children:
            element.loop(loop_duration)

    @property
    def _widget_children(self):
        """Return the list of visible widgets in the frame."""
        return list(filter(lambda elem: not isinstance(elem, Frame) and elem.can_be_focused and not elem.disabled, self.visible_children))

    @property
    def _frame_childern(self) -> list[Frame]:
        """Return all children that are visible frames."""
        return list(filter(lambda elem: isinstance(elem, Frame), self.visible_children))

    @property
    def _all_frame_children(self) -> list[Frame]:
        """Return all children that are frames, visible or not."""
        return list(filter(lambda elem: isinstance(elem, Frame), self.children))

    def make_surface(self) -> pygame.Surface:
        """Return the surface of the frame as a pygame.Surface"""
        if self.focused:
            background = self.focused_background.get(match=self.background if self._continue_animation else None, **self.game.settings)
        else:
            background = self.background.get(None, **self.game.settings)
        for child in self.visible_children:
            background.blit(child.get_surface(), child.relative_rect.topleft)

        surf = self.camera.get_surface(background, self.game.settings)
        if self.window.size != self.camera.size:
            surf = pygame.transform.scale(surf, self.window.size)
        return surf

    def move_camera(self, dx, dy):
        """Move the camera on the frame."""
        dx = np.clip(int(dx), - self.camera.left, self.width - self.camera.right)
        dy = np.clip(int(dy), - self.camera.top, self.height - self.camera.bottom)

        if dx != 0 or dy != 0:
            self.camera.move_ip(dx, dy)
            self._compute_wc_ratio()
            for child in self.children:
                child.get_on_master() # All children recompute whether they are on the master (this frame) or out.
            self.notify_change()

    def set_camera_position(self, new_x, new_y, anchor: AnchorLike = TOP_LEFT):
        """Reset the camera position on the frame with a new value."""
        anchor = Anchor(anchor)
        new_y = np.clip(int(new_y - anchor[1]*self.camera.height), 0, self.height - self.camera.height)
        new_x = np.clip(int(new_x - anchor[0]*self.camera.width), 0, self.width - self.camera.width)

        if (new_x, new_y) != self.window.topleft:
            self.camera.move_ip(self.camera.left - new_x, self.camera.top - new_y)
            self._compute_wc_ratio()
            for child in self.children:
                child.get_on_master()
            self.notify_change()

    def zoom_camera(self, ratio_x: float, target: AnchorLike = CENTER_CENTER, ratio_y = None):

        """
        Zoom by a given factor on the target point.

        if ratio is > 1, the camera will zoom by a factor ratio (the details will appear bigger).
        if ratio is < 1, the camera will unzoom by a factor ratio (the details will appear smaller).
        """

        target = Anchor(target)

        if ratio_y is None:
            ratio_y = ratio_x

        new_width = np.minimum(self.camera.width/ratio_x, self.width)
        new_height = np.minimum(self.camera.height/ratio_y, self.height)

        if ratio_x != 1 or ratio_y != 1:
            zoom_point = self.camera.width*target[0], self.camera.height*target[1]
            left = zoom_point[0] - new_width
            top = zoom_point[1] - new_height
            left = np.clip(left, 0, self.width - new_width)
            top = np.clip(top, 0, self.height - new_height)

            self.camera.inflate_ip(ratio_x, ratio_y)
            self.camera.topleft = (top, left)
            self._compute_wc_ratio()
            for child in self.children:
                child.get_on_master() # All children recompute whether they are on the master (this frame) or out.
            self.notify_change()
        
    def unset_hover(self):
        for child in self.children:
            child.unset_hover()
    
    def is_child_on_me(self, child):
        """Return whether the child is visible on the frame or not."""
        return self.camera.colliderect(child.relative_rect)

    @property
    def relative_left(self):
        return self.window.left
    
    @property
    def relative_top(self):
        return self.window.top
    
    @property
    def relative_right(self):
        return self.window.right
    
    @property
    def relative_bottom(self):
        return self.window.bottom

    @property
    def absolute_left(self):
        """The absolute coordinates of the frame depends on the camera."""
        return int(self.master.absolute_left + self.relative_left - self.camera.left*self.wc_ratio[0])

    @property
    def absolute_top(self):
        """The absolute coordinates of the frame depends on the camera."""
        return int(self.master.absolute_top + self.relative_top - self.camera.top*self.wc_ratio[1])

    @property
    def absolute_right(self):
        """The absolute coordinates of the frame depends on the camera."""
        return self.absolute_left + self.window.width*self.wc_ratio[0]

    @property
    def absolute_bottom(self):
        """The absolute coordinates of the frame depends on the camera."""
        return self.absolute_top + self.window.height*self.wc_ratio[1]
