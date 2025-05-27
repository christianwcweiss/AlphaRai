from itertools import combinations
from typing import List, Tuple


def create_combination_bitmasks(length: int = 6) -> List[Tuple[bool, ...]]:
    """Generates all possible boolean combinations of n items, returning a list of tuples"""
    return [
        tuple(i in combination for i in range(length))
        for repetitions in range(length + 1)
        for combination in combinations(range(length), repetitions)
    ]
