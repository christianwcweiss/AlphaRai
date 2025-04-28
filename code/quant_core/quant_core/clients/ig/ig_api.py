import abc
import json
from functools import lru_cache
from pprint import pprint
from typing import Dict, Any, List, Optional, Union

import boto3
import requests

from quant_core.enums.environment import Environment
from quant_core.enums.ig.instrument_type import InstrumentType
from quant_core.enums.ig.market_status import MarketStatus
from quant_core.enums.ig.order_type import IGOrderType
from quant_core.enums.ig.time_in_force import TimeInForce
from quant_core.enums.trade_direction import TradeDirection
from quant_core.services.core_logger import CoreLogger
from quant_core.settings.configuration import Configuration


@lru_cache(1)
class IGApiHeader:
    def __init__(self, api_key: str, account_id: str) -> None:
        self._api_key = api_key
        self._account_id = account_id
        self._content_type = "application/json"
        self._accept = "application/json"

    def to_header(self) -> Dict[str, str]:
        return {
            "X-IG-API-KEY": self._api_key,
            "IG-ACCOUNT-ID": self._account_id,
            "Content-Type": self._content_type,
            "Accept": self._accept,
        }


# BODIES
class IGApiBody(abc.ABC):
    @abc.abstractmethod
    def to_body(self) -> Dict[str, Any]:
        pass


class IGApiSessionBody(IGApiBody):
    def __init__(self, user_name: str, password: str) -> None:
        self._user_name = user_name
        self._password = password

    def to_body(
        self,
    ) -> Dict[str, Any]:
        return {"identifier": self._user_name, "password": self._password}


class IGApiPostPositionsOrderBody(IGApiBody):
    def __init__(
        self,
        currency_code: str,
        direction: Union[TradeDirection, str],
        epic: str,
        expiry: str,
        force_open: bool,
        guaranteed_stop: bool,
        order_type: Union[IGOrderType, str],
        size: float,
        time_in_force: Union[TimeInForce, str],
        trailing_stop: bool,
        deal_reference: Optional[str] = None,
        level: Optional[float] = None,
        quote_id: Optional[str] = None,
        trailing_stop_increment: Optional[float] = None,
        stop_distance: Optional[float] = None,
        stop_level: Optional[float] = None,
        limit_distance: Optional[float] = None,
        limit_level: Optional[float] = None,
    ) -> None:
        self._currency_code = currency_code
        self._deal_reference = deal_reference
        self._direction = direction if isinstance(direction, TradeDirection) else TradeDirection(direction)
        self._epic = epic
        self._expiry = expiry
        self._force_open = force_open
        self._guaranteed_stop = guaranteed_stop
        self._level = level
        self._limit_distance = limit_distance
        self._limit_level = limit_level
        self._order_type = order_type if isinstance(order_type, IGOrderType) else IGOrderType(order_type)
        self._quote_id = quote_id
        self._size = size
        self._stop_distance = stop_distance
        self._stop_level = stop_level
        self._time_in_force = time_in_force if isinstance(time_in_force, TimeInForce) else TimeInForce(time_in_force)
        self._trailing_stop = trailing_stop
        self._trailing_stop_increment = trailing_stop_increment

    def validate(self) -> None:
        if self._limit_level and self._limit_distance:
            raise ValueError("Set only one of {limitLevel,limitDistance}")
        if self._limit_level or self._limit_distance:
            if not self._force_open:
                raise ValueError("If a limitLevel or limitDistance is set, then forceOpen must be true")
        if self._stop_level and self._stop_distance:
            raise ValueError("Set only one of {stopLevel,stopDistance}")
        if self._stop_level or self._stop_distance:
            if not self._force_open:
                raise ValueError("If a stopLevel or stopDistance is set, then forceOpen must be true")
        if self._guaranteed_stop:
            if self._stop_level and self._stop_distance:
                raise ValueError("If guaranteedStop equals true, then set only one of stopLevel,stopDistance")
            if not self._stop_level and not self._stop_distance:
                raise ValueError("If guaranteedStop equals true, then set only one of stopLevel,stopDistance")
        if self._order_type is IGOrderType.LIMIT:
            if self._quote_id:
                raise ValueError("If orderType equals LIMIT, then DO NOT set quoteId")
            if not self._level:
                raise ValueError("If orderType equals LIMIT, then set level")
        if self._order_type is IGOrderType.MARKET:
            if self._level:
                raise ValueError("If orderType equals MARKET, then DO NOT set level")
            if self._quote_id:
                raise ValueError("If orderType equals MARKET, then DO NOT set quoteId")
        if self._trailing_stop:
            if self._trailing_stop_increment:
                raise ValueError("If trailingStop equals false, then DO NOT set trailingStopIncrement")
        if not self._trailing_stop:
            if self._trailing_stop_increment:
                raise ValueError("If trailingStop equals true, then DO NOT set stopLevel")
            if self._guaranteed_stop:
                raise ValueError("If trailingStop equals true, then guaranteedStop must be false")
            if not self._stop_distance and not self._trailing_stop_increment:
                raise ValueError("If trailingStop equals true, then set stopDistance,trailingStopIncrement")

    def to_body(self) -> Dict[str, Any]:
        body_dict = {}

        if self._trailing_stop_increment:
            body_dict["trailingStopIncrement"] = self._trailing_stop_increment
        if self._stop_distance:
            body_dict["stopDistance"] = self._stop_distance
        if self._stop_level:
            body_dict["stopLevel"] = self._stop_level
        if self._limit_distance:
            body_dict["limitDistance"] = self._limit_distance
        if self._limit_level:
            body_dict["limitLevel"] = self._limit_level
        if self._deal_reference:
            body_dict["dealReference"] = self._deal_reference
        if self._level:
            body_dict["level"] = self._level
        if self._quote_id:
            body_dict["quoteId"] = self._quote_id

        return body_dict | {
            "currencyCode": self._currency_code,
            "direction": self._direction.value,
            "epic": self._epic,
            "expiry": self._expiry,
            "forceOpen": self._force_open,
            "guaranteedStop": self._guaranteed_stop,
            "orderType": self._order_type.value,
            "size": self._size,
        }


class IGApiPostWorkingOrderBody(IGApiBody):
    def __init__(
        self,
        currency_code: str,
        direction: Union[TradeDirection, str],
        epic: str,
        expiry: str,
        force_open: bool,
        guaranteed_stop: bool,
        level: float,
        order_type: Union[IGOrderType, str],
        size: float,
        time_in_force: Union[TimeInForce, str],
        deal_reference: Optional[str] = None,
        good_till_date: Optional[str] = None,
        stop_distance: Optional[float] = None,
        stop_level: Optional[float] = None,
        limit_distance: Optional[float] = None,
        limit_level: Optional[float] = None,
    ) -> None:
        self._currency_code = currency_code
        self._deal_reference = deal_reference
        self._direction = direction if isinstance(direction, TradeDirection) else TradeDirection(direction)
        self._epic = epic
        self._expiry = expiry
        self._force_open = force_open
        self._good_till_date = good_till_date
        self._guaranteed_stop = guaranteed_stop
        self._level = level
        self._limit_distance = limit_distance
        self._limit_level = limit_level
        self._order_type = order_type if isinstance(order_type, IGOrderType) else IGOrderType(order_type)
        self._size = size
        self._stop_distance = stop_distance
        self._stop_level = stop_level
        self._time_in_force = time_in_force if isinstance(time_in_force, TimeInForce) else TimeInForce(time_in_force)

    def validate(self) -> None:
        if self._limit_level and self._limit_distance:
            raise ValueError("Set only one of {limitLevel,limitDistance}")
        if self._stop_level and self._stop_distance:
            raise ValueError("Set only one of {stopLevel,stopDistance}")
        if self._time_in_force is TimeInForce.GOOD_TILL_DATE and not self._good_till_date:
            raise ValueError("If timeInForce equals GOOD_TILL_DATE, then set goodTillDate")

    def to_body(self) -> Dict[str, Any]:
        body_dict = {}

        if self._stop_distance:
            body_dict["stopDistance"] = self._stop_distance
        if self._stop_level:
            body_dict["stopLevel"] = self._stop_level
        if self._limit_distance:
            body_dict["limitDistance"] = self._limit_distance
        if self._limit_level:
            body_dict["limitLevel"] = self._limit_level
        if self._deal_reference:
            body_dict["dealReference"] = self._deal_reference

        return body_dict | {
            "currencyCode": self._currency_code,
            "direction": self._direction.value,
            "epic": self._epic,
            "expiry": self._expiry,
            "forceOpen": self._force_open,
            "guaranteedStop": self._guaranteed_stop,
            "level": self._level,
            "timeInForce": self._time_in_force.value,
            "type": self._order_type.value,
            "size": self._size,
        }


class IGApiGetSearchTermBody(IGApiBody):
    def __init__(self, search_term: str) -> None:
        self._search_term = search_term

    @property
    def search_term(self) -> str:
        return self._search_term

    def to_body(self) -> Dict[str, Any]:
        return {"searchTerm": self._search_term}


class IGApiGetPricesBody(IGApiBody):
    def __init__(
        self,
        epic: str,
        resolution: str,
        page_size: int = 20,
        max_items: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page_number: Optional[int] = None,
    ) -> None:
        self._epic = epic
        self._resolution = resolution
        self._start_date = start_date
        self._end_date = end_date
        self._max_items = max_items
        self._page_size = page_size
        self._page_number = page_number

    @property
    def epic(self) -> str:
        return self._epic

    @property
    def resolution(self) -> str:
        return self._resolution

    @property
    def start_date(self) -> str:
        return self._start_date

    @property
    def end_date(self) -> str:
        return self._end_date

    @property
    def max_items(self) -> int:
        return self._max_items

    @property
    def page_size(self) -> int:
        return self._page_size

    @property
    def page_number(self) -> int:
        return self._page_number

    def to_body(self) -> Dict[str, Any]:
        return {
            "epic": self._epic,
            "resolution": self._resolution,
            "startDate": self._start_date,
            "endDate": self._end_date,
            "max": self._max_items,
            "pageSize": self._page_size,
            "pageNumber": self._page_number,
        }

    def to_path_params(self) -> str:
        return (
            f"{self.epic}?"
            f"resolution={self.resolution}&max={self.max_items}&pageSize={self.page_size}&pageNumber={self.page_number}"
        )


# RESPONSES
class IGApiResponse(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def from_response(response: Dict[str, Any]) -> None:
        pass


class IGApiSession(IGApiResponse):
    def __init__(self, cst: str, x_security_token: str) -> None:
        self._cst = cst
        self._x_security_token = x_security_token

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGApiSession":
        return IGApiSession(cst=response["CST"], x_security_token=response["X-SECURITY-TOKEN"])

    @property
    def cst(self) -> str:
        return self._cst

    @property
    def x_security_token(self) -> str:
        return self._x_security_token

    def __str__(self) -> str:
        return f"CST: {self.cst} | X-SECURITY-TOKEN: {self.x_security_token}"

    def to_header(self) -> Dict[str, str]:
        return {
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.x_security_token,
        }


class IGApiMarket(IGApiResponse):
    def __init__(
        self,
        bid: float,
        delay_time: int,
        epic: str,
        expiry: str,
        high: float,
        instrument_name: str,
        instrument_type: InstrumentType,
        low: float,
        market_status: MarketStatus,
        net_change: float,
        offer: float,
        percentage_change: float,
        scaling_factor: int,
        streaming_prices_available: bool,
        update_time: str,
        update_time_utc: str,
    ) -> None:
        self._bid = bid
        self._delay_time = delay_time
        self._epic = epic
        self._expiry = expiry
        self._high = high
        self._instrument_name = instrument_name
        self._instrument_type = instrument_type
        self._low = low
        self._market_status = market_status
        self._net_change = net_change
        self._offer = offer
        self._percentage_change = percentage_change
        self._scaling_factor = scaling_factor
        self._streaming_prices_available = streaming_prices_available
        self._update_time = update_time
        self._update_time_utc = update_time_utc

    @property
    def bid(self) -> float:
        return self._bid

    @property
    def delay_time(self) -> int:
        return self._delay_time

    @property
    def epic(self) -> str:
        return self._epic

    @property
    def expiry(self) -> str:
        return self._expiry

    @property
    def high(self) -> float:
        return self._high

    @property
    def instrument_name(self) -> str:
        return self._instrument_name

    @property
    def instrument_type(self) -> InstrumentType:
        return self._instrument_type

    @property
    def low(self) -> float:
        return self._low

    @property
    def market_status(self) -> MarketStatus:
        return self._market_status

    @property
    def net_change(self) -> float:
        return self._net_change

    @property
    def offer(self) -> float:
        return self._offer

    @property
    def percentage_change(self) -> float:
        return self._percentage_change

    @property
    def scaling_factor(self) -> int:
        return self._scaling_factor

    @property
    def streaming_prices_available(self) -> bool:
        return self._streaming_prices_available

    @property
    def update_time(self) -> str:
        return self._update_time

    @property
    def update_time_utc(self) -> str:
        return self._update_time_utc

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGApiMarket":
        return IGApiMarket(
            bid=response["bid"],
            delay_time=response["delayTime"],
            epic=response["epic"],
            expiry=response["expiry"],
            high=response["high"],
            instrument_name=response["instrumentName"],
            instrument_type=InstrumentType(response["instrumentType"]),
            low=response["low"],
            market_status=MarketStatus(response["marketStatus"]),
            net_change=response["netChange"],
            offer=response["offer"],
            percentage_change=response["percentageChange"],
            scaling_factor=response["scalingFactor"],
            streaming_prices_available=response["streamingPricesAvailable"],
            update_time=response["updateTime"],
            update_time_utc=response["updateTimeUTC"],
        )


class IGApiCandleComponent(IGApiResponse):
    def __init__(
        self,
        ask: float,
        bid: float,
        last_traded: Optional[float] = None,
    ) -> None:
        self._ask = ask
        self._bid = bid
        self._last_traded = last_traded

    @property
    def ask(self) -> float:
        return self._ask

    @property
    def bid(self) -> float:
        return self._bid

    @property
    def last_traded(self) -> Optional[float]:
        return self._last_traded

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGApiCandleComponent":
        return IGApiCandleComponent(ask=response["ask"], bid=response["bid"], last_traded=response.get("lastTraded"))


class IGApiPrice(IGApiResponse):
    def __init__(
        self,
        close_price: IGApiCandleComponent,
        high_price: IGApiCandleComponent,
        low_price: IGApiCandleComponent,
        open_price: IGApiCandleComponent,
        snapshot_time: str,
        snapshot_time_utc: str,
        last_traded_volume: Optional[int] = None,
    ) -> None:
        self._close_price = close_price
        self._high_price = high_price
        self._low_price = low_price
        self._open_price = open_price
        self._snapshot_time = snapshot_time
        self._snapshot_time_utc = snapshot_time_utc
        self._last_traded_volume = last_traded_volume

    @property
    def close_price(self) -> IGApiCandleComponent:
        return self._close_price

    @property
    def high_price(self) -> IGApiCandleComponent:
        return self._high_price

    @property
    def last_traded_volume(self) -> Optional[int]:
        return self._last_traded_volume

    @property
    def low_price(self) -> IGApiCandleComponent:
        return self._low_price

    @property
    def open_price(self) -> IGApiCandleComponent:
        return self._open_price

    @property
    def snapshot_time(self) -> str:
        return self._snapshot_time

    @property
    def snapshot_time_utc(self) -> str:
        return self._snapshot_time_utc

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGApiPrice":
        return IGApiPrice(
            close_price=IGApiCandleComponent.from_response(response["closePrice"]),
            high_price=IGApiCandleComponent.from_response(response["highPrice"]),
            low_price=IGApiCandleComponent.from_response(response["lowPrice"]),
            open_price=IGApiCandleComponent.from_response(response["openPrice"]),
            snapshot_time=response["snapshotTime"],
            snapshot_time_utc=response["snapshotTimeUTC"],
            last_traded_volume=response["lastTradedVolume"],
        )


class IGApiWorkingOrderResponse(IGApiResponse):
    def __init__(
        self,
        created_date: str,
        currency_code: str,
        deal_id: str,
        direction: TradeDirection,
        dma: bool,
        epic: str,
        level: float,
        size: float,
        order_type: IGOrderType,
        limit_risk_premium: Optional[float] = None,
        limit_level: Optional[float] = None,
        stop_distance: Optional[float] = None,
        stop_level: Optional[float] = None,
        limit_distance: Optional[float] = None,
        good_till_date: Optional[str] = None,
    ) -> None:
        self._created_date = created_date
        self._currency_code = currency_code
        self._deal_id = deal_id
        self._direction = direction
        self._dma = dma
        self._epic = epic
        self._good_till_date = good_till_date
        self._level = level
        self._limit_distance = limit_distance
        self._limit_level = limit_level
        self._limit_risk_premium = limit_risk_premium
        self._size = size
        self._stop_distance = stop_distance
        self._stop_level = stop_level
        self._order_type = order_type

    @property
    def created_date(self) -> str:
        return self._created_date

    @property
    def currency_code(self) -> str:
        return self._currency_code

    @property
    def deal_id(self) -> str:
        return self._deal_id

    @property
    def direction(self) -> TradeDirection:
        return self._direction

    @property
    def dma(self) -> bool:
        return self._dma

    @property
    def epic(self) -> str:
        return self._epic

    @property
    def level(self) -> float:
        return self._level

    @property
    def limit_distance(self) -> Optional[float]:
        return self._limit_distance

    @property
    def limit_risk_premium(self) -> float:
        return self._limit_risk_premium

    @property
    def limit_level(self) -> Optional[float]:
        return self._limit_level

    @property
    def size(self) -> float:
        return self._size

    @property
    def stop_distance(self) -> Optional[float]:
        return self._stop_distance

    @property
    def stop_level(self) -> Optional[float]:
        return self._stop_level

    @property
    def order_type(self) -> IGOrderType:
        return self._order_type

    @property
    def good_till_date(self) -> Optional[str]:
        return self._good_till_date

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGApiWorkingOrderResponse":
        return IGApiWorkingOrderResponse(
            created_date=response["createdDate"],
            currency_code=response["currencyCode"],
            deal_id=response["dealId"],
            direction=TradeDirection(response["direction"]),
            dma=response["dma"],
            epic=response["epic"],
            level=response["orderLevel"],
            limit_distance=response.get("limitDistance"),
            limit_risk_premium=response["limitedRiskPremium"],
            size=response["orderSize"],
            stop_distance=response.get("stopDistance"),
            order_type=IGOrderType(response["orderType"]),
            good_till_date=response.get("goodTill"),
        )


class IGApiPositionResponse(IGApiResponse):
    def __init__(
        self,
        deal_id: str,
    ) -> None:
        self._deal_id = deal_id

    @property
    def deal_id(self) -> str:
        return self._deal_id

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGApiPositionResponse":
        return IGApiPositionResponse(
            deal_id=response["dealId"],
        )


class IGApiAccount(IGApiResponse):
    def __init__(
        self,
        account_alias: str,
        account_id: str,
        account_name: str,
        account_type: str,
        balance: Dict[str, float],
        can_transfer_from: bool,
        can_transfer_to: bool,
        currency: str,
        preferred: bool,
        status: str,
    ) -> None:
        self._account_alias = account_alias
        self._account_id = account_id
        self._account_name = account_name
        self._account_type = account_type
        self._balance = balance
        self._can_transfer_from = can_transfer_from
        self._can_transfer_to = can_transfer_to
        self._currency = currency
        self._preferred = preferred
        self._status = status

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGApiAccount":
        return IGApiAccount(
            account_alias=response["accountAlias"],
            account_id=response["accountId"],
            account_name=response["accountName"],
            account_type=response["accountType"],
            balance=response["balance"],
            can_transfer_from=response["canTransferFrom"],
            can_transfer_to=response["canTransferTo"],
            currency=response["currency"],
            preferred=response["preferred"],
            status=response["status"],
        )

    @property
    def account_alias(self) -> str:
        return self._account_alias

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def account_name(self) -> str:
        return self._account_name

    @property
    def account_type(self) -> str:
        return self._account_type

    @property
    def balance(self) -> Dict[str, float]:
        return self._balance

    @property
    def can_transfer_from(self) -> bool:
        return self._can_transfer_from

    @property
    def can_transfer_to(self) -> bool:
        return self._can_transfer_to

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def preferred(self) -> bool:
        return self._preferred

    @property
    def status(self) -> str:
        return self._status

    def __str__(self) -> str:
        return (
            f"Account: {self.account_name} | "
            f"Alias: {self.account_alias} | "
            f"ID: {self.account_id} | "
            f"Type: {self.account_type} | "
            f"Balance: {self.balance} | "
            f"Currency: {self.currency} | "
            f"Can Transfer From: {self.can_transfer_from} | "
            f"Can Transfer To: {self.can_transfer_to} | "
            f"Preferred: {self.preferred} | "
            f"Status: {self.status}"
        )


class IGPostOrderResponse(IGApiResponse):
    def __init__(self, deal_reference: str) -> None:
        self._deal_reference = deal_reference

    @property
    def deal_reference(self) -> str:
        return self._deal_reference

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGPostOrderResponse":
        return IGPostOrderResponse(deal_reference=response["dealReference"])


class IGDealConfirmationResponse(IGApiResponse):
    def __init__(
        self,
        deal_id: str,
    ) -> None:
        self._deal_id = deal_id

    @property
    def deal_id(self) -> str:
        return self._deal_id

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGDealConfirmationResponse":
        return IGDealConfirmationResponse(
            deal_id=response["dealId"],
        )


class IGApiMarketDataResponse(IGApiResponse):
    def __init__(
        self,
        bid: float,
        delay_time: int,
        epic: str,
        exchange_id: str,
        expiry: str,
        high: float,
        instrument_name: str,
        instrument_type: InstrumentType,
        lot_size: float,
        low: float,
        market_status: MarketStatus,
        net_change: float,
        offer: float,
        percentage_change: float,
        scaling_factor: int,
        streaming_prices_available: bool,
        update_time: str,
        update_time_utc: str,
    ) -> None:
        self._bid = bid
        self._delay_time = delay_time
        self._epic = epic
        self._exchange_id = exchange_id
        self._expiry = expiry
        self._high = high
        self._instrument_name = instrument_name
        self._instrument_type = instrument_type
        self._lot_size = lot_size
        self._low = low
        self._market_status = market_status
        self._net_change = net_change
        self._offer = offer
        self._percentage_change = percentage_change
        self._scaling_factor = scaling_factor
        self._streaming_prices_available = streaming_prices_available
        self._update_time = update_time
        self._update_time_utc = update_time_utc

    @property
    def bid(self) -> float:
        return self._bid

    @property
    def delay_time(self) -> int:
        return self._delay_time

    @property
    def epic(self) -> str:
        return self._epic

    @property
    def exchange_id(self) -> str:
        return self._exchange_id

    @property
    def expiry(self) -> str:
        return self._expiry

    @property
    def high(self) -> float:
        return self._high

    @property
    def instrument_name(self) -> str:
        return self._instrument_name

    @property
    def instrument_type(self) -> InstrumentType:
        return self._instrument_type

    @property
    def lot_size(self) -> float:
        return self._lot_size

    @property
    def low(self) -> float:
        return self._low

    @property
    def market_status(self) -> MarketStatus:
        return self._market_status

    @property
    def net_change(self) -> float:
        return self._net_change

    @property
    def offer(self) -> float:
        return self._offer

    @property
    def percentage_change(self) -> float:
        return self._percentage_change

    @property
    def scaling_factor(self) -> int:
        return self._scaling_factor

    @property
    def streaming_prices_available(self) -> bool:
        return self._streaming_prices_available

    @property
    def update_time(self) -> str:
        return self._update_time

    @property
    def update_time_utc(self) -> str:
        return self._update_time_utc

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "IGApiMarketDataResponse":
        return IGApiMarketDataResponse(
            bid=response["bid"],
            delay_time=response["delayTime"],
            epic=response["epic"],
            exchange_id=response["exchangeId"],
            expiry=response["expiry"],
            high=response["high"],
            instrument_name=response["instrumentName"],
            instrument_type=InstrumentType(response["instrumentType"]),
            lot_size=response["lotSize"],
            low=response["low"],
            market_status=MarketStatus(response["marketStatus"]),
            net_change=response["netChange"],
            offer=response["offer"],
            percentage_change=response["percentageChange"],
            scaling_factor=response["scalingFactor"],
            streaming_prices_available=response["streamingPricesAvailable"],
            update_time=response["updateTime"],
            update_time_utc=response["updateTimeUTC"],
        )


class IGApi:
    _BASE_URL = (
        "https://api.ig.com/gateway/deal"
        if Configuration().environment == Environment.PROD
        else "https://demo-api.ig.com/gateway/deal"
    )

    def __init__(
        self,
        user_name: str,
        password: str,
        api_key: str,
        account_id: str,
    ) -> None:
        self._user_name = user_name
        self._password = password
        self._api_key = api_key
        self._account_id = account_id

    def _get_headers(self) -> Dict[str, str]:
        return IGApiHeader(
            api_key=self._api_key,
            account_id=self._account_id,
        ).to_header()

    def get_accounts(self) -> List[IGApiAccount]:
        try:
            response = requests.get(
                f"{IGApi._BASE_URL}/accounts", headers=self._get_headers() | self.post_session().to_header()
            )
            if response.status_code > 299 or response.status_code < 200:
                raise ValueError(f"Error getting accounts: {response.text}")

            return [IGApiAccount.from_response(account) for account in response.json()["accounts"]]
        except ValueError:
            raise

    def get_search_term(self, body: IGApiGetSearchTermBody) -> List[IGApiMarket]:
        try:
            response = requests.get(
                f"{IGApi._BASE_URL}/markets?searchTerm={body.search_term}",
                headers=self._get_headers() | self.post_session().to_header(),
            )
            if response.status_code > 299 or response.status_code < 200:
                raise ValueError(f"Error getting search term: {response.text}")

            return [IGApiMarket.from_response(market) for market in response.json()["markets"]]
        except ValueError:
            raise

    def get_prices(self, body: IGApiGetPricesBody) -> List[IGApiPrice]:
        try:
            url = f"{IGApi._BASE_URL}/prices/{body.to_path_params()}"
            CoreLogger().info(f"Getting prices from {url=}")
            response = requests.get(
                url, headers=self._get_headers() | self.post_session().to_header() | {"Version": "3"}
            )
            if response.status_code > 299 or response.status_code < 200:
                raise ValueError(f"Error getting prices from url: {url}, with {response.status_code}: {response.text}")
            return [IGApiPrice.from_response(price) for price in response.json()["prices"]]
        except ValueError:
            raise

    def get_working_orders(self) -> List[IGApiWorkingOrderResponse]:
        try:
            response = requests.get(
                f"{IGApi._BASE_URL}/workingorders",
                headers=self._get_headers() | self.post_session().to_header() | {"Version": "2"},
            )

            if response.status_code > 299 or response.status_code < 200:
                raise ValueError(f"Error getting working orders: {response.text}")

            return [
                IGApiWorkingOrderResponse.from_response(item["workingOrderData"])
                for item in response.json().get("workingOrders", [])
            ]
        except ValueError:
            raise

    def get_positions(self) -> List[IGApiPositionResponse]:
        try:
            response = requests.get(
                f"{IGApi._BASE_URL}/positions", headers=self._get_headers() | self.post_session().to_header()
            )
            if response.status_code > 299 or response.status_code < 200:
                raise ValueError(f"Error getting positions: {response.text}")

            return [
                IGApiPositionResponse.from_response(item["position"]) for item in response.json().get("positions", [])
            ]
        except ValueError:
            raise

    def get_confirmation(self, deal_reference: str) -> IGDealConfirmationResponse:
        try:
            response = requests.get(
                f"{IGApi._BASE_URL}/confirms/{deal_reference}",
                headers=self._get_headers() | self.post_session().to_header(),
            )
            if response.status_code > 299 or response.status_code < 200:
                raise ValueError(f"Error getting confirmation: {response.text}")

            return IGDealConfirmationResponse.from_response(response.json())
        except ValueError:
            raise

    ##############################
    # POST Requests
    ##############################
    def post_session(self) -> IGApiSession:
        try:
            response = requests.post(
                f"{IGApi._BASE_URL}/session",
                headers=self._get_headers(),
                json=IGApiSessionBody(
                    user_name=self._user_name,
                    password=self._password,
                ).to_body(),
            )
            if response.status_code > 299 or response.status_code < 200:
                raise ValueError(f"Error getting session: {response.text}")
            return IGApiSession.from_response(
                {"CST": response.headers["CST"], "X-SECURITY-TOKEN": response.headers["X-SECURITY-TOKEN"]}
            )
        except ValueError:
            raise

    def post_positions_otc(self, body: IGApiPostPositionsOrderBody) -> IGPostOrderResponse:
        try:
            response = requests.post(
                f"{IGApi._BASE_URL}/positions/otc",
                headers=self._get_headers() | self.post_session().to_header(),
                json=body.to_body(),
            )
            if response.status_code > 299 or response.status_code < 200:
                raise ValueError(f"Error posting positions otc: {response.text}")

            return IGPostOrderResponse.from_response(response.json())

        except ValueError:
            raise

    def post_working_otc(self, body: IGApiPostWorkingOrderBody) -> IGPostOrderResponse:
        try:
            body.validate()
            response = requests.post(
                f"{IGApi._BASE_URL}/workingorders/otc",
                headers=self._get_headers() | self.post_session().to_header() | {"Version": "2"},
                json=body.to_body(),
            )

            if response.status_code > 299 or response.status_code < 200:
                CoreLogger().error(f"Error posting working otc: {response.text}")
                raise ValueError(f"Error posting working otc: {response.text}")

            return IGPostOrderResponse.from_response(response.json())

        except ValueError:
            raise

    ##############################
    # DELETE Requests
    ##############################
    def delete_working_orders_otc(self, order_id: str) -> None:
        CoreLogger().info(f"Deleting working order with order_id: {order_id}")
        try:
            response = requests.delete(
                f"{IGApi._BASE_URL}/workingorders/otc/{order_id}",
                headers=self._get_headers() | self.post_session().to_header() | {"Version": "2"},
            )
            if response.status_code > 299 or response.status_code < 200:
                if response.json()["errorCode"] == "error.service.delete.working.order.not.found":
                    CoreLogger().info("Order does not exist!")
                    return

                raise ValueError(f"Error deleting working order: {response.text}")
        except ValueError:
            raise


if __name__ == "__main__":

    def _get_ig_credentials(secret_id: str) -> tuple[str, str, str, str]:
        """
        Retrieve IG credentials from secrets manager.
        """
        # Assuming the secret_id is used to fetch the credentials from a secrets manager
        # This part of the code is not provided in the original snippet
        secrets_manager = boto3.client("secretsmanager", region_name="eu-west-1")
        secret = secrets_manager.get_secret_value(SecretId=secret_id)
        secret_dict = json.loads(secret["SecretString"])
        user_name = secret_dict.get("IG_USERNAME")
        password = secret_dict.get("IG_PASSWORD")
        api_key = secret_dict.get("IG_API_KEY")
        account_id = secret_dict.get("IG_ACCOUNT_ID")
        if not all([user_name, password, api_key, account_id]):
            raise ValueError("Missing IG credentials in secrets manager.")

        return user_name, password, api_key, account_id

    user_name, password, api_key, account_id = _get_ig_credentials("IG_API_SECRETS_PROD")

    ig_api = IGApi(
        user_name=user_name,
        password=password,
        api_key=api_key,
        account_id=account_id,
    )
    result = ig_api.get_search_term(IGApiGetSearchTermBody(search_term="eurgbp"))

    pprint([item.__dict__ for item in result])
