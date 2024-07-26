from .backgrounds import Backgrounds, BackgroundsLike
import pygame
from ..inputs import Inputs
from .element import Element

class Frame(Element):

    def __init__(
        self, 
        master, 
        x: int, 
        y :int, 
        width: int, 
        height: int, 
        background: BackgroundsLike, 
        layer: int = 0, 
        gif_duration: int = 1000,
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
        If it is a list of one of them, create a list of surfaces. The background is then changed every gif_duration
        layer: the layer of the frame on its master. Objects having the same master are blitted on it by increasing layer.
        gif_duration (ms): If a list is provided as background, the background of the frame is change every gif_duration.
        """
        self.children: list[Element] = []
        Element.__init__(self, master, background, x, y, width, height, layer, gif_duration, hover_surface, hover_cursor)
        self.width = width
        self.height = height
        self._current_object_focus = None
        self.backgrounds = Backgrounds(width, height, background)
    
    @property
    def shape(self):
        return (self.width, self.height)

    @property
    def top_left(self):
        return (self.x, self.y)

    @property
    def rect(self):
        return pygame.rect.Rect(self.x, self.y, self.width, self.height)

    def add_child(self, child: Element):
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
                    object.unfocus()
            else:
                object.unfocus()
        if not one_is_clicked:
            self._current_object_focus = None
        
    def next_object_focus(self):
        """Change the focused object."""
        if self._current_object_focus is None:
            self._current_object_focus = 0
        
        for object in self.children:
            if object.can_be_focused:
                object.unfocus()

        for i in range(1, len(self.children)):
            j = (i + self._current_object_focus)%len(self.children)
            if self.children[j].can_be_focused:
                self.children[j].focus()
                self._current_object_focus = j
                break

    def remove_focus(self):
        """Remove the focus of all the children."""
        self.focus = False
        for child in self.children:
            child.unfocus()
    
    def _update_objects(self, inputs: Inputs, loop_duration: int):
        """Update all the children."""
        for object in self.children:
            object.update(inputs, loop_duration, self.x, self.y)
        
    @property
    def visible_children(self):
        return sorted(filter(lambda ch: ch.visible, self.children), key= lambda w: w.layer)
        
    def get_surface(self):
        background = self.backgrounds.get_background(self._gif_index).copy()
        for child in self.visible_children:
            x = child.x
            y = child.y
            surface = child.get_surface()
            background.blit(surface, (x,y))
        return background

    def update(self, inputs: Inputs, loop_duration: int):
        self._update_animation(loop_duration)
        self._update_objects(inputs, loop_duration)
