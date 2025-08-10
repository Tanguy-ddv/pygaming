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
from ..states import WidgetStates

# togglegridselection: checkbuttons on a grid, composite
# gridselector: player selector, with an overlay

T = TypeVar("T")
def _get_obj_or_none(obj: List[List[T | None]], i: int, j: int) -> T | None:
    if obj is None:
        return None    
    return obj[i][j]

def _get_obj_or_none_or_single(obj: List[List[T | None]], i: int, j: int) -> T | None:
    if obj is None:
        return None
    elif isinstance(obj, (str, Color, tuple, Anchor)):
        return obj
    
    return obj[i][j]
class _ToggleGridSelector(CompositeWidget):

    def get(self) -> List[tuple[int, int]]:
        return [(i,j) for count, (i,j) in enumerate(self.grids[0]._objects.keys()) if self.focusable_children[count].get()]
    
    def get_flat(self) -> List[int]:
        return [c for c, bt in enumerate(self.focusable_children) if bt.get()]

    def update(self, dt):

        if self.state == WidgetStates.FOCUSED:

            if self.game.keyboard.actions_down_or_repeated['right']:
                for i, ch in enumerate(self.focusable_children):
                    if ch.state == WidgetStates.FOCUSED:
                        ch.unfocus()
                        for ch2 in self.focusable_children[i+1:] + self.focusable_children[:i+1]:
                            if ch2.state != WidgetStates.DISABLED:
                                ch2.focus()
                                break
                                
                    break

            if self.game.keyboard.actions_down_or_repeated['left']:
                for i, ch in enumerate(self.focusable_children):
                    if ch.state == WidgetStates.FOCUSED:
                        ch.unfocus()
                        for ch2 in reversed(self.focusable_children[i:] + self.focusable_children[:i]):
                            if ch2.state != WidgetStates.DISABLED:
                                ch2.focus()
                                break
                    break
            
            if self.game.keyboard.actions_down_or_repeated['down']:
                all_items = list(self.grids[0]._objects.keys())
                for i, ch in enumerate(self.focusable_children):
                    if ch.state == WidgetStates.FOCUSED:
                        current_focused = i
                        ch.unfocus()
                        break
                i, j  = all_items[current_focused]
                new_i = (i+1)%len(set(x for x,y in all_items))
                new_j = min(j,
                    sum(1 for x,y in all_items if (
                        x == new_i
                        and self.focusable_children[all_items.index((x, y))].state != WidgetStates.DISABLED
                    )
                ))
                self.focusable_children[all_items.index((new_i, new_j))].focus()
        
            if self.game.keyboard.actions_down_or_repeated['up']:
                all_items = list(self.grids[0]._objects.keys())
                for i, ch in enumerate(self.focusable_children):
                    if ch.state == WidgetStates.FOCUSED:
                        current_focused = i
                        ch.unfocus()
                        break
                i, j  = all_items[current_focused]
                new_i = (i-1)%len(set(x for x,y in all_items))
                new_j = min(j,
                    sum(1 for x,y in all_items if (
                        x == new_i
                        and self.focusable_children[all_items.index((x, y))].state != WidgetStates.DISABLED
                    )
                ))
                self.focusable_children[all_items.index((new_i, new_j))].focus()

        return super().update(dt)

class ToggleGridSelector(_ToggleGridSelector):
    
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



        super().__init__(master, (0, 0), update_if_invisible, **kwargs)

        count = 0

        for i in range(len(unselected_normal_background)):
            for j in range(len(unselected_normal_background[i])):

                def new_on_unclick(count=count):
                    if len(self.get()) >= max_selected:
                        self.focusable_children[count]._change(1)
                    occ = _get_obj_or_none(on_click_command, i, j)
                    if occ is not None:
                        occ

                MultiStateButton(
                    self,
                    [_get_obj_or_none(unselected_normal_background, i, j), _get_obj_or_none(selected_normal_background,i,j)],
                    [_get_obj_or_none(unselected_active_background, i, j), _get_obj_or_none(selected_active_background, i, j)],
                    [_get_obj_or_none(unselected_focused_background, i, j), _get_obj_or_none(selected_focused_background, i, j)],
                    [_get_obj_or_none(unselected_disabled_background, i, j), _get_obj_or_none(selected_disabled_background, i, j)],
                    [_get_obj_or_none(unselected_hovered_background, i, j), _get_obj_or_none(selected_hovered_background, i, j)],
                    [_get_obj_or_none(unselected_hitbox, i, j), _get_obj_or_none(selected_hitbox, i, j)],
                    _get_obj_or_none(tooltips, i, j),
                    cursor,
                    new_on_unclick,
                    _get_obj_or_none(on_unclick_command, i, j),
                    continue_animation, update_if_invisible, reset_on_start
                ).grid(i, j, None, 1, 1, padx, pady)

                count += 1

        self._width, self._height = self.grids[0].size
        self.grids[0]._update(0, 0, 0, 0)

class TextToggleGridSelector(_ToggleGridSelector):
    
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
        
        super().__init__(master, (0, 0), update_if_invisible, **kwargs)

        count = 0

        for i in range(len(unselected_normal_background)):
            for j in range(len(unselected_normal_background[i])):
                
                def new_on_unclick(count=count):
                    if len(self.get()) >= max_selected:
                        self.focusable_children[count]._change(1)
                    occ = _get_obj_or_none(on_click_command, i, j)
                    if occ is not None:
                        occ

                TextMultiStateButton(
                    self,
                    [_get_obj_or_none(unselected_normal_background, i, j), _get_obj_or_none(selected_normal_background,i,j)],
                    [_get_obj_or_none_or_single(unselected_normal_font, i, j), _get_obj_or_none_or_single(selected_normal_font, i, j)],
                    [_get_obj_or_none_or_single(unselected_normal_font_color, i, j), _get_obj_or_none_or_single(selected_normal_font_color, i, j)],
                    [localizations_or_texts[i][j], localizations_or_texts[i][j]],
                    [_get_obj_or_none(unselected_active_background, i, j), _get_obj_or_none(selected_active_background, i, j)],
                    [_get_obj_or_none_or_single(unselected_active_font, i, j), _get_obj_or_none_or_single(selected_active_font, i, j)],
                    [_get_obj_or_none_or_single(unselected_active_font_color, i, j), _get_obj_or_none_or_single(selected_active_font_color, i, j)],
                    [_get_obj_or_none(unselected_focused_background, i, j), _get_obj_or_none(selected_focused_background, i, j)],
                    [_get_obj_or_none_or_single(unselected_focused_font, i, j), _get_obj_or_none_or_single(selected_focused_font, i, j)],
                    [_get_obj_or_none_or_single(unselected_focused_font_color, i, j), _get_obj_or_none_or_single(selected_focused_font_color, i, j)],
                    [_get_obj_or_none(unselected_disabled_background, i, j), _get_obj_or_none(selected_disabled_background, i, j)],
                    [_get_obj_or_none_or_single(unselected_disabled_font, i, j), _get_obj_or_none_or_single(selected_disabled_font, i, j)],
                    [_get_obj_or_none_or_single(unselected_disabled_font_color, i, j), _get_obj_or_none_or_single(selected_disabled_font_color, i, j)],
                    [_get_obj_or_none(unselected_hovered_background, i, j), _get_obj_or_none(selected_hovered_background, i, j)],
                    [_get_obj_or_none_or_single(unselected_hovered_font, i, j), _get_obj_or_none_or_single(selected_hovered_font, i, j)],
                    [_get_obj_or_none_or_single(unselected_hovered_font_color, i, j), _get_obj_or_none_or_single(selected_hovered_font_color, i, j)],
                    [_get_obj_or_none(unselected_hitbox, i, j), _get_obj_or_none(selected_hitbox, i, j)],
                    _get_obj_or_none(tooltips, i, j),
                    cursor,
                    new_on_unclick,
                    _get_obj_or_none(on_unclick_command, i, j),
                    _get_obj_or_none_or_single(justify, i, j),
                    continue_animation, update_if_invisible, reset_on_start
                ).grid(i, j, None, 1, 1, padx, pady)

                count += 1

        self._width, self._height = self.grids[0].size
        self.grids[0]._update(0, 0, 0, 0)
