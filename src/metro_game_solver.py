#!/usr/bin/env python3
"""
Metro Game Solver - Interactive solver for Shanghai Metro Guess Game

Takes station name and guess outputs (district match, line match, year match) from stdin,
and returns a list of stations with attributes matching those constraints.

Usage:
    python metro_game_solver.py

Input format (one per line):
    station_name district_match line_match year_match

Where:
    - station_name: Name of the guessed station
    - district_match: 2 (every), 1 (some), or 0 (none)
    - line_match: 2 (every), 1 (some), or 0 (none)
    - year_match: -1 (target < guess), 0 (target = guess), or 1 (target > guess)

Example:
    航头 2 2 0
    徐家汇 1 0 1

Type 'quit' to stop.
"""

try:
    from .metro_game_core import MetroGameCore, Station, GuessAttributeDifference
except ImportError:
    from metro_game_core import MetroGameCore, Station, GuessAttributeDifference

from typing import List, Optional
import sys


class MetroGameSolver:
    """Solver for Shanghai Metro Guess Game based on guess constraints."""

    def __init__(self, stations_file: str = "stations.json"):
        """Initialize the solver with station data."""
        self.game_core = MetroGameCore(stations_file)
        self.possible_stations: List[Station] = self.game_core.stations.copy()
        self.guess_history: List[dict] = []

    def _convert_numeric_to_text(self, numeric_match: int) -> str:
        """Convert numeric match value to text representation."""
        mapping = {2: "every", 1: "some", 0: "none"}
        return mapping.get(numeric_match, "none")

    def reset_solver(self) -> None:
        """Reset the solver to start fresh."""
        self.possible_stations = self.game_core.stations.copy()
        self.guess_history = []

    def apply_constraint(
        self, guess_name: str, district_match: int, line_match: int, year_match: int
    ) -> Optional[List[Station]]:
        """
        Apply a constraint based on a guess and its attribute matches.

        Args:
            guess_name: Name of the guessed station
            district_match: 2 (every), 1 (some), or 0 (none)
            line_match: 2 (every), 1 (some), or 0 (none)
            year_match: -1, 0, or 1

        Returns:
            List of stations that match all constraints, or None if guess station not found
        """
        # Find the guess station
        guess_station = self.game_core.get_station_by_name(guess_name)
        if not guess_station:
            return None

        # Convert numeric input to text format for game core
        district_text = self._convert_numeric_to_text(district_match)
        line_text = self._convert_numeric_to_text(line_match)

        # Create the target difference pattern
        target_diff: GuessAttributeDifference = {
            "district": district_text,
            "line": line_text,
            "year": year_match,
        }

        # Filter stations that match this constraint
        matching_stations = self.game_core._filter_stations_by_criteria(
            self.possible_stations, guess_station, target_diff
        )

        # Update possible stations and history
        self.possible_stations = matching_stations
        self.guess_history.append(
            {
                "guess": guess_name,
                "district": district_match,
                "line": line_match,
                "year": year_match,
                "remaining_count": len(matching_stations),
            }
        )

        return matching_stations

    def get_station_summary(self, station: Station) -> str:
        """Get a summary string for a station."""
        lines_str = ", ".join(station["line"])
        districts_str = ", ".join(station["district"])
        return f"{station['name']} ({lines_str} | {districts_str} | {station['year']})"

    def print_results(self, stations: List[Station]) -> None:
        """Print the results in a formatted way."""
        if not stations:
            print("❌ No stations match the given constraints.")
            return

        print(f"✅ Found {len(stations)} matching station(s):")

        # If more than 20 stations, randomly sample 20
        if len(stations) > 20:
            import random

            sampled_stations = random.sample(stations, 20)
            print("🎲 Sampling from station list (showing 20 random stations):")
            stations_to_display = sampled_stations
        else:
            stations_to_display = stations

        print("----------------------------------------")
        for i, station in enumerate(stations_to_display, 1):
            print(f"{i:2}. {self.get_station_summary(station)}")
        print("----------------------------------------")

    def print_guess_history(self) -> None:
        """Print the history of guesses and constraints."""

        print("📊 Guess History:")
        print("----------------------------------------")
        for i, guess in enumerate(self.guess_history, 1):
            # Convert back to readable format for display
            district_display = f"{guess['district']} ({self._convert_numeric_to_text(guess['district'])})"
            line_display = (
                f"{guess['line']} ({self._convert_numeric_to_text(guess['line'])})"
            )
            print(
                f"{i}. {guess['guess']} -> "
                f"District: {district_display}, "
                f"Line: {line_display}, "
                f"Year: {guess['year']} "
                f"({guess['remaining_count']} remaining)"
            )
        print("----------------------------------------")

    def parse_input_line(self, line: str) -> Optional[tuple]:
        """
        Parse an input line into station name and constraints.

        Returns:
            Tuple of (station_name, district_match, line_match, year_match) or None if invalid
        """
        parts = line.strip().split()
        if len(parts) != 4:
            return None

        station_name, district_match_str, line_match_str, year_match_str = parts

        # Validate and convert district and line match values
        try:
            district_match = int(district_match_str)
            if district_match not in [0, 1, 2]:
                return None
        except ValueError:
            return None

        try:
            line_match = int(line_match_str)
            if line_match not in [0, 1, 2]:
                return None
        except ValueError:
            return None

        # Validate and convert year match
        try:
            year_match = int(year_match_str)
            if year_match not in [-1, 0, 1]:
                return None
        except ValueError:
            return None

        return station_name, district_match, line_match, year_match

    def print_help(self) -> None:
        """Print help information."""
        print("\nInput format:")
        print("  <station_name> <district_match> <line_match> <year_match>")
        print("\nMatch values:")
        print("  district_match: 2 (every), 1 (some), 0 (none)")
        print("  line_match: 2 (every), 1 (some), 0 (none)")
        print(
            "  year_match: -1 (target < guess), 0 (target = guess), 1 (target > guess)"
        )
        print("\nExample inputs:")
        print("  航头 2 2 0")
        print("  徐家汇 1 0 1")
        print("  人民广场 0 1 -1")

    def solve_interactive(self) -> None:
        """Start an interactive solving session."""
        print("🚇 Shanghai Metro Guess Game Solver")
        print()
        print("Enter station name and constraint matches.")
        print()
        print(f"Total stations: {len(self.game_core.stations)}")

        while True:
            print()
            print("========================================")
            print(f"📋 Current possible stations: {len(self.possible_stations)}")

            user_input = input(
                "\nEnter your input (or 'quit' to exit, 'reset' for new round, 'help' for input format): "
            ).strip()

            if user_input.lower() == "quit":
                print("👋 Goodbye!")
                break
            elif user_input.lower() == "help":
                self.print_help()
                continue
            elif user_input.lower() == "reset":
                self.reset_solver()
                print("\n🔄 Solver reset. Starting fresh with all stations.")
                continue

            parsed = self.parse_input_line(user_input)
            if not parsed:
                print("❌ Invalid input format. Type 'help' for usage information.")
                continue

            station_name, district_match, line_match, year_match = parsed

            # Apply constraint
            result = self.apply_constraint(
                station_name, district_match, line_match, year_match
            )

            if result is None:
                print(f"❌ Station '{station_name}' not found.")
                continue

            # If only one station remains, we might have found the answer
            if len(result) == 1:
                print(f"🎉 Only one station remains: {result[0]['name']}")
                print("This might be your target station!")
            elif len(result) == 0:
                print(
                    "💡 No stations match all constraints. You may have made an error."
                )
                print("Type 'reset' to start over.")

            print()
            self.print_guess_history()
            print()
            self.print_results(self.possible_stations)


def main():
    """Main function to start the interactive solver."""
    solver = MetroGameSolver()
    solver.solve_interactive()


if __name__ == "__main__":
    main()
