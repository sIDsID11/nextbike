# Imports
import requests
import json
from os.path import exists
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Client():
    _data: dict = field(init=False)
    _url: str = "https://api.nextbike.net/maps/nextbike-live.json"
    _logfolder: str = "logfiles"

    def fetch(self: 'Client'):
        '''Get the recent data of the nextbike api.'''
        res = requests.get(self._url)
        if not res.ok:
            print("Fetching failed. API not reachable.")
            return
        self._data = res.json()

    def log(self: 'Client'):
        '''Log the previously fetched data into a json file'''
        timestamp = datetime.now().strftime("%d:%m:%Y_%H:%M:%S")
        path = self._logfolder + f"/log_{timestamp}.json"
        if exists(path):
            print("Log already exists for the current timestamp. Please wait")
            return
        with open(path, "x") as f:
            f.write(json.dumps(self._data, indent=4))

    def country(self, country_code: str) -> dict:
        for c in self._data["countries"]:
            if c["country"] == country_code.upper():
                return c


if __name__ == "__main__":
    c = Client()
    c.fetch()
    c.log()
    print(c.country("DE"))