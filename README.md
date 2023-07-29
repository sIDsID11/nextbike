# NextBike API

Get simple access to the distribution of the bikes rented by nextbike.

## Installation

You can run from the terminal:

```bash
pip install git+https://github.com/sIDsID11/nextbike
```

## Usage

You can access the information directly from the Client like shown below:

```python
import nextbike

client = nextbike.Client()

# Country
de = client.country("de")

# organization
org = client.organization("Frelo Freiburg")

# City
city = client.city(619)

# Station
uni = client.station(15430457)

# Bike
bike = client.bike(32928)
```

## Documentation

### Class `Client`

#### `Client` Attributes

- `organizations: dict[str, organization]` : A dictionary of all featured organizations. Keys are organizations names.
- `countries: dict[str, Country]` : A dictionary of all featured countries. Keys are country codes.

#### `Client` Methods

- `fetch` : Fetches the most recent data from the nextbike api.
- `scrape`: Scrapes data periodically.
- `log_xxx` : Writes the latest data from xxx into a JSON file.
- `load_xxx`: Loads a previously logged xxx.

### Class `organization`

#### `organization` Attributes

- `organization_name: str` : Name of the organization
- `country_name: str` : Country name of the organization
- `country_code: str` : Country code of the organization
- `cities: dict[str, City]` A dictionary of cities where the organization is active. Keys are city IDs.

#### `organization` Methods

- `city` : Returns a specific city based on country ID.

### Class `Country`

#### `Country` Attributes

- `country_name: str` : Country name of the organization
- `country_code: str` : Country code of the organization
- `cities: dict[int, City]` A dictionary of cities where the organization is active. Keys are city IDs.

#### `Country` Methods

- `city` : Returns a specific city based on city ID.
- `add_city:` Adds a given city to the cities of the country.

### Class `City`

#### `City` Attributes

- `city_id: int` : ID of the city
- `city_name: str` : Name of the city
- `avaiable_bikes: int` : Amount of bikes that are currently avaiable
- `stations: dict[int, Station]` : A dictionary of stations of the city. Keys are station IDs.

#### `City` Methods

- `station` : Returns a specific Station based on station Station ID

### Class `Station`

#### `Station` Attributes

- `station_id: int` : ID of the station
- `station_name: str` : Name of the station
- `station_number: int` : Number of the station
- `free_racks: int` : Amount of racks that are free at the station
- `bikes_available: int` : Amount of bikes that are available to rent
- `bikes: dict[int, Bike]` : A Dictionary of bikes at the station. Keys are bike numbers
- `bikes_available_list: list[Bike]` A List of bikes that are avaiable to rent

#### `Station` Methods

- `bike` : Returns a specific bike based on bike ID

### Class `Bike`

#### `Bike` Attributes

- `bike_id: int` ID of the bike
- `bike_type: int` : Type of the bike
- `active: bool` : Wether the bike is active
- `state: str` : State of the bike
