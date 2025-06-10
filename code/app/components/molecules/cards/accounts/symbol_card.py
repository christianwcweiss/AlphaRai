import os

from components.atoms.card.card import AlphaCard, AlphaCardHeader
from dash import html
from models.main.account_config import AccountConfig
from quant_core.utils.image_utils import encode_image


class AccountConfigCard:  # pylint: disable=too-few-public-methods
    """A card to display account configuration options."""

    def __init__(self, edit_button_id: str, account_config: AccountConfig) -> None:
        self._account_config = account_config
        self._edit_button_id = edit_button_id

    def _render_header(self) -> html.Div:
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "assets", "icons", "general")
        edit_icon = encode_image(file_path=os.path.join(icon_path, "edit.png"))

        return AlphaCardHeader(
            html.Div(
                [
                    html.A(
                        html.Div(
                            html.H5(self._account_config.platform_asset_id, style={"margin": 0}),
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        style={"textDecoration": "none", "color": "inherit"},
                    ),
                    html.Button(
                        html.Img(
                            src=f"data:image/png;base64,{edit_icon}",
                            style={"height": "24px", "marginRight": "0.5rem"},
                        ),
                        id={"type": self._edit_button_id, "index": self._account_config.platform_asset_id},
                        style={
                            "background": "none",
                            "border": "none",
                            "padding": "0",
                            "cursor": "pointer",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "width": "100%",
                },
            )
        ).render()

    def _render_body(self) -> html.Div:
        def info_row(label, value):
            return html.Div(
                [
                    html.Span(label, style={"fontWeight": "500", "flex": "1"}),
                    html.Span(value, style={"flex": "1", "textAlign": "right"}),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "padding": "4px 0",
                    "borderBottom": "1px solid #eee",
                },
            )

        cfg = self._account_config

        return html.Div(
            [
                info_row("Stagger", f"{ cfg.n_staggers} @ {cfg.entry_stagger_method.value}"),
                info_row("Risk %", f"{cfg.risk_percent:.2f}"),
                info_row("Enabled", cfg.enabled_trade_direction.value),
            ],
            style={
                "padding": "12px",
                "fontSize": "14px",
                "lineHeight": "1.6",
            },
        )

    def render(self) -> html.Div:
        """Renders the account settings card."""
        return AlphaCard(
            header=self._render_header(),
            body=self._render_body(),
            style={"backgroundColor": "#ffffff"},
        ).render()
