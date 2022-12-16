"""Testing for static properties (non-exhaustive list)"""

import unittest
from datetime import datetime

import pandas
import requests

from tbj_statsapp import api, info


# Test grabbing news
class TestNewsGrab(unittest.TestCase):
    """Class for testing news grabbers"""

    @classmethod
    def setUpClass(cls):
        """Instantiate session for testing, try to reconnect twice if fail"""
        # Request
        cls.test_session = requests.session()
        adapter = requests.adapters.HTTPAdapter(max_retries=2)
        cls.test_session.mount("https://", adapter)
        cls.test_session.mount("http://", adapter)

    def test_news(self):
        """Test general news, and that only 4 recent articles are grabbed"""
        news = info.get_recent_news(self.test_session)
        # Assert expected articles are grabbed
        self.assertIn("title", news.keys())
        self.assertIn("link", news.keys())
        self.assertIn("author", news.keys())
        self.assertIn("image", news.keys())
        self.assertIn("date", news.keys())
        # Aseert only 4 articles are grabbed
        self.assertEqual(len(news.get("title")), 4)

    def test_team_news(self):
        """Test ability to grab team news, and that only 4 recent articles are
        grabbed"""
        team_news = info.get_recent_news(self.test_session, team="bluejays")
        # Assert expected articles are grabbed
        self.assertIn("title", team_news.keys())
        self.assertIn("link", team_news.keys())
        self.assertIn("author", team_news.keys())
        self.assertIn("image", team_news.keys())
        self.assertIn("date", team_news.keys())
        # Assert that only 4 articles are grabbed
        self.assertEqual(len(team_news.get("title")), 4)


class TestInfoGrab(unittest.TestCase):
    """Class to test team / player grabber"""

    @classmethod
    def setUpClass(cls):
        """Instantiate session for testing, try to reconnect twice if fail"""
        cls.test_session = requests.session()
        adapter = requests.adapters.HTTPAdapter(max_retries=2)
        cls.test_session.mount("https://", adapter)
        cls.test_session.mount("http://", adapter)
        # Team info
        cls.team_id = 141
        cls.team_name = "Toronto Blue Jays"
        cls.club_name = "bluejays"
        cls.abbreviation = "TOR"
        cls.division = "AL East"
        cls.venue = "Rogers Centre"
        # Player
        cls.player_id = 665489
        cls.player_name = "Vladimir Guerrero Jr."
        cls.player_category = "hitting"
        cls.bat_side = "R"
        cls.pitch_hand = "R"
        cls.stat_category = "homeRuns"

    def test_team_info(self):
        """Check appropriate team information is grabbed"""
        team_info = info.get_team_info(self.team_id, self.test_session)
        self.assertEqual(team_info.get("team_id"), self.team_id)
        self.assertEqual(team_info.get("name"), self.team_name)
        self.assertEqual(team_info.get("club_name"), self.club_name)
        self.assertEqual(team_info.get("abbreviation"), self.abbreviation)
        self.assertEqual(team_info.get("division"), self.division)
        self.assertEqual(team_info.get("venue"), self.venue)

    def test_get_team_roster(self):
        """Check rosters are grabbed and players exist"""
        team_roster = info.get_team_roster(
            self.team_id, datetime.now().year, self.test_session
        )
        # Check if pitchers exist
        self.assertIn("pitchers", team_roster.keys())
        self.assertGreater(len(team_roster.get("pitchers")), 0)
        # Check if hitters exist
        self.assertIn("hitters", team_roster.keys())
        self.assertGreater(len(team_roster.get("hitters")), 0)

    def test_get_player(self):
        """Check get_player"""
        player_info = info.get_player(self.player_id, self.test_session)
        # Check player info
        self.assertEqual(player_info.get("id"), self.player_id)
        self.assertEqual(player_info.get("name"), self.player_name)
        self.assertEqual(player_info.get("bat_side"), self.bat_side)
        self.assertEqual(player_info.get("pitch_hand"), self.pitch_hand)

    def test_get_career_stats(self):
        """Test career stats"""
        # Check career return of the right type
        career_info = info.get_career_stats(
            self.player_id, self.player_category, self.test_session
        )
        self.assertIsInstance(career_info, pandas.core.frame.DataFrame)
        # Check error raised if false category provided
        self.assertRaises(
            ValueError,
            info.get_career_stats,
            self.player_id,
            "abc",
            self.test_session,
        )

    def test_leaders(self):
        """Test leaders for a single category"""
        leaders = info.get_leaders(
            self.stat_category, "hitting", self.test_session
        )
        # Check for correct number of players
        self.assertEqual(len(leaders.get("rank")), 5)
        # Check for categories
        self.assertIn("rank", leaders.keys())
        self.assertIn("value", leaders.keys())
        self.assertIn("position", leaders.keys())
        self.assertIn("first_name", leaders.keys())
        self.assertIn("last_name", leaders.keys())
        self.assertIn("player_id", leaders.keys())
        self.assertIn("player_photo", leaders.keys())


class TestStandingsGrab(unittest.TestCase):
    """Test for grabbing standings"""

    @classmethod
    def setUpClass(cls):
        """Instantiate session for testing, try to reconnect twice if fail"""
        # Request
        cls.test_session = requests.session()
        adapter = requests.adapters.HTTPAdapter(max_retries=2)
        cls.test_session.mount("https://", adapter)
        cls.test_session.mount("http://", adapter)
        # Info
        cls.standing_id = 103
        cls.division_name = "AL East"
        cls.team_ids = [147, 141, 139, 110, 111]
        cls.abbreviations = ["NYY", "TOR", "TB", "BAL", "BOS"]
        cls.team_names = ["yankees", "bluejays", "rays", "orioles", "redsox"]

    def test_standings_api(self):
        """Check to make sure standings are grabbed correctly
        Only check to make sure all 3 divisions are grabbed
        """
        standings = api.get_standings(self.standing_id, self.test_session)
        self.assertEqual(len(standings), 3)

    def test_get_division(self):
        division = info.get_divisions(
            api.get_standings(self.standing_id, self.test_session),
            0,
            self.test_session,
        )
        self.assertEqual(division.get("name"), self.division_name)
        self.assertEqual(division.get("team_ids"), self.team_ids)
        self.assertEqual(division.get("abbreviations"), self.abbreviations)
        self.assertEqual(division.get("team_names"), self.team_names)


if __name__ == "__main__":
    unittest.main()
