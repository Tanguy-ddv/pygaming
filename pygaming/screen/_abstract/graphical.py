"""The visual module contains the Visual class, an abstract for all object displayable on the screen."""
import pygame
from .visual import Visual
from .child import Child
from .master import Master
from ..states import States, WidgetStates
from ...settings import Settings
from ..art import Art

class Arts:

    def __init__(self, normal: Art) -> None:
        """
        Two options: continue_anmation is true, when we change state, we keep the same index. in this case, we only update the main
        and match its index
        continue_animaltion is false: when we change state, we reset all.
        """
        self._arts: dict[States, Art | None] = {WidgetStates.NORMAL : normal}
        self._continue_animation = False
    
    @property
    def width(self):
        return self._arts[WidgetStates.NORMAL].width

    @property
    def height(self):
        return self._arts[WidgetStates.NORMAL].height

    @property
    def size(self):
        return self._arts[WidgetStates.NORMAL].size

    @property
    def main(self):
        return self._arts[WidgetStates.NORMAL]
    
    def add(self, state: States, art: Art):
        self._arts[state] = art
    
    def set_continue_animation(self, value: bool):
        self._continue_animation = value
    
    def update(self, dt: int, state: States = WidgetStates.NORMAL) -> bool:
        if self._continue_animation or self._arts.get(state, None) is None:
            return self._arts[WidgetStates.NORMAL].update(dt)
        else:
            return self._arts[state].update(dt)
    
    def get(self, state: States = WidgetStates.NORMAL, **ld_kwargs) -> pygame.Surface:
        state = WidgetStates.NORMAL if self._arts.get(state, None) is None else state
        match = self._arts[WidgetStates.NORMAL] if self._continue_animation else None
        return self._arts[state].get(match, **ld_kwargs)

    def start(self, start_all: bool = False, **ld_kwargs):
        if start_all:
            for art in self._arts.values():
                art.start(**ld_kwargs)
        else:
            self._arts[WidgetStates.NORMAL].start(**ld_kwargs)
    
    def end(self):
        for art in self._arts.values():
            art.end()
    
    def new_state(self):
        if not self._continue_animation:
            for art in self._arts.values():
                if art is not None:
                    art.reset()

class Graphical(Visual):
    """The Graphicals are visual object having an art as main display."""

    def __init__(self, art: Art, **kwargs):
        super().__init__(**kwargs)
        self._arts = Arts(art)
        self.state = WidgetStates.NORMAL

    @property
    def width(self):
        return self._arts.width

    @property
    def height(self):
        return self._arts.height

    def begin(self, settings: Settings, **kwargs):
        """Call this method at the beginning of the phase."""
        self._arts.start(**settings)
        self.notify_change()
        super().begin(settings=settings, **kwargs)

    def finish(self):
        """Call this method at the end of the phase."""
        super().finish()
        self._arts.end()

    def loop(self, dt: int):
        """Call this method at every loop iteration."""
        has_changed = self._arts.update(dt)
        if has_changed:
            self.notify_change()
        self.update(dt)

class GraphicalChild(Child, Graphical):

    def __init__(self, master: Master, art: Art, update_if_invisible: bool = False, **kwargs) -> None:
        super().__init__(master=master, update_if_invisible=update_if_invisible, art=art, **kwargs)
    
    def begin(self, **kwargs):
        """Call this method at the beginning of the phase."""
        self._arts.start(**self.game.settings)
        self.notify_change()
        super().begin(settings=self.game.settings, **kwargs)

    def loop(self, dt: int):
        """Call this method at every loop iteration."""
        if self.is_visible() or self._update_if_invisible:
            has_changed = self._arts.update(dt)
            if has_changed:
                self.notify_change()
            self.update(dt)

    def make_surface(self) -> pygame.Surface:
        """Create the image of the visual as a pygame surface."""
        return self._arts.get(self.state, **self.game.settings)
