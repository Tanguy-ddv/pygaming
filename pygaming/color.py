from pygame import Color as Cl
from pygame.colordict import THECOLORS
from typing import overload, Union
import colorsys

def _from_hsla(h: float, s: float, l: float, a: float) -> 'Color':
    """Convert an hsla tuple to a color"""
    r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
    return Color(int(r*255), int(g*255), int(b*255), int(a*255))

class Color(Cl):

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
                        color_string = f"#{color_string[0]}{color_string[0]}{color_string[1]}{color_string[1]}{color_string[2]}{color_string[2]}"
                    super().__init__(color_string)
                
            else:
                super().__init__(*values)
        else:
            # We are in the first overload
            super().__init__(values)

    def darken(self, percentage) -> 'Color':
        
        h, s, l, _a = self.hsla
        l = l * (1 - percentage)
        return _from_hsla(h, s, l, self.a/255)

    def lighten(self, percentage) -> 'Color':
        
        h, s, l, _a = self.hsla
        l = 100 - (100 - l)* (1 - percentage)
        return _from_hsla(h, s, l, self.a/255)
    
    def desaturate(self, percentage) -> 'Color':
        
        h, s, l, _a = self.hsla
        s = s * (1 - percentage)
        return _from_hsla(h, s, l, self.a/255)

    def saturate(self, percentage) -> 'Color':
        
        h, s, l, _a = self.hsla
        s = 100 - (100 - s)* (1 - percentage)
        return _from_hsla(h, s, l, self.a/255)
