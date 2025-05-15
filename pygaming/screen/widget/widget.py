"""The widget module contains the widget class, which is a base for all widgets."""
from abc import abstractmethod

from pygame import Surface, SRCALPHA
from ..frame import Frame
from .._abstract import Disableable, TextualDisableable, GraphicalDisableable, Placeable, Focusable, Master
from ..art import Art
from ..hover import Cursor, Tooltip, Hoverable, TextualHoverable
from ..hitbox import Hitbox
from ..states import WidgetStates
from ...color import Color
from ...database import TextFormatter
from ..anchors import Anchor, CENTER

class Widget(Hoverable, GraphicalDisableable):
    """Base class for hoverable and disableable widgets."""

    def __init__(
        self,
        master: Frame,
        art: Art,
        focused_art: Art | None = None,
        disabled_art: Art | None = None,
        hovered_art: Art | None = None,
        hitbox: Hitbox | None = None,
        tooltip: Tooltip | None = None,
        cursor: Cursor | None = None,
        continue_animation: bool = True,
        update_if_invisible: bool = False,
        **kwargs
    ) -> None:
    
        super().__init__(
            master=master,
            art=art,
            disabled_art=disabled_art,
            focused_art=focused_art,
            hitbox=hitbox,
            hovered_art=hovered_art,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible,
            **kwargs
        )

    @abstractmethod
    def get(self):
        """Return the value of the widget input."""
        raise NotImplementedError()

class TextualWidget(TextualHoverable, TextualDisableable):
    """Base class for hoverable, disableable and textual widgets."""

    def __init__(
        self,
        master: Frame,
        art: Art,
        font: str,
        color: Color,
        text_or_loc: str | TextFormatter,
        focused_art: Art | None = None, 
        focused_font: str | None = None,
        focused_font_color: Color | None = None,
        disabled_art: Art | None = None,
        disabled_font: str | None = None,
        disabled_font_color: Color | None = None,
        hovered_art: Art | None = None,
        hovered_font: str | None = None,
        hovered_font_color: Color | None = None,
        hitbox: Hitbox | None = None,
        tooltip: Tooltip | None = None,
        cursor: Cursor | None = None,
        continue_animation: bool = True,
        update_if_invisible: bool = False,
        justify: Anchor = CENTER,
        **kwargs
    ) -> None:
        
        super().__init__(
            master=master,
            art=art,
            font=font,
            color=color,
            disabled_art=disabled_art,
            focused_art=focused_art,
            hitbox=hitbox,
            text_or_loc=text_or_loc,
            justify=justify,
            hovered_art=hovered_art,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible,
            focused_font=focused_font,
            focused_font_color=focused_font_color,
            disabled_font=disabled_font,
            disabled_font_color=disabled_font_color,
            hovered_font=hovered_font,
            hovered_font_color=hovered_font_color,
            **kwargs
        )

    @abstractmethod
    def get(self):
        """Return the value of the widget input."""
        raise NotImplementedError()

class CompositeWidget(Master, Disableable):
    """A Composite widget is a widget composed of several widgets."""
    
    def __init__(self, master: Frame, size: tuple[int, int], update_if_invisible: bool = True, **kwargs):
        self._width, self._height = size
        super().__init__(master=master, update_if_invisible=update_if_invisible, hitbox=None, **kwargs)
        self._linked_focus_widget: Focusable | None = None
        self.master.add_child(self, False, False, False, True, False)
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return self._width, self._height
    
    def set_link_focus(self, widget: Focusable):
        """Add a new widget to the list of subwidgets."""
        self._linked_focus_widget = widget

    def disable(self):
        """Disable the object."""
        if self.state != WidgetStates.DISABLED:
            for widget in self.disableable_children:
                widget.disable()
            self.state = WidgetStates.DISABLED
            self.notify_change()

    def enable(self):
        """Enable the object."""
        if self.state == WidgetStates.DISABLED:
            for widget in self.disableable_children:
                widget.enable()
            self.state = WidgetStates.NORMAL
            self.notify_change()

    def focus(self):
        """Focus the object."""
        for widget in self.focusable_children: # make sure every subwidget is unfocused.
            widget.unfocus()
        if self.state == WidgetStates.NORMAL:
            if self._linked_focus_widget is not None:
                self._linked_focus_widget.focus()
            self.state = WidgetStates.FOCUSED
            self.notify_change()

    def unfocus(self):
        """Unfocus the object."""
        if self.state == WidgetStates.FOCUSED:
            for widget in self.focusable_children: # make sure every subwidget is unfocused.
                widget.unfocus()
            self.state = WidgetStates.NORMAL
            self.notify_change()

    def make_surface(self) -> Surface:
        surf = Surface(self.size, SRCALPHA)
        for widget in self.visible_children():
            surf.blit(widget.get_surface(), widget.relative_rect.topleft)
        return surf

    def is_child_on_me(self, child):
        """Return whether the child is visible on the frame or not."""
        return (child in self.placeable_children
            and child._x is not None
            and self.relative_rect.colliderect(child.relative_rect)
            )
    
    def notify_change_all(self):
        """Force the change notification to remake every surface."""
        self.notify_change()

        for child in self.children:
            child.notify_change()
