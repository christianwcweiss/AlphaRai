import json
import os.path
from argparse import Namespace, ArgumentParser
from uuid import uuid4

from back_tester import BackTester
from quant_core.loader.data_loader import DataLoader
from quant_core.services.core_logger import CoreLogger
from quant_core.entities.strategy_configuration import StrategyConfiguration
from quant_core.services.data_forge import DataForge
from pycaret.classification import setup, compare_models, pull, predict_model, save_model

_NEW_LINE = "\n"


def parse_arguments() -> Namespace:
    argument_parser = ArgumentParser()

    argument_parser.add_argument("--data", type=str, required=True, help="Path to the data")

    argument_parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")

    argument_parser.add_argument("--include-ohlcv", action="store_true", help="Include OHLCV data")

    return argument_parser.parse_args()


def log_arguments(arguments: Namespace) -> None:
    CoreLogger().info("\n******************ARGUMENTS******************\n")
    CoreLogger().info(f"Data File: {arguments.data}")
    CoreLogger().info(f"Config File: {arguments.config}")
    CoreLogger().info(f"Include OHLCV: {arguments.include_ohlcv}")
    CoreLogger().info("\n*********************************************\n")


def main() -> None:
    backtest_uid = str(uuid4())
    CoreLogger().info(f"Starting optimization and backtesting - {backtest_uid}")
    arguments = parse_arguments()

    log_arguments(arguments)

    data_frame = DataLoader().load_data(arguments.data)

    strategy_configuration = StrategyConfiguration(arguments.config)
    data_forge = DataForge(data_frame, strategy_configuration)

    data_frame = data_forge.data_frame()

    feature_columns = strategy_configuration.feature_settings.feature_columns
    if arguments.include_ohlcv:
        feature_columns += ["open", "high", "low", "close", "volume"]

    CoreLogger().info("\n*********************************************\n")
    CoreLogger().info(f"Data Frame columns:\n {_NEW_LINE.join(data_frame.columns)}")
    CoreLogger().info("\n*********************************************\n")
    CoreLogger().info(f"Feature columns: {_NEW_LINE.join(feature_columns)}")
    CoreLogger().info("\n*********************************************\n")

    user_input = input("Do you want to continue? (y/n): ")
    if user_input.lower() != "y":
        CoreLogger().info("User cancelled the operation")
        return

    feature_data_frame = data_frame[feature_columns + ["label_value"]]

    CoreLogger().info("\n*********************************************\n")
    CoreLogger().info(f"Feature data frame columns:\n {_NEW_LINE.join(feature_data_frame.columns)}")
    CoreLogger().info("\n*********************************************\n")

    _ = setup(
        data=feature_data_frame,
        target="label_value",
    )

    best_model = compare_models()

    results = pull()

    CoreLogger().info("\n*********************************************\n")
    CoreLogger().info("Best model found:")
    CoreLogger().info(best_model)
    CoreLogger().info("\n*********************************************\n")
    CoreLogger().info("\nModel comparison results:")
    CoreLogger().info(str(results))

    predictions = predict_model(best_model, data=feature_data_frame)
    data_frame["prediction"] = predictions["prediction_label"]

    if not os.path.exists(os.path.join(os.path.dirname(__file__), "results")):
        os.makedirs(os.path.join(os.path.dirname(__file__), "results"))

    os.makedirs(os.path.join(os.path.dirname(__file__), "results", backtest_uid))
    data_frame.to_csv(os.path.join(os.path.dirname(__file__), "results", backtest_uid, "predictions.csv"))
    save_model(best_model, os.path.join(os.path.join(os.path.dirname(__file__), "results", backtest_uid, "model")))

    backtester = BackTester(data_frame, strategy_configuration)
    backtester.backtest()

    CoreLogger().info(f"Results saved to: {os.path.join(os.path.dirname(__file__), 'results', backtest_uid)}")
    CoreLogger().info(f"Backtest completed - {backtest_uid}")
    CoreLogger().info("\n*********************************************\n")
    CoreLogger().info("\nBacktest Summary:")
    CoreLogger().info(json.dumps(backtester.get_summary()))

    CoreLogger().info("\n*********************************************\n")
    CoreLogger().info("Optimization and backtesting completed")

    user_input = input("Do you want to upload and enable trading? (y/n): ")

    if user_input.lower() != "y":
        CoreLogger().info("User cancelled the operation")
        return

    CoreLogger().info("Uploading and enabling trading")


if __name__ == "__main__":
    main()
