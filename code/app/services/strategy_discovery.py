import hashlib
import importlib.util
import os
import traceback
from pathlib import Path
from typing import List

from quant_core.services.core_logger import CoreLogger
from quant_core.strategy.strategy import Strategy


def compute_folder_hash(folder_path: str) -> str:
    hash_obj = hashlib.sha256()

    for root, _, files in sorted(os.walk(folder_path)):
        for file_name in sorted(files):
            file_path = os.path.join(root, file_name)

            # Add file name and relative path to hash to catch renamed/moved files
            relative_path = os.path.relpath(file_path, folder_path)
            hash_obj.update(relative_path.encode("utf-8"))

            with open(file_path, "rb") as f:
                while chunk := f.read(4096):
                    hash_obj.update(chunk)

    return hash_obj.hexdigest()


def discover_strategies(strategy_dir: str) -> List[dict]:
    logger = CoreLogger()
    strategies = []

    for folder in Path(strategy_dir).iterdir():
        strategy_py = folder / "strategy.py"
        if not strategy_py.exists():
            continue

        try:
            spec = importlib.util.spec_from_file_location("strategy_module", strategy_py)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            logger.warning(f"Failed to import strategy in {folder.name}:\n{traceback.format_exc()}")
            continue

        if not hasattr(module, "STRATEGY"):
            logger.warning(f"No STRATEGY object in {folder.name}")
            continue

        strategy = module.STRATEGY
        if not isinstance(strategy, Strategy):
            logger.warning(f"STRATEGY in {folder.name} is not a Strategy instance")
            continue

        try:
            strategy_hash = compute_folder_hash(str(folder))
        except Exception as e:
            logger.warning(f"Failed to compute hash for {folder.name}: {e}")
            continue

        strategies.append(
            {
                "id": getattr(strategy, "__ID__", folder.name),
                "type": getattr(strategy, "__TYPE__", "unknown"),
                "path": str(folder),
                "hash": strategy_hash,
            }
        )

    logger.info(f"Discovered {len(strategies)} strategy folder(s)")
    return strategies
