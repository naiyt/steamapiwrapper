"""
Retrieves information about Steam users from the Steam API.

"""

import json
import re
from SteamBase import SteamAPI
from bs3.BeautifulSoup import BeautifulSoup


class ProfileError(Exception):
	"""Raised if you call a method on a private profile that requires a publice one"""
	pass

class BackpackError(Exception):
	"""Raised if you get a bad status for a backpack"""
	pass

class BadGameException(Exception):
	"""Raised when the game passed in is not TF2 or Dota2 (or in a bad format)"""
	pass

class SteamUsers(SteamAPI):
	"""	
	Creates a new User object that contains various methods to retrieve info about a
	user. When the object is created, an API call to Steam is automatically made 
	looking for their Steam info. It can then be retrieved with .get_user_info(), or 
	other methods can be called.

	Usage:
		my_user = SteamAPI.User()   #Create user
		my_user.get_user_info()     #Retrieve a dictionary of the user's info

	Many of the methods are dependant on the profile visibilty, which can be
	retrieved with SteamUsers.is_private(steamid)

	"""

	def __init__(self, steam_id, api_key):
		"""Sets SteamID and API key, as well as retrieving this user's info"""
		SteamAPI.__init__(self, steam_id, api_key)
		self.user_info = self._get_user_info()
		if self.good_id:
			self.visibility = self.user_info['profile_visible']
		self.games_dict = {}

	def _get_user_info(self):
		"""
		Called during __init__. Returns a user's profile visibility, time Steam Account
		was created, Steam Username, Profile URL, and avatar URL in a dictionary. 
		Retrieve this info with get_user_info

		"""

		url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}".format(self.api_key, self.steam_id)
		json_data = self._get_json(url)

		# A lot of what we do will depend on the visibility of the profile, so we'll 
		# check this first. 3 means it's public, 2 and 1 essentially mean it's private.
		profile_visibility = False
		if len(json_data['response']['players']) == 0:
			self.good_id = False
		else:
			self.good_id = True
			if json_data['response']['players'][0]['communityvisibilitystate'] == 3:
				profile_visibility = True

			timecreated = None
			if profile_visibility:
				timecreated = self._date(json_data['response']['players'][0]['timecreated'])

			username = json_data['response']['players'][0]['personaname']
			profileurl = json_data["response"]["players"][0]["profileurl"]
			avatar = json_data['response']['players'][0]['avatarfull']

			return {'profile_visible': profile_visibility, 'timecreated': timecreated,
					'username': username, 'profileurl': profileurl, 'avatar': avatar}

	def get_steam(self):
		return self.steam_id

	def get_user_info(self):
		"""The user info was already retrieved, just return it now"""
		return self.user_info

	def get_username(self):
		return self.user_info['username']

	def get_time_created(self):
		return self.user_info['timecreated']

	def get_profileurl(self):
		return self.user_info['profileurl']

	def get_avatar(self):
		return self.user_info['avatar']

	def is_visible(self):
		return self.visibility


	def get_games(self):
		"""
		Currently, Steam offers no API call to get a user's games. However, if the
		profile is public we can snag them from the source of the page. Kind of a
		nasty hack, so hopefully Steam adds an  API call for this. Required BS3 for some
		scraping.

		Returns a dict mapping game_name -> appid

		"""

		# Only run if the profile is visible
		if self.visibility:
			page = self._open_url("http://steamcommunity.com/profiles/{}/games?tab=all".format(self.steam_id)).read()
			json_begin = page.find('rgGames = [')
			json_end = page.find('}];', json_begin + 1)
			games_info = page[json_begin+10:json_end + 2]
			json_data = json.loads(games_info)
			games_dict = {}
			for game in json_data:
				appid = int(game['appid'])
				game_name = game['name']
				if 'hours_forever' in game:
					hours_played = float(game['hours_forever'].replace(',', '')) # Remove commas for numbers over 999
				else:
					hours_played = 0.0
				games_dict[appid] = {'appid': appid, 'game_name': game_name, 'hours': hours_played}
			self.games_dict = games_dict
			return games_dict
		else:
			raise ProfileError('Private profile. Cannot retrieve games.')

	def get_game_appids(self):
		"""Returns just the user's appids"""
		if self.games_dict:
			return self.games_dict.keys()
		else:
			self.get_games()
			return self.games_dict.keys()

	def get_items(self, game):
		"""
		Return a dictionary of the user's TF2 or Dota2 items.
		Pass in either 'Dota2' or 'TF2'

		Returns the following: status, num_backpack_slots, id, original_id, defindex,
		level, quantity, original_id, tradable, craftable, quality, custom_name,
		custom_description, style

		See here for more info on these variables:
		http://wiki.teamfortress.com/wiki/WebAPI/GetPlayerItems

		"""

		game_id = ''
		if game.lower() == 'tf2':
			game_id = "440"
		elif game.lower() == 'dota2':
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
		
		backpack_slots = json_data["result"]["num_backpack_slots"]

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
			# Optional Elements
			if item.get("flag_cannot_trade") is None:  
				values["tradable"] = True
			else:
				values["tradable"] = False
			if item.get("flag_cannot_craft") is None:
				values["craftable"] = True
			else:
				values["craftable"] = False

			defindex = item.get("defindex")
			all_items[defindex] = values

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
		"""Scrape for a user's groups. No API call avaialble."""
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
