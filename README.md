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

# Organisation
org = client.organisation("Frelo Freiburg")

# City
city = client.city(619)

# Station
uni = client.station(15430457)

# Bike
bike = client.bike(32928)
```

## Documentation

### Class `Client`

#### `Client` Properties

- `organisations: dict[str, Organisation]` : A dictionary of all featured organisations. Keys are organisations names.
- `countries: dict[str, Country` : A dictionary of all featured countries. Keys are country codes.

#### `Client` Mehthods

- `organisation: str -> Organisation]` : Returns a specific organisation based on the organisation name.
- `country: str -> Country]` : Returns a specific country based on the country code.
- `fetch -> None` : Fetches the most recent data from the nextbike api.
- `log: -> None` : Writes the latest data into a JSON file.

### Class `Organisation`

#### `Organisation` Properties

- `organisation_name: str` : Name of the organisation
- `country_name: str` : Country name of the organisation
- `country_code: str` : Country code of the organisation
- `cities: dict[str, City]` A dictionary of cities where the organisation is active. Keys are city IDs.

#### `Organisation` Mehthods

- `city: int -> City` : Returns a specific city based on country ID.

### Class `Country`

#### `Country` Properties

- `country_name: str` : Country name of the organisation
- `country_code: str` : Country code of the organisation
- `cities: dict[int, City]` A dictionary of cities where the organisation is active. Keys are city IDs.

#### `Country` Methods

- `city: int -> City` : Returns a specific city based on city ID.
- `add_city: str, City -> None` Adds a given city to the cities of the country.

### Class `City`

#### `City` Properties

- `city_id: int` : ID of the city
- `city_name: str` : Name of the city
- `avaiable_bikes: int` : Amount of bikes that are currently avaiable
- `stations: dict[int, Station]` : A dictionary of stations of the city. Keys are station IDs.

#### `City` Mehtods

- `station: int -> Station` : Returns a specific Station based on station Station ID

### Class `Station`

#### `Station` Properties

- `station_id: int` : ID of the station
- `station_name: str` : Name of the station
- `station_number: int` : Number of the station
- `free_racks: int` : Amount of racks that are free at the station
- `bikes_available: int` : Amount of bikes that are available to rent
- `bikes: dict[int, Bike]` : A Dictionary of bikes at the station. Keys are bike numbers
- `bikes_available_list: list[Bike]` A List of bikes that are avaiable to rent

#### `Station` Methods

- `bike: int -> Bike` : Returns a specific bike based on bike ID

### Class `Bike`

#### `Bike` Properties

- `bike_id: int` ID of the bike
- `bike_type: int` : Type of the bike
- `active: bool` : Wether the bike is active
- `state: str` : State of the bike
