# Imports
from __future__ import annotations
from typing import Optional
import requests
import json
from os.path import exists
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Client():
    __data: Optional[dict] = None
    __organisations: Optional[dict[str, Organisation]] = None
    __countries: Optional[dict[str, Country]] = None
    __url: str = "https://api.nextbike.net/maps/nextbike-live.json"
    __logfolder: str = "logfiles"

    def __process_raw_data(self):
        '''Processes json formatted data into a data structure.'''
        # Fill data into defined data structure
        self.__organisations = dict()
        self.__countries = dict()
        for organisation in self.__data["countries"]:
            organisation_name = organisation["name"]
            country_name = organisation["country_name"]
            country_code = organisation["country"]
            cities = dict()
            for city in organisation["cities"]:
                city_id = city["uid"]
                city_name = city["name"]
                available_bikes = city["available_bikes"]
                stations = dict()
                for station in city["places"]:
                    station_id = station["uid"]
                    station_name = station["name"]
                    station_number = station["number"]
                    free_racks = station["free_racks"]
                    bikes_available_to_rent = station["bikes_available_to_rent"]
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
                                                   free_racks,
                                                   bikes_available_to_rent,
                                                   bikes)
                city = City(city_id,
                            city_name,
                            available_bikes,
                            stations)
                cities[city_id] = city
                # Add city to country
                if country_code not in self.__countries.keys():
                    self.__countries[country_code] = Country(country_name,
                                                             country_code,
                                                             dict())
                self.__countries[country_code].add_city(city)

            self.__organisations[organisation_name] = Organisation(organisation_name,
                                                                   country_name,
                                                                   country_code,
                                                                   cities)

    def fetch(self: 'Client'):
        '''Get the recent data of the nextbike api.'''
        res = requests.get(self.__url)
        if not res.ok:
            print("Fetching failed. API not reachable.")
            return
        self.__data = res.json()
        self.__process_raw_data()

    def log(self: 'Client'):
        '''Log the previously fetched data into a json file'''
        if not self.__data:
            Exception("Data was never fetched. Run fetch() to get latest data.")
        timestamp = datetime.now().strftime("%d.%m.%Y_%H:%M:%S")
        path = self.__logfolder + f"/log_{timestamp}.json"
        if exists(path):
            print("Log already exists for the current timestamp. Please wait")
            return
        with open(path, "x", encoding="utf-8") as f:
            f.write(json.dumps(self._data, indent=4))

    @property
    def countries(self: Client) -> dict:
        if not self.__data:
            Exception("Data was never fetched. Run fetch() to get latest data.")
        return self.__countries

    @property
    def organisations(self: Client) -> dict:
        if not self.__data:
            Exception("Data was never fetched. Run fetch() to get latest data.")
        return self.__organisations

    def organisation(self: Client, organisation_name: str) -> Organisation:
        '''Get data of a specific organisation.'''
        if not self.__data:
            Exception("Data was never fetched. Run fetch() to get latest data.")
        return self.__organisations[organisation_name]

    def country(self: Client, country_code: str) -> Country:
        '''Get data of a specific country.'''
        if not self.__data:
            Exception("Data was never fetched. Run fetch() to get latest data.")
        return self.__countries[country_code.upper()]


@dataclass
class Country():
    __country_name: str
    __country_code: str
    __cities: dict[str, City]

    @property
    def country_name(self: Country) -> str:
        return self.__country_name

    @property
    def country_code(self: Country) -> str:
        return self.__country_code

    @property
    def cities(self: Country) -> dict[str, City]:
        return self.__cities

    def __str__(self: Country) -> str:
        return "Class Country\n" + \
            f"\tCountry name   : {self.__country_name}\n" + \
            f"\tCountry code   : {self.__country_code}\n" + \
            f"\tCities         : {len(self.__cities)}"

    def add_city(self: Country, city: City):
        if city.city_id in self.__cities:
            print(f"Key {city.city_id} already registered in country '{self.__country_code}'.\nNothing changed.")
        self.__cities[city.city_id] = city

    def city(self: Country, city_id: int) -> City:
        '''Get data of a specific city.'''
        return self.__cities[city_id]


@dataclass
class Organisation():
    __organisation_name: str
    __country_name: str
    __country_code: str
    __cities: dict[str, City]

    @property
    def organisation_name(self: Organisation) -> str:
        return self.__organisation_name

    @property
    def country_name(self: Organisation) -> str:
        return self.__country_name

    @property
    def country_code(self: Organisation) -> str:
        return self.__country_code

    @property
    def cities(self: Organisation) -> dict[str, City]:
        return self.__cities

    def __str__(self: Organisation) -> str:
        return f"Class Organisation\n" + \
            f"\tOrganisation name   : {self.__organisation_name}\n" + \
            f"\tCountry name        : {self.__country_name}\n" + \
            f"\tCountry Code        : {self.__country_code}\n" + \
            f"\tCities              : {len(self.__cities)}"

    def city(self: Organisation, city_id: int) -> City:
        '''Get data of a specific city.'''
        return self.__cities[city_id]


@dataclass
class City():
    __city_id: int
    __city_name: str
    __available_bikes: int
    __stations: dict[str, Station]

    @property
    def city_id(self: City) -> int:
        return self.__city_id

    @property
    def city_name(self: City) -> str:
        return self.__city_name

    @property
    def available_bikes(self: City) -> int:
        return self.__available_bikes

    @property
    def stations(self: City) -> dict[str, Station]:
        return self.__stations

    def __str__(self: City) -> str:
        return "Class City\n" + \
            f"\tID              : {self.__city_id}\n" + \
            f"\tName            : {self.__city_name}\n" + \
            f"\tAvailable Bikes : {self.__available_bikes}\n" + \
            f"\tStations        : {len(self.__stations)}"

    def station(self: City, station_id: int) -> Station:
        '''Get data of a specific station.'''
        return self.__stations[station_id]


@dataclass
class Station():
    __station_id: int
    __station_name: str
    __station_number: int
    __free_racks: int
    __bikes_available_to_rent: int
    __bikes: dict[str, Bike]

    @property
    def station_id(self: Station) -> int:
        return self.__station_id

    @property
    def station_name(self: Station) -> str:
        return self.__station_name

    @property
    def station_number(self: Station) -> int:
        return self.__station_number

    @property
    def free_racks(self: Station) -> int:
        return self.__free_racks

    @property
    def bikes_avaiable(self: Station) -> int:
        return self.__bikes_available

    @property
    def bikes(self: Station) -> dict[int, int]:
        return self.__bikes

    @property
    def bikes_available_list(self: Station) -> list[Bike]:
        available_bikes = []
        for bike_id, bike in self.__bikes.items():
            if bike.state == "ok" and bike.active:
                available_bikes.append(bike)
        return available_bikes

    def __str__(self: Station) -> str:
        return "Class Station\n" + \
            f"\tID              : {self.__station_id}\n" + \
            f"\tName            : {self.__station_name}\n" + \
            f"\tNumber          : {self.__station_number}\n" + \
            f"\tFree racks      : {self.__free_racks}\n" + \
            f"\tBikes available : {self.__bikes_available_to_rent}"

    def bike(self: Station, bike_id: int) -> Bike:
        '''Get data of a specific bike.'''
        return self.__bikes[bike_id]


@dataclass
class Bike():
    __bike_id: int
    __bike_type: int
    __active: bool
    __state: str

    @property
    def bike_id(self: 'Bike') -> int:
        return self.__bike_id

    @property
    def bike_type(self: 'Bike') -> int:
        return self.__bike_type

    @property
    def active(self: 'Bike') -> bool:
        return self.__active

    @property
    def state(self: 'Bike') -> str:
        return self.__state

    def __str__(self: Bike) -> str:
        return "Class Bike\n" + \
            f"\tID     : {self.__bike_id}\n" + \
            f"\tType   : {self.__bike_type}\n" + \
            f"\tActive : {self.__active}\n" + \
            f"\tState  : {self.__state}\n"


if __name__ == "__main__":
    c = Client()
    c.fetch()
    de = c.country("de")
    fr = de.city(619)
    messe = fr.station(15430457)
    print(messe.bikes_available_list)