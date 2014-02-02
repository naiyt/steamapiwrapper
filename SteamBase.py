import json
import datetime
import urllib2
from time import sleep

class SteamAPI:
    """Base class for our other Steam API classes"""

    def __init__(self, steam_id, api_key):
        """Sets the steam id of the user in question and your API key."""
        self.api_key = api_key
        self.steam_id = steam_id


    def _get_json(self, url, params = None):
        """Retrieves json from a particular url, and returns it as a json object."""
        if params is None:
            return json.load(self._open_url(url))
        else:
            return json.load(self._open_url(url % params))

    def _open_url(self, url):
        """Put here to make catching exceptions easier"""
        try:
            return urllib2.urlopen(url)
        except urllib2.URLError as e:
            print 'URLError = ' + str(e.reason)
        except urllib2.HTTPError as e:
            print 'HTTPError = ' + str(e.code)
            return self._retry(self, url, 5, 5)
        except ValueError as e:
            print 'Not a proper URL'
        except:
            return self._retry(url, 20, 3)

    def _retry(self, url, time, retries):
        """Retries n number of times, with time between each"""
        print "{} is unreachable, retrying {} number of times".format(url, retries)
        for num in range(retries):
            try:
                return urllib2.urlopen(url)
            except:
                sleep(time)
        return None

    def _date(self, date):
        return datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M:%S')