from .widget.base_widget import BaseWidget
import pygame
from ..utils.color import Color, white
from .inputs import Inputs
from .positionable import Positionable

class Frame(Positionable):

    def __init__(self, x: int, y :int, width: int, height: int, background: pygame.Surface | Color = white, layer: int = 0) -> None:
        self.widgets: list[BaseWidget] = []
        Positionable.__init__(self, x, y, layer)
        self.width = width
        self.height = height
        
        if isinstance(background, Color):
            self.background = pygame.Surface((width, height))
            self.background.fill(background.to_RGBA())
        else:
            self.background = background.subsurface((0,0, width, height))
    
    @property
    def shape(self):
        return (self.width, self.height)

    @property
    def top_left(self):
        return (self.x, self.y)

    @property
    def rect(self):
        return pygame.rect.Rect(self.x, self.y, self.width, self.height)

    def add_widget(self, widget: BaseWidget):
        self.widgets.append(widget)
    
    def update_focus(self, click_x, click_y):
        """Update the focus of all the widgets in the phase."""
        click_x -= self.x
        click_y -= self.y
        for widget in self.widgets:
            if widget.visible:
                if widget.x < click_x < widget.x + widget.width and widget.y < click_y < widget.y + widget.height:
                    widget.focus()
                else:
                    widget.unfocus()
            else:
                widget.unfocus()

    def remove_focus(self):
        """Remove the focus of all the widgets."""
        for widget in self.widgets:
            widget.unfocus()
    
    def update_widgets(self, inputs: Inputs, loop_duration: int):
        """Update all the widgets."""
        for widget in self.widgets:
            widget.update(inputs, loop_duration, self.x, self.y)
        
    def get_surface(self):
        background = self.background.copy()
        for widget in self.widgets:
            x = widget.x
            y = widget.y
            surface = widget.get_surface()
            background.blit(surface, (x,y))
        return background