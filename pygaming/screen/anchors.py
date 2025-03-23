"""The anchor module contains anchors for selecting the position on the screen."""
from enum import Enum, EnumMeta
from typing import Sequence, Union
from pygame import Vector2

class _AnchorMeta(EnumMeta):
    """Metaclass for FloatEnum that allows dynamic creation of new members."""
    
    def __call__(cls, value, *args, **kwargs):

        if isinstance(value, Enum) and isinstance(value.value, Vector2):
            return value  # If we use an Anchor to create an anchor, we just return itself

        if not isinstance(value, Vector2): # If we use a sequence
            if isinstance(value, Sequence):
                if len(value) != 2:
                    raise ValueError(f"{value} cannot be used to instanciate an Anchor.")
                value = Vector2(*value[0:2])
            else: # If we use two arguments
                if len(args) == 1:
                    value = Vector2(value, args[0])
                else:
                    raise ValueError(f"{value} cannot be used to instanciate an Anchor.")
    
        for member in cls.__members__.values():  
            if member.value == value:
                return member  # Return existing member

        if not isinstance(value[0], (float, int)) or not isinstance(value[1], (float, int)) or  not (0. <= value[0] <= 1. and 0. <= value[1] <= 1.):
            raise ValueError(f"Anchors can be instanciated only with two floats within [0., 1.], got {value[0]} and {value[1]}")
        # Dynamically create a new member
        new_member = object.__new__(cls)
        new_member._value_ = value  # Set value explicitly
        name = str((value.x, value.y))
        new_member._name_ = name
        # object.__setattr__(new_member, "_name_", name)  
        cls._member_map_[name] = new_member  # Store in enum
        return new_member
class Anchor(Enum, metaclass=_AnchorMeta):

    TOP_LEFT = Vector2(0., 0.)
    TOP_RIGHT = Vector2(1., 0.)
    TOP = TOP_CENTER = Vector2(0.5, 0.)
    LEFT = CENTER_LEFT = Vector2(0., 0.5)
    RIGHT = CENTER_RIGHT = Vector2(1., 0.5)
    CENTER = CENTER_CENTER = Vector2(0.5, 0.5)
    BOTTOM_LEFT = Vector2(0., 1.)
    BOTTOM_RIGHT = Vector2(1., 1.)
    BOTTOM = BOTTOM_CENTER = Vector2(0.5, 1.)

    @property
    def x(self):
        return self.value.x

    @property
    def y(self):
        return self.value.y

    def __add__(self, other):
        if isinstance(other, Anchor):
            other = other.value
        return Anchor(Vector2(self.value.x, self.value.y) + other)
    
    def __truediv__(self, other):
        return Anchor(Vector2(self.value.x, self.value.y) / other)

    def __mul__(self, other):
        return Anchor(Vector2(self.value.x, self.value.y) * other)
    
    def __getitem__(self, idx):
        if idx in [0, 1, -1]:
            return self.y if idx else self.x
        if idx in ['x', 'y']:
            return self.x if idx == 'x' else self.y
        raise IndexError(f"Anchors can only be subscripted by -1, 0, 1 , 'x' and 'y', but got {idx}")

    def __iter__(self):
        yield self.value.x
        yield self.value.y

def barycenter(anchors: Sequence['Anchor'], weights: Sequence[float] = None):
    """Return the barycenter of several anchors."""
    if weights:
        if len(weights) != len(anchors):
            raise ValueError(f"the anchors and weights arguments should be sequencies of the same length, got {len(anchors)} and {len(weights)}")
    else:
        weights = [1 for _ in anchors]
    sum_w = sum(weights)
    return sum([anch*(w/sum_w) for anch, w in zip(anchors, weights)], start=Anchor.TOP_LEFT)

def midpoint(anchor1: 'Anchor', anchor2: 'Anchor'):
    """Return the middle point of two anchors."""
    return barycenter([anchor1, anchor2])

TOP_LEFT = Anchor.TOP_LEFT
TOP_RIGHT = Anchor.TOP_RIGHT
TOP = TOP_CENTER = Anchor.TOP_CENTER
CENTER = CENTER_CENTER = Anchor.CENTER
LEFT = CENTER_LEFT = Anchor.CENTER_LEFT
RIGHT = CENTER_RIGHT = Anchor.CENTER_RIGHT
BOTTOM_LEFT = Anchor.BOTTOM_LEFT
BOTTOM_RIGHT = Anchor.BOTTOM_RIGHT
BOTTOM = BOTTOM_CENTER = Anchor.BOTTOM_CENTER

AnchorLike = Union[Anchor, tuple[float, float], Vector2]
