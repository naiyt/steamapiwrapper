from steamapiwrapper.GameItems import GameItems
from steamapiwrapper.Users import SteamUser
from steamapiwrapper.SteamGames import Games 
from steamapiwrapper import SteamBase
import unittest
import json
from mock import Mock, patch

class MockUrllib2Resp:
    def __init__(self, response):
        self.response = response

    def read(self):
        return self.response

class GameItemsTests(unittest.TestCase):
    def setUp(self):
        pass

class SteamBaseTests(unittest.TestCase):
    def setUp(self):
        self.api = SteamBase.SteamAPI('steamid', 'apikey')
        self.urllib2resp = MockUrllib2Resp('{"name": "nate"}')
        self.url = 'http://steampowered.com'
        self.url_params = 'http://steampowered.com/%s'
        self.params = 'nate'

    @patch.object(SteamBase.SteamAPI, '_open_url')
    def test_get_json_no_params(self, mock_open):
        mock_open.return_value = self.urllib2resp
        self.api._get_json(self.url)
        mock_open.assert_called_with(self.url)

    # @patch.object(SteamBase.SteamAPI, '_open_url')
    # def test_get_json_with_params(self, mock_open):
    #     mock_open.return_value = self.urllib2resp
    #     self.api._get_json(self.url, self.params)
    #     mock_open.assert_called_with(self.url_params % self.params)

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
