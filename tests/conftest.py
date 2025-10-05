"""
Shared pytest fixtures and configuration
"""

import pytest

from src import MetroGameCore, MetroGamePlayer


@pytest.fixture(scope="session")
def game_core():
    """Create a single MetroGameCore instance for the entire test session."""
    return MetroGameCore()


@pytest.fixture
def game_player():
    """Create a fresh MetroGamePlayer instance for each test."""
    return MetroGamePlayer()
