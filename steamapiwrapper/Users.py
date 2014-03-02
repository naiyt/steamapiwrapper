"""
Retrieves information about Steam users from the Steam API.

"""

import json
import re
from SteamBase import SteamAPI
from bs4 import BeautifulSoup


class ProfileError(Exception):
    """Raised if you call a method on a private profile that requires a publice one"""
    pass

class BackpackError(Exception):
    """Raised if you get a bad status for a backpack"""
    pass

class BadGameException(Exception):
    """Raised when the game passed in is not TF2 or Dota2 (or in a bad format)"""
    pass

class SteamUser(SteamAPI):
    """ 
    When a SteamUser object is instantiated, a Steam API call is automatically made
    to retrieve their Steam info.

    Prereq: You need their SteamID and a Steam Web API key.

    Usage:
        my_user = SteamUser(steamid, api_key)
        my_user.avatar # returns a link to their avatar image

    """

    def __init__(self, steam_id, api_key):
        """Sets SteamID and API key, as well as retrieving this user's info"""
        SteamAPI.__init__(self, steam_id, api_key)
        self._get_user_info()
        self.games_dict = None


    def _get_user_info(self):
        "Called during __init__ to retrieve basic user info"

        url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}".format(self.api_key, self.steam_id)
        json_data = self._get_json(url)
        self.raw_json = json_data
        self.visible = False
        if len(json_data['response']['players']) == 0:
            raise ProfileError('Error loading profile')
        else:
            if json_data['response']['players'][0]['communityvisibilitystate'] == 3:
                self.visible = True
            self.timecreated = None
            if self.visible:
                self.timecreated = self._date(json_data['response']['players'][0]['timecreated'])
            self.username = json_data['response']['players'][0]['personaname']
            self.profileurl = json_data["response"]["players"][0]["profileurl"]
            self.avatar = json_data['response']['players'][0]['avatarfull']            


    def get_games(self):
        """Returns a list of dictionaries containing information about the games a user owns."""
        if self.visible:
            url =  'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json&include_played_free_games=1&include_appinfo=1'.format(
                self.api_key, self.steam_id)
            json_data = self._get_json(url)
            self.games_dict = json_data['response']['games']
            return self.games_dict
        else:
            raise ProfileError('Private profile. Cannot retrieve games.')
        
        
    def get_items(self, game, raw_json=False):
        """
        Return a dictionary of the user's TF2 or Dota2 items.
    
        args:
            game -- either 'dota2' or 'tf2'
            raw_json -- pass in True if you want the full json object from Steam, and not the dict constructed
                         here

        Returns the following: status, num_backpack_slots, id, original_id, defindex,
        level, quantity, original_id, tradable, craftable, quality, custom_name,
        custom_description, style

        See here for more info on these variables:
        http://wiki.teamfortress.com/wiki/WebAPI/GetPlayerItems
    
        """

        game_id = None
        game = game.lower()
        if game == 'tf2':
            game_id = "440"
        elif game == 'dota2':
            game_id = "570"
        else:
            raise BadGameException("Invalid game. Please call with 'Dota2' or 'TF2'")

        url = "http://api.steampowered.com/IEconItems_{}/GetPlayerItems/v0001/?key={}&SteamID={}".format(game_id, self.api_key, self.steam_id)
        json_data = self._get_json(url)

        status = json_data["result"]["status"]    # Status codes are 1, 8, 15, 18

        if status == 8 or status == 18:
            raise BackpackError("Invalid SteamID")
        elif status == 15:
            raise BackpackError("Backpack is private")

        all_items ={}
        for item in json_data["result"]["items"]:
            values = {}
            values["item_id"] = item.get("id")
            values["original_id"] = item.get("original_id")
            values["level"] = item.get("level")
            values["quality"] = item.get("quality")
            values["quantity"] = item.get("quantity")
            values["custom_name"] = item.get("custom_name")
            values["custom_desc"] = item.get("custom_desc")
            values["style"] = item.get("style")
            defindex = item.get("defindex")
            # Optional Elements
            if item.get("flag_cannot_trade") is None:  
                values["tradable"] = True
            else:
                values["tradable"] = False
            if item.get("flag_cannot_craft") is None:
                values["craftable"] = True
            else:
                values["craftable"] = False
            all_items[defindex] = values

        if raw_json:
            return json_data['result']['items']

        return all_items

    @staticmethod
    def get_steam_id(fed_identity):
        """
        Retrieves a Steam ID given a Fed fed_identity
        from OpenID. http://steamcommunity.com/dev for OpenID info

        """
        ID_RE = r"http://steamcommunity.com/openid/id/[0-9]+"
        NUM = r"[0-9]+"
        if not re.match(ID_RE,fed_identity):
            raise ProfileError("Invalid Identity")
        else:
            return re.findall(NUM, fed_identity)[0]

    def get_gifts(self):
        """Scrape for all of user's current gifts (no API call for this currently) - returns their appid"""
        url = "http://steamcommunity.com/profiles/{}/inventory/json/753/1/".format(self.steam_id)
        json_data = self._get_json(url)
        gifts_list = []
        if 'rgDescriptions' in json_data:
            for item in json_data['rgDescriptions']:
                link = json_data['rgDescriptions'][item]['actions'][0]['link']
                search = re.search(r'([0-9]+)', link)
                if search:
                    gifts_list.append(int(search.group(1)))
            return gifts_list
        else:
            return []

    def get_wishlist(self):
        """Retrieves all appids for games on a user's wishlist (scrapes it, no API call available)."""
        url = "http://steamcommunity.com/profiles/{}/wishlist".format(self.steam_id)
        soup = BeautifulSoup(self._open_url(url))
        wish_games = soup.findAll("div", "wishlistRow")
        all_games = []

        for game in wish_games:
            current_id = game['id']
            if current_id:
                search = re.search(r'([0-9]+)', current_id)
                if search:
                    all_games.append(int(search.group(1)))

        return all_games

    def get_groups(self):
        """Scrape for a user's groups. No API call available."""
        url = "http://steamcommunity.com/profiles/{}/groups/".format(self.steam_id)
        soup = BeautifulSoup(self._open_url(url))
        groups = soup.findAll('div', 'groupBlockMedium')
        all_groups = []
        for group in groups:
            group = group.find('a')
            if group:
                group_url = group['href']
                if group_url:                    
                    all_groups.append(group_url)
        return all_groups
