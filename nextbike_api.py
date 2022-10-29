# Imports
from __future__ import annotations
from platform import freedesktop_os_release
import requests
import json
from os.path import exists
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Client():
    _data: dict = field(init=False)
    _countries: dict[str, Country] = field(init=False)
    _url: str = "https://api.nextbike.net/maps/nextbike-live.json"
    _logfolder: str = "logfiles"

    def process_raw_data(self):
        '''Processes json formatted data into a data structure.'''
        # Fill data into defined data structure
        for country in self._data["countries"]:
            country_name = country["country_name"]
            country_code = country["country"]
            cities = dict()
            for city in country["cities"]:
                city_id = city["uid"]
                city_name = city["name"]
                booked_bikes = city["booked_bikes"]
                available_bikes = city["available_bikes"]
                stations = dict()
                for station in city["places"]:
                    station_id = station["uid"]
                    station_name = station["name"]
                    station_number = station["number"]
                    racks = station["bike_racks"]
                    free_racks = station["free_racks"]
                    bikes_available_to_rent = station["bikes_available_to_rent"]
                    bikes_booked = station["booked_bikes"]
                    bikes = dict()
                    for bike in station["bike_list"]:
                        bike_id = bike["number"]
                        bike_type = bike["bike_type"]
                        active = bike["active"]
                        state = bike["state"]
                        bikes[bike_id] = Bike(bike_id, bike_type, active, state)
                    stations[station_id] = Station(station_id,
                                                   station_name,
                                                   station_number,
                                                   racks,
                                                   free_racks,
                                                   bikes_available_to_rent,
                                                   bikes_booked,
                                                   bikes)
                cities[city_id] = City(city_id,
                                       city_name,
                                       booked_bikes,
                                       available_bikes,
                                       stations)
            self._countries = Country(country_name,
                                      country_code,
                                      cities)

    def fetch(self: 'Client'):
        '''Get the recent data of the nextbike api.'''
        res = requests.get(self._url)
        if not res.ok:
            print("Fetching failed. API not reachable.")
            return
        self._data = res.json()
        self.process_raw_data()

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
    _cities: dict[str, City]

    @property
    def country_name(self: 'Country') -> str:
        return self._country_name

    @property
    def country_code(self: 'Country') -> str:
        return self._country_code

    @property
    def cities(self: 'Country') -> dict[str, City]:
        return self._cities


@dataclass
class City():
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
class Station():
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
class Bike():
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