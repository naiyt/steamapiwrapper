from steamapiwrapper.GameItems import GameItems
from steamapiwrapper.Users import SteamUser
from steamapiwrapper.SteamGames import Games 
from steamapiwrapper import SteamBase
import unittest

class GameItemsTests(unittest.TestCase):
    def setUp(self):
        pass

class SteamBaseTests(unittest.TestCase):
    def setUp(self):
        self.api = SteamBase.SteamAPI('steamid', 'apikey')

    def test_get_json_no_params(self):
        pass

    def test_get_json_with_params(self):
        pass

    def test_open_url(self):
        pass

    def test_retry(self):
        pass

    def test_date(sel):
        date = '2014-07-26 20:20:20'

class GamesTests(unittest.TestCase):
    def setUp(self):
        pass

class UsersTests(unittest.TestCase):
    def setUp(self):
        self.games = Games()

if __name__ == '__main__':
    unittest.main()
