# 🚀 AlphaRai

_Smarter Trading. Fully Automated. Beautifully Engineered._

AlphaRai is your all-in-one quant trading platform — built for strategy devs, data lovers, and alpha chasers. From trade signals to execution, from live dashboards to backtested brilliance, AlphaRai gives you the tools to scale your edge in style.

---

## ✨ Key Features

- 📈 **Real-Time Strategy Execution**  
  Run ML-based or rule-driven strategies across multiple brokers like MetaTrader 5 and IG.

- 🧠 **Pluggable Strategy Architecture**  
  Drop in your strategies as folders, automatically loaded and versioned by content hash.

- 📊 **Live Dash App Interface**  
  Sleek web interface powered by Dash and Plotly. Monitor trades, confirm signals, analyze P&L — all in one place.

- 📦 **Modular Trade Metrics & Analytics**  
  Like technical indicators, but for trade history. Extend via your own `TradeMetric` classes.

- 🔐 **Secure Credential Storage**  
  Credentials managed via AWS Secrets Manager. No plaintext secrets ever.

---

## 🔍 Example Strategy


```
# strategies/my_strategy/strategy.py

from quant_core.strategies import StrategyBase

class MyCoolStrategy(StrategyBase):
    def prepare(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        # Initialize model, fetch context, etc.
        pass

    def run(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        # Logic to run the strategy
        pass
        
    def get_prediction(self, data_frame: pd.DataFrame) -> PredictionLabel:
        # Logic to get the prediction
        pass

STRATEGY = MyCoolStrategy()
```

---

## 📜 License
This project is open source, but non-commercial.
See LICENSE for details.

---

## 🧙‍♂️ About
Created with love by Christian Weiss.
Always chasing alpha. Always building cool stuff.

Feel free to fork, star, or contribute!