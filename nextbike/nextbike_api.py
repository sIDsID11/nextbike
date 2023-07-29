# Imports
from __future__ import annotations
import threading
import time
from typing import Optional
import requests
import json
from datetime import datetime
from dataclasses import dataclass
import os


@dataclass
class Client():
    data: Optional[dict] = None
    organisations: Optional[dict[str, Organisation]] = None
    countries: Optional[dict[str, Country]] = None
    cities: Optional[dict[int, City]] = None
    stations: Optional[dict[int, Station]] = None
    bikes: Optional[dict[int, Bike]] = None
    url: str = "https://api.nextbike.net/maps/nextbike-live.json"
    logfolder: str = "logfiles"
    scrape_count: int = 0

    def __process_raw_data(self):
        '''Processes json formatted data into a data structure.'''
        self.organisations = dict()
        self.countries = dict()
        self.cities = dict()
        self.stations = dict()
        self.bikes = dict()
        for organisation in self.data["countries"]:
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
                        self.bikes[bike_id] = Bike(bike_id, bike_type, active, state)
                    station = Station(station_id, station_name, station_number, free_racks, bikes_available_to_rent, bikes)
                    stations[station_id] = station
                    self.stations[station_id] = station
                city = City(city_id,
                            city_name,
                            available_bikes,
                            stations)
                cities[city_id] = city
                self.cities[city_id] = city
                # Add city to country
                if country_code not in self.countries.keys():
                    self.countries[country_code] = Country(country_name,
                                                           country_code,
                                                           dict())
                self.countries[country_code].add_city(city)
            self.organisations[organisation_name] = Organisation(organisation_name,
                                                                 country_name,
                                                                 country_code,
                                                                 cities)

    def fetch(self: Client):
        '''Get the most recent data of the nextbike api.'''
        res = requests.get(self.url)
        if not res.ok:
            print("Fetching failed. API not reachable.")
            return
        res.encoding = "utf-8"
        self.data = res.json()
        self.__process_raw_data()

    # ------------------------ Scraping -----------------------------------------
    def scrape(self: Client, interval_secs: int,
               country_codes: list[str] = [],
               organisation_names: list[str] = [],
               city_ids: list[int] = [],
               station_ids: list[int] = [],
               bike_ids: list[int] = []):
        self.fetch()
        for country_code in country_codes:
            self.log_country(country_code)
        for organisation_name in organisation_names:
            self.log_organisation(organisation_name)
        for city_id in city_ids:
            self.log_city(city_id)
        for station_id in station_ids:
            self.log_station(station_id)
        for bike_id in bike_ids:
            self.log_bike(bike_id)
        self.scrape_count += 1
        print(f"\rScraped: {self.scrape_count}                             ", end="")

        threading.Timer(interval_secs, self.scrape, args=[interval_secs, country_codes, organisation_names, city_ids, station_ids, bike_ids]).start()

    # ------------------------ Logging -----------------------------------------
    def log_country(self: Client, country_code: str):
        '''Log a given country'''
        country = self.country(country_code)
        typ = "countries"
        id = country_code
        self.__log(country, typ, id)

    def log_organisation(self: Client, organisation_name: str):
        '''Log a given organisation'''
        organisation = self.organisation(organisation_name)
        typ = "organisations"
        id = organisation_name
        self.__log(organisation, typ, id)

    def log_city(self: Client, city_id: int):
        '''Log a given City'''
        city = self.city(city_id)
        typ = "cities"
        id = str(city_id)
        self.__log(city, typ, id)

    def log_station(self: Client, station_id: int):
        '''Log a given station'''
        station = self.station(station_id)
        typ = "stations"
        id = str(station_id)
        self.__log(station, typ, id)

    def log_bike(self: Client, bike_id: int):
        '''Log a given bike'''
        bike = self.bike(bike_id)
        typ = "bikes"
        id = str(bike_id)
        self.__log(bike, typ, id)

    def __log(self: Client, obj: Country | Organisation | City | Station | Bike, typ: str, id: str):
        timestamp = datetime.now().strftime("%d.%m.%Y_%H:%M:%S")
        if not os.path.exists(self.logfolder):
            os.mkdir(self.logfolder)
        if not os.path.exists(os.path.join(self.logfolder, typ)):
            os.mkdir(os.path.join(self.logfolder, typ))
        if not os.path.exists(os.path.join(self.logfolder, typ, id)):
            os.mkdir(os.path.join(self.logfolder, typ, id))
        file = os.path.join(self.logfolder, typ, id, f"log_{timestamp}.json")
        if os.path.exists(file):
            print("Log already exists for the current timestamp. Try later again.")
            return
        with open(file, "w+", encoding="utf-8") as f:
            f.write(obj.to_json())

    # ------------------------ Loading ----------------------------------------
    def load_country(self: Client, file: str) -> Country:
        '''Load a Country from a stored File'''
        country = Country("", "", "")
        print(self.load_dict(file))
        country.__dict__ = self.load_dict(file)

    def load_organisation(self: Client, file: str) -> Organisation:
        '''Load an organisation from a stored File'''
        organisation = Organisation("", "", "", "")
        organisation.__dict__ = self.load_dict(file)

    def load_city(self: Client, file: str) -> City:
        '''Load an city from a stored File'''
        city = City("", "", "", "")
        city.__dict__ = self.load_dict(file)
        return city

    def load_station(self: Client, file: str) -> Station:
        '''Load an station from a stored File'''
        station = Station("", "", "", "", "", "")
        station.__dict__ = self.load_dict(file)

    def load_bike(self: Client, file: str) -> Bike:
        '''Load an bike from a stored File'''
        bike = Bike("", "", "", "")
        bike.__dict__ = self.load_dict(file)

    def load_dict(self: Client, file: str):
        '''Load the logfile and converts to a dictionary.'''
        if not os.path.exists(file):
            print("File at path {filename} not found. Skipping.")
        with open(file, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d

    # ------------------------ Methods ----------------------------------------
    def organisation(self: Client, organisation_name: str) -> Organisation:
        '''Get data of a specific organisation.'''
        return self.organisations[organisation_name]

    def country(self: Client, country_code: str) -> Country:
        '''Get data of a specific country.'''
        return self.countries[country_code.upper()]

    def city(self: Client, city_id: int) -> City:
        '''Get data of a specific city.'''
        return self.cities[city_id]

    def station(self: Client, station_id: int) -> Station:
        '''Get data of a specific station.'''
        return self.stations[station_id]

    def bike(self: Client, bike_id: int) -> Bike:
        '''Get data of a specific station.'''
        return self.bikes[bike_id]


@dataclass
class Country():
    country_name: str
    country_code: str
    cities: dict[str, City]

    def __str__(self: Country) -> str:
        return "Country\n" + \
            f"\tCountry name   : {self.country_name}\n" + \
            f"\tCountry code   : {self.country_code}\n" + \
            f"\tCities         : {len(self.cities)}"

    def to_json(self: Country) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def add_city(self: Country, city: City):
        if city.city_id in self.cities:
            print(f"Key {city.city_id} already registered in country '{self.country_code}'.\nNothing changed.")
        self.cities[city.city_id] = city

    def city(self: Country, city_id: int) -> City:
        '''Get data of a specific city.'''
        return self.cities[city_id]


@dataclass
class Organisation():
    organisation_name: str
    country_name: str
    country_code: str
    cities: dict[str, City]

    def __str__(self: Organisation) -> str:
        return f"Organisation\n" + \
            f"\tOrganisation name   : {self.organisation_name}\n" + \
            f"\tCountry name        : {self.country_name}\n" + \
            f"\tCountry Code        : {self.country_code}\n" + \
            f"\tCities              : {len(self.cities)}"

    def to_json(self: Organisation) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def city(self: Organisation, city_id: int) -> City:
        '''Get data of a specific city.'''
        return self.cities[city_id]


@dataclass
class City():
    city_id: int
    city_name: str
    available_bikes: int
    stations: dict[str, Station]

    def __str__(self: City) -> str:
        return "City\n" + \
            f"\tID              : {self.city_id}\n" + \
            f"\tName            : {self.city_name}\n" + \
            f"\tAvailable Bikes : {self.available_bikes}\n" + \
            f"\tStations        : {len(self.stations)}"

    def to_json(self: City) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def station(self: City, station_id: int) -> Station:
        '''Get data of a specific station.'''
        return self.stations[station_id]


@dataclass
class Station():
    station_id: int
    station_name: str
    station_number: int
    free_racks: int
    bikes_available_to_rent: int
    bikes: dict[str, Bike]

    @property
    def bikes_available_list(self: Station) -> list[Bike]:
        available_bikes = []
        for _, bike in self.bikes.items():
            if bike.state == "ok" and bike.active:
                available_bikes.append(bike)
        return available_bikes

    def __str__(self: Station) -> str:
        return "Station\n" + \
            f"\tID              : {self.station_id}\n" + \
            f"\tName            : {self.station_name}\n" + \
            f"\tNumber          : {self.station_number}\n" + \
            f"\tFree racks      : {self.free_racks}\n" + \
            f"\tBikes available : {self.bikes_available_to_rent}"

    def to_json(self: Station) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def bike(self: Station, bike_id: int) -> Bike:
        '''Get data of a specific bike.'''
        return self.bikes[bike_id]


@dataclass
class Bike():
    bike_id: int
    bike_type: int
    active: bool
    state: str

    def __str__(self: Bike) -> str:
        return "Bike\n" + \
            f"\tID     : {self.bike_id}\n" + \
            f"\tType   : {self.bike_type}\n" + \
            f"\tActive : {self.active}\n" + \
            f"\tState  : {self.state}\n"

    def to_json(self: Bike) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)