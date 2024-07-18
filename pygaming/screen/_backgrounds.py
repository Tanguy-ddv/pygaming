"""Contains a class to manage the backgrounds of a widget or any object."""

import pygame
from typing import Union, List
from ._draw import make_background, make_rounded_rectangle

BackgroundLike = Union[str, pygame.Surface, pygame.Color]
BackgroundsLike = Union[List[BackgroundLike], BackgroundLike]

class Backgrounds:
    """
    The backgrounds class is used to store all the backgrounds of a frame.
    """

    def __init__(
        self,
        width: int,
        height: int,
        backgrounds: BackgroundsLike,
        focus_backgrounds: BackgroundsLike | None = None,
        disable_backgrounds: BackgroundsLike | None = None,
        other_backgrounds: dict[str, BackgroundLike | BackgroundsLike] = {},
        can_be_focused: bool = True,
        can_be_disabled: bool = True,
        rounded_background: bool = False
    ) -> None:
        """
        Create the backgrounds

        params:
        ----
        width: int, the width of the object.
        height: int, the hieght of the object.
        backgrounds: BackgroundsLike, The backgrounds of the objects.
        if only one element is given, it is treated as a list of length 1
        If it is a (list of) color or a str, create a list of surface of this color with the shape (width, height)
        If it is a (list of) surface, resize the surface with (width, height)
        Can be a list of colors and surfaces, str
        focus_backgrounds: BackgroundsLike | None, The backgrounds of the objects when it is focused.
        if only one element is given, it is treated as a list of length 1
        If it is a (list of) color or a str, create a list of surface of this color with the shape (width, height)
        If it is a (list of) surface, resize the surface with (width, height)
        If it is a (list of) None, copy the background.
        Can be a list of color, surfaces, str and None.
        If the list have not the same size as 'background', the list is resized
        disable_backgrounds: BackgroundsLike | None, The backgrounds of the objects when it is disabled.
        if only one element is given, it is treated as a list of length 1        
        If it is a (list of) color or a str, create a list of surface of this color with the shape (width, height)
        If it is a (list of) surface, resize the surface with (width, height)
        If it is a (list of) None, copy the background.
        Can be a list of color, surfaces, str and None.
        If the list have not the same size as 'background', the list is resized
        other_backgrounds: BackgroundsLike | None, other backgrounds for the object, accessible with a str key.
        if only one element is given for a key, it is treated as a list of length 1        
        If it is a (list of) color or a str, create a list of surface of this color with the shape (width, height)
        If it is a (list of) surface, resize the surface with (width, height)
        If it is a (list of) None, copy the background.
        Can be a list of color, surfaces, str and None.
        The lists can have any size.
        can_be_focused: If False, the get_background never returns the focus bakcground.
        can_be_disabled: If False, the get_background never returns the disable background.
        """
        
        self._can_be_focused = can_be_focused
        self._can_be_disabled = can_be_disabled
        
        self._n_bg = len(backgrounds)
        if rounded_background:
            f = make_rounded_rectangle
        else:
            f = make_background

        # Create the backgrounds
        if not isinstance(backgrounds, list):
            backgrounds = [backgrounds]

        self._backgrounds: list[pygame.Surface] = []
        for bg in backgrounds:
            self._backgrounds.append(f(bg, width, height, None))
        
        # Create the focus backgrounds
        if focus_backgrounds is None:
            self._focus_backgrounds = [bg.copy() for bg in self._backgrounds]
        else:
            if not isinstance(focus_backgrounds, list):
                focus_backgrounds = [focus_backgrounds]
            while len(focus_backgrounds) < self._n_bg:
                focus_backgrounds.extend(focus_backgrounds)
            focus_backgrounds[:self._n_bg]

            self._focus_backgrounds = []
            for (i,bg) in enumerate(focus_backgrounds):
                self._focus_backgrounds.append(f(bg, width, height, self._backgrounds[i]))

        # Create the disable backgrounds
        if disable_backgrounds is None:
            self._disable_backgrounds = [bg.copy() for bg in self._backgrounds]
        else:
            if not isinstance(disable_backgrounds, list):
                disable_backgrounds = [disable_backgrounds]
            while len(disable_backgrounds) < self._n_bg:
                disable_backgrounds.extend(disable_backgrounds)
            disable_backgrounds[:self._n_bg]

            self._disable_backgrounds = []
            for (i,bg) in enumerate(disable_backgrounds):
                self._disable_backgrounds.append(f(bg, width, height, self._backgrounds[i]))

        # Create the other backgrounds
        self._other_backgrounds: dict[str, list] = {}
        for key, o_bgs in other_backgrounds.items():
            if not isinstance(o_bgs, list):
                o_bgs = [o_bgs]
            self._other_backgrounds[key] = []
            for (i,bg) in enumerate(o_bgs):
                self._other_backgrounds[key].append(f(bg, width, height, self._backgrounds[i%self._n_bg]))

    def get_background(self, index=0, focus: bool = False, disabled: bool = False, key: str | None = None):
        """
        Return the background.
        
        Params:
        ---
        index: int = 0, the index of the background in its list.
        focus: bool = False. If True, return the focus_background.
        disabled: bool = False. If True, return the disable_background.
        key: str | None = None. If not None, return the other_background[key]
        """
        if key is not None:
            return self._other_backgrounds[key][index]
        if focus and self._can_be_focused:
            return self._focus_backgrounds[index]
        if disabled and self._can_be_disabled:
            return self._disable_backgrounds[index]
        return self._backgrounds[index]
        