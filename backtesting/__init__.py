"""
Backtesting Module
Walk-forward backtesting to validate model performance over time
"""

from .backtest_goals import backtest_goals
from .backtest_value_bets import backtest_value_bets
from .utils import calculate_roi, calculate_kelly_stake

__all__ = [
    'backtest_goals',
    'backtest_value_bets',
    'calculate_roi',
    'calculate_kelly_stake'
]
