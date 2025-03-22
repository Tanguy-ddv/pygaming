from typing import overload, TypeAlias, Union, Sequence
class Anchor1D:
    """Represents a 1D anchor."""

    @overload
    def __init__(self, x: Union[float, 'Anchor1D']): ...

    @overload
    def __init__(self, x: Union[float, 'Anchor1D'], name: str): ...

    def __init__(self, x: Union[float, 'Anchor1D'], name: str = None):
        if not isinstance(x, (float, Anchor1D)) or 0. > x or x > 1.:
            raise ValueError(f"{x} cannot be an Anchor1D as it should be a float within [0, 1]")
        self._value = float(x)

        if name is None:
            self.__name = f"Anchor1D({self._value})"
        else:
            self.__name = f"Anchor1D.{name}"

    def __float__(self):
        return self._value

    def __repr__(self):
        return self.__name
    
    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return other*self._value
        elif isinstance(other, Anchor1D):
            return other._value*self._value
        else:
            raise TypeError(f"Anchor1D objects can only be multiplied by numbers or other Anchor1D.")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        return isinstance(other, (Anchor1D, float)) and float(other) == self._value

    def __validate_other(self, other):
        if not isinstance(other, (Anchor1D, float)):
            raise TypeError(f"Anchor1D cannot be compared to {type(other)}")
        return float(other)
    
    def __le__(self, other):
        other = self.__validate_other(other)
        return self._value <= other

    def __lt__(self, other):
        other = self.__validate_other(other)
        return self._value < other

    def __ge__(self, other):
        other = self.__validate_other(other)
        return self._value >= other

    def __gt__(self, other):
        other = self.__validate_other(other)
        return self._value > other

# Define named constants
LEFT = Anchor1D(0., "LEFT")
RIGHT = Anchor1D(1., "RIGHT")
CENTER = Anchor1D(0.5, "CENTER")
TOP = Anchor1D(0., "TOP")
BOTTOM = Anchor1D(1., "BOTTOM")
FRONT = Anchor1D(1., "FRONT")
BACK = Anchor1D(0., "BACK")

Anchor1DLike: TypeAlias = Union[Anchor1D, float]

class Anchor2D:
    """Represents a 2D anchor with named positions."""

    @overload
    def __init__(self, x: float | Anchor1D, y: float | Anchor1D): ...

    @overload
    def __init__(self, x: Sequence[float | Anchor1D]): ...

    @overload
    def __init__(self, x: float | Anchor1D, y: float | Anchor1D, name: str): ...

    def __init__(self, x: float | Anchor1D, y: float | Anchor1D = None, name: str = None):
        if y is None:
            if isinstance(x, Sequence) and len(x) == 2:
                x, y = x
            else:
                raise ValueError(f"{x} isn't an acceptable argument for an Anchor2D if y is None. It should be a tuple of 2 floats.")

        if not isinstance(x, (float, Anchor1D)) or 0. > x or x > 1. or not isinstance(y, (float, Anchor1D)) or 0. > y or y > 1.:
            raise ValueError(f"{x, y} cannot be an Anchor1D as it should be a tuple of floats within [0, 1]")

        x = float(x)
        y = float(y)

        self._anchorx = x
        self._anchory = y

        if name is None:
            self.__name = f"Anchor2D{self._anchorx, self._anchory}"
        else:
            self.__name = f"Anchor2D.{name}"

    def __repr__(self):
        return self.__name
    
    def __eq__(self, other):
        if not isinstance(other, (tuple, Anchor2D)):
            return False
        other = tuple(other)
        return len(other) == 2 and other[0] == self._anchorx and other[1] == self._anchory

    def __iter__(self):
        yield self._anchorx
        yield self._anchory

    def __getitem__(self, idx: int):
        if idx not in [0, 1, -1]:
            raise IndexError(f"Anchors can only be subscripted by 0, 1 or -1, not {idx}")
        return self._anchory if idx else self._anchorx

TOP_LEFT = Anchor2D(0., 0., "TOP_LEFT")
TOP_RIGHT = Anchor2D(1., 0., "TOP_RIGHT")
BOTTOM_LEFT = Anchor2D(0., 1., "BOTTOM_LEFT")
BOTTOM_RIGHT = Anchor2D(1., 1., "BOTTOM_RIGHT")
CENTER_CENTER = Anchor2D(0.5, 0.5, "CENTER_CENTER")
CENTER_LEFT = Anchor2D(0., 0.5, "CENTER_LEFT")
CENTER_RIGHT = Anchor2D(1., 0.5, "CENTER_RIGHT")
TOP_CENTER = Anchor2D(0.5, 0., "TOP_CENTER")
BOTTOM_CENTER = Anchor2D(0.5, 1., "BOTTOM_CENTER")

Anchor2DLike: TypeAlias = Union[Anchor2D, float]
