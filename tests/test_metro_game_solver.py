"""
Test cases for MetroGameSolver class.
"""

import pytest
from src.metro_game_solver import MetroGameSolver
from src.metro_game_core import Station


class TestMetroGameSolver:
    """Test cases for MetroGameSolver class."""

    @pytest.fixture
    def solver(self):
        """Create a MetroGameSolver instance for testing."""
        return MetroGameSolver()

    def test_solver_initialization(self, solver):
        """Test solver initialization."""
        assert solver.game_core is not None
        assert len(solver.possible_stations) > 0
        assert len(solver.guess_history) == 0
        # Check that all stations are loaded
        original_count = len(solver.game_core.stations)
        assert len(solver.possible_stations) == original_count

    def test_reset_solver(self, solver):
        """Test resetting the solver."""
        # Apply a constraint first
        result = solver.apply_constraint("航头", 2, 2, 0)
        assert result is not None
        assert len(solver.possible_stations) < len(solver.game_core.stations)
        assert len(solver.guess_history) == 1

        # Reset and check
        solver.reset_solver()
        assert len(solver.possible_stations) == len(solver.game_core.stations)
        assert len(solver.guess_history) == 0

    def test_apply_constraint_valid_station(self, solver):
        """Test applying constraint with valid station."""
        initial_count = len(solver.possible_stations)
        result = solver.apply_constraint("航头", 2, 2, 0)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) <= initial_count
        assert len(solver.guess_history) == 1

        # Check that all returned stations match the constraint
        guess_station = solver.game_core.get_station_by_name("航头")
        for station in result:
            diff = solver.game_core.get_attribute_difference(station, guess_station)
            assert diff["district"] == "every"
            assert diff["line"] == "every"
            assert diff["year"] == 0

    def test_apply_constraint_invalid_station(self, solver):
        """Test applying constraint with invalid station."""
        result = solver.apply_constraint("不存在的站", 2, 2, 0)
        assert result is None
        assert len(solver.guess_history) == 0

    def test_apply_multiple_constraints(self, solver):
        """Test applying multiple constraints in sequence."""
        # First constraint
        result1 = solver.apply_constraint("航头", 2, 2, 0)
        assert result1 is not None
        count1 = len(result1)

        # Second constraint that should further filter
        result2 = solver.apply_constraint("徐家汇", 0, 0, 1)
        assert result2 is not None
        count2 = len(result2)

        # Should have fewer or equal stations after second constraint
        assert count2 <= count1
        assert len(solver.guess_history) == 2

    def test_get_station_summary(self, solver):
        """Test station summary formatting."""
        station = solver.game_core.get_station_by_name("航头")
        assert station is not None

        summary = solver.get_station_summary(station)
        assert "航头" in summary
        # Check that the summary contains station information
        assert (
            "(" in summary and ")" in summary
        )  # Format: name (lines | districts | year)
        assert "|" in summary  # Has separators
        assert str(station["year"]) in summary

    def test_constraint_consistency(self, solver):
        """Test that constraints are applied consistently."""
        # Apply constraint for a specific station
        guess_station = solver.game_core.get_station_by_name("人民广场")
        assert guess_station is not None

        result = solver.apply_constraint("人民广场", 1, 0, -1)
        assert result is not None

        # Verify all results match the constraint
        for station in result:
            diff = solver.game_core.get_attribute_difference(station, guess_station)
            assert diff["district"] == "some"
            assert diff["line"] == "none"
            assert diff["year"] == -1

    def test_exact_match_constraint(self, solver):
        """Test constraint that should return the exact same station."""
        result = solver.apply_constraint("航头", 2, 2, 0)
        assert result is not None

        # Should include the guessed station itself
        station_names = [s["name"] for s in result]
        assert "航头" in station_names

    def test_no_match_constraint(self, solver):
        """Test constraint that results in no matches."""
        # Apply a very restrictive constraint that should eliminate most stations
        solver.apply_constraint("航头", 2, 2, 0)

        # Apply another constraint that conflicts
        result = solver.apply_constraint("徐家汇", 1, 0, 1)

        # This specific combination should result in no matches
        assert result is not None
        assert len(result) == 0


class TestParseInputLine:
    """Test cases for parse_input_line method."""

    @pytest.fixture
    def solver(self):
        """Create a MetroGameSolver instance for testing."""
        return MetroGameSolver()

    def test_valid_input(self, solver):
        """Test parsing valid input lines."""
        # Test basic valid input
        result = solver.parse_input_line("航头 2 2 0")
        assert result == ("航头", 2, 2, 0)

        # Test different constraint values
        result = solver.parse_input_line("徐家汇 1 0 -1")
        assert result == ("徐家汇", 1, 0, -1)

        result = solver.parse_input_line("人民广场 0 1 1")
        assert result == ("人民广场", 0, 1, 1)

    def test_invalid_input_format(self, solver):
        """Test parsing invalid input formats."""
        # Too few arguments
        result = solver.parse_input_line("航头 2 2")
        assert result is None

        # Too many arguments
        result = solver.parse_input_line("航头 2 2 0 extra")
        assert result is None

        # Empty input
        result = solver.parse_input_line("")
        assert result is None

        # Single argument
        result = solver.parse_input_line("航头")
        assert result is None

    def test_invalid_constraint_values(self, solver):
        """Test parsing with invalid constraint values."""
        # Invalid district match
        result = solver.parse_input_line("航头 3 2 0")
        assert result is None

        # Invalid line match
        result = solver.parse_input_line("航头 2 -1 0")
        assert result is None

        # Invalid year match
        result = solver.parse_input_line("航头 2 2 2")
        assert result is None

        result = solver.parse_input_line("航头 2 2 -2")
        assert result is None

        result = solver.parse_input_line("航头 2 2 abc")
        assert result is None

        # Non-numeric district/line values
        result = solver.parse_input_line("航头 every 2 0")
        assert result is None

        result = solver.parse_input_line("航头 2 some 0")
        assert result is None

    def test_whitespace_handling(self, solver):
        """Test parsing with extra whitespace."""
        # Extra spaces
        result = solver.parse_input_line("  航头   2   2   0  ")
        assert result == ("航头", 2, 2, 0)

        # Tabs and spaces
        result = solver.parse_input_line("\t航头\t2\t2\t0\t")
        assert result == ("航头", 2, 2, 0)


class TestIntegrationScenarios:
    """Integration test scenarios for realistic game solving."""

    @pytest.fixture
    def solver(self):
        """Create a fresh MetroGameSolver instance for each test."""
        return MetroGameSolver()

    def test_typical_solving_scenario(self, solver):
        """Test a typical game solving scenario."""
        initial_count = len(solver.possible_stations)

        # First guess: narrow down by year and general attributes
        result1 = solver.apply_constraint("人民广场", 1, 1, 0)
        assert result1 is not None
        count1 = len(result1)
        assert count1 < initial_count

        # Second guess: further narrow down
        result2 = solver.apply_constraint("徐家汇", 0, 0, 1)
        assert result2 is not None
        count2 = len(result2)
        assert count2 <= count1

        # Verify history is maintained
        assert len(solver.guess_history) == 2
        assert solver.guess_history[0]["guess"] == "人民广场"
        assert solver.guess_history[1]["guess"] == "徐家汇"

    def test_progressive_filtering(self, solver):
        """Test that each constraint progressively filters the results."""
        counts = []

        # Track station count after each constraint
        counts.append(len(solver.possible_stations))

        solver.apply_constraint("航头", 2, 2, 0)
        counts.append(len(solver.possible_stations))

        solver.apply_constraint("龙阳路", 0, 1, -1)
        counts.append(len(solver.possible_stations))

        # Each step should maintain or reduce the count
        for i in range(1, len(counts)):
            assert counts[i] <= counts[i - 1]

    def test_solver_with_reset(self, solver):
        """Test solver behavior with reset operations."""
        # Apply some constraints
        solver.apply_constraint("航头", 2, 2, 0)
        solver.apply_constraint("徐家汇", 1, 0, 1)

        mid_count = len(solver.possible_stations)
        mid_history = len(solver.guess_history)

        assert mid_count < len(solver.game_core.stations)
        assert mid_history == 2

        # Reset and verify
        solver.reset_solver()
        assert len(solver.possible_stations) == len(solver.game_core.stations)
        assert len(solver.guess_history) == 0

        # Apply new constraints after reset
        result = solver.apply_constraint("龙阳路", 0, 1, 1)
        assert result is not None
        assert len(solver.guess_history) == 1
