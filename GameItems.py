"""
This API call just snags everything for Dota2 or TF2 from the API and stores
it in GameItems.items. Less useful for finding info on a particular item (although
you can do that just fine as well), and more handy for updating info for all current
items in the store at once.

"""

from SteamBase import SteamAPI

class BadGameException(Exception):
    """Raised when the game passed in is not TF2 or Dota2 (or in a bad format)"""
    pass

class BadItemException(Exception):
    """Raised when an incorrect item is passed in"""
    pass

class GameItems(SteamAPI):
    """
    Returns all of the current items in the TF2 or Dota2 store.
    See http://wiki.teamfortress.com/wiki/WebAPI/GetPlayerItems for more
    info on the various fields.

    """

    def __init__(self, api_key):
        """We don't need a SteamID, only an api key here."""
        SteamAPI.__init__(self, "", api_key)
        self.tf2_items = None
        self.dota2_items = None


    def _get_items(self, game, raw_json=False):
        """Gets the item info and puts it into an easier to use format."""

        url = "http://api.steampowered.com/IEconItems_{}/GetSchema/v0001/?key={}".format(game, self.api_key)
        json_data = self._get_json(url)

        if raw_json:
            return json_data['result']['items']

        all_items = {}
        for item in json_data["result"]["items"]:
            values = {}
            values['defindex'] = item.get('defindex')
            values['item_class'] = item.get('item_class')
            values['item_type_name'] = item.get('item_type_name')
            values['proper_name'] = item.get('proper_name')
            values['item_slot'] = item.get('item_slot')
            values['item_quality'] = item.get('item_quality')
            values['image_url'] = item.get('image_url')
            values['image_url_large'] = item.get('image_url_large')
            values['craft_class'] = item.get('craft_class')

            if item.get('capabilities') is not None:
                capable = item.get('capabilities')
                capabilities = {}
                capabilities['nameable'] = capable.get('nameable')
                capabilities['can_gift_wrap'] = capable.get('can_gift_wrap')
                capabilities['can_craft_mark'] = capable.get('can_craft_mark')
                capabilities['can_be_restored'] = capable.get('can_be_restored')
                capabilities['strange_parts'] = capable.get('strange_parts')
                capabilities['can_card_upgrade'] = capable.get('can_card_upgrade')
                values['capabilities'] = capabilities
            if item.get('used_by_classes') is not None:
                game_classes = []
                for character_class in item.get('used_by_classes'):
                    game_classes.append(character_class)
                values['used_by_classes'] = game_classes

            all_items[item.get('name')] = values

        return all_items

    def get_all(self, game, raw_json=False):
        """
        I do a bit of massaging to the get the data in an easier to use format.
        If you want the exact json from Steam, pass in True for raw_json

        """
        self.game = ''
        if game.lower() == 'tf2':
            if self.tf2_items is None:
                self.tf2_items = self._get_items('440', raw_json)
            return self.tf2_items
        elif game.lower() == 'dota2':
            if self.dota2_items is None:
                self.dota2_items = self._get_items('570', raw_json)
            return self.dota2_items
        else:
            raise BadGameException("Please enter either TF2 or Dota2")