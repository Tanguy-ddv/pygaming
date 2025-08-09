from typing import List, Any, TypeVar, Callable
from pygaming.screen.frame import Frame
from .widget import CompositeWidget
from ..art import Art
from ..hitbox import Hitbox
from .button import MultiStateButton, TextMultiStateButton
from ..hover import Tooltip, Cursor
from ...color import ColorLike, Color
from ...database import TextFormatter
from ..anchors import AnchorLike, CENTER, Anchor

# togglegridselection: checkbuttons on a grid, composite
# gridselector: player selector, with an overlay

class ToggleGridSelector(CompositeWidget):
    
    def __init__(self,
        master: Frame,
        selected_normal_background: List[List[Art]],
        unselected_normal_background: List[List[Art]],
        selected_active_background: List[List[Art | None]] | None = None,
        selected_focused_background: List[List[Art | None]] | None = None,
        selected_disabled_background: List[List[Art | None]] | None = None,
        selected_hovered_background: List[List[Art | None]] | None = None,
        selected_hitbox: List[List[Hitbox]] | None = None,
        unselected_active_background: List[List[Art | None]] | None = None,
        unselected_focused_background: List[List[Art | None]] | None = None,
        unselected_disabled_background: List[List[Art | None]] | None = None,
        unselected_hovered_background: List[List[Art | None]] | None = None,
        unselected_hitbox: List[List[Hitbox]] | None  = None,
        tooltips: List[List[Tooltip]] | None  = None,
        cursor: Cursor | None = None,
        padx: int = 0,
        pady: int = 0,
        on_click_command: List[List[Callable[[], Any] | None]] | None = None,
        on_unclick_command: List[List[Callable[[], Any] | None]] | None = None,
        update_if_invisible: bool = True,
        max_selected: int = 1,
        continue_animation: bool = True,
        reset_on_start: bool = False,
        **kwargs
        ):

        T = TypeVar("T")
        def get_obj_or_none(obj: List[List[T | None]], i: int, j: int) -> T | None:
            if obj is None:
                return None    
            return obj[i][j]

        super().__init__(master, (0, 0), update_if_invisible, **kwargs)

        count = 0

        for i in range(len(unselected_normal_background)):
            for j in range(len(unselected_normal_background[i])):

                def new_on_unclick(count=count):
                    if len(self.get()) >= max_selected:
                        self.focusable_children[count]._change(1)
                    occ = get_obj_or_none(on_click_command, i, j)
                    if occ is not None:
                        occ

                MultiStateButton(
                    self,
                    [get_obj_or_none(unselected_normal_background, i, j), get_obj_or_none(selected_normal_background,i,j)],
                    [get_obj_or_none(unselected_active_background, i, j), get_obj_or_none(selected_active_background, i, j)],
                    [get_obj_or_none(unselected_focused_background, i, j), get_obj_or_none(selected_focused_background, i, j)],
                    [get_obj_or_none(unselected_disabled_background, i, j), get_obj_or_none(selected_disabled_background, i, j)],
                    [get_obj_or_none(unselected_hovered_background, i, j), get_obj_or_none(selected_hovered_background, i, j)],
                    [get_obj_or_none(unselected_hitbox, i, j), get_obj_or_none(selected_hitbox, i, j)],
                    get_obj_or_none(tooltips, i, j),
                    cursor,
                    new_on_unclick,
                    get_obj_or_none(on_unclick_command, i, j),
                    continue_animation, update_if_invisible, reset_on_start
                ).grid(i, j, None, 1, 1, padx, pady)

                count += 1

        self._width, self._height = self.grids[0].size
        self.grids[0]._update(0, 0, 0, 0)
    
    def get(self) -> List[tuple[int, int]]:
        return [(i,j) for count, (i,j) in enumerate(self.grids[0]._objects.keys()) if self.focusable_children[count].get()]
    
    def get_flat(self) -> List[int]:
        return [c for c, bt in enumerate(self.focusable_children) if bt.get()]

class TextToggleGridSelector(CompositeWidget):
    
    def __init__(self,
        master: Frame,
        
        
        selected_normal_background: List[List[Art]],
        selected_normal_font: List[List[str]] | str,
        selected_normal_font_color: List[List[ColorLike]] | ColorLike,
        unselected_normal_background: List[List[Art]],
        unselected_normal_font: List[List[str]] | str,
        unselected_normal_font_color: List[List[ColorLike]] | ColorLike,
        localizations_or_texts: List[List[str | TextFormatter]],
        selected_active_background: List[List[Art | None]] | None = None,
        selected_active_font: List[List[str]] | str | None = None,
        selected_active_font_color: List[List[ColorLike]] | ColorLike | None = None,
        selected_focused_background: List[List[Art | None]] | None = None,
        selected_focused_font: List[List[str]] | str | None = None,
        selected_focused_font_color: List[List[ColorLike]] | ColorLike | None = None,
        selected_disabled_background: List[List[Art | None]] | None = None,
        selected_disabled_font: List[List[str]] | str | None = None,
        selected_disabled_font_color: List[List[ColorLike]] | ColorLike | None = None,
        selected_hovered_background: List[List[Art | None]] | None = None,
        selected_hovered_font: List[List[str]] | str | None = None,
        selected_hovered_font_color: List[List[ColorLike]] | ColorLike | None = None,
        selected_hitbox: List[List[Hitbox]] | None = None,
        unselected_active_background: List[List[Art | None]] | None = None,
        unselected_active_font: List[List[str]] | str | None = None,
        unselected_active_font_color: List[List[ColorLike]] | ColorLike | None = None,
        unselected_focused_background: List[List[Art | None]] | None = None,
        unselected_focused_font: List[List[str]] | str | None = None,
        unselected_focused_font_color: List[List[ColorLike]] | ColorLike | None = None,
        unselected_disabled_background: List[List[Art | None]] | None = None,
        unselected_disabled_font: List[List[str]] | str | None = None,
        unselected_disabled_font_color: List[List[ColorLike]] | ColorLike | None = None,
        unselected_hovered_background: List[List[Art | None]] | None = None,
        unselected_hovered_font: List[List[str]] | str | None = None,
        unselected_hovered_font_color: List[List[ColorLike]] | ColorLike | None = None,
        unselected_hitbox: List[List[Hitbox]] | None = None,
        tooltips: List[List[Tooltip]] | None  = None,
        cursor: Cursor | None = None,
        padx: int = 0,
        pady: int = 0,
        on_click_command: List[List[Callable[[], Any] | None]] | None = None,
        on_unclick_command: List[List[Callable[[], Any] | None]] | None = None,
        update_if_invisible: bool = True,
        max_selected: int = 1,
        justify: List[List[AnchorLike]] | AnchorLike = CENTER,
        continue_animation: bool = True,
        reset_on_start: bool = False,
        **kwargs
        ):

        T = TypeVar("T")
        def get_obj_or_none(obj: List[List[T | None]], i: int, j: int) -> T | None:
            if obj is None:
                return None
            else:
                return obj[i][j]
        
        def get_obj_or_none_or_single(obj: List[List[T | None]], i: int, j: int) -> T | None:
            if obj is None:
                return None
            elif isinstance(obj, (str, Color, tuple, Anchor)):
                return obj
            
            return obj[i][j]

        super().__init__(master, (0, 0), update_if_invisible, **kwargs)

        count = 0

        for i in range(len(unselected_normal_background)):
            for j in range(len(unselected_normal_background[i])):
                
                def new_on_unclick(count=count):
                    if len(self.get()) >= max_selected:
                        self.focusable_children[count]._change(1)
                    occ = get_obj_or_none(on_click_command, i, j)
                    if occ is not None:
                        occ

                TextMultiStateButton(
                    self,
                    [get_obj_or_none(unselected_normal_background, i, j), get_obj_or_none(selected_normal_background,i,j)],
                    [get_obj_or_none_or_single(unselected_normal_font, i, j), get_obj_or_none_or_single(selected_normal_font, i, j)],
                    [get_obj_or_none_or_single(unselected_normal_font_color, i, j), get_obj_or_none_or_single(selected_normal_font_color, i, j)],
                    [localizations_or_texts[i][j], localizations_or_texts[i][j]],
                    [get_obj_or_none(unselected_active_background, i, j), get_obj_or_none(selected_active_background, i, j)],
                    [get_obj_or_none_or_single(unselected_active_font, i, j), get_obj_or_none_or_single(selected_active_font, i, j)],
                    [get_obj_or_none_or_single(unselected_active_font_color, i, j), get_obj_or_none_or_single(selected_active_font_color, i, j)],
                    [get_obj_or_none(unselected_focused_background, i, j), get_obj_or_none(selected_focused_background, i, j)],
                    [get_obj_or_none_or_single(unselected_focused_font, i, j), get_obj_or_none_or_single(selected_focused_font, i, j)],
                    [get_obj_or_none_or_single(unselected_focused_font_color, i, j), get_obj_or_none_or_single(selected_focused_font_color, i, j)],
                    [get_obj_or_none(unselected_disabled_background, i, j), get_obj_or_none(selected_disabled_background, i, j)],
                    [get_obj_or_none_or_single(unselected_disabled_font, i, j), get_obj_or_none_or_single(selected_disabled_font, i, j)],
                    [get_obj_or_none_or_single(unselected_disabled_font_color, i, j), get_obj_or_none_or_single(selected_disabled_font_color, i, j)],
                    [get_obj_or_none(unselected_hovered_background, i, j), get_obj_or_none(selected_hovered_background, i, j)],
                    [get_obj_or_none_or_single(unselected_hovered_font, i, j), get_obj_or_none_or_single(selected_hovered_font, i, j)],
                    [get_obj_or_none_or_single(unselected_hovered_font_color, i, j), get_obj_or_none_or_single(selected_hovered_font_color, i, j)],
                    [get_obj_or_none(unselected_hitbox, i, j), get_obj_or_none(selected_hitbox, i, j)],
                    get_obj_or_none(tooltips, i, j),
                    cursor,
                    new_on_unclick,
                    get_obj_or_none(on_unclick_command, i, j),
                    get_obj_or_none_or_single(justify, i, j),
                    continue_animation, update_if_invisible, reset_on_start
                ).grid(i, j, None, 1, 1, padx, pady)

                count += 1

        self._width, self._height = self.grids[0].size
        self.grids[0]._update(0, 0, 0, 0)
    
    def get(self) -> List[tuple[int, int]]:
        return [(i,j) for count, (i,j) in enumerate(self.grids[0]._objects.keys()) if self.focusable_children[count].get()]
    
    def get_flat(self) -> List[int]:
        return [c for c, bt in enumerate(self.focusable_children) if bt.get()]

