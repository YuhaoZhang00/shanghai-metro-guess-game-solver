"""
Shanghai Metro Guess Game Package

A guessing game based on the Shanghai Metro system.
"""

from .metro_game_core import (
    MetroGameCore,
    Station,
    GuessResult,
    GuessAttributeDifference,
)
from .metro_game_player import MetroGamePlayer

__all__ = [
    "MetroGameCore",
    "MetroGamePlayer",
    "Station",
    "GuessResult",
    "GuessAttributeDifference",
]

__version__ = "1.0.0"
