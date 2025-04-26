import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, callback, Input, Output, ctx

from components.atoms.buttons.button import AlphaButton
from components.atoms.charts.chart import ChartMargin
from components.atoms.charts.line.line_chart import LineChart, LineChartStyle
from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from db.database import SessionLocal
from models.account import Account
from pages.base_page import BasePage
from quant_core.clients.mt5.mt5_client import Mt5Client
from quant_core.enums.platform import Platform
from quant_core.metrics.account.absolute_account_growth_over_time import AccountGrowthAbsoluteOverTime
from quant_core.metrics.account.percentage_account_growth_over_time import AccountGrowthPercentageOverTime
from quant_core.services.core_logger import CoreLogger
from services.db.trades import truncate_trades_table, upsert_trade, get_all_trades

dash.register_page(__name__, path="/analysis", name="Analysis")


class AnalysisPage(BasePage):
    def render(self):
        return PageBody(
            [
                PageHeader("📈 Strategy Analysis"),
                MainContent(
                    [
                        dcc.Loading(html.Div(id="analysis-output"), type="circle"),
                        AlphaButton(
                            label="Sync MT5 Trade History",
                            button_id="load-analysis-btn",
                        ).render(),
                    ]
                ),
            ]
        )


page = AnalysisPage("Strategy Analysis")
layout = page.layout


@callback(
    Output("analysis-output", "children"),
    Input("load-analysis-btn", "n_clicks"),
    Input("url", "pathname"),
    prevent_initial_call=False,
)
def handle_analysis_page(load_clicks, pathname):
    """Handles both page load and button press: load from DB, or sync and reload."""
    triggered_id = ctx.triggered_id

    if triggered_id == "load-analysis-btn":
        CoreLogger().info("🔄 Button clicked: Truncate + Reload from MT5.")

        truncate_trades_table()

        with SessionLocal() as session:
            accounts = session.query(Account).filter_by(platform=Platform.METATRADER.value, enabled=True).all()

        for account in accounts:
            try:
                CoreLogger().info(f"🔍 Loading MT5 trades for {account.uid}...")
                client = Mt5Client(secret_id=account.secret_name)
                trades_df = client.get_history_df(days=9999)
                client.shutdown()

                for _, row in trades_df.iterrows():
                    trade_data = {
                        "ticket": row["ticket"],
                        "order": row["order"],
                        "time": row["time"],
                        "type": row["type"],
                        "entry": row["entry"],
                        "size": row["size"],
                        "symbol": row["symbol"],
                        "price": row["price"],
                        "commission": row["commission"],
                        "swap": row["swap"],
                        "profit": row["profit"],
                        "magic": row["magic"],
                        "comment": row["comment"],
                    }
                    upsert_trade(trade_data, account_id=account.uid)

            except Exception as e:
                CoreLogger().error(f"❌ Failed to load MT5 data for {account.uid}: {e}")
    else:
        CoreLogger().info("📥 Page load: Just loading trades from database.")

    trades = get_all_trades()

    if not trades:
        return dbc.Alert("⚠️ No trade data found. Please sync first.", color="warning")

    data_frame = pd.DataFrame([{
        "ticket": t.ticket,
        "order": t.order,
        "time": t.time,
        "type": t.type,
        "entry": t.entry,
        "size": t.size,
        "symbol": t.symbol,
        "price": t.price,
        "commission": t.commission,
        "swap": t.swap,
        "profit": t.profit,
        "magic": t.magic,
        "comment": t.comment,
        "Account": t.account_id,
    } for t in trades])

    if data_frame.empty:
        return dbc.Alert("⚠️ No trade data available.", color="warning")

    # Calculate metrics
    absolute_growth_metric_data_frame = AccountGrowthAbsoluteOverTime().calculate(data_frame=data_frame)
    percentage_growth_metric_data_frame = AccountGrowthPercentageOverTime().calculate(data_frame=data_frame)

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(figure=LineChart(
                            data_frame=absolute_growth_metric_data_frame).plot(
                            x_col="time",
                            y_col="absolute_balance",
                            group_by="Account",
                            line_chart_style=LineChartStyle(
                                title="Absolute Account Growth Over Time",
                                x_axis_title="Date",
                                x_axis_title_show=True,
                                x_grid_show=True,
                                y_axis_title="Absolute Balance",
                                y_grid_show=True,
                                y_axis_title_show=True,
                                show_legend=True,
                                margin=ChartMargin(
                                    left=20,
                                    right=20,
                                    top=20,
                                    bottom=20,
                                )
                            )
                        )),
                        xs=12,
                        sm=12,
                        md=6,
                        lg=4,
                        xl=4,
                    )
                ]
            ),
            # dbc.Row([dbc.Col(dcc.Graph(figure=None), width=12)]),
        ],
        fluid=True,
    )
