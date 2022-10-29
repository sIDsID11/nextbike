# Imports
import requests
import json
from os.path import exists
from datetime import datetime
from dataclasses import dataclass, field
from __future__ import annotations


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


@dataclass
class Country():
    _country_name: str
    _country_code: str
    _currency: str
    _hotline: str
    _cities: dict[str, City]

    @property
    def country_name(self: 'Country') -> str:
        return self._country_name

    @property
    def country_code(self: 'Country') -> str:
        return self._country_code

    @property
    def currency(self: 'Country') -> str:
        return self._currency

    @property
    def hotline(self: 'Country') -> str:
        return self._hotline

    @property
    def cities(self: 'Country') -> dict[str, City]:
        return self._cities


@dataclass
class City(Country):
    _city_id: int
    _city_name: str
    _booked_bikes: int
    _available_bikes: int
    _stations: dict[str, Station]

    @property
    def city_id(self: 'City') -> int:
        return self._city_id

    @property
    def city_name(self: 'City') -> str:
        return self._city_name

    @property
    def booked_bikes(self: 'City') -> int:
        return self._booked_bikes

    @property
    def available_bikes(self: 'City') -> int:
        return self._available_bikes

    @property
    def stations(self: 'City') -> dict[str, Station]:
        return self._stations


@dataclass
class Station(City):
    _station_id: int
    _station_name: str
    _station_number: int
    _racks: int
    _free_racks: int
    _bikes_available_to_rent: int
    _bikes_booked: int
    _bikes: dict[str, Bike]

    @property
    def station_id(self: 'Station') -> int:
        return self._station_id

    @property
    def station_name(self: 'Station') -> str:
        return self._station_name

    @property
    def station_number(self: 'Station') -> int:
        return self._station_number

    @property
    def racks(self: 'Station') -> int:
        return self._racks

    @property
    def free_racks(self: 'Station') -> int:
        return self._free_racks

    @property
    def bike_avaiable_to_rent(self: 'Station') -> int:
        return self._bikes_available_to_rent

    @property
    def bikes_booked(self: 'Station') -> int:
        return self._bikes_booked

    @property
    def bikes(self: 'Station') -> dict[str, int]:
        return self._bikes


@dataclass
class Bike(Station):
    _bike_id: int
    _bike_type: int
    _active: bool
    _state: str

    @property
    def bike_id(self: 'Bike') -> int:
        return self._bike_id

    @property
    def bike_type(self: 'Bike') -> int:
        return self._bike_type

    @property
    def active(self: 'Bike') -> bool:
        return self._active

    @property
    def state(self: 'Bike') -> str:
        return self._state


if __name__ == "__main__":
    c = Client()
    c.fetch()
    c.log()
    print(c.country("DE"))