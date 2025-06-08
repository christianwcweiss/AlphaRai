from typing import Any, Dict, List, Union

import dash_bootstrap_components as dbc
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.molecules.charts.balance_over_time.balance_over_time import BalanceOverTimeMolecule
from components.molecules.toolbars.analytics_toolbar import analytics_bar_filter_trades, analytics_bar_get_active_states
from constants import colors
from dash import Input, Output, callback, ctx
from dash.development.base_component import Component
from pages.analytics.overview.overview_constants import PREFIX
from quant_core.enums.chart_mode import ChartMode
from quant_core.metrics.account_balance_over_time.balance_over_time import AccountBalanceOverTime
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime
from services.db.cache.trade_history import get_all_trades_df


@callback(
    Output(f"{PREFIX}-content", "children"),
    Output(f"{PREFIX}-group-by-account-id", "active"),
    Output(f"{PREFIX}-group-by-symbol", "active"),
    Output(f"{PREFIX}-group-by-asset-type", "active"),
    Output(f"{PREFIX}-group-by-direction", "active"),
    Output(f"{PREFIX}-group-by-hour", "active"),
    Output(f"{PREFIX}-group-by-weekday", "active"),
    Output(f"{PREFIX}-show-abs-values", "active"),
    Output(f"{PREFIX}-show-rel-values", "active"),
    Input(f"{PREFIX}-filter-by-account-id", "value"),
    Input(f"{PREFIX}-filter-by-symbol", "value"),
    Input(f"{PREFIX}-filter-by-asset-type", "value"),
    Input(f"{PREFIX}-group-by-account-id", "active"),
    Input(f"{PREFIX}-group-by-symbol", "active"),
    Input(f"{PREFIX}-group-by-asset-type", "active"),
    Input(f"{PREFIX}-group-by-direction", "active"),
    Input(f"{PREFIX}-group-by-hour", "active"),
    Input(f"{PREFIX}-group-by-weekday", "active"),
    Input(f"{PREFIX}-show-abs-values", "active"),
    Input(f"{PREFIX}-show-rel-values", "active"),
    Input(f"{PREFIX}-group-by-account-id", "n_clicks"),
    Input(f"{PREFIX}-group-by-symbol", "n_clicks"),
    Input(f"{PREFIX}-group-by-asset-type", "n_clicks"),
    Input(f"{PREFIX}-group-by-direction", "n_clicks"),
    Input(f"{PREFIX}-group-by-hour", "n_clicks"),
    Input(f"{PREFIX}-group-by-weekday", "n_clicks"),
    Input(f"{PREFIX}-show-abs-values", "n_clicks"),
    Input(f"{PREFIX}-show-rel-values", "n_clicks"),
)
def render_overview_content(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    account_ids: List[str],
    symbols: List[str],
    asset_types: List[str],
    group_by_account_id: bool,
    group_by_symbol: bool,
    group_by_asset_type: bool,
    group_by_direction: bool,
    group_by_hour: bool,
    group_by_weekday: bool,
    show_abs: bool,
    show_rel: bool,
    _group_by_account_id_clicks: int,
    _group_by_symbol_clicks: int,
    _group_by_asset_type_clicks: int,
    _group_by_direction_clicks: int,
    _group_by_hour_clicks: int,
    _group_by_weekday_clicks: int,
    _show_abs_values_clicks: int,
    _show_rel_values_clicks: int,
) -> Union[Dict[str, Any], List[Component], dbc.Alert, AlphaRow]:
    """Render the overview content based on the selected filters and grouping options."""
    trades_df = get_all_trades_df()
    trades_df = analytics_bar_filter_trades(
        trades_df=trades_df,
        account_ids=account_ids,
        symbols=symbols,
        asset_types=asset_types,
    )
    if trades_df.empty:
        return (
            dbc.Alert("⚠️ No trade data found.", color=colors.ERROR_COLOR),
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            False,
        )

    (
        group_by_account_id,
        group_by_symbol,
        group_by_asset_type,
        group_by_direction,
        group_by_hour,
        group_by_weekday,
        show_abs,
        show_rel,
    ) = analytics_bar_get_active_states(
        group_by_account_id,
        group_by_symbol,
        group_by_asset_type,
        group_by_direction,
        group_by_hour,
        group_by_weekday,
        show_abs,
        show_rel,
        trigger_id=ctx.triggered_id,
        prefix=PREFIX,
    )

    groups = TradeMetricOverTime.groups(
        group_by_account_id, group_by_symbol, group_by_asset_type, group_by_direction, group_by_hour, group_by_weekday
    )
    balance_over_time_data_frame = AccountBalanceOverTime().calculate(
        data_frame=trades_df,
        group_by_account_id=group_by_account_id,
        group_by_symbol=group_by_symbol,
        group_by_asset_type=group_by_asset_type,
        group_by_direction=group_by_direction,
        group_by_hour=group_by_hour,
        group_by_weekday=group_by_weekday,
    )

    chart_mode = ChartMode.ABSOLUTE if show_abs else ChartMode.RELATIVE

    return (
        AlphaRow(
            [
                AlphaCol(
                    BalanceOverTimeMolecule(balance_over_time_data_frame).render(groups=groups, chart_mode=chart_mode),
                    xs=12,
                    sm=12,
                    md=12,
                    lg=12,
                    xl=12,
                )
            ]
        ),
        group_by_account_id,
        group_by_symbol,
        group_by_asset_type,
        group_by_direction,
        group_by_hour,
        group_by_weekday,
        show_abs,
        show_rel,
    )
