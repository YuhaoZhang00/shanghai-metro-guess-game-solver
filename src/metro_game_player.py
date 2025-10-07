try:
    from .metro_game_core import MetroGameCore, Station
except ImportError:
    from metro_game_core import MetroGameCore, Station
from typing import List
import unicodedata

# hardcoded all possible attribute values for hints
# these values should be updated if stations.json is updated
# by calling __main__ function in metro_game_core.py
all_possible_districts = [
    "嘉定区",
    "奉贤区",
    "宝山区",
    "徐汇区",
    "昆山市",
    "普陀区",
    "普陀区，静安区",
    "杨浦区",
    "松江区",
    "浦东新区",
    "虹口区",
    "长宁区",
    "闵行区",
    "青浦区",
    "静安区",
    "静安区，虹口区",
    "黄浦区",
]
all_possible_lines = [
    "1号线",
    "2号线",
    "3号线",
    "4号线",
    "5号线",
    "6号线",
    "7号线",
    "8号线",
    "9号线",
    "10号线",
    "11号线",
    "12号线",
    "13号线",
    "14号线",
    "15号线",
    "16号线",
    "17号线",
    "18号线",
    "浦江线",
    "磁悬浮",
    "机场联络线",
]
all_possible_years = [
    1993,
    1995,
    1996,
    1999,
    2000,
    2003,
    2004,
    2005,
    2006,
    2007,
    2009,
    2010,
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
    2024,
]


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


def pad_string(text: str, target_width: int) -> str:
    """Pad a string to target display width, accounting for wide characters."""
    current_width = get_display_width(text)
    if current_width >= target_width:
        return text

    padding = target_width - current_width
    return text + " " * padding


class MetroGamePlayer:
    """Interactive game player for Shanghai Metro Guess Game."""

    def __init__(self, stations_file: str = "stations.json"):
        """Initialize the game player."""
        self.game_core = MetroGameCore(stations_file)
        self.target_station: Station = None
        self.remaining_stations: List[Station] = []
        self.guess_count = 0
        # Hint variables to track possible attribute values
        self.possible_districts_guessed: List[str] = []
        self.possible_districts_not_tried: List[str] = []
        self.possible_lines_guessed: List[str] = []
        self.possible_lines_not_tried: List[str] = []
        self.possible_years: List[int] = []
        # Flags to track if we've found the exact answer
        self.districts_exact_match_found: bool = False
        self.lines_exact_match_found: bool = False
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game with a new random target station."""
        self.target_station = self.game_core.get_random_station()
        self.remaining_stations = self.game_core.stations.copy()
        self.guess_count = 0
        # Reset hint variables to all possible values
        self.possible_districts_guessed = []
        self.possible_districts_not_tried = all_possible_districts.copy()
        self.possible_lines_guessed = []
        self.possible_lines_not_tried = all_possible_lines.copy()
        self.possible_years = all_possible_years.copy()
        # Reset exact match flags
        self.districts_exact_match_found = False
        self.lines_exact_match_found = False

    # def set_target(self, station_name: str) -> bool:
    #     """Set a specific station as the target."""
    #     station = self.game_core.get_station_by_name(station_name)
    #     if station:
    #         self.target_station = station
    #         self.remaining_stations = self.game_core.stations.copy()
    #         self.guess_count = 0
    #         return True
    #     return False

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

        # Update hint variables based on the guess result
        self._update_hints(guess_station, result)

        return {"valid_guess": True, "guess_number": self.guess_count, **result}

    def _update_hints(self, guess_station: Station, result: dict) -> None:
        """Update hint variables based on the guess result."""
        if result["district"] == "every":
            # Target has exactly the same districts as the guess
            self.possible_districts_not_tried = []
            self.possible_districts_guessed = guess_station["district"].copy()
            self.districts_exact_match_found = True
        elif result["district"] == "some":
            if not self.districts_exact_match_found:
                # Move guessed districts from not_tried to guessed only if we haven't found exact match
                guess_districts = set(guess_station["district"])
                self.possible_districts_not_tried = [
                    d
                    for d in self.possible_districts_not_tried
                    if d not in guess_districts
                ]
                for district in guess_station["district"]:
                    if district not in self.possible_districts_guessed:
                        self.possible_districts_guessed.append(district)
            # else, if exact match already found, no need to manipulate possible lists
        elif result["district"] == "none":
            # Target shares no districts with the guess
            if not self.districts_exact_match_found:
                guess_districts = set(guess_station["district"])
                self.possible_districts_guessed = [
                    d
                    for d in self.possible_districts_guessed
                    if d not in guess_districts
                ]
                self.possible_districts_not_tried = [
                    d
                    for d in self.possible_districts_not_tried
                    if d not in guess_districts
                ]
            # else, if exact match already found, no need to manipulate possible lists

        # Update possible lines based on line match result
        if result["line"] == "every":
            # Target has exactly the same lines as the guess
            self.possible_lines_not_tried = []
            self.possible_lines_guessed = guess_station["line"].copy()
            self.lines_exact_match_found = True
        elif result["line"] == "some":
            if not self.lines_exact_match_found:
                # Move guessed lines from not_tried to guessed only if we haven't found exact match
                guess_lines = set(guess_station["line"])
                self.possible_lines_not_tried = [
                    l for l in self.possible_lines_not_tried if l not in guess_lines
                ]
                for line in guess_station["line"]:
                    if line not in self.possible_lines_guessed:
                        self.possible_lines_guessed.append(line)
            # else, if exact match already found, no need to manipulate possible lists
        elif result["line"] == "none":
            # Target shares no lines with the guess
            if not self.lines_exact_match_found:
                guess_lines = set(guess_station["line"])
                self.possible_lines_guessed = [
                    l for l in self.possible_lines_guessed if l not in guess_lines
                ]
                self.possible_lines_not_tried = [
                    l for l in self.possible_lines_not_tried if l not in guess_lines
                ]
            # else, if exact match already found, no need to manipulate possible lists

        # Update possible years based on year comparison result
        if result["year"] == 0:
            # Target has the same year as the guess
            self.possible_years = [guess_station["year"]]
        elif result["year"] == 1:
            # Target year is greater than guess year
            self.possible_years = [
                y for y in self.possible_years if y > guess_station["year"]
            ]
        elif result["year"] == -1:
            # Target year is less than guess year
            self.possible_years = [
                y for y in self.possible_years if y < guess_station["year"]
            ]

    # def get_remaining_station_names(self) -> List[str]:
    #     """Get names of all remaining possible stations."""
    #     return [station["name"] for station in self.remaining_stations]

    def print_hints(self) -> None:
        """Print hints showing possible attribute values."""
        print("💡 Hints - Possible attribute values:")
        total_districts = len(self.possible_districts_guessed) + len(
            self.possible_districts_not_tried
        )
        total_lines = len(self.possible_lines_guessed) + len(
            self.possible_lines_not_tried
        )

        # Format districts with guessed ones in brackets
        districts_display = ""
        if self.possible_districts_guessed:
            districts_display += f"[{', '.join(self.possible_districts_guessed)}] "
        districts_display += ", ".join(self.possible_districts_not_tried)
        print(f"📍 Districts ({total_districts}): {districts_display}")

        # Format lines with guessed ones in brackets
        lines_display = ""
        if self.possible_lines_guessed:
            lines_display += f"[{', '.join(self.possible_lines_guessed)}] "
        lines_display += ", ".join(self.possible_lines_not_tried)
        print(f"🚇 Lines ({total_lines}): {lines_display}")

        years_display = (
            f"[{self.possible_years[0]}]"
            if len(self.possible_years) == 1
            else f"{', '.join(map(str, self.possible_years))}"
        )
        print(f"📅 Years ({len(self.possible_years)}): {years_display}")

    def play_interactive(self) -> None:
        """Start an interactive game session."""
        print("🚇 Welcome to Shanghai Metro Guess Game!")
        print(f"Target station set. Try to guess it!")
        print()
        print(f"Total stations: {len(self.game_core.stations)}")
        self.print_hints()
        print()

        while True:
            remaining_count = len(self.remaining_stations)
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
                district_emoji = {"every": "✅", "some": "🟡", "none": "❌"}
                line_emoji = {"every": "✅", "some": "🟡", "none": "❌"}
                if result["year"] == 1:
                    year_emoji = "⬆️"
                elif result["year"] == -1:
                    year_emoji = "⬇️"
                else:
                    year_emoji = "🟰"

                # Properly pad strings for display width
                district_str = ", ".join(station_info["district"])
                district_padded = pad_string(district_str, 15)
                lines_padded = pad_string(lines_str, 38)
                year_padded = pad_string(str(station_info["year"]), 7)
                district_emoji_padded = pad_string(
                    district_emoji[result["district"]], 15
                )
                line_emoji_padded = pad_string(line_emoji[result["line"]], 38)
                year_emoji_padded = pad_string(year_emoji, 8)
                min_stations_padded = pad_string(str(result["minStations"]), 15)
                min_transfer_padded = pad_string(str(result["minTransfer"]), 16)

                # First table: Station attributes and matches
                print(
                    "┌─────────────────┬────────────────────────────────────────┬─────────┐"
                )
                print(
                    "│ 📍 District     │ 🚇 Lines                               │ 📅 Year │"
                )
                print(
                    "├─────────────────┼────────────────────────────────────────┼─────────┤"
                )
                print(f"│ {district_padded} │ {lines_padded} │ {year_padded} │")
                print(
                    "├─────────────────┼────────────────────────────────────────┼─────────┤"
                )
                print(
                    f"│ {district_emoji_padded} │ {line_emoji_padded} │ {year_emoji_padded} │"
                )
                print(
                    "└─────────────────┴────────────────────────────────────────┴─────────┘"
                )

                # Second table: Distance information
                print("┌─────────────────┬──────────────────┐")
                print("│ 🚶 Min stations │ 🔄 Min transfers │")
                print("├─────────────────┼──────────────────┤")
                print(f"│ {min_stations_padded} │ {min_transfer_padded} │")
                print("└─────────────────┴──────────────────┘")

                # Remaining stations count and list
                print(
                    f"🎯 Remaining stations (attributes matching): {len(result['remain'])}"
                )

                if len(result["remain"]) <= 10:
                    remaining_names = [
                        f"{s['name']} ({', '.join(s['line'])} | {', '.join(s['district'])})"
                        for s in result["remain"]
                    ]
                    print(f"   {', '.join(remaining_names)}")

                # Display hints for possible attribute values
                print()
                self.print_hints()


def main():
    """Main function to start the interactive game."""
    player = MetroGamePlayer()
    player.play_interactive()


if __name__ == "__main__":
    main()
