"""
Tests for metro_game_player.py module
Tests utility functions, MetroGamePlayer functionality, and edge cases
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import io

from src.metro_game_player import get_display_width, pad_string, MetroGamePlayer, main


class TestUtilityFunctions:
    """Test utility functions for display formatting."""

    def test_get_display_width_ascii(self):
        """Test display width calculation for ASCII characters."""
        assert get_display_width("hello") == 5
        assert get_display_width("world") == 5
        assert get_display_width("") == 0
        assert get_display_width("a") == 1

    def test_get_display_width_chinese(self):
        """Test display width calculation for Chinese characters."""
        assert get_display_width("上海") == 4  # 2 Chinese chars = 4 width
        assert get_display_width("地铁") == 4  # 2 Chinese chars = 4 width
        assert get_display_width("上海地铁") == 8  # 4 Chinese chars = 8 width

    def test_get_display_width_mixed(self):
        """Test display width calculation for mixed ASCII and Chinese."""
        assert get_display_width("上海Metro") == 9  # 2 Chinese (4) + 5 ASCII (5) = 9
        assert get_display_width("Line1号线") == 9  # Line1 (5) + 号线 (4) = 9

    def test_get_display_width_emojis(self):
        """Test display width calculation for emojis used in the file."""
        assert get_display_width("🚇") == 2
        assert get_display_width("🎉") == 2
        assert get_display_width("📊") == 2
        assert get_display_width("✅❌") == 4  # 2 emojis = 4 width
        assert get_display_width("🚇上海") == 6  # emoji (2) + Chinese (4) = 6

    def test_pad_string_ascii(self):
        """Test string padding for ASCII text."""
        assert pad_string("hello", 10) == "hello     "
        assert pad_string("world", 8) == "world   "
        assert pad_string("test", 4) == "test"  # exact width
        assert pad_string("toolong", 5) == "toolong"  # already too long

    def test_pad_string_chinese(self):
        """Test string padding for Chinese text."""
        assert pad_string("上海", 6) == "上海  "  # 4 width + 2 spaces = 6
        assert pad_string("地铁", 8) == "地铁    "  # 4 width + 4 spaces = 8

    def test_pad_string_mixed(self):
        """Test string padding for mixed text."""
        assert pad_string("上海Metro", 12) == "上海Metro   "  # 9 width + 3 spaces = 12
        assert pad_string("🚇Line1", 10) == "🚇Line1   "  # 7 width + 3 spaces = 10

    def test_pad_string_edge_cases(self):
        """Test edge cases for string padding."""
        assert pad_string("", 5) == "     "  # empty string
        assert pad_string("test", 0) == "test"  # zero target width
        assert pad_string("test", -1) == "test"  # negative target width


class TestMetroGamePlayer:
    """Test cases for MetroGamePlayer class."""

    def test_player_initialization(self, game_player):
        """Test that the player initializes correctly."""
        assert game_player.game_core is not None
        assert game_player.target_station is not None
        assert len(game_player.remaining_stations) > 0
        assert game_player.guess_count == 0

    # def test_target_setting(self, game_player):
    #     """Test setting a specific target station."""
    #     target_name = game_player.game_core.stations[10]["name"]
    #     success = game_player.set_target(target_name)
    #     assert success is True
    #     assert game_player.get_target_name() == target_name

    #     # Test invalid target
    #     success = game_player.set_target("Invalid Station Name")
    #     assert success is False

    def test_valid_guess_processing(self, game_player):
        """Test processing a valid guess."""
        station_name = game_player.game_core.stations[5]["name"]
        result = game_player.make_guess(station_name)

        assert result["valid_guess"] is True
        assert result["guess_number"] == 1
        assert "stationInfo" in result
        assert "correct" in result
        assert game_player.guess_count == 1

    def test_invalid_guess_processing(self, game_player):
        """Test processing an invalid guess."""
        result = game_player.make_guess("Invalid Station Name")

        assert result["valid_guess"] is False
        assert "error" in result
        assert game_player.guess_count == 0  # Should not increment for invalid guess

    def test_correct_guess(self, game_player):
        """Test making a correct guess."""
        target_name = game_player.get_target_name()
        result = game_player.make_guess(target_name)

        assert result["valid_guess"] is True
        assert result["correct"] is True
        assert result["guess_number"] == 1

    # def test_remaining_station_names(self, game_player):
    #     """Test getting remaining station names."""
    #     names = game_player.get_remaining_station_names()
    #     assert isinstance(names, list)
    #     assert len(names) > 0
    #     assert all(isinstance(name, str) for name in names)

    def test_game_reset(self, game_player):
        """Test resetting the game."""
        # Make a guess first
        station_name = game_player.game_core.stations[5]["name"]
        game_player.make_guess(station_name)

        assert game_player.guess_count == 1

        game_player.reset_game()

        assert game_player.guess_count == 0
        assert len(game_player.remaining_stations) == len(
            game_player.game_core.stations
        )
        assert game_player.target_station is not None


class TestMetroGamePlayerExtended:
    """Extended tests for MetroGamePlayer class functionality."""

    def test_correct_guess(self, game_player):
        """Test a correct guess."""
        target_name = game_player.get_target_name()

        # First correct guess
        result1 = game_player.make_guess(target_name)
        assert result1["correct"] is True
        assert result1["guess_number"] == 1

    def test_multiple_incorrect_guesses_sequence(self, game_player):
        """Test a sequence of incorrect guesses."""
        target_name = game_player.get_target_name()
        all_stations = game_player.game_core.stations

        wrong_stations = [s for s in all_stations if s["name"] != target_name][:5]

        for i, station in enumerate(wrong_stations, 1):
            result = game_player.make_guess(station["name"])
            assert result["valid_guess"] is True
            assert result["correct"] is False
            assert result["guess_number"] == i
            assert game_player.guess_count == i

    def test_remaining_stations_decrease_with_guesses(self, game_player):
        """Test that remaining stations decrease after each guess."""
        target_name = game_player.get_target_name()
        all_stations = game_player.game_core.stations

        initial_count = len(game_player.remaining_stations)

        wrong_stations = [s for s in all_stations if s["name"] != target_name][:5]
        prev_count = initial_count

        for station in wrong_stations:
            result = game_player.make_guess(station["name"])
            new_count = len(game_player.remaining_stations)
            assert new_count <= prev_count
            assert result["valid_guess"] is True
            prev_count = new_count

    # def test_set_target_to_current_target(self, game_player):
    #     """Test setting target to the same station."""
    #     current_target = game_player.get_target_name()
    #     success = game_player.set_target(current_target)
    #     assert success is True
    #     assert game_player.get_target_name() == current_target

    def test_reset_game_multiple_times(self, game_player):
        """Test resetting the game multiple times."""
        original_total = len(game_player.game_core.stations)

        for _ in range(5):
            # Make some guesses
            station_name = game_player.game_core.stations[1]["name"]
            game_player.make_guess(station_name)

            # Reset
            game_player.reset_game()

            # Verify reset state
            assert game_player.guess_count == 0
            assert len(game_player.remaining_stations) == original_total
            assert game_player.target_station is not None

    def test_empty_guess(self, game_player):
        """Test making an empty guess."""
        result = game_player.make_guess("")
        assert result["valid_guess"] is False
        assert "error" in result

    def test_whitespace_guess(self, game_player):
        """Test making a guess with only whitespace."""
        result = game_player.make_guess("   ")
        assert result["valid_guess"] is False
        assert "error" in result

    def test_special_characters_guess(self, game_player):
        """Test making a guess with special characters."""
        result = game_player.make_guess("@#$%^&*()")
        assert result["valid_guess"] is False
        assert "error" in result


class TestInteractivePlayMocking:
    """Test interactive play functionality with mocking."""

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_play_interactive_quit(self, mock_stdout, mock_input):
        """Test quitting the interactive game immediately."""
        # Mock user input to quit immediately
        mock_input.return_value = "quit"

        player = MetroGamePlayer()
        player.play_interactive()

        output = mock_stdout.getvalue()
        assert "Thanks for playing!" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_play_interactive_answer_then_quit(self, mock_stdout, mock_input):
        """Test asking for answer then quitting."""
        # Mock user input: answer command then quit
        mock_input.side_effect = ["answer", "quit"]

        player = MetroGamePlayer()
        player.play_interactive()

        output = mock_stdout.getvalue()
        assert "The answer is:" in output
        assert "Thanks for playing!" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_play_interactive_reset_then_quit(self, mock_stdout, mock_input):
        """Test reset command then quit."""
        # Mock user input: reset then quit
        mock_input.side_effect = ["reset", "quit"]

        player = MetroGamePlayer()
        player.play_interactive()

        output = mock_stdout.getvalue()
        assert "New game started!" in output
        assert "Thanks for playing!" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_play_interactive_guess_then_quit(self, mock_stdout, mock_input):
        """Test reset command then quit."""
        # Mock user input: reset then quit
        mock_input.side_effect = ["人民广场", "quit"]

        player = MetroGamePlayer()
        player.play_interactive()

        output = mock_stdout.getvalue()
        assert "Guess #1:" in output
        assert "Thanks for playing!" in output
