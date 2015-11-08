steamapiwrapper
===============

NOTE
----

This project has not been maintained in some time, and I offer no guarantees about whether or not it will be compatible with the current Steam web API.

---

A Steam API wrapper that can be used to retrieve info about all games currently on the Steam Store, info on Steam Users (their basic info [ID, avatar, last logon, etc], all games they own, groups, wishlists, etc), and info on all Dota 2 and Team Fortress 2 items.

The Steam Web API is a little poorly documented, and there are a lot of things that you can't do with it. This wrapper should make those things easier, and do things that the API doesn't directly support -- such as getting a list of a user's gifts.

There's lots of cool things you can do with this! See below for examples.

Demo
----

[See this page for a simple example which updates the total price of all Steam games once a day.](http://buyallofsteam.appspot.com)

Installation
============

Will get this on pip soon; for now, just download the source and import the modules directly.

Prerequisites
=============

The `Users` and `GameItems` modules require an API key. [http://steamcommunity.com/dev/apikey](Get one here).

Games Examples
==============

First, import the module and create a Games() object:

	from steamapiwrapper.SteamGames import Games
	games = Games()

Get the current name and price of all Steam Games
-------------------------------------------------


	all_games = games.get_all('US') # Pass in the Country Code
	for game in all_games:
		print "{} - price: {}".format(game.name, game.price)

`Games.get_all()` returns a generator that retrieves 25 games from the Steam API at a time, so you can easily create the object and only use as much as you need.

Find all Linux compatible games
-------------------------------

	all_games = games.get_all('US')
	for game in all_games:
		if game.platforms['linux']:
			print game.name


Get info for specific appids
----------------------------

	appids = [65710, 66001, 66000]
	for game in games.get_info_for(appids):
		print info.price


Find all DLC in the Steam Store
-------------------------------

	dlc = [x for x in games.get_all('US') if x.type == 'dlc']

**Note**: Games.get_all() returns an generator that (by default) retrieves 25 games from the Steam API per call. Iterating over the values with a for loop will give you results quickly for each call. A list comprehension like this works as well, but it will take some time for the call to finish (as it has to make many calls to the Steam API).


Want to parse the JSON returned by Steam yourself?
--------------------------------------------------

	all_games = games.get_all('US')
	for game in all_games:
		do_something_with(game.raw_json)

Steam Users Examples
====================

First, create a SteamUser object:

	from steamapiwrapper.Users import SteamUser
	user = SteamUser(steam_id, api_key) # Pass your api key in, as well as a Steam ID


Get basic info on the user
--------------------------
	print "Username: {}\n Profile Visible: {}\n Date Created: {}".format(user.username, 
		user.visible, user.timecreated)
	print "Profile URL: {}\n Avatar: {}".format(user.profileurl, user.avatar)

Get a list of a user's Steam games
----------------------------------

	games = user.get_games()


Get a user's gifts, wishlists, and groups:
------------------------------------------

	gifts = user.get_gifts()
	wishlists = user.get_wishlist()
	groups = user.get_groups()


Game Items Examples
===================

First, create a GameItems object:

	from steamapiwrapper.GameItems import GameItems
	items = GameItems(api_key) # Pass in your Steam API key

Get info on TF2 or Dota 2items
---------------------

	tf2 = items.get_all('tf2')
	dota2 = items.get_all('dota2')

The info for every item is organized into a dict returned by item.get_all(). If you want to parse the JSON returned from Steam yourself:

	tf2_raw = items.get_all('tf2', raw_json=True)


Full Documenation
=================

Coming Soon
