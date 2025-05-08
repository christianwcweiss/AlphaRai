import pandas as pd


class KellyCriterionPerAccount:
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df[df["profit"].notna()]
        result = []

        for account, group in df.groupby("account_id"):
            wins = group[group["profit"] > 0]
            losses = group[group["profit"] < 0]

            win_rate = len(wins) / len(group) if len(group) > 0 else 0.0
            avg_win = wins["profit"].mean() if not wins.empty else 0.0
            avg_loss = abs(losses["profit"].mean()) if not losses.empty else 1e-6

            rr = avg_win / avg_loss if avg_loss > 0 else 0.0
            kelly = (win_rate - (1 - win_rate) / rr) * 100 if rr > 0 else 0.0

            result.append({"account_id": account, "kelly_pct": round(kelly, 2)})

        return pd.DataFrame(result)
