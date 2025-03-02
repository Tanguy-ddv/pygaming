"""The color module contains the class Color, used to represent colors in the game."""
from typing import overload, Union
import colorsys
from pygame import Color as _Cl
from pygame.colordict import THECOLORS

def _from_hsla(h: int, s: int, l: int, a: int) -> 'Color':
    """Convert an hsla tuple to a color"""
    r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
    return Color(int(r*255), int(g*255), int(b*255), a)

class Color(_Cl):
    """The Color class is used to represent colors in the game."""

    @overload
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        ...

    @overload
    def __init__(self, color_string: str):
        ...

    @overload
    def __init__(self, rgba: Union[tuple[int, int, int], tuple[int, int, int, int]]):
        ...

    def __init__(self, *values):
        if len(values) == 1:
            if isinstance(values[0], str):
                # We are in the second overload
                color_string = values[0]
                if color_string in THECOLORS:
                    # We specified the name of the color
                    super().__init__(THECOLORS[color_string])
                else:
                    if color_string.startswith('#') and len(color_string) == 4:
                        # Add support for short html-format strings
                        color_string = f"#{color_string[1]*2}{color_string[2]*2}{color_string[3]*2}"
                    super().__init__(color_string)

            else:
                super().__init__(*values)
        else:
            # We are in the first overload
            super().__init__(values)

    def darken(self, percentage: int | float) -> 'Color':
        """Darken the color."""
        percentage /= 100
        h, s, l, _a = self.hsla
        l = l * (1 - percentage)
        return _from_hsla(h, s, l, self.a)

    def lighten(self, percentage: int | float) -> 'Color':
        """Lighten the color."""
        percentage /= 100
        h, s, l, _a = self.hsla
        l = 100 - (100 - l)* (1 - percentage)
        return _from_hsla(h, s, l, self.a)

    def desaturate(self, percentage: int | float) -> 'Color':
        """Desaturate the color."""
        percentage /= 100
        h, s, l, _a = self.hsla
        s = s * (1 - percentage)
        return _from_hsla(h, s, l, self.a)

    def saturate(self, percentage: int | float) -> 'Color':
        """Saturate the color."""
        percentage /= 100
        h, s, l, _a = self.hsla
        s = 100 - (100 - s)* (1 - percentage)
        return _from_hsla(h, s, l, self.a)

    def shift_hue(self, value: int) -> 'Color':
        """Shift the hue of the color."""
        h, s, l, _a = self.hsla
        return _from_hsla((h+value)%360, s, l, self.a)

    @staticmethod
    def from_hlsa(h: int, s: int, l: int, a: int = 255) -> 'Color':
        """Create a color from the hue-saturation-luminosity format."""
        return _from_hsla(h, s, l, a)

    @staticmethod
    def from_hlsv(h: int, s:int, v:int, a: int = 255) -> 'Color':
        """Create a color from the hue-saturation-value format."""
        r, g, b = colorsys.hsv_to_rgb(h/360, s/100, v/100)
        return Color(int(r*255), int(g*255), int(b*255), a)

    @staticmethod
    def from_cmyk(c: int, y:int, m:int, k:int, a:int = 255) -> 'Color':
        """Create a color from the cyan-yellow-magenta-black format."""
        r = int(255*(100 - c)*(100 - k)/10000)
        g = int(255*(100 - m)*(100 - k)/10000)
        b = int(255*(100 - y)*(100 - k)/10000)
        return Color(r,g,b,a)

ColorLike = Union[Color|tuple[int, int, int], tuple[int, int, int, int]]
