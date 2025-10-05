"""
Test the core game logic using pytest
"""


class TestMetroGameCoreDetailed:
    """Detailed test cases for MetroGameCore functionality."""
    
    def test_data_integrity(self, game_core):
        """Test that loaded data has proper structure."""
        for station in game_core.stations[:3]:  # Test first 3 stations
            assert 'id' in station
            assert 'name' in station
            assert 'line' in station
            assert 'nearStation' in station
            assert 'district' in station
            assert 'year' in station
            
            assert isinstance(station['id'], int)
            assert isinstance(station['name'], str)
            assert isinstance(station['line'], list)
            assert isinstance(station['nearStation'], list)
            assert isinstance(station['district'], str)
            assert isinstance(station['year'], int)
    
    def test_line_stations_consistency(self, game_core):
        """Test that line-station mappings are consistent."""
        for line_name, stations in list(game_core.line_stations.items())[:3]:  # Test first 3 lines
            for station in stations:
                assert line_name in station['line']
    
    def test_adjacent_stations_exist(self, game_core):
        """Test that adjacent stations exist in the dataset."""
        test_station = game_core.stations[0]
        for near_id in test_station['nearStation']:
            near_station = game_core.get_station_by_id(near_id)
            assert near_station is not None, f"Adjacent station {near_id} not found"
    
    def test_min_stations_edge_cases(self, game_core):
        """Test edge cases for minimum stations calculation."""
        station1 = game_core.stations[0]
        station2 = game_core.stations[1]
        
        # Same station
        assert game_core.get_min_stations(station1, station1) == 0
        
        # Adjacent stations should have distance 1
        if station2['id'] in station1['nearStation']:
            assert game_core.get_min_stations(station1, station2) == 1
    
    def test_min_transfer_same_line(self, game_core):
        """Test minimum transfer for stations on the same line."""
        # Find two stations on the same line
        first_line = list(game_core.line_stations.keys())[0]
        line_stations = game_core.get_line_stations(first_line)
        
        if len(line_stations) >= 2:
            station1, station2 = line_stations[0], line_stations[1]
            transfers = game_core.get_min_transfer(station1, station2)
            assert transfers == 0, "Stations on same line should require 0 transfers"
    
    def test_attribute_difference_same_station(self, game_core):
        """Test attribute difference for the same station."""
        station = game_core.stations[0]
        diff = game_core.get_attribute_difference(station, station)
        
        assert diff['district'] is True
        assert diff['line'] == 'every'
        assert diff['year'] == 0
    
    def test_guess_result_correct_guess(self, game_core):
        """Test guess result when guess is correct."""
        target = game_core.stations[0]
        remaining = [target, game_core.stations[1], game_core.stations[2]]
        
        result = game_core.get_guess_result(target, target, remaining)
        
        assert result['correct'] is True
        assert result['stationInfo'] == target
        assert result['minStations'] == 0
        assert result['minTransfer'] == 0
        assert result['district'] is True
        assert result['line'] == 'every'
        assert result['year'] == 0
    
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