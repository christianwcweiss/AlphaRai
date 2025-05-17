class MT5Symbol:
    """MT5 Symbol class."""

    def __init__(
        self,
        is_custom: bool,
        chart_mode: int,
        select: bool,
        visible: bool,
        session_deals: int,
        session_buy_orders: int,
        session_sell_orders: int,
        volume: int,
        volume_high: int,
        volume_low: int,
        time: int,
        digits: int,
        spread: int,
        spread_float: bool,
        ticks_bookdepth: int,
        trade_calc_mode: int,
        trade_mode: int,
        start_time: int,
        expiration_time: int,
        trade_stops_level: int,
        trade_freeze_level: int,
        trade_exemode: int,
        swap_mode: int,
        swap_rollover3days: int,
        margin_hedged_use_leg: bool,
        expiration_mode: int,
        filling_mode: int,
        order_mode: int,
        order_gtc_mode: int,
        option_mode: int,
        option_right: int,
        bid: float,
        bidhigh: float,
        bidlow: float,
        ask: float,
        askhigh: float,
        asklow: float,
        last: float,
        lasthigh: float,
        lastlow: float,
        volume_real: float,
        volumehigh_real: float,
        volumelow_real: float,
        option_strike: float,
        point: float,
        trade_tick_value: float,
        trade_tick_value_profit: float,
        trade_tick_value_loss: float,
        trade_contract_size: float,
        trade_accrued_interest: float,
        trade_face_value: float,
        trade_liquidity_rate: float,
        volume_min: float,
        volume_max: float,
        volume_step: float,
        volume_limit: float,
        swap_long: float,
        swap_short: float,
        margin_initial: float,
        margin_maintenance: float,
        session_volume: float,
        session_turnover: float,
        session_interest: float,
        session_buy_orders_volume: float,
        session_sell_orders_volume: float,
        session_open: float,
        session_close: float,
        session_aw: float,
        session_price_settlement: float,
        session_price_limit_min: float,
        session_price_limit_max: float,
        margin_hedged: float,
        price_change: float,
        price_volatility: float,
        price_theoretical: float,
        price_greeks_delta: float,
        price_greeks_theta: float,
        price_greeks_gamma: float,
        price_greeks_vega: float,
        price_greeks_rho: float,
        price_greeks_omega: float,
        price_sensitivity: float,
        basis: str,
        category: str,
        currency_base: str,
        currency_profit: str,
        currency_margin: str,
        bank: str,
        description: str,
        exchange: str,
        formula: str,
        isin: str,
        name: str,
        page: str,
        path: str,
    ) -> None:
        self._is_custom = is_custom
        self._chart_mode = chart_mode
        self._select = select
        self._visible = visible
        self._session_deals = session_deals
        self._session_buy_orders = session_buy_orders
        self._session_sell_orders = session_sell_orders
        self._volume = volume
        self._volume_high = volume_high
        self._volume_low = volume_low
        self._time = time
        self._digits = digits
        self._spread = spread
        self._spread_float = spread_float
        self._ticks_bookdepth = ticks_bookdepth
        self._trade_calc_mode = trade_calc_mode
        self._trade_mode = trade_mode
        self._start_time = start_time
        self._expiration_time = expiration_time
        self._trade_stops_level = trade_stops_level
        self._trade_freeze_level = trade_freeze_level
        self._trade_exemode = trade_exemode
        self._swap_mode = swap_mode
        self._swap_rollover3days = swap_rollover3days
        self._margin_hedged_use_leg = margin_hedged_use_leg
        self._expiration_mode = expiration_mode
        self._filling_mode = filling_mode
        self._order_mode = order_mode
        self._order_gtc_mode = order_gtc_mode
        self._option_mode = option_mode
        self._option_right = option_right
        self._bid = bid
        self._bidhigh = bidhigh
        self._bidlow = bidlow
        self._ask = ask
        self._askhigh = askhigh
        self._asklow = asklow
        self._last = last
        self._lasthigh = lasthigh
        self._lastlow = lastlow
        self._volume_real = volume_real
        self._volumehigh_real = volumehigh_real
        self._volumelow_real = volumelow_real
        self._option_strike = option_strike
        self._point = point
        self._trade_tick_value = trade_tick_value
        self._trade_tick_value_profit = trade_tick_value_profit
        self._trade_tick_value_loss = trade_tick_value_loss
        self._trade_contract_size = trade_contract_size
        self._trade_accrued_interest = trade_accrued_interest
        self._trade_face_value = trade_face_value
        self._trade_liquidity_rate = trade_liquidity_rate
        self._volume_min = volume_min
        self._volume_max = volume_max
        self._volume_step = volume_step
        self._volume_limit = volume_limit
        self._swap_long = swap_long
        self._swap_short = swap_short
        self._margin_initial = margin_initial
        self._margin_maintenance = margin_maintenance
        self._session_volume = session_volume
        self._session_turnover = session_turnover
        self._session_interest = session_interest
        self._session_buy_orders_volume = session_buy_orders_volume
        self._session_sell_orders_volume = session_sell_orders_volume
        self._session_open = session_open
        self._session_close = session_close
        self._session_aw = session_aw
        self._session_price_settlement = session_price_settlement
        self._session_price_limit_min = session_price_limit_min
        self._session_price_limit_max = session_price_limit_max
        self._margin_hedged = margin_hedged
        self._price_change = price_change
        self._price_volatility = price_volatility
        self._price_theoretical = price_theoretical
        self._price_greeks_delta = price_greeks_delta
        self._price_greeks_theta = price_greeks_theta
        self._price_greeks_gamma = price_greeks_gamma
        self._price_greeks_vega = price_greeks_vega
        self._price_greeks_rho = price_greeks_rho
        self._price_greeks_omega = price_greeks_omega
        self._price_sensitivity = price_sensitivity
        self._basis = basis
        self._category = category
        self._currency_base = currency_base
        self._currency_profit = currency_profit
        self._currency_margin = currency_margin
        self._bank = bank
        self._description = description
        self._exchange = exchange
        self._formula = formula
        self._isin = isin
        self._name = name
        self._page = page
        self._path = path

    @property
    def is_custom(self) -> bool:
        """Check if the symbol is custom."""
        return self._is_custom

    @property
    def chart_mode(self) -> int:
        """Get the chart mode."""
        return self._chart_mode

    @property
    def select(self) -> bool:
        """Check if the symbol is selected."""
        return self._select

    @property
    def visible(self) -> bool:
        """Check if the symbol is visible."""
        return self._visible

    @property
    def session_deals(self) -> int:
        """Get the number of session deals."""
        return self._session_deals

    @property
    def session_buy_orders(self) -> int:
        """Get the number of session buy orders."""
        return self._session_buy_orders

    @property
    def session_sell_orders(self) -> int:
        """Get the number of session sell orders."""
        return self._session_sell_orders

    @property
    def volume(self) -> int:
        """Get the volume."""
        return self._volume

    @property
    def volume_high(self) -> int:
        """Get the high volume."""
        return self._volume_high

    @property
    def volume_low(self) -> int:
        """Get the low volume."""
        return self._volume_low

    @property
    def time(self) -> int:
        """Get the time."""
        return self._time

    @property
    def digits(self) -> int:
        """Get the number of digits."""
        return self._digits

    @property
    def spread(self) -> int:
        """Get the spread."""
        return self._spread

    @property
    def spread_float(self) -> bool:
        """Check if the spread is float."""
        return self._spread_float

    @property
    def ticks_bookdepth(self) -> int:
        """Get the ticks book depth."""
        return self._ticks_bookdepth

    @property
    def trade_calc_mode(self) -> int:
        """Get the trade calculation mode."""
        return self._trade_calc_mode

    @property
    def trade_mode(self) -> int:
        """Get the trade mode."""
        return self._trade_mode

    @property
    def start_time(self) -> int:
        """Get the start time."""
        return self._start_time

    @property
    def expiration_time(self) -> int:
        """Get the expiration time."""
        return self._expiration_time

    @property
    def trade_stops_level(self) -> int:
        """Get the trade stops level."""
        return self._trade_stops_level

    @property
    def trade_freeze_level(self) -> int:
        """Get the trade freeze level."""
        return self._trade_freeze_level

    @property
    def trade_exemode(self) -> int:
        """Get the trade execution mode."""
        return self._trade_exemode

    @property
    def swap_mode(self) -> int:
        """Get the swap mode."""
        return self._swap_mode

    @property
    def swap_rollover3days(self) -> int:
        """Get the swap rollover for 3 days."""
        return self._swap_rollover3days

    @property
    def margin_hedged_use_leg(self) -> bool:
        """Check if the margin is hedged using leg."""
        return self._margin_hedged_use_leg

    @property
    def expiration_mode(self) -> int:
        """Get the expiration mode."""
        return self._expiration_mode

    @property
    def filling_mode(self) -> int:
        """Get the filling mode."""
        return self._filling_mode

    @property
    def order_mode(self) -> int:
        """Get the order mode."""
        return self._order_mode

    @property
    def order_gtc_mode(self) -> int:
        """Get the order GTC mode."""
        return self._order_gtc_mode

    @property
    def option_mode(self) -> int:
        """Get the option mode."""
        return self._option_mode

    @property
    def option_right(self) -> int:
        """Get the option right."""
        return self._option_right

    @property
    def bid(self) -> float:
        """Get the bid price."""
        return self._bid

    @property
    def bidhigh(self) -> float:
        """Get the high bid price."""
        return self._bidhigh

    @property
    def bidlow(self) -> float:
        """Get the low bid price."""
        return self._bidlow

    @property
    def ask(self) -> float:
        """Get the ask price."""
        return self._ask

    @property
    def askhigh(self) -> float:
        """Get the high ask price."""
        return self._askhigh

    @property
    def asklow(self) -> float:
        """Get the low ask price."""
        return self._asklow

    @property
    def last(self) -> float:
        """Get the last price."""
        return self._last

    @property
    def lasthigh(self) -> float:
        """Get the high last price."""
        return self._lasthigh

    @property
    def lastlow(self) -> float:
        """Get the low last price."""
        return self._lastlow

    @property
    def volume_real(self) -> float:
        """Get the real volume."""
        return self._volume_real

    @property
    def volumehigh_real(self) -> float:
        """Get the high real volume."""
        return self._volumehigh_real

    @property
    def volumelow_real(self) -> float:
        """Get the low real volume."""
        return self._volumelow_real

    @property
    def option_strike(self) -> float:
        """Get the option strike price."""
        return self._option_strike

    @property
    def point(self) -> float:
        """Get the point value."""
        return self._point

    @property
    def trade_tick_value(self) -> float:
        """Get the trade tick value."""
        return self._trade_tick_value

    @property
    def trade_tick_value_profit(self) -> float:
        """Get the trade tick value profit."""
        return self._trade_tick_value_profit

    @property
    def trade_tick_value_loss(self) -> float:
        """Get the trade tick value loss."""
        return self._trade_tick_value_loss

    @property
    def trade_contract_size(self) -> float:
        """Get the trade contract size."""
        return self._trade_contract_size

    @property
    def trade_accrued_interest(self) -> float:
        """Get the trade accrued interest."""
        return self._trade_accrued_interest

    @property
    def trade_face_value(self) -> float:
        """Get the trade face value."""
        return self._trade_face_value

    @property
    def trade_liquidity_rate(self) -> float:
        """Get the trade liquidity rate."""
        return self._trade_liquidity_rate

    @property
    def volume_min(self) -> float:
        """Get the minimum volume."""
        return self._volume_min

    @property
    def volume_max(self) -> float:
        """Get the maximum volume."""
        return self._volume_max

    @property
    def volume_step(self) -> float:
        """Get the volume step."""
        return self._volume_step

    @property
    def volume_limit(self) -> float:
        """Get the volume limit."""
        return self._volume_limit

    @property
    def swap_long(self) -> float:
        """Get the long swap."""
        return self._swap_long

    @property
    def swap_short(self) -> float:
        """Get the short swap."""
        return self._swap_short

    @property
    def margin_initial(self) -> float:
        """Get the initial margin."""
        return self._margin_initial

    @property
    def margin_maintenance(self) -> float:
        """Get the maintenance margin."""
        return self._margin_maintenance

    @property
    def session_volume(self) -> float:
        """Get the session volume."""
        return self._session_volume

    @property
    def session_turnover(self) -> float:
        """Get the session turnover."""
        return self._session_turnover

    @property
    def session_interest(self) -> float:
        """Get the session interest."""
        return self._session_interest

    @property
    def session_buy_orders_volume(self) -> float:
        """Get the session buy orders volume."""
        return self._session_buy_orders_volume

    @property
    def session_sell_orders_volume(self) -> float:
        """Get the session sell orders volume."""
        return self._session_sell_orders_volume

    @property
    def session_open(self) -> float:
        """Get the session open price."""
        return self._session_open

    @property
    def session_close(self) -> float:
        """Get the session close price."""
        return self._session_close

    @property
    def session_aw(self) -> float:
        """Get the session AW price."""
        return self._session_aw

    @property
    def session_price_settlement(self) -> float:
        """Get the session price settlement."""
        return self._session_price_settlement

    @property
    def session_price_limit_min(self) -> float:
        """Get the session price limit minimum."""
        return self._session_price_limit_min

    @property
    def session_price_limit_max(self) -> float:
        """Get the session price limit maximum."""
        return self._session_price_limit_max

    @property
    def margin_hedged(self) -> float:
        """Get the margin hedge."""
        return self._margin_hedged

    @property
    def price_change(self) -> float:
        """Get the price change."""
        return self._price_change

    @property
    def price_volatility(self) -> float:
        """Get the price volatility."""
        return self._price_volatility

    @property
    def price_theoretical(self) -> float:
        """Get the theoretical price."""
        return self._price_theoretical

    @property
    def price_greeks_delta(self) -> float:
        """Get the delta value."""
        return self._price_greeks_delta

    @property
    def price_greeks_theta(self) -> float:
        """Get the theta value."""
        return self._price_greeks_theta

    @property
    def price_greeks_gamma(self) -> float:
        """Get the gamma value."""
        return self._price_greeks_gamma

    @property
    def price_greeks_vega(self) -> float:
        """Get the vega value."""
        return self._price_greeks_vega

    @property
    def price_greeks_rho(self) -> float:
        """Get the rho value."""
        return self._price_greeks_rho

    @property
    def price_greeks_omega(self) -> float:
        """Get the omega value."""
        return self._price_greeks_omega

    @property
    def price_sensitivity(self) -> float:
        """Get the price sensitivity."""
        return self._price_sensitivity

    @property
    def basis(self) -> str:
        """Get the basis."""
        return self._basis

    @property
    def category(self) -> str:
        """Get the category."""
        return self._category

    @property
    def currency_base(self) -> str:
        """Get the base currency."""
        return self._currency_base

    @property
    def currency_profit(self) -> str:
        """Get the profit currency."""
        return self._currency_profit

    @property
    def currency_margin(self) -> str:
        """Get the margin currency."""
        return self._currency_margin

    @property
    def bank(self) -> str:
        """Get the bank."""
        return self._bank

    @property
    def description(self) -> str:
        """Get the description."""
        return self._description

    @property
    def exchange(self) -> str:
        """Get the exchange."""
        return self._exchange

    @property
    def formula(self) -> str:
        """Get the formula."""
        return self._formula

    @property
    def isin(self) -> str:
        """Get the ISIN."""
        return self._isin

    @property
    def name(self) -> str:
        """Get the name."""
        return self._name

    @property
    def page(self) -> str:
        """Get the page."""
        return self._page

    @property
    def path(self) -> str:
        """Get the path."""
        return self._path
