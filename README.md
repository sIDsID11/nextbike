# NextBike API

Interact with the Nextbike API and fetch real-time bike-sharing data for various countries, organizations, cities, stations, and bikes. The data is processed and organized into data classes, making it easy to work with and log the data to files for further analysis.

## Installation

You can run from the terminal:

```bash
pip install git+https://github.com/sIDsID11/nextbike
```

## Basic Usage

### Setup

Import the `Client` class and create an instance of it.

```python
from nextbike import Client
c = Client()
```

### Direct access

Fetch the latest data from the Nextbike API into the client.

```python
c.fetch()
```

Access the data using the available methods.

```python
de = c.country("de")
frelo = c.organization("Frelo Freiburg")
freiburg = c.city(619)
messe_uni = c.station(15430457)
bike = c.bike(32928)
```

### Scraping

Scrape data at regular intervals into JSON files.

```python
c.scrape(interval_secs=5 * 60, 
        country_codes=["de"],
        organization_names=["Frelo Freiburg"],
        city_ids=[619],
        station_ids=[15430457],
        bike_ids=[32928])
```

Load data from stored JSON files later on for further analysis.

```python
country = c.load_country("file_path")
organization = c.load_organization("file_path")
city = c.load_city("file_path")
station = c.load_station("file_path")
bike = c.load_bike("file_path")
```

### Visualization

Visualize a country, organization or city.

```python
country= Country(...)
heatmap(country)  # Creates an html file of the heatmap

city = City(...)
bikemap(city)  # Creates an html file of the bikemap
```

## Classes and Methods

### Class: `Client`

#### Attributes:

- `data: Optional[dict]` - The raw JSON data fetched from the Nextbike API.
- `organizations: Optional[dict[str, Organization]]` - A dictionary containing organizations' data indexed by their names.
- `countries: Optional[dict[str, Country]]` - A dictionary containing countries' data indexed by their country codes.
- `cities: Optional[dict[int, City]]` - A dictionary containing cities' data indexed by their city IDs.
- `stations: Optional[dict[int, Station]]` - A dictionary containing stations' data indexed by their station IDs.
- `bikes: Optional[dict[int, Bike]]` - A dictionary containing bikes' data indexed by their bike IDs.
- `logfolder: str` - The folder path where log files will be saved.
- `scrape_count: int` - The number of times the data has been scraped using the `scrape` method.

#### Methods:

- `fetch()`: Fetches the latest data from the Nextbike API and processes it into data structures.
- `scrape(interval_secs: int, country_codes: list[str] = [], organization_names: list[str] = [], city_ids: list[int] = [], station_ids: list[int] = [], bike_ids: list[int] = [])`: Scrapes data at regular intervals for specific countries, organizations, cities, stations, or bikes.
- `log_country(country_code: str)`: Logs data for a specific country identified by its country code.
- `log_organization(organization_name: str)`: Logs data for a specific organization identified by its name.
- `log_city(city_id: int)`: Logs data for a specific city identified by its city ID.
- `log_station(station_id: int)`: Logs data for a specific station identified by its station ID.
- `log_bike(bike_id: int)`: Logs data for a specific bike identified by its bike ID.
- `load_country(file: str) -> Country`: Loads a Country object from a stored file.
- `load_organization(file: str) -> Organization`: Loads an Organization object from a stored file.
- `load_city(file: str) -> City`: Loads a City object from a stored file.
- `load_station(file: str) -> Station`: Loads a Station object from a stored file.
- `load_bike(file: str) -> Bike`: Loads a Bike object from a stored file.
- `organization(organization_name: str) -> Organization`: Returns data for a specific organization identified by its name.
- `country(country_code: str) -> Country`: Returns data for a specific country identified by its country code.
- `city(city_id: int) -> City`: Returns data for a specific city identified by its city ID.
- `station(station_id: int) -> Station`: Returns data for a specific station identified by its station ID.
- `bike(bike_id: int) -> Bike`: Returns data for a specific bike identified by its bike ID.

### Class: `Country`

#### Attributes:

- `name: str` - The name of the country.
- `code: str` - The country code.
- `lat: float` - The latitude coordinate of the country.
- `lng: float` - The longitude coordinate of the country.
- `cities: dict[str, City]` - A dictionary containing cities' data indexed by their city IDs.

#### Methods:

- `city(city_id: int) -> City`: Returns data for a specific city identified by its city ID.

### Class: `Organization`

#### Attributes:

- `name: str` - The name of the organization.
- `country_name: str` - The name of the country where the organization operates.
- `country_code: str` - The country code where the organization operates.
- `lat: float` - The latitude coordinate of the organization.
- `lng: float` - The longitude coordinate of the organization.
- `cities: dict[int, City]` - A dictionary containing cities' data indexed by their city IDs.

#### Methods:

- `city(city_id: int) -> City`: Returns data for a specific city identified by its city ID.

### Class: `City`

#### Attributes:

- `id: int` - The ID of the city.
- `name: str` - The name of the city.
- `lat: float` - The latitude coordinate of the city.
- `lng: float` - The longitude coordinate of the city.
- `available_bikes: int` - The number of available bikes in the city.
- `stations: dict[int, Station]` - A dictionary containing stations' data indexed by their station IDs.

#### Methods:

- `station(station_id: int) -> Station`: Returns data for a specific station identified by its station ID.

### Class: `Station`

#### Attributes:

- `id: int` - The ID of the station.
- `name: str` - The name of the station.
- `number: int` - The station number.
- `lat: float` - The latitude coordinate of the station.
- `lng: float` - The longitude coordinate of the station.
- `free_racks: int` - The number of free racks at the station.
- `bikes_available_to_rent: int` - The number of bikes available to rent at the station.
- `bikes: dict[int, Bike]` - A dictionary containing bikes' data indexed by their bike IDs.

#### Methods:

- `bike(bike_id: int) -> Bike`: Returns data for a specific bike identified by its bike ID.

### Class: `Bike`

#### Attributes:

- `id`: int - The ID of the bike.
- `type`: int - The type of the bike.
- `active`: bool - Indicates if the bike is active or not.
- `state`: str - The state of the bike.


### Functions:

- `heatmap(obj: Country | Organization | City, folder: Optional[str] = None, filename: Optional[str] = None)`: Creates a html file of a heatmap from the given object.
- `bikemap(obj: Country | Organization | City, folder: Optional[str] = None, filename: Optional[str] = None)`: Creates a html file of a bikemap from the given object.
