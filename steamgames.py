"""
A small API wrapper intended to retrieve all available store information
for either a specific appid, or all appids.

Thanks for this SteamDB.info blog post for the idea on the best way to do this:
http://steamdb.info/blog/5/

This should give you all of the same info that, say, SteamCalculator's script does
(https://github.com/spezifanta/SteamCalculator-Scripts), but it's much more efficient and
can return much more info.

"""

import urllib
import json
from SteamBase import SteamAPI


class Games(SteamAPI):
	"""
	Class used to retrieve either all Game objects, or specific ones given a list of appids.

	Example:
	games = Games()
	all_games = games.get_all('US') # Get a generator with all game info

	# Get a generator for just the appids you specify
	some_games = games.get_appids_info([123,1245])

	"""

	def __init__(self,num=None):
		""" Num is how many we can check against the Steam API per iteration. Defaults to 150 """

		if num is None:
			self.num = 150
		else:
			self.num = num

		"""
		appids_to_names is a dict mapping appid -> game names
		names_to_appids is a dict mapping names -> appids
		Probably not necessary to have both
		"""

		self.appids_to_names, self.names_to_appids = None, None

	def _create_url(self, appids, cc):
		"""Given a list of appids, creates an API url to retrieve them"""
		appids = [str(x) for x in appids]
		list_of_ids = ','.join(appids)
		data = {'appids': list_of_ids, 'cc': cc, 'l': 'english', 'v': '1'}
		url_vals = urllib.urlencode(data)
		return "http://store.steampowered.com/api/appdetails/?{}".format(url_vals)

	def _get_urls(self, appids, cc):
		"""Returns urls for all of appids"""
		list_of_ids = list(self._chunks(appids,self.num))
		all_urls = []
		for x in list_of_ids:
			all_urls.append(self._create_url(x, cc))
		return all_urls

	def get_all(self, cc):
		"""
		A generator that returns all games currently in the Steam Store as Game objects.
		This wraps around _get_games_from, so that the even though we have seperate urls for
		the games, when you call this method you just get one generator, that will give you
		one game object at a time.

		"""
		if self.appids_to_names is None or self.names_to_appids is None:
			self.appids_to_names, self.names_to_appids = self.get_ids_and_names()
		urls = self._get_urls(self.appids_to_names.keys(), cc)
		for url in urls:
			print "Making next API call..."
			curr_games = self._get_games_from(url)
			for game in curr_games:
				yield game

	def _get_games_from(self, url):
		"""
		This generator actually creates the Game objects, and can be called from 
		any method if you pass a list of url's to create the game appids from.

		"""

		page = json.loads(self._open_url(url).read())
		for appid in page:
			game = Game(page[appid], appid)
			if game.success:
				yield game

	def get_info_for(self, appids, cc):
		"""Given a list of appids, returns their Game objects"""
		urls = self._get_urls(appids, cc)
		for url in urls:
			print "Opening a new page of games..."
			curr_games = self._get_games_from(url)
			for game in curr_games:
				yield game

	def get_ids_and_names(self):
		"""Returns all appids in the store as a dictionary mapping appid to game_name"""
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
		if game_name in self.names_to_appids:
			return self.names_to_appids[game_name]

	def get_name(self, appid):
		"""Given a game name returns its appid"""
		if appid in self.appids_to_names:
			return self.appids_to_names[appid]

	def _chunks(self, params, number):
		"""Breaks a list into a set of equally sized chunked lists, with remaining entries in last list"""
		print "Setting things up..."
		for i in xrange(0, len(params), number):
			yield params[i:i+number]



class Game(SteamAPI):
	"""
	The actual Game() object -- really this is just a wrapper around the base
	json response from Steam, that makes it a bit easier to go through the data.

	"""

	def __init__(self, game_json, appid):
		"""
		Curently, this just sets member variables for the various values
		that the game object should have. Not all of these exist on all
		appids, so there's some defaults whenever there is a key error.
		I'll admit this looks kind of nasty, but it works. Perhaps someone
		would be willing to make this look a bit better/more Pythonic?

		"""

		self.appid = appid
		if 'success' in game_json:
			self.success = game_json['success']
			if self.success:
				self.store_url = self._calc_store_url(self.appid)
				data = game_json['data']
				self.type = data['type']
				self.description = data['detailed_description']

				# Some appids don't have names
				try:
					self.name = data['name']
				except KeyError:
					self.name = "No Name"

				try:
					self.supported_languages = data['supported_languages']
				except KeyError:
					self.supported_languages = None

				self.header_image = "http://cdn.steampowered.com/v/gfx/apps/%s/capsule_184x69.jpg" % self.appid
				self.website = data['website']

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
			print "Error! Can't read the game for {}".format(appid)

	def _calc_price(self, amount):
		"""Prices from the API are represented by cents -- convert to dollars"""
		return float(amount) / 100.0

	def _calc_store_url(self, appid):
		return "http://store.steampowered.com/app/{}".format(appid)