"""The color objects represent colors."""
from string import hexdigits
from dataclasses import dataclass

@dataclass(init=False)
class Color:
    """Color obejcts represent colors."""

    def __init__(self, R: int, G: int, B: int, A: int = 255) -> None:
        if not isinstance(R, int) or R < 0 or R > 255:
            raise ValueError(f"invalid color format, got {R}")
        if not isinstance(G, int) or G < 0 or G > 255:
            raise ValueError(f"invalid color format, got {G}")
        if not isinstance(B, int) or B < 0 or B > 255:
            raise ValueError(f"invalid color format, got {B}")
        if not isinstance(A, int) or A < 0 or A > 255:
            raise ValueError(f"invalid color format, got {A}")

        self._r = R
        self._g = G
        self._b = B
        self._a = A
    
    def to_RGBA(self):
        """Return a tuple of int between 0 and 255 representing the color."""
        return (self._r, self._g, self._b, self._a)
    
    def to_rgba(self):
        """Return a tuple of float between 0 and 1 representing the color."""
        return (self._r/255, self._g/255, self._b/255, self._/255)

    def to_hex(self):
        """Return a string of the hexadecimal represention of the color."""
        r = hexdigits[self._r//16] + hexdigits[self._r%16]
        g = hexdigits[self._g//16] + hexdigits[self._g%16]
        b = hexdigits[self._b//16] + hexdigits[self._b%16]
        return '#' + r + g + b


def from_RGBA(R, G, B, A=255) -> Color:
    """Create a color object from a tuple of int between and 255."""
    return Color(R, G, B, A)


def from_rgba(r, g, b, a) -> Color:
    """Create a color object from a tuple of float between 0 and 1."""
    return Color(
        R = int(r*255),
        G = int(g*255),
        B = int(b*255),
        A = int(a*255)
    )
    
def from_hex(hex: str) -> Color:
    """Create a color object from a hexadecimal representation of colors."""
    hex = hex.lower()
    if len(hex) == 4:
        # We got a format #rgb
        r_hex = hex[1]
        R = hexdigits.index(r_hex)*16
        g_hex = hex[2]
        G = hexdigits.index(g_hex)*16
        b_hex = hex[3]
        B = hexdigits.index(b_hex)*16
        return Color(R, G, B)

    if len(hex == 7):
        # We got a format #rgb
        r1_hex = hex[1]
        r2_hex = hex[2]
        R = hexdigits.index(r1_hex)*16 + hexdigits.index(r2_hex)
        g1_hex = hex[3]
        g2_hex = hex[4]
        G = hexdigits.index(g1_hex)*16 + hexdigits.index(g2_hex)
        b1_hex = hex[5]
        b2_hex = hex[6]
        B = hexdigits.index(b1_hex)*16 + hexdigits.index(b2_hex)
        return Color(R, G, B)

    raise ValueError(f"Invalid color format, got {hex}")

# Define some colors.
red = from_RGBA(255,0,0)
blue = from_RGBA(0,0,255)
green = from_RGBA(0,255,0)
black = from_RGBA(0,0,0)
white = from_RGBA(255,255,255)
full_transparency = from_RGBA(255,255,255,0)
orange = from_RGBA(255,128,0)
yellow = from_RGBA(255,255,0)
pink = from_RGBA(255,100,150)
magenta = from_RGBA(255,0,255)
cyan = from_RGBA(0,255,255)
grey = from_RGBA(128,128,128)
