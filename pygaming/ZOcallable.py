"""The module ZOCallable contains functions that can be use as transitions. ZO stands for Zero-One."""
from typing import Callable
import numpy as np

ZOCallable = Callable[[float | int], float | int]
_test_values = range(1, 10)

def verify_ZOCallable(ZOC):
    """Verify if the provided function is a ZO callable."""
    if not isinstance(ZOC, Callable):
        raise ValueError(f"The provided object {ZOC} isn't callable.")
    if round(ZOC(0), 3) != 0 or round(ZOC(1), 3) != 1:
       raise ValueError(f"The provided function  {ZOC} do not verify f(0) = 0 or f(1) = 1.")
    for x in _test_values:
        if not 0 <= round(ZOC(x/10), 2) <= 1:
            raise ValueError(f"The provided function {ZOC} ranges outside of [0, 1] as f({x/10:.1f}) = {ZOC(x/10):.3f}.")

linear = lambda x:x
square_in = lambda x:x**2
square_out = lambda x: 1 - (1- x)**2
square_in_out = lambda x: 2 * x**2 if x < 0.5 else 1 - 2 * (1 - x) ** 2
root_out = lambda x:x**(1/2)
root_in = lambda x: 1 - (1 - x)**(1/2)

exp_decay = lambda x: 1 - 2**(-10 * x)
sigmoid = lambda x: 1 / (1 + (2.718 ** (-12 * (x - 0.5))))
elastic = lambda x: x**2 * (2.5 * (x - 1)**2 + 1)

def normalize_ZOCallable(ZOC):
    """Normalize a function to be a ZOCCallable."""
    if ZOC(1) == 0:
        raise ValueError("This function cannot be normalized as a ZO callable.")
    return lambda t: (ZOC(t) - ZOC(0)) / ZOC(1)
    
def cubic_bezier(p0, p1, p2, p3):
    """
    Return a ZOCallable following a cubic bezier curve.
    
    Params:
    - p0, p1, p2, p3: floats, 0 <= p <= 1. The parameters of the curve.
    """
    unnormalized = lambda t: (1.-t)**3 * p0 + 3*(1.-t)**2*t * p1 + 3*(1.-t)*t**2 * p2 + t**3 * p3 - p0
    return normalize_ZOCallable(unnormalized)

ease = cubic_bezier(0.25, 1., 0.25, 1.)
ease_in = cubic_bezier(0.42, 0., 1., 1.)
ease_out = cubic_bezier(0., 0., 0.58, 1.)
ease_in_out = cubic_bezier(0.42, 0., 0.58, 1.)

def bounce(n):
    """
    Return a ZOCallable that looks like bounces.
    
    Params:
    ---
    - n: int >= 0, the number of bounces.
    """
    if n < 0 or not isinstance(n, int):
        raise ValueError(f"{n} is not an acceptable argument for the number of bounce.")
    def bounce_n(x):
        if x == 0 or x == 1:  # Handle the edge case to avoid division by zero
            return x
        new_x = (n+1) * np.pi * np.power(x, 3/2)
        sinc = np.sin(new_x) / new_x
        return 1 - np.abs(sinc)
    return bounce_n

def jump(n):
    """
    Return a ZOCallable being successive jumps.
    
    Params:
    ---
    - n: int >= 0
    """

    if n <= 0:
        raise ValueError(f"{n} is not an acceptable argument for the number of jumps.")
    return lambda x: np.minimum(np.round(x*(n+1))/n, 1)
