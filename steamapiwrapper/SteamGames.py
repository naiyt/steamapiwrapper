"""
A small API wrapper intended to retrieve all available store information
for either a specific appid, or all appids.

Thanks for this SteamDB.info blog post for the idea on the best way to do this:
http://steamdb.info/blog/5/

"""

import urllib
import json
from SteamBase import SteamAPI


class Games(SteamAPI):
    """
    Retrieve either all Game objects, or specific ones given a list of appids.

    Example:
    games = Games()
    all_games = games.get_all('US') # Get a generator with all game info

    # Get a generator for just the appids you specify
    some_games = games.get_appids_info([123,1245])

    """

    def __init__(self,num=None):
        """
        args:
        num -- number of games to query per call. The default 150 should work in most cases.

        """
        self.num = 25 if num is None else num
        self.appids_to_names, self.names_to_appids = None, None

    def _create_url(self, appids, cc):
        """Given a list of appids, creates an API url to retrieve them"""
        appids = ','.join([str(x) for x in appids])
        data = {'appids': appids, 'cc': cc, 'l': 'english', 'v': '1'}
        return "http://store.steampowered.com/api/appdetails/?{}".format(urllib.urlencode(data))

    def _get_urls(self, appids, cc):
        """Returns urls for all of appids"""
        list_of_ids = list(self._chunks(appids,self.num))
        return [self._create_url(x, cc) for x in list_of_ids]

    def get_all(self, cc):
        """
        Gets all games currently in the Steam store (as a generator)

        args:
        cc -- Country Code

        """
        if self.appids_to_names is None or self.names_to_appids is None:
            self.appids_to_names, self.names_to_appids = self.get_ids_and_names()
        urls = self._get_urls(self.appids_to_names.keys(), cc)
        for url in urls:
            for game in self._get_games_from(url):
                yield game

    def _get_games_from(self, url):
        """Generator to create the actual game objects"""
        page = json.loads(self._open_url(url).read())
        for appid in page:
            game = Game(page[appid], appid)
            if game.success:
                yield game

    def get_info_for(self, appids, cc):
        """Given a list of appids, returns their Game objects"""
        urls = self._get_urls(appids, cc)
        for url in urls:
            for game in self._get_games_from(url):
                yield game

    def get_ids_and_names(self):
        """
        Returns two dicts: one mapping appid->game name, and one game name->appid
        TODO: Refactor the code so we don't need to seperate dicts

        """
        url = self._open_url("http://api.steampowered.com/ISteamApps/GetAppList/v2")
        url_info = json.loads(url.read())
        all_ids = {}
        all_names = {}
        for app in url_info['applist']['apps']:
            all_ids[app['appid']] = app['name']
            all_names[app['name']] = app['appid']
        return all_ids, all_names

    def get_id(self, game_name):
        """Given an appid, returns the game name"""
        if self.appids_to_names is None or self.names_to_appids is None:
            self.appids_to_names, self.names_to_appids = self.get_ids_and_names()
        if game_name in self.names_to_appids:
            return self.names_to_appids[game_name]

    def get_name(self, appid):
        """Given a game name returns its appid"""
        if self.appids_to_names is None or self.names_to_appids is None:
            self.appids_to_names, self.names_to_appids = self.get_ids_and_names()
        if appid in self.appids_to_names:
            return self.appids_to_names[appid]

    def _chunks(self, params, number):
        """Breaks a list into a set of equally sized chunked lists, with remaining entries in last list"""
        for i in xrange(0, len(params), number):
            yield params[i:i+number]


class Game(SteamAPI):
    """
    The actual Game() object -- really this is just a wrapper around the base
    json response from Steam, that makes it a bit easier to sift through the data.

    """

    def __init__(self, game_json, appid):
        """
        This sets member variables for the various values
        that the game object should have. Not all of these exist on all
        appids, so there's some defaults whenever there is a key error.

        TODO: This is so awful. Rewrite this whole ugly method into
        smaller ones.

        """

        self.appid = appid
        if 'success' in game_json:
            self.success = game_json['success']
            if self.success:
                self.store_url = self._store_url(self.appid)
                data = game_json['data']
                self.raw_json = data
                self.type = data['type']
                self.descriptidataon = data['detailed_description']

                # Some appids don't have names
                try:
                    self.name = data['name']
                except KeyError:
                    self.name = "No Name"

                try:
                    self.supported_languages = data['supported_languages']
                except KeyError:
                    self.supported_languages = None

                self.header_image = "http://cdn.steampowered.com/v/gfx/apps/{}/capsule_184x69.jpg".format(self.appid)
                self.website = data['website']

                # If any of these don't exit all of them don't exist,
                # which is why I think it's okay to wrap them all in one try/except.
                try:
                    self.currency = data['price_overview']['currency']
                    self.price = self._calc_price(data['price_overview']['initial'])
                    self.discounted_price = self._calc_price(data['price_overview']['final'])
                    self.discount_percent = data['price_overview']['discount_percent']
                except KeyError:
                    self.currency = None
                    self.price = 0
                    self.discounted_price = 0
                    self.discount_percent = 0

                try:
                    self.packages = data['packages']
                except KeyError:
                    self.packages = None

                self.platforms = data['platforms']

                try:
                    self.categories = data['categories']
                except KeyError:
                    self.categories = None

        else:
            print "Error! Can't read the game info for {}".format(appid)

    def _calc_price(self, amount):
        """Prices from the API are represented by cents -- convert to dollars"""
        return float(amount) / 100.0

    def _store_url(self, appid):
        return "http://store.steampowered.com/app/{}".format(appid)