import math
from typing import List

from quant_core.enums.stagger_method import StaggerMethod


def _fibonacci_staggering(a: float, b: float, k) -> List[float]:
    """Calculate fibonacci levels from stop loss and entry price"""
    modifier = 1 if b > a else -1
    distance_available = abs(b - a)

    fibonacci_numbers = [0, 1]
    while len(fibonacci_numbers) <= k:
        fibonacci_numbers.append(fibonacci_numbers[-1] + fibonacci_numbers[-2])
    fib_sum = sum(fibonacci_numbers)

    distances = [
        modifier * distance_available * (sum(fibonacci_numbers[: i + 1]) / fib_sum)
        for i in range(len(fibonacci_numbers))
    ]

    return [a + distance for distance in distances][:-1]


def _linear_staggering(a: float, b: float, k: int) -> List[float]:
    """Calculate linear levels between two prices"""
    modifier = 1 if b > a else -1
    distance_available = abs(b - a)
    step = distance_available / (k)

    return [a + modifier * step * i for i in range(k)]


def _logarithmic_staggering(a: float, b: float, k: int) -> List[float]:
    """Calculate logarithmic levels between two prices"""
    modifier = 1 if b > a else -1
    distance_available = abs(b - a)
    step = math.log(distance_available + 1) / (k)

    return [a + modifier * (math.exp(step * i) - 1) for i in range(k)]


def get_stagger_levels(from_price: float, to_price: float, stagger_method: StaggerMethod, k: int = 5) -> List[float]:
    """Get stagger levels between two prices"""

    if k < 1:
        raise ValueError("Number of levels must be at least 1")

    if k == 1:
        return [from_price]

    if stagger_method is StaggerMethod.NONE:
        return [from_price for _ in range(k)]
    elif stagger_method is StaggerMethod.FIBONACCI:
        return _fibonacci_staggering(from_price, to_price, k)
    elif stagger_method is StaggerMethod.LINEAR:
        return _linear_staggering(from_price, to_price, k)
    elif stagger_method is StaggerMethod.LOGARITHMIC:
        return _logarithmic_staggering(from_price, to_price, k)

    raise ValueError(f"Invalid stagger method: {stagger_method}")


def get_stagger_sizes(size: float, max_size: float, k: int, stagger_method: StaggerMethod) -> List[float]:
    """Get stagger sizes based on the method"""
    if k < 1:
        raise ValueError("Number of levels must be at least 1")

    if k == 1:
        return [size]

    if stagger_method is StaggerMethod.NONE:
        return [size for _ in range(k)]
    elif stagger_method is StaggerMethod.FIBONACCI:
        return _fibonacci_staggering(size, max_size, k)
    elif stagger_method is StaggerMethod.LINEAR:
        return _linear_staggering(size, max_size, k)
    elif stagger_method is StaggerMethod.LOGARITHMIC:
        return _logarithmic_staggering(size, max_size, k)

    raise ValueError(f"Invalid stagger method: {stagger_method}")
