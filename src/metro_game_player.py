try:
    from .metro_game_core import MetroGameCore, Station
except ImportError:
    from metro_game_core import MetroGameCore, Station
from typing import List
import unicodedata


def get_display_width(text: str) -> int:
    """Calculate the display width of a string, accounting for wide characters like Chinese."""
    # Hardcoded emojis used in this file (all counted as width 2)
    emojis_in_file = {
        "🚇",
        "🎉",
        "📊",
        "✅",
        "❌",
        "🟡",
        "⬆️",
        "⬇️",
        "🟰",
        "📍",
        "📅",
        "🚶",
        "🔄",
        "🎯",
        "👋",
    }

    width = 0
    for char in text:
        if char in emojis_in_file:
            width += 2
        # East Asian Wide and Fullwidth characters take 2 columns
        elif unicodedata.east_asian_width(char) in ("F", "W"):
            width += 2
        else:
            width += 1
    return width


def pad_string(text: str, target_width: int, align: str = "left") -> str:
    """Pad a string to target display width, accounting for wide characters."""
    current_width = get_display_width(text)
    if current_width >= target_width:
        return text

    padding = target_width - current_width
    if align == "left":
        return text + " " * padding
    elif align == "right":
        return " " * padding + text
    elif align == "center":
        left_pad = padding // 2
        right_pad = padding - left_pad
        return " " * left_pad + text + " " * right_pad
    return text


class MetroGamePlayer:
    """Interactive game player for Shanghai Metro Guess Game."""

    def __init__(self, stations_file: str = "stations.json"):
        """Initialize the game player."""
        self.game_core = MetroGameCore(stations_file)
        self.target_station: Station = None
        self.remaining_stations: List[Station] = []
        self.guess_count = 0
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game with a new random target station."""
        self.target_station = self.game_core.get_random_station()
        self.remaining_stations = self.game_core.stations.copy()
        self.guess_count = 0

    def set_target(self, station_name: str) -> bool:
        """Set a specific station as the target."""
        station = self.game_core.get_station_by_name(station_name)
        if station:
            self.target_station = station
            self.remaining_stations = self.game_core.stations.copy()
            self.guess_count = 0
            return True
        return False

    def get_target_name(self) -> str:
        """Get the name of the target station."""
        return self.target_station["name"]

    def make_guess(self, guess_name: str) -> dict:
        """Make a guess and return the result."""
        guess_station = self.game_core.get_station_by_name(guess_name)
        if not guess_station:
            return {"error": f"Station '{guess_name}' not found.", "valid_guess": False}

        self.guess_count += 1
        result = self.game_core.get_guess_result(
            self.target_station, guess_station, self.remaining_stations
        )

        # Update remaining stations
        self.remaining_stations = result["remain"]

        return {"valid_guess": True, "guess_number": self.guess_count, **result}

    def get_game_stats(self) -> dict:
        """Get current game statistics."""
        return {
            "target": self.target_station["name"],
            "total_stations": len(self.game_core.stations),
            "remaining_stations": len(self.remaining_stations),
            "guess_count": self.guess_count,
            "game_won": self.guess_count > 0
            and len(self.remaining_stations) == 1
            and self.remaining_stations[0] == self.target_station,
        }

    def get_remaining_station_names(self) -> List[str]:
        """Get names of all remaining possible stations."""
        return [station["name"] for station in self.remaining_stations]

    def play_interactive(self) -> None:
        """Start an interactive game session."""
        print("🚇 Welcome to Shanghai Metro Guess Game!")
        print(f"Target station set. Try to guess it!")
        print(f"Total stations: {len(self.game_core.stations)}")
        print()

        while True:
            remaining_count = len(self.remaining_stations)
            print()
            print("========================================")
            print(f"Remaining possible stations: {remaining_count}")

            guess_name = input(
                "\nEnter your guess (or 'quit' to exit, 'answer' to see answer, 'reset' for new game): "
            ).strip()

            if guess_name.lower() == "quit":
                print("Thanks for playing! 👋")
                break
            elif guess_name.lower() == "answer":
                print(f"The answer is: {self.get_target_name()}")
                continue
            elif guess_name.lower() == "reset":
                self.reset_game()
                print("\n🔄 New game started!")
                print(f"New target set. Total stations: {len(self.game_core.stations)}")
                continue

            result = self.make_guess(guess_name)

            if not result["valid_guess"]:
                print(f"❌ {result['error']}")
                continue

            if result["correct"]:
                print(f"🎉 Correct! You won in {result['guess_number']} guesses!")
                play_again = input("\nPlay again? (y/n): ").strip().lower()
                if play_again == "y":
                    self.reset_game()
                    print("\n🔄 New game started!")
                    print(
                        f"New target set. Total stations: {len(self.game_core.stations)}"
                    )
                else:
                    print("Thanks for playing! 👋")
                    break
            else:
                station_info = result["stationInfo"]
                lines_str = ", ".join(station_info["line"])

                print(f"\n📊 Guess #{result['guess_number']}: {station_info['name']}")

                # Match results
                district_emoji = "✅" if result["district"] else "❌"
                line_emoji = {"every": "✅", "some": "🟡", "none": "❌"}
                if result["year"] == 1:
                    year_emoji = "⬆️"
                elif result["year"] == -1:
                    year_emoji = "⬇️"
                else:
                    year_emoji = "🟰"

                # Properly pad strings for display width
                district_padded = pad_string(station_info["district"], 11)
                lines_padded = pad_string(lines_str, 38)
                year_padded = pad_string(str(station_info["year"]), 7)
                # Pad emoji results
                district_emoji_padded = pad_string(district_emoji, 11)
                line_emoji_padded = pad_string(line_emoji[result["line"]], 38)
                year_emoji_padded = pad_string(year_emoji, 8)
                # Pad distance information
                min_stations_padded = pad_string(str(result["minStations"]), 15)
                min_transfer_padded = pad_string(str(result["minTransfer"]), 16)

                # First table: Station attributes and matches
                print(
                    "┌─────────────┬────────────────────────────────────────┬─────────┐"
                )
                print(
                    "│ 📍 District │ 🚇 Lines                               │ 📅 Year │"
                )
                print(
                    "├─────────────┼────────────────────────────────────────┼─────────┤"
                )
                print(f"│ {district_padded} │ {lines_padded} │ {year_padded} │")
                print(
                    "├─────────────┼────────────────────────────────────────┼─────────┤"
                )
                print(
                    f"│ {district_emoji_padded} │ {line_emoji_padded} │ {year_emoji_padded} │"
                )
                print(
                    "└─────────────┴────────────────────────────────────────┴─────────┘"
                )

                # Second table: Distance information
                print("┌─────────────────┬──────────────────┐")
                print("│ 🚶 Min stations │ 🔄 Min transfers │")
                print("├─────────────────┼──────────────────┤")
                print(f"│ {min_stations_padded} │ {min_transfer_padded} │")
                print("└─────────────────┴──────────────────┘")

                # Remaining stations count and list
                print(f"🎯 Remaining: {len(result['remain'])} stations")

                if len(result["remain"]) <= 10:
                    remaining_names = [s["name"] for s in result["remain"]]
                    print(f"   {', '.join(remaining_names)}")


def main():
    """Main function to start the interactive game."""
    player = MetroGamePlayer()
    player.play_interactive()


if __name__ == "__main__":
    main()
