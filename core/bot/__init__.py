Trading Bot Core Module v6.0
Main.py 모듈화

from .trading_bot import TradingBotV2
from .lifecycle import BotLifecycle
from .scanner import StockScanner
from .trader import TradeExecutor

__all__ = [
    'TradingBotV2',
    'BotLifecycle',
    'StockScanner',
    'TradeExecutor'
]
