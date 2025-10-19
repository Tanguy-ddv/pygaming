"""The frame module contain the Frame class."""
from typing import Optional, Self
import numpy as np
import pygame
from functools import lru_cache
from ._abstract import Master, GraphicalFocusable, Focusable, Child, Collideable
from .art.art import Art
from .camera import Camera
from .anchors import CENTER_CENTER, TOP_LEFT, Anchor, AnchorLike
from ..inputs import Click
from .hover import Cursor, Tooltip
from .states import WidgetStates
class Frame(GraphicalFocusable, Collideable, Master):
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
        self.window = pygame.Rect(0, 0, *(background.size if size is None else size))
        self.children: set[Child]
        self.frame_children: set[Frame]
        self.has_a_widget_focused = False

        if camera is None:
            camera = Camera(0, 0, *self.window.size)
        
        self.camera = camera

        super().__init__(
            master=master,
            hitbox=None,
            art=background,
            focused_art=focused_background,
            update_if_invisible=update_if_invisible,
            continue_animation=continue_animation
        )
        self.master.add_child(self, False, False, False, True, False)
        self._compute_wc_ratio()

        self.views = set()

    @property
    def width(self):
        return self.window.width

    @property
    def height(self):
        return self.window.height

    def _compute_wc_ratio(self, master: Master = None):
        """Recompute the ratio between the window and the camera dimensions."""
        if master is None:
            master = self.master
        self.wc_ratio = self.window.width/self.camera.width*master.wc_ratio[0], self.window.height/self.camera.height*master.wc_ratio[1]

    def get_hover(self, pos) -> tuple[Tooltip | None, Cursor | None]:
        """Update the hovering."""
        if self.is_contact(pos):
            tooltip, cursor = None, None
            for child in self.hoverable_children:
                child_tooltip, child_cursor = child.get_hover(pos)
                if child_tooltip is not None:
                    tooltip = child_tooltip
                if child_cursor is not None:
                    cursor = child_cursor
            return tooltip, cursor
        return None, None

    def notify_change(self):
        """Notify a change in the visual."""
        self._surface_changed = True
        for view in self.views:
            view.notify_change()
        if self.is_visible():
            self.master.notify_change()

    def unfocus(self):
        """Unfocus the Frame by unfocusing itself and its children"""
        super().unfocus()
        for child in self.focusable_children:
            child.unfocus()
        self.notify_change()

    def next_object_focus(self):
        """Change the focused object."""
        if self.state == WidgetStates.FOCUSED and self.has_a_widget_focused:
            widget_children: list[Focusable] = list(
                filter(
                    lambda child: child.state != WidgetStates.DISABLED,
                    self.focusable_children
                )
            )
            if len(widget_children) > 1:

                for element in widget_children:
                    element.unfocus()

                next_index = (1 + self._current_object_focus)%len(widget_children)
                widget_children[next_index].focus()
                self._current_object_focus = next_index

        else:
            for child in self.frame_children:
                child.next_object_focus()

    def remove_focus(self):
        """Remove the focus of all the children."""
        self.focused = False
        self.has_a_widget_focused = False
        focused_children = list(
            child for child in self.focusable_children if child.state == WidgetStates.FOCUSED
        )
        if focused_children:
            for child in focused_children:
                child.unfocus()
            self._arts.new_state()
            self.notify_change()

    def loop(self, dt: int):
        """Update the frame every loop iteration."""
        # Update the frame's background
        has_changed = self._arts.update(dt, self.state)
        if has_changed:
            self.notify_change()
        # Update the frame
        self.update(dt)

        # Update the children
        for element in self.children:
            element.loop(dt)

    @lru_cache()
    def visible_children(self):
        return sorted(filter(lambda ch: (ch.is_visible() and ch._x is not None), self.placeable_children), key=lambda ch: ch.layer)

    def make_surface(self) -> pygame.Surface:
        """Return the surface of the frame as a pygame.Surface"""
        background = self._arts.get(self.state, **self.game.settings).copy()
        for child in self.visible_children():
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
            for child in self.visible_children():
                if child._x is not None:
                    child.on_master = child.get_on_master()
            self.notify_change()

    def set_camera_position(self, new_x, new_y, anchor: AnchorLike = TOP_LEFT):
        """Reset the camera position on the frame with a new value."""
        anchor = Anchor(anchor)
        new_y = np.clip(int(new_y - anchor[1]*self.camera.height), 0, self.height - self.camera.height)
        new_x = np.clip(int(new_x - anchor[0]*self.camera.width), 0, self.width - self.camera.width)

        if (new_x, new_y) != self.window.topleft:
            self.camera.move_ip(self.camera.left - new_x, self.camera.top - new_y)
            self._compute_wc_ratio()
            for child in self.visible_children():
                child.on_master = child.get_on_master()
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
            for child in self.visible_children():
                child.on_master = child.get_on_master()
            self.notify_change()
        
    def unset_hover(self):
        for child in self.hoverable_children:
            child.unset_hover()
    
    def is_child_on_me(self, child):
        """Return whether the child is visible on the frame or not."""
        return (child in self.placeable_children
            and child._x is not None
            and (
                self.camera.colliderect(child.relative_rect) or any(
                    view.camera.collierect(child.relative_rect) for view in self.views
                )
            )
        )


    def place(self, x: int, y: int, anchor: AnchorLike = TOP_LEFT, layer=0) -> Self:
        super().place(x, y, anchor, layer)
        self.window.topleft = x - anchor[0]*self.window.width, y - anchor[1]*self.window.height
        return self

    def grid(self,
        row: int,
        column: int,
        grid = None,
        rowspan: int = 1,
        columnspan: int = 1,
        padx: int = 0,
        pady: int = 0,
        anchor: AnchorLike = TOP_LEFT,
        justify: AnchorLike = CENTER_CENTER,
        layer: int = 0
    ) -> Self:

        super().grid(row, column, grid, rowspan, columnspan, padx, pady, anchor, justify, layer) 
        self.window.topleft = self._x - anchor[0]*self.window.width, self._y - anchor[1]*self.window.height

        return self

    def move(self, dx: int = 0, dy: int = 0):
        if self._x is None:
            return

        super().move(dx, dy)
        self.window.topleft = self._x - self.anchor[0]*self.window.width, self._y - self.anchor[1]*self.window.height

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
        return int(self.master.absolute_left + self.relative_left)

    @property
    def absolute_top(self):
        """The absolute coordinates of the frame depends on the camera."""
        return int(self.master.absolute_top + self.relative_top)

    @property
    def absolute_right(self):
        """The absolute coordinates of the frame depends on the camera."""
        return self.absolute_left + self.window.width*self.master.wc_ratio[0]

    @property
    def absolute_bottom(self):
        """The absolute coordinates of the frame depends on the camera."""
        return self.absolute_top + self.window.height*self.master.wc_ratio[1]
