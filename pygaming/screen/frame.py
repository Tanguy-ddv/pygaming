"""The frame module contain the Frame class, base of all displayed object."""
import pygame
from .backgrounds import Backgrounds, BackgroundsLike
from .element import Element

class Frame(Element):
    """
    The Frame represent a fraction of the screen.
    It has backgrounds and can contain many elements, including other frames, widgets and actors.
    """

    def __init__(
        self,
        master,
        x: int,
        y :int,
        width: int,
        height: int,
        background: BackgroundsLike,
        focus_background: BackgroundsLike = None,
        layer: int = 0,
        image_duration: list[int] | int = 1000,
        focus_image_duration: list[int] | int = 1000,
        image_introduction: int = 0,
        focus_image_introduction: int = 0,
        hover_surface: pygame.Surface | None = None,
        hover_cursor: pygame.Cursor | None = None,
    ) -> None:
        """
        Create the frame.

        Params:
        ----
        master: Another Frame or a phase.
        x, y: the coordinate of the top left of the frame, in its master.
        width, height: the dimension of the frame.
        background: A BackgroundsLike object. If it is a Color, create a surface of this color. RGBA colors are possible.
        if it is a str, and this str is in the pygame.colors.THECOLORS dict, find the color with the dict.
        if it is Surface, reshape the surface.
        if it is an ImageFile, get the surface from it.
        If it is a list of one of them, create a list of surfaces. The background is then changed every gif_duration.
        focus_background: Another BackgroundsLike object. Same as 'background' but used when the frame is focused.
        layer: the layer of the frame on its master. Objects having the same master are blitted on it by increasing layer.
        image_duration (ms): If a list is provided as background, the background of the frame is changes every image_duration.
        if image_duration is a list, it must have the same length as background.
        in this case, the i-th image of the background will be displayed image_duration[i] ms.
        focus_image_duration: same as image_duration but when the frame is focused.
        image_introduction: int, if you provided a list for the backgrounds, the background will not cycle back to 0
        but to this index. 
        focus_image_introduction: same as image_introduction but when the frame is focused.
        hover_surface: Surface. If a surface is provided, it to be displayed at the mouse location when the
        frame is hovered by the mouse.
        hover_cursor: Cursor. If a cursor is provided, it is the cursor of the mouse when the mouse is over the frame.
        """
        self.children: list[Element] = []
        if focus_background is None:
            focus_background = background
        Element.__init__(
            self,
            master,
            background,
            x,
            y,
            width,
            height,
            layer,
            image_duration,
            image_introduction,
            hover_surface,
            hover_cursor
        )
        self.width = width
        self.height = height
        self.focused = False
        self._current_object_focus = None
        self.focus_background = Backgrounds(
            width,
            height,
            focus_background,
            focus_image_duration,
            focus_image_introduction
        )
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
        for child in self.children:
            child.unfocus()

    def _update_objects(self, loop_duration: int):
        """Update all the children."""
        for element in self.children:
            element.update(loop_duration)

    @property
    def visible_children(self):
        """Return the list of visible children sorted by increasing layer."""
        return sorted(filter(lambda ch: ch.visible, self.children), key= lambda w: w.layer)

    def get_surface(self):
        """Return the surface of the frame as a pygame.Surface"""
        background = self.backgrounds.get().copy()
        for child in self.visible_children:
            x = child.x
            y = child.y
            surface = child.get_surface()
            background.blit(surface, (x,y))
        return background

    def update(self, loop_duration: int):
        """Update the frame."""
        self._update_objects(loop_duration)
