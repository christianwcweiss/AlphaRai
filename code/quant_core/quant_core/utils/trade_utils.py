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


def calculate_risk_reward(entry: float, stop_loss: float, take_profit: float) -> float:
    """
    Calculate the risk-reward ratio (RRR) based on entry, stop loss and take profit targets.
    Returns average RRR across all TP levels.
    """
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)

    if risk == 0:
        return float("inf")

    return round(reward / risk, 2)


def calculate_weighted_risk_reward(risk_rewards: List[float], sizes: List[float]) -> float:
    """
    Calculate the weighted average risk-reward ratio based on individual RRRs and sizes.
    """
    total_size = sum(sizes)
    if total_size == 0:
        return float("inf")

    weighted_risk_reward = sum(risk_reward * size for risk_reward, size in zip(risk_rewards, sizes)) / total_size

    return round(weighted_risk_reward, 2)

def calculate_position_size(entry_price: float, stop_loss_price: float, lot_size: float, percentage_risk: float, balance: float) -> float:
    if entry_price <= 0 or stop_loss_price <= 0 or lot_size <= 0 or percentage_risk <= 0 or balance <= 0:
        raise ValueError("All input values must be greater than zero.")

    # Calculate monetary risk
    risk_amount = (percentage_risk / 100.0) * balance

    # Pip or point difference
    stop_distance = abs(entry_price - stop_loss_price)
    if stop_distance == 0:
        raise ValueError("Stop loss and entry cannot be the same.")

    # Size (volume)
    size = risk_amount / (stop_distance * lot_size)
    size = round(max(size, 0.01), 2)  # MT5 requires minimum 0.01 lots

    return size