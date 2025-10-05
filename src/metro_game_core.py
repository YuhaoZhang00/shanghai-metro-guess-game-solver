import json
import random
from typing import Dict, List, Set, Optional, TypedDict


class Station(TypedDict):
    id: int
    name: str
    line: List[str]
    nearStation: List[int]
    district: str
    year: int


class GuessAttributeDifference(TypedDict):
    district: bool
    line: str  # 'every', 'some', or 'none'
    year: int  # -1, 0, or 1


class GuessResult(TypedDict):
    correct: bool
    stationInfo: Station
    minStations: int
    minTransfer: int
    remain: List[Station]
    district: bool
    line: str
    year: int


class MetroGameCore:
    """Core game logic for Shanghai Metro Guess Game."""

    def __init__(self, stations_file: str = "stations.json"):
        """Initialize the game core with station data from JSON file."""
        with open(stations_file, "r", encoding="utf-8") as f:
            self.stations: List[Station] = json.load(f)

        # Initialize data structures
        self.stations_by_name: Dict[str, Station] = {}
        self.stations_by_id: Dict[int, Station] = {}
        self.line_stations: Dict[str, List[Station]] = {}

        # Build lookup maps
        for station in self.stations:
            self.stations_by_name[station["name"]] = station
            self.stations_by_id[station["id"]] = station

            for line in station["line"]:
                if line not in self.line_stations:
                    self.line_stations[line] = []
                self.line_stations[line].append(station)

    # ========================================
    # PART 1: ACCESSOR METHODS
    # ========================================

    def get_station_by_name(self, name: str) -> Optional[Station]:
        """Get station by name."""
        return self.stations_by_name.get(name)

    def get_station_by_id(self, station_id: int) -> Optional[Station]:
        """Get station by ID."""
        return self.stations_by_id.get(station_id)

    def get_line_stations(self, line_name: str) -> List[Station]:
        """Get all stations on a given line."""
        return self.line_stations.get(line_name, [])

    def get_random_station(self) -> Station:
        """Get a random station from all stations."""
        return random.choice(self.stations)

    # ========================================
    # PART 2: CORE CALCULATION METHODS
    # ========================================

    def get_min_stations(self, target: Station, guess: Station) -> int:
        """Calculate minimum number of stations to travel from guess to target."""
        if target["id"] == guess["id"]:
            return 0

        min_stations = 0
        current_stations = [guess["id"]]
        visited_stations: Set[int] = set()

        while target["id"] not in current_stations:
            min_stations += 1
            previous_stations = current_stations
            current_stations = []

            for station_id in previous_stations:
                if station_id not in visited_stations:
                    visited_stations.add(station_id)
                    station = self.get_station_by_id(station_id)
                    if station:
                        current_stations.extend(
                            [
                                near_id
                                for near_id in station["nearStation"]
                                if near_id not in visited_stations
                            ]
                        )

            if not current_stations:
                return float("inf")

        return min_stations

    def get_min_transfer(self, target: Station, guess: Station) -> int:
        """Calculate minimum number of transfers needed from guess to target."""
        target_lines = set(target["line"])
        guess_lines = set(guess["line"])

        # Check if they share any lines (no transfer needed)
        if target_lines & guess_lines:
            return 0

        min_transfer = 0
        current_lines = guess["line"].copy()
        visited_lines: Set[str] = set()

        while True:
            # Get all stations reachable on current lines
            reachable_stations = []
            for line in current_lines:
                reachable_stations.extend(self.get_line_stations(line))

            # Check if target is reachable
            if target in reachable_stations:
                break

            min_transfer += 1

            # Mark current lines as visited
            for line in current_lines:
                visited_lines.add(line)

            previous_lines = current_lines
            current_lines = []

            # Find new lines accessible through transfers
            for line in previous_lines:
                for station in self.get_line_stations(line):
                    for transfer_line in station["line"]:
                        if transfer_line not in visited_lines:
                            current_lines.append(transfer_line)

            if not current_lines:
                return float("inf")

        return min_transfer

    def get_attribute_difference(
        self, target: Station, guess: Station
    ) -> GuessAttributeDifference:
        """Compare attributes between target and guess stations."""
        target_lines = set(target["line"])
        guess_lines = set(guess["line"])
        intersection = target_lines & guess_lines

        # Determine line overlap
        if intersection == target_lines == guess_lines:
            line_result = "every"
        elif len(intersection) > 0:
            line_result = "some"
        else:
            line_result = "none"

        return {
            "district": guess["district"] == target["district"],
            "line": line_result,
            "year": self._sign(target["year"] - guess["year"]),
        }

    def _sign(self, value: int) -> int:
        """Return the sign of a number (-1, 0, or 1)."""
        if value > 0:
            return 1
        elif value < 0:
            return -1
        else:
            return 0

    # ========================================
    # PART 3: GAME RESULT PROCESSING
    # ========================================

    def _filter_stations_by_criteria(
        self,
        stations: List[Station],
        guess: Station,
        target_diff: GuessAttributeDifference,
    ) -> List[Station]:
        """Filter stations based on attribute differences from a guess (private method)."""
        return [
            station
            for station in stations
            if self.get_attribute_difference(station, guess) == target_diff
        ]

    def get_guess_result(
        self, target: Station, guess: Station, remaining_stations: List[Station]
    ) -> GuessResult:
        """Process a guess and return the complete result with all game information."""
        # Calculate core game metrics
        min_stations = self.get_min_stations(target, guess)
        min_transfer = self.get_min_transfer(target, guess)
        attribute_difference = self.get_attribute_difference(target, guess)

        # Filter remaining stations based on attribute differences
        filtered_remaining = self._filter_stations_by_criteria(
            remaining_stations, guess, attribute_difference
        )

        return {
            "correct": guess == target,
            "stationInfo": guess,
            "minStations": min_stations,
            "minTransfer": min_transfer,
            "remain": filtered_remaining,
            "district": attribute_difference["district"],
            "line": attribute_difference["line"],
            "year": attribute_difference["year"],
        }
