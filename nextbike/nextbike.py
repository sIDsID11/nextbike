# Imports
from __future__ import annotations
import os
import json
import requests
import threading
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from .utils import country_code_map


@dataclass
class Client:
    countries: Optional[dict[str, Country]] = None
    organizations: Optional[dict[str, Organization]] = None
    cities: Optional[dict[int, City]] = None
    stations: Optional[dict[int, Station]] = None
    bikes: Optional[dict[int, Bike]] = None
    logfolder: str = "./logfiles"
    data: Optional[dict] = None
    _url: str = "https://api.nextbike.net/maps/nextbike-live.json"

    # ------------------------ fetching -----------------------------------------
    def fetch(self):
        '''Get the most recent data of the nextbike api.'''
        res = requests.get(self._url)
        if not res.ok:
            print("Fetching failed. API not reachable.")
            return
        res.encoding = "utf-8"
        self.data = res.json()
        self._process_raw_data()

    def _process_raw_data(self):
        '''Processes json formatted data into a data structure.'''
        if self.data is None:
            raise ValueError("No data to process. Fetch data first.")

        self.organizations = dict()
        self.countries = dict()
        self.cities = dict()
        self.stations = dict()
        self.bikes = dict()
        for organization in self.data["countries"]:
            organization_name = organization["name"]
            country_name = organization["country_name"]
            country_code = organization["country"].lower()
            org_lat = float(organization["lat"])
            org_lng = float(organization["lng"])
            cities = dict()
            for city in organization["cities"]:
                city_id = int(city["uid"])
                city_name = city["name"]
                available_bikes = city["available_bikes"]
                city_lat = float(city["lat"])
                city_lng = float(city["lng"])
                stations = dict()
                for station in city["places"]:
                    station_id = int(station["uid"])
                    station_name = station["name"]
                    station_number = int(station["number"])
                    free_racks = int(station["free_racks"])
                    bikes_available_to_rent = station["bikes_available_to_rent"]
                    station_lat = float(station["lat"])
                    station_lng = float(station["lng"])
                    bikes = dict()
                    for bike in station["bike_list"]:
                        bike_id = int(bike["number"])
                        bike_type = int(bike["bike_type"])
                        active = bike["active"]
                        state = bike["state"]
                        bikes[bike_id] = Bike(bike_id, bike_type, active, state, station_lat, station_lng)
                        self.bikes[bike_id] = Bike(bike_id, bike_type, active, state, station_lat, station_lng)
                    station = Station(station_id, station_name, station_number, station_lat,
                                      station_lng, free_racks, bikes_available_to_rent, bikes)
                    stations[station_id] = station
                    self.stations[station_id] = station
                city = City(city_id, city_name, city_lat, city_lng, available_bikes, stations)
                cities[city_id] = city
                self.cities[city_id] = city
                if country_code not in self.countries.keys():
                    country_lat, country_lng = country_code_map[country_code]
                    self.countries[country_code] = Country(country_name, country_code, country_lat, country_lng, dict())
                self.countries[country_code]._add_city(city)
            self.organizations[organization_name] = Organization(
                organization_name, country_name, country_code, org_lat, org_lng, cities)

    # ------------------------ scraping -----------------------------------------
    def scrape(self, interval_secs: int,
               country_codes: list[str] = [],
               organization_names: list[str] = [],
               city_ids: list[int] = [],
               station_ids: list[int] = [],
               bike_ids: list[int] = [],
               scrape_count: int = 0):
        self.fetch()
        for country_code in country_codes:
            self.log_country(country_code)
        for organization_name in organization_names:
            self.log_organization(organization_name)
        for city_id in city_ids:
            self.log_city(city_id)
        for station_id in station_ids:
            self.log_station(station_id)
        for bike_id in bike_ids:
            self.log_bike(bike_id)
        scrape_count += 1
        print(100 * " ", end="\r")
        print(f"\rScraped: {scrape_count}", end="")

        threading.Timer(interval_secs, self.scrape, args=[
                        interval_secs, country_codes, organization_names, city_ids, station_ids, bike_ids, scrape_count]
                        ).start()

    # ------------------------ logging -----------------------------------------
    def log_country(self, country_code: str):
        '''Log a given country'''
        country = self.get_country(country_code)
        typ = "countries"
        id = country_code
        self._log(country, typ, id)

    def log_organization(self, organization_name: str):
        '''Log a given organization'''
        organization = self.get_organization(organization_name)
        typ = "organizations"
        id = organization_name
        self._log(organization, typ, id)

    def log_city(self, city_id: int):
        '''Log a given City'''
        city = self.get_city(city_id)
        typ = "cities"
        id = str(city_id)
        self._log(city, typ, id)

    def log_station(self, station_id: int):
        '''Log a given station'''
        station = self.get_station(station_id)
        typ = "stations"
        id = str(station_id)
        self._log(station, typ, id)

    def log_bike(self, bike_id: int):
        '''Log a given bike'''
        bike = self.get_bike(bike_id)
        typ = "bikes"
        id = str(bike_id)
        self._log(bike, typ, id)

    def _log(self, obj: Country | Organization | City | Station | Bike, typ: str, id: str):
        timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
        folder = os.path.join(self.logfolder, typ, id)
        os.makedirs(folder, exist_ok=True)

        file = os.path.join(folder, f"log_{timestamp}.json")
        with open(file, "w", encoding="utf-8") as f:
            json.dump(obj, f, default=lambda o: o.__dict__, ensure_ascii=False, sort_keys=True, indent=4)

    # ------------------------ loading ----------------------------------------
    def load_country(self, file: str) -> Country:
        '''Load a Country from a stored File'''
        country_data = self._load_dict(file)
        country = Country(country_data['name'], country_data['code'], country_data["lat"], country_data["lng"], {})
        for city_id, city_data in country_data['cities'].items():
            city_id = int(city_id)
            city = City(city_id, city_data['name'], city_data['lat'], city_data['lng'],
                        city_data['available_bikes'], {})
            for station_id, station_data in city_data['stations'].items():
                station_id = int(station_id)
                station = Station(station_id, station_data['name'], station_data['number'],
                                  station_data['lat'], station_data['lng'], station_data['free_racks'],
                                  station_data['bikes_available_to_rent'], {})
                for bike_id, bike_data in station_data['bikes'].items():
                    bike_id = int(bike_id)
                    bike = Bike(bike_id, bike_data['type'], bike_data['active'],
                                bike_data['state'], bike_data["lat"], bike_data["lng"])
                    station.bikes[bike_id] = bike
                city.stations[station_id] = station
            country.cities[city_id] = city
        return country

    def load_organization(self, file: str) -> Organization:
        '''Load an organization from a stored File'''
        org_data = self._load_dict(file)
        organization = Organization(org_data['name'], org_data['country_name'], org_data['country_code'],
                                    org_data['lat'], org_data['lng'], {})
        for city_id, city_data in org_data['cities'].items():
            city_id = int(city_id)
            city = City(city_id, city_data['name'], city_data['lat'], city_data['lng'],
                        city_data['available_bikes'], {})
            for station_id, station_data in city_data['stations'].items():
                station_id = int(station_id)
                station = Station(station_id, station_data['name'], station_data['number'],
                                  station_data['lat'], station_data['lng'], station_data['free_racks'],
                                  station_data['bikes_available_to_rent'], {})
                for bike_id, bike_data in station_data['bikes'].items():
                    bike_id = int(bike_id)
                    bike = Bike(bike_id, bike_data['type'], bike_data['active'],
                                bike_data['state'], bike_data["lat"], bike_data["lng"])
                    station.bikes[bike_id] = bike
                city.stations[station_id] = station
            organization.cities[city_id] = city
        return organization

    def load_city(self, file: str) -> City:
        '''Load a city from a stored File'''
        city_data = self._load_dict(file)
        city = City(city_data['id'], city_data['name'], city_data['lat'], city_data['lng'],
                    city_data['available_bikes'], {})
        for station_id, station_data in city_data['stations'].items():
            station_id = int(station_id)
            station = Station(station_id, station_data['name'], station_data['number'],
                              station_data['lat'], station_data['lng'], station_data['free_racks'],
                              station_data['bikes_available_to_rent'], {})
            for bike_id, bike_data in station_data['bikes'].items():
                bike_id = int(bike_id)
                bike = Bike(bike_id, bike_data['type'], bike_data['active'],
                            bike_data['state'], bike_data["lat"], bike_data["lng"])
                station.bikes[bike_id] = bike
            city.stations[station_id] = station
        return city

    def load_station(self, file: str) -> Station:
        '''Load a station from a stored File'''
        station_data = self._load_dict(file)
        station = Station(station_data['id'], station_data['name'], station_data['number'],
                          station_data['lat'], station_data['lng'], station_data['free_racks'],
                          station_data['bikes_available_to_rent'], {})
        for bike_id, bike_data in station_data['bikes'].items():
            bike_id = int(bike_id)
            bike = Bike(bike_id, bike_data['type'], bike_data['active'],
                        bike_data['state'], bike_data["lat"], bike_data["lng"])
            station.bikes[bike_id] = bike
        return station

    def load_bike(self, file: str) -> Bike:
        '''Load a bike from a stored File'''
        bike_data = self._load_dict(file)
        bike = Bike(bike_data['id'], bike_data['type'], bike_data['active'],
                    bike_data['state'], bike_data["lat"], bike_data["lng"])
        return bike

    def _load_dict(self, file: str):
        '''Load the logfile and converts to a dictionary.'''
        if not os.path.exists(file):
            print("File at path {filename} not found. Skipping.")
        with open(file, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d

    # ------------------------ methods ----------------------------------------
    def get_organization(self, organization_name: str) -> Organization:
        '''Get data of a specific organization.'''
        if self.organizations is None:
            raise ValueError("No data available. Fetch data first.")
        return self.organizations[organization_name]

    def get_country(self, country_code: str) -> Country:
        '''Get data of a specific country.'''
        if self.countries is None:
            raise ValueError("No data available. Fetch data first.")
        return self.countries[country_code]

    def get_city(self, city_id: int) -> City:
        '''Get data of a specific city.'''
        if self.cities is None:
            raise ValueError("No data available. Fetch data first.")
        return self.cities[city_id]

    def get_station(self, station_id: int) -> Station:
        '''Get data of a specific station.'''
        if self.stations is None:
            raise ValueError("No data available. Fetch data first.")
        return self.stations[station_id]

    def get_bike(self, bike_id: int) -> Bike:
        '''Get data of a specific station.'''
        if self.bikes is None:
            raise ValueError("No data available. Fetch data first.")
        return self.bikes[bike_id]


@dataclass
class Country:
    name: str
    code: str
    lat: float
    lng: float
    cities: dict[int, City]

    def __str__(self) -> str:
        return "Country:\n" + \
            f"\tCountry name   : {self.name}\n" + \
            f"\tCountry code   : {self.code}\n" + \
            f"\tLatitude       : {self.lat}\n" + \
            f"\tLongitude      : {self.lng}\n" + \
            f"\tCities         : {len(self.cities)}"

    def _add_city(self, city: City):
        if city.id in self.cities:
            print(f"WARNING: Key {city.id} already registered in country '{self.code}'.\nNothing changed.")
        self.cities[city.id] = city

    def city(self, city_id: int) -> City:
        '''Get data of a specific city.'''
        return self.cities[city_id]

    @property
    def stations(self) -> dict[int, Station]:
        s = dict()
        for city in self.cities.values():
            for station in city.stations.values():
                if station.id in s.keys():
                    print(f"WARNING: Multiple stations with ID {station.id}.")
                s[station.id] = station
        return s

    @property
    def bikes(self) -> dict[int, Bike]:
        b = dict()
        for station in self.stations.values():
            for bike in station.bikes.values():
                if bike.id in b.keys():
                    print(f"WARNING: Multiple bikes with ID {bike.id}.")
                b[bike.id] = bike
        return b


@dataclass
class Organization:
    name: str
    country_name: str
    country_code: str
    lat: float
    lng: float
    cities: dict[int, City]

    def __str__(self) -> str:
        return f"organization:\n" + \
            f"\torganization name   : {self.name}\n" + \
            f"\tCountry name        : {self.country_name}\n" + \
            f"\tCountry Code        : {self.country_code}\n" + \
            f"\tLatitude            : {self.lat}\n" + \
            f"\tLongitude           : {self.lng}\n" + \
            f"\tCities              : {len(self.cities)}"

    def city(self, city_id: int) -> City:
        '''Get data of a specific city.'''
        return self.cities[city_id]

    @property
    def stations(self) -> dict[int, Station]:
        s = dict()
        for city in self.cities.values():
            for id, station in city.stations.items():
                if id in s.keys():
                    print(f"WARNING: Multiple stations with ID {id}.")
                s[id] = station
        return s

    @property
    def bikes(self) -> dict[int, Bike]:
        b = dict()
        for station in self.stations.values():
            for id, bike in station.bikes.items():
                if id in b.keys():
                    print(f"WARNING: Multiple bikes with ID {id}.")
                b[id] = bike
        return b


@dataclass
class City:
    id: int
    name: str
    lat: float
    lng: float
    available_bikes: int
    stations: dict[int, Station]

    def __str__(self: City) -> str:
        return "City:\n" + \
            f"\tID              : {self.id}\n" + \
            f"\tName            : {self.name}\n" + \
            f"\tLatitude        : {self.lat}\n" + \
            f"\tLongitude       : {self.lng}\n" + \
            f"\tAvailable Bikes : {self.available_bikes}\n" + \
            f"\tStations        : {len(self.stations)}"

    def station(self: City, station_id: int) -> Station:
        '''Get data of a specific station.'''
        return self.stations[station_id]

    @property
    def bikes(self) -> dict[int, Bike]:
        b = dict()
        for id, station in self.stations.items():
            for bike in station.bikes.values():
                if id in b.keys():
                    print(f"Multiple bikes with ID {id}.")
                b[id] = bike
        return b


@dataclass
class Station:
    id: int
    name: str
    number: int
    lat: float
    lng: float
    free_racks: int
    bikes_available_to_rent: int
    bikes: dict[int, Bike]

    @property
    def bikes_available(self) -> dict[int, Bike]:
        available_bikes = dict()
        for id, bike in self.bikes.items():
            if bike.state == "ok" and bike.active:
                available_bikes[id] = bike
        return available_bikes

    def __str__(self) -> str:
        return "Station:\n" + \
            f"\tID              : {self.id}\n" + \
            f"\tName            : {self.name}\n" + \
            f"\tNumber          : {self.number}\n" + \
            f"\tLatitude        : {self.lat}\n" + \
            f"\tLongitude       : {self.lng}\n" + \
            f"\tFree racks      : {self.free_racks}\n" + \
            f"\tBikes available : {self.bikes_available_to_rent}"

    def bike(self, bike_id: int) -> Bike:
        '''Get data of a specific bike.'''
        return self.bikes[bike_id]


@dataclass
class Bike:
    id: int
    type: int
    active: bool
    state: str
    lat: float
    lng: float

    def __str__(self: Bike) -> str:
        return "Bike:\n" + \
            f"\tID     : {self.id}\n" + \
            f"\tType   : {self.type}\n" + \
            f"\tActive : {self.active}\n" + \
            f"\tState  : {self.state}\n" + \
            f"\tLat    : {self.lat}\n" + \
            f"\tLng    : {self.lng}"
