"""
To run these tests, place your api key below, as well as a Steam ID to test.

For the user tests to work, make sure to use a Steam ID with a PUBLIC profile,
that also has public TF2 and Dota 2 inventories. If you don't have one to test with,
just disable those tests.

TODO - These are really basic tests that just make sure all of the methods 
are executing without errors. Would probably be good to do some tests that verify
the of info being returned.

"""

from GameItems import GameItems
from Users import SteamUser
from SteamGames import Games 
import unittest

test_steam_id = # Enter a steam ID to test here
api_key = # Enter api key here

class SteamAPITests(unittest.TestCase):

    def setUp(self):
        self.games = Games()
        self.user = SteamUser(test_steam_id, api_key)
        self.items = GameItems(api_key)

    def tearDown(self):
        pass

    def test_get_all_games(self):
        games_list = self.games.get_all('US')
        for i in range(3):
            games_list.next()

    def test_specific_game(self):
        appids = [65710, 66001, 66000]
        self.games.get_info_for(appids, 'US')

    def test_game_ids_names(self):
        assert self.games.get_id('Team Fortress 2') == 440
        assert self.games.get_name(440) == 'Team Fortress 2'

    def test_user_games(self):
        self.user.get_games()
        self.user.get_game_appids()

    def test_user_items(self):
        self.user.get_items('tf2')
        self.user.get_items('dota2')
        self.user.get_items('tf2', raw_json=True)
        self.user.get_items('dota2', raw_json=True)

    def test_user_gifts(self):
        self.user.get_gifts()

    def test_user_wishlists(self):
        self.user.get_wishlist()

    def test_user_groups(self):
        self.user.get_groups()

    def test_tf2_items(self):
        self.items.get_all('tf2')
        self.items.get_all('tf2', raw_json=True)

    def test_dota2_items(self):
        self.items.get_all('dota2')
        self.items.get_all('dota2', raw_json=True)


if __name__ == '__main__':
    unittest.main()