"""Internal REST v3 endpoint families."""

from maicoin.v3._endpoints.convert import ConvertEndpoints
from maicoin.v3._endpoints.funds import FundsEndpoints
from maicoin.v3._endpoints.m_wallet import MWalletEndpoints
from maicoin.v3._endpoints.order_intake_history import OrderIntakeHistoryEndpoints
from maicoin.v3._endpoints.public_market_data import PublicMarketDataEndpoints

__all__ = [
    "ConvertEndpoints",
    "FundsEndpoints",
    "MWalletEndpoints",
    "OrderIntakeHistoryEndpoints",
    "PublicMarketDataEndpoints",
]
