"""
Tests for metro_game_core.py module
Tests MetroGameCore class functionality and data integrity
"""


class TestMetroGameCore:
    """Test cases for MetroGameCore class."""

    def test_core_initialization(self, game_core):
        """Test that the core initializes correctly."""
        assert len(game_core.stations) > 0
        assert len(game_core.stations_by_name) == len(game_core.stations)
        assert len(game_core.stations_by_id) == len(game_core.stations)
        assert len(game_core.line_stations) > 0

    def test_data_integrity(self, game_core):
        """Test that loaded data has proper structure."""
        for station in game_core.stations[:3]:  # Test first 3 stations
            assert "id" in station
            assert "name" in station
            assert "line" in station
            assert "nearStation" in station
            assert "district" in station
            assert "year" in station

            assert isinstance(station["id"], int)
            assert isinstance(station["name"], str)
            assert isinstance(station["line"], list)
            assert isinstance(station["nearStation"], list)
            assert isinstance(station["district"], str)
            assert isinstance(station["year"], int)

    def test_station_lookup_by_name(self, game_core):
        """Test station lookup by name."""
        found_station = game_core.get_station_by_name("人民广场")
        assert found_station["id"] == 2180
        assert found_station["name"] == "人民广场"
        assert found_station["line"] == ["8号线", "1号线", "2号线"]
        assert found_station["district"] == "黄浦区"
        assert found_station["nearStation"] == [2489, 1985, 2248, 2351, 2384, 2322]
        assert found_station["year"] == 1995

        assert game_core.get_station_by_name("国权路")["name"] == "国权路"
        assert game_core.get_station_by_name("武宁路")["name"] == "武宁路"

        assert game_core.get_station_by_name("Non-existent Station") is None

    def test_station_lookup_by_id(self, game_core):
        """Test station lookup by ID."""
        found_station = game_core.get_station_by_id(2180)
        assert found_station["id"] == 2180
        assert found_station["name"] == "人民广场"
        assert found_station["line"] == ["8号线", "1号线", "2号线"]
        assert found_station["district"] == "黄浦区"
        assert found_station["nearStation"] == [2489, 1985, 2248, 2351, 2384, 2322]
        assert found_station["year"] == 1995

        assert game_core.get_station_by_id(2130)["name"] == "外高桥保税区北"
        assert game_core.get_station_by_id(2255)["name"] == "虹桥路"

        assert game_core.get_station_by_id(-1) is None

    def test_line_stations_lookup(self, game_core):
        """Test getting stations on a line."""
        line_stations = game_core.get_line_stations("1号线")
        assert "人民广场" in [station["name"] for station in line_stations]
        assert "中山公园" not in [station["name"] for station in line_stations]

        assert game_core.get_line_stations("Non-existent Line") == []

    def test_line_stations_consistency(self, game_core):
        """Test that line-station mappings are consistent."""
        for line_name, stations in list(game_core.line_stations.items()):
            for station in stations:
                assert line_name in station["line"]

    def test_adjacent_stations_exist(self, game_core):
        """Test that adjacent stations exist in the dataset."""
        for test_station in game_core.stations:
            for near_id in test_station["nearStation"]:
                near_station = game_core.get_station_by_id(near_id)
                assert near_station is not None

    def test_random_station(self, game_core):
        """Test getting a random station."""
        random_station = game_core.get_random_station()
        assert random_station in game_core.stations

    def test_min_stations_calculation(self, game_core):
        """Test minimum stations calculation."""
        station1 = game_core.get_station_by_name("漕盈路")
        station2 = game_core.get_station_by_name("南大路")
        station3 = game_core.get_station_by_name("南浦大桥")
        station4 = game_core.get_station_by_name("龙阳路")
        station5 = game_core.get_station_by_name("虹口足球场")
        station6 = game_core.get_station_by_name("徐家汇")

        assert game_core.get_min_stations(station1, station1) == 0
        assert game_core.get_min_stations(station1, station2) == 23
        assert game_core.get_min_stations(station1, station3) == 23
        assert game_core.get_min_stations(station1, station4) == 17
        assert game_core.get_min_stations(station1, station5) == 23
        assert game_core.get_min_stations(station1, station6) == 18

        station7 = game_core.get_station_by_name("航头")
        station8 = game_core.get_station_by_name("下沙")

        assert game_core.get_min_stations(station7, station7) == 0
        assert game_core.get_min_stations(station7, station8) == 1

        station9 = game_core.get_station_by_name("浦东南路（2号线）")
        station10 = game_core.get_station_by_name("浦东南路（14号线）")

        assert game_core.get_min_stations(station9, station10) == 2

    def test_min_transfer_calculation(self, game_core):
        """Test minimum transfer calculation."""
        station1 = game_core.get_station_by_name("漕盈路")
        station2 = game_core.get_station_by_name("南大路")
        station3 = game_core.get_station_by_name("南浦大桥")
        station4 = game_core.get_station_by_name("龙阳路")
        station5 = game_core.get_station_by_name("虹口足球场")
        station6 = game_core.get_station_by_name("徐家汇")

        assert game_core.get_min_transfer(station1, station1) == 0
        assert game_core.get_min_transfer(station1, station2) == 2
        assert game_core.get_min_transfer(station1, station3) == 2
        assert game_core.get_min_transfer(station1, station4) == 1
        assert game_core.get_min_transfer(station1, station5) == 2
        assert game_core.get_min_transfer(station1, station6) == 2

        station7 = game_core.get_station_by_name("航头")
        station8 = game_core.get_station_by_name("下沙")

        assert game_core.get_min_transfer(station7, station7) == 0
        assert game_core.get_min_transfer(station7, station8) == 0

        station9 = game_core.get_station_by_name("浦东南路（2号线）")
        station10 = game_core.get_station_by_name("浦东南路（14号线）")

        assert game_core.get_min_transfer(station9, station10) == 1

        station11 = game_core.get_station_by_name("上海赛车场")
        station12 = game_core.get_station_by_name("白银路")

        assert game_core.get_min_transfer(station11, station12) == 0

    def test_attribute_difference(self, game_core):
        """Test attribute difference calculation."""
        station1 = game_core.get_station_by_name("航头")
        station2 = game_core.get_station_by_name("下沙")

        diff1 = game_core.get_attribute_difference(station1, station1)
        assert diff1["district"] == True
        assert diff1["line"] == "every"
        assert diff1["year"] == 0
        diff2 = game_core.get_attribute_difference(station1, station2)
        assert diff2["district"] == True
        assert diff2["line"] == "every"
        assert diff2["year"] == 0

        station3 = game_core.get_station_by_name("浦东南路（2号线）")
        station4 = game_core.get_station_by_name("浦东南路（14号线）")
        diff3 = game_core.get_attribute_difference(station3, station4)
        assert diff3["district"] == True
        assert diff3["line"] == "none"
        assert diff3["year"] == -1

        station5 = game_core.get_station_by_name("丹阳路")
        diff4 = game_core.get_attribute_difference(station2, station5)
        assert diff4["district"] == False
        assert diff4["line"] == "every"
        assert diff4["year"] == -1

        station7 = game_core.get_station_by_name("龙华中路")
        station8 = game_core.get_station_by_name("龙阳路")
        diff5 = game_core.get_attribute_difference(station7, station8)
        assert diff5["district"] == False
        assert diff5["line"] == "some"
        assert diff5["year"] == 1

    def test_filter_stations_by_criteria(self, game_core):
        """Test station filtering by criteria."""
        station1 = game_core.get_station_by_name("航头")
        station2 = game_core.get_station_by_name("下沙")
        diff = game_core.get_attribute_difference(station1, station2)

        filtered = game_core._filter_stations_by_criteria(
            game_core.stations.copy(), station1, diff
        )
        filtered_names = [a["name"] for a in filtered]
        assert (
            len(filtered) == 8
        )  # There is a data annotation error for "迎春路". Once data source is fixed, change this to 7.
        assert "航头" in filtered_names
        assert "下沙" in filtered_names
        assert "鹤涛路" in filtered_names
        assert "沈梅路" in filtered_names
        assert "繁荣路" in filtered_names
        assert "周浦" in filtered_names
        assert "康桥" in filtered_names

    def test_filter_consistency(self, game_core):
        """Test that filtering produces consistent results."""
        station1 = game_core.stations[0]
        station2 = game_core.stations[1]
        all_stations = game_core.stations[:10]  # Test with first 10 stations

        diff = game_core.get_attribute_difference(station1, station2)
        filtered = game_core._filter_stations_by_criteria(all_stations, station2, diff)

        # All filtered stations should have the same attribute difference from station2
        for station in filtered:
            station_diff = game_core.get_attribute_difference(station, station2)
            assert station_diff == diff

    def test_guess_result_correct_guess(self, game_core):
        """Test guess result when guess is correct."""
        target1 = game_core.get_station_by_name("五角场")
        guess1 = target1
        remaining_station1 = game_core.get_station_by_name("江湾体育场")
        remaining_station2 = game_core.get_station_by_name("洲海路")
        remaining1 = [target1, remaining_station1, remaining_station2]

        result1 = game_core.get_guess_result(target1, guess1, remaining1)
        assert result1["correct"] is True
        assert result1["stationInfo"] == target1
        assert result1["minStations"] == 0
        assert result1["minTransfer"] == 0
        assert result1["remain"] == [target1, remaining_station1]
        assert result1["district"] is True
        assert result1["line"] == "every"
        assert result1["year"] == 0

        target2 = game_core.get_station_by_name("白银路")
        guess2 = game_core.get_station_by_name("天潼路")
        remaining2 = game_core.stations.copy()

        result2 = game_core.get_guess_result(target2, guess2, remaining2)
        assert result2["correct"] is False
        assert result2["stationInfo"] == guess2
        assert result2["minStations"] == 18
        assert result2["minTransfer"] == 1
        assert len(result2["remain"]) == 177
        assert result2["district"] is False
        assert result2["line"] == "none"
        assert result2["year"] == -1
