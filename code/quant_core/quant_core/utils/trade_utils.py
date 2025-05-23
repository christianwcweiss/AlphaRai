import math
from typing import List, Tuple

from models.main.account_config import AccountConfig
from quant_core.enums.asset_type import AssetType
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
    if stagger_method is StaggerMethod.FIBONACCI:
        return _fibonacci_staggering(from_price, to_price, k)
    if stagger_method is StaggerMethod.LINEAR:
        return _linear_staggering(from_price, to_price, k)
    if stagger_method is StaggerMethod.LOGARITHMIC:
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
    if stagger_method is StaggerMethod.FIBONACCI:
        return _fibonacci_staggering(size, max_size, k)
    if stagger_method is StaggerMethod.LINEAR:
        return _linear_staggering(size, max_size, k)
    if stagger_method is StaggerMethod.LOGARITHMIC:
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


def lookup_tick_and_contract_details(account_config: AccountConfig) -> Tuple[float, float, float]:
    if account_config.asset_type is AssetType.FOREX:
        tick_value = 10.0
        tick_size = 10 ** (-account_config.decimal_points + 1)
        contract_size = account_config.lot_size
    elif account_config.asset_type is AssetType.CRYPTO:
        tick_value = 1.0
        tick_size = 1.0
        contract_size = account_config.lot_size
    elif account_config.asset_type is AssetType.COMMODITIES:
        tick_value = 1.0
        tick_size = 10 ** (-account_config.decimal_points)
        contract_size = account_config.lot_size
    elif account_config.asset_type is AssetType.STOCK:
        tick_value = 1.0
        tick_size = 10 ** (-account_config.decimal_points)
        contract_size = account_config.lot_size
    elif account_config.asset_type is AssetType.INDICES:
        tick_value = 1.0
        tick_size = 1.0
        contract_size = account_config.lot_size
    else:
        raise ValueError(f"Invalid asset type: {account_config.asset_type}")

    return tick_value, tick_size, contract_size


def calculate_position_size(
    entry_price: float, stop_loss_price: float, percentage_risk: float, balance: float, account_config: AccountConfig
) -> float:
    """
    Calculate the appropriate lot size for a trade based on risk parameters and asset metadata.
    """
    if entry_price <= 0 or stop_loss_price <= 0 or percentage_risk <= 0 or balance <= 0:
        raise ValueError("All input values must be greater than zero.")

    stop_distance = abs(entry_price - stop_loss_price)
    if stop_distance == 0:
        raise ValueError("Stop loss and entry price cannot be the same.")

    tick_value, tick_size, contract_size = lookup_tick_and_contract_details(account_config)

    pip_value_per_lot = tick_value / tick_size

    risk_amount = (percentage_risk / 100.0) * balance
    lot_size = risk_amount / (stop_distance * pip_value_per_lot)

    return round(max(lot_size, 0.01), 2)
