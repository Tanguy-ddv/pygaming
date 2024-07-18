from ._backgrounds import Backgrounds, BackgroundsLike
import pygame
from ..inputs import Inputs
from ._positionable import Positionable

class Frame(Positionable):

    def __init__(self, master, x: int, y :int, width: int, height: int, background: BackgroundsLike, layer: int = 0) -> None:
        self.children: list[Positionable] = []
        Positionable.__init__(self, x, y, layer)
        self.width = width
        self.height = height
        self.focus = False
        self.visible = True
        self._current_object_focus = None
        self.backgrounds = Backgrounds(width, height, background)
        self.master = master
        self.master.add_child(self)
    
    @property
    def shape(self):
        return (self.width, self.height)

    @property
    def top_left(self):
        return (self.x, self.y)

    @property
    def rect(self):
        return pygame.rect.Rect(self.x, self.y, self.width, self.height)

    def add_child(self, child: Positionable):
        self.children.append(child)
    
    def update_focus(self, click_x, click_y):
        """Update the focus of all the objects in the phase."""
        click_x -= self.x
        click_y -= self.y
        self.focus = True
        one_is_clicked = False
        for (i,object) in enumerate(self.children):
            if object.visible and object.can_be_focused:
                if object.x < click_x < object.x + object.width and object.y < click_y < object.y + object.height:
                    object.focus()
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
    
    def __update_objects(self, inputs: Inputs, loop_duration: int):
        """Update all the children."""
        for object in self.children:
            object.update(inputs, loop_duration, self.x, self.y)
        
    def get_surface(self):
        background = self.backgrounds.get_background().copy()
        for object in sorted(self.objects, key= lambda w: w.layer):
            x = object.x
            y = object.y
            surface = object.get_surface()
            background.blit(surface, (x,y))
        return background

    def update(self, inputs: Inputs, loop_duration: int):
        self.__update_objects(inputs, loop_duration)
