import os
from typing import Optional, Dict

import pandas as pd

from quant_core.enums.label import PredictionLabel
from quant_core.entities.strategy_configuration import StrategyConfiguration


class BacktestTrade:
    def __init__(
        self,
        entry_index: int,
        exit_index: int,
        side: str,
        entry_price: float,
        exit_price: float,
        quantity: float,
        pnl: float,
        stop_loss: float,
        take_profit: float,
    ):
        self.entry_index = entry_index
        self.exit_index = exit_index
        self.side = side
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.quantity = quantity
        self.pnl = pnl
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def __repr__(self):
        return (
            f"BacktestTrade("
            f"entry_idx={self.entry_index}, "
            f"exit_idx={self.exit_index}, "
            f"side='{self.side}', "
            f"entry_price={self.entry_price}, "
            f"exit_price={self.exit_price}, "
            f"quantity={self.quantity}, "
            f"pnl={self.pnl}, "
            f"stop_loss={self.stop_loss}, "
            f"take_profit={self.take_profit}"
            f")"
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "entry_index": self.entry_index,
            "exit_index": self.exit_index,
            "side": self.side,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "pnl": self.pnl,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
        }


class BackTester:
    def __init__(self, df: pd.DataFrame, strategy_configuration: StrategyConfiguration) -> None:
        self._df = df.reset_index(drop=True)
        self._strategy_cfg = strategy_configuration

        self.initial_balance = 10000.0
        self.current_balance = self.initial_balance

        self.current_side = None
        self.entry_price = None
        self.entry_index = None
        self.quantity = 0.0

        self.stop_loss = None
        self.take_profit = None

        self.trades = []

    def backtest(self) -> None:
        for i, row in enumerate(self._df.iterrows()):
            row = self._df.iloc[i]
            signal_value = PredictionLabel(row["prediction"])
            if self.current_side is not None:
                exit_price = self._check_stop_loss_take_profit(row)
                if exit_price is not None:
                    self._close_position(i, exit_price)
                    self._evaluate_signal(i, row, signal_value)
                    continue

                if not self._same_side(signal_value):
                    self._close_position(i, row["close"])
                    self._evaluate_signal(i, row, signal_value)
            else:
                self._evaluate_signal(i, row, signal_value)

        if self.current_side is not None:
            final_index = len(self._df) - 1
            final_price = self._df.iloc[-1]["close"]
            self._close_position(final_index, final_price)

        print("Backtest Complete.")
        print(f"Initial balance: {self.initial_balance}")
        print(f"Final balance:   {self.current_balance}")
        print("Trades:")
        for t in self.trades:
            print(t)

    def get_summary(self) -> Dict[str, float]:
        total_trades = len(self.trades)
        if total_trades == 0:
            return {
                "final_balance": self.current_balance,
                "total_trades": 0,
                "win_ratio": 0.0,
                "average_pnl": 0.0,
                "total_pnl": self.current_balance - self.initial_balance,
                "average_win": 0.0,
                "average_loss": 0.0,
            }

        wins = [t for t in self.trades if t.pnl > 0]
        losses = [t for t in self.trades if t.pnl < 0]

        total_wins = len(wins)
        total_losses = len(losses)

        win_ratio = total_wins / total_trades if total_trades else 0.0
        average_pnl = sum(t.pnl for t in self.trades) / total_trades
        average_win = sum(t.pnl for t in wins) / total_wins if total_wins else 0.0
        average_loss = sum(t.pnl for t in losses) / total_losses if total_losses else 0.0

        return {
            "final_balance": self.current_balance,
            "total_trades": total_trades,
            "win_ratio": win_ratio,
            "average_pnl": average_pnl,
            "total_pnl": self.current_balance - self.initial_balance,
            "average_win": average_win,
            "average_loss": average_loss,
        }

    def _evaluate_signal(self, i: int, row: pd.Series, signal_value: PredictionLabel) -> None:
        if signal_value in [PredictionLabel.STRONG_BUY, PredictionLabel.BUY]:
            self._open_position(i, row, side="long")
        elif signal_value in [PredictionLabel.SELL, PredictionLabel.STRONG_SELL]:
            self._open_position(i, row, side="short")

    def _check_stop_loss_take_profit(self, row: pd.Series) -> Optional[float]:
        if self.current_side == "short":
            tp = self.take_profit
            sl = self.stop_loss
            if row["high"] >= sl:
                return sl
            if row["low"] <= tp:
                return tp

            return None

        elif self.current_side == "long":
            tp = self.take_profit
            sl = self.stop_loss
            if row["low"] <= sl:
                return sl

            if row["high"] >= tp:
                return tp

            return None

        return None

    def _open_position(self, i: int, row: pd.Series, side: str):
        """
        Opens a position at the bar's close, uses
        the relevant stop_loss/take_profit columns for that side.
        """
        if self.current_side is not None:
            # Already in a position (shouldn't happen if logic is correct)
            return

        self.current_side = side
        self.entry_index = i
        entry_price = row["close"]
        self.entry_price = entry_price

        if side == "short":
            self.stop_loss = row["short_stop_loss"]
            self.take_profit = row["short_take_profit"]
        else:  # side == "long"
            self.stop_loss = row["long_stop_loss"]
            self.take_profit = row["long_take_profit"]

        # Naive "all-in" sizing
        self.quantity = self.current_balance / entry_price

    def _close_position(self, i: int, exit_price: float) -> None:
        if self.current_side is None:
            return

        if self.current_side == "long":
            pnl = (exit_price - self.entry_price) * self.quantity
        else:  # short
            pnl = (self.entry_price - exit_price) * self.quantity

        self.current_balance += pnl

        trade = BacktestTrade(
            entry_index=self.entry_index,
            exit_index=i,
            side=self.current_side,
            entry_price=self.entry_price,
            exit_price=exit_price,
            quantity=self.quantity,
            pnl=pnl,
            stop_loss=self.stop_loss,
            take_profit=self.take_profit,
        )
        self.trades.append(trade)

        self.current_side = None
        self.entry_price = None
        self.entry_index = None
        self.quantity = 0.0
        self.stop_loss = None
        self.take_profit = None

    def _same_side(self, signal_value: PredictionLabel) -> bool:
        return (self.current_side == "long" and signal_value in [PredictionLabel.STRONG_BUY, PredictionLabel.BUY]) or (
            self.current_side == "short" and signal_value in [PredictionLabel.SELL, PredictionLabel.STRONG_SELL]
        )


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    data_file = os.path.join(current_dir, "test.csv")
    config_file = os.path.join(current_dir, "config.yaml")

    data_frame = pd.read_csv(data_file)
    rows = len(data_frame)
    start_index = int(rows * 0.7)
    data_frame = data_frame.iloc[start_index:]

    strategy_configuration = StrategyConfiguration(config_file)

    backtester = BackTester(data_frame, strategy_configuration)
    backtester.backtest()

    summary = backtester.get_summary()
    print("\nBacktest Summary:")
    for k, v in summary.items():
        print(f"{k}: {v}")
