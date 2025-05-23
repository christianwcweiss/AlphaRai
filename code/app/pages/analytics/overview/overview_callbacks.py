from typing import Dict, List, Any, Union

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, ctx
from dash.development.base_component import Component

from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.molecules.charts.balance_over_time.balance_over_time import (
    BalanceOverTimeMolecule,
)
from components.molecules.toolbars.analytics_toolbar import analytics_bar_filter_trades, analytics_bar_get_active_states
from constants import colors
from quant_core.enums.chart_mode import ChartMode
from quant_core.metrics.account_balance_over_time.balance_over_time import AccountBalanceOverTime
from quant_core.services.core_logger import CoreLogger
from services.db.cache.trade_history import get_all_trades_df


@callback(
    Output("overview-content", "children"),
    Output("group-by-account-id", "active"),
    Output("group-by-symbol", "active"),
    Output("group-by-asset-type", "active"),
    Output("group-by-direction", "active"),
    Output("group-by-hour", "active"),
    Output("group-by-weekday", "active"),
    Output("show-abs-values", "active"),
    Output("show-rel-values", "active"),
    Input("filter-by-account-id", "value"),
    Input("filter-by-symbol", "value"),
    Input("filter-by-asset-type", "value"),
    Input("group-by-account-id", "n_clicks"),
    Input("group-by-symbol", "n_clicks"),
    Input("group-by-asset-type", "n_clicks"),
    Input("group-by-direction", "n_clicks"),
    Input("group-by-hour", "n_clicks"),
    Input("group-by-weekday", "n_clicks"),
    Input("show-abs-values", "active"),
    Input("show-rel-values", "active"),
    Input("show-abs-values", "n_clicks"),
    Input("show-rel-values", "n_clicks"),
)
def render_overview_content(
    account_ids: List[str],
    symbols: List[str],
    asset_types: List[str],
    group_by_account_id_clicks: int,
    group_by_symbol_clicks: int,
    group_by_asset_type_clicks: int,
    group_by_direction_clicks: int,
    group_by_hour_clicks: int,
    group_by_weekday_clicks: int,
    show_abs: bool,
    show_rel: bool,
    _: int,
    __: int,
) -> Union[Dict[str, Any], List[Component], dbc.Alert, AlphaRow]:
    trades_df = get_all_trades_df()
    trades_df = analytics_bar_filter_trades(
        trades_df=trades_df,
        account_ids=account_ids,
        symbols=symbols,
        asset_types=asset_types,
    )
    if trades_df.empty:
        return dbc.Alert("⚠️ No trade data found.", color=colors.ERROR_COLOR)

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
        group_by_account_id_clicks,
        group_by_symbol_clicks,
        group_by_asset_type_clicks,
        group_by_direction_clicks,
        group_by_hour_clicks,
        group_by_weekday_clicks,
        show_abs,
        show_rel,
        trigger_id=ctx.triggered_id,
    )

    groups = AccountBalanceOverTime.groups(
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
    CoreLogger().info(f"Chart mode: {chart_mode}")

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
