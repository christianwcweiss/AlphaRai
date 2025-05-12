import asyncio
import json
from typing import Dict, Any, List

import boto3
from quant_core.bots.bots import BaseTradingBot
from quant_core.services.core_logger import CoreLogger


class SqsListeningTradingBot(BaseTradingBot):
    """
    Trading bot that polls an SQS queue (connected to an SNS topic) and executes trades based on messages received.
    """

    def __init__(self, account_id: str, symbols: List[str], queue_url: str, polling_interval: int = 5):
        super().__init__(account_id, symbols)
        self._queue_url = queue_url
        self._polling_interval = polling_interval
        self._sqs = boto3.client("sqs")

    async def _handle_signal(self, message: Dict[str, Any]):
        signal = message.get("signal")
        size = message.get("size", 1.0)

        if signal and signal.get("symbol") in self._symbols:
            CoreLogger().info(f"[{self._account_id}] Executing trade for {signal['symbol']}...")
            self.execute_trade(signal, size)

    async def bot_loop(self) -> None:
        CoreLogger().info(f"Bot loop started for account {self._account_id}, polling from SQS: {self._queue_url}")
        while True:
            try:
                messages = self._sqs.receive_message(
                    QueueUrl=self._queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,
                )
            except Exception as e:
                CoreLogger().error(f"Failed to receive messages from SQS: {e}")
                await asyncio.sleep(self._polling_interval)
                continue

            for msg in messages.get("Messages", []):
                try:
                    sns_wrapped = json.loads(msg["Body"])
                    message = json.loads(sns_wrapped.get("Message", "{}"))
                    await self._handle_signal(message)

                    # Delete the message after successful processing
                    self._sqs.delete_message(
                        QueueUrl=self._queue_url,
                        ReceiptHandle=msg["ReceiptHandle"]
                    )
                except Exception as e:
                    CoreLogger().error(f"Failed to handle message: {e}")

            await asyncio.sleep(self._polling_interval)

    def execute_trade(self, signal: Dict[str, Any], size: float) -> bool:
        CoreLogger().info(f"[{self._account_id}] Placing trade: {signal} with size {size}")
        # TODO: implement actual trade placement
        return True

    def close_all_positions(self) -> None:
        CoreLogger().warning(f"[{self._account_id}] Closing all open positions")
        # TODO: implement platform-specific logic
