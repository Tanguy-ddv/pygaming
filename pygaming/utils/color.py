"""The color objects represent colors."""

__HEX = ['0','1','2','3','4','5','6','7','8','9','a','b', 'c', 'd', 'e', 'f']

class Color:
    """Color obejcts represent colors."""

    def __init__(self, R:int, G:int, B:int, A:int = 255) -> None:
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
        r = __HEX[self._r//16] + __HEX[self._r%16]
        g = __HEX[self._g//16] + __HEX[self._g%16]
        b = __HEX[self._b//16] + __HEX[self._b%16]
        return '#' + r + g + b

    @staticmethod
    def from_RGBA(R, G, B, A=255) -> 'Color':
        """Create a color object from a tuple of int between and 255."""
        return Color(R, G, B, A)
    
    @staticmethod
    def from_rgba(r, g, b, a) -> 'Color':
        """Create a color object from a tuple of float between 0 and 1."""
        return Color(
            R = int(r*255),
            G = int(g*255),
            B = int(b*255),
            A = int(a*255)
        )
    
    @staticmethod
    def from_hex(hex: str) -> 'Color':
        """Create a color object from a hexadecimal representation of colors."""
        if len(hex) == 4:
            # We got a format #rgb
            r_hex = hex[1]
            R = __HEX.index(r_hex)*16
            g_hex = hex[2]
            G = __HEX.index(g_hex)*16
            b_hex = hex[3]
            B = __HEX.index(b_hex)*16
            return Color(R, G, B)

        if len(hex == 7):
            # We got a format #rgb
            r1_hex = hex[1]
            r2_hex = hex[2]
            R = __HEX.index(r1_hex)*16 + __HEX.index(r2_hex)
            g1_hex = hex[3]
            g2_hex = hex[4]
            G = __HEX.index(g1_hex)*16 + __HEX.index(g2_hex)
            b1_hex = hex[5]
            b2_hex = hex[6]
            B = __HEX.index(b1_hex)*16 + __HEX.index(b2_hex)
            return Color(R, G, B)


        raise ValueError(f"Invalid color format, got {hex}")