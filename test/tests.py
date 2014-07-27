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

    def test_get_json_no_params(self, 'http://test_url.com'):
        pass

    def test_get_json_with_params(self, 'http://test_url.com'):
        pass

    def test_open_url(self, 'http://test_url.com'):
        pass

    def test_retry(self, 'http://test_url.com'):
        pass

    def test_date(self, '2014-07-26 20:20:20'):
        pass

class GamesTests(unittest.TestCase):
    def setUp(self):
        pass

class UsersTests(unittest.TestCase):
    def setUp(self):
        self.games = Games()

if __name__ == '__main__':
    unittest.main()
