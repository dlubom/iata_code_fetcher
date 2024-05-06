
# IATA Code Data Fetcher

## Overview
This Python project automatically fetches data for airline carriers and airports from the IATA (International Air Transport Association) publication pages. It generates two-letter carrier codes or three-letter airport codes and retrieves information published on the IATA website corresponding to these codes. The data fetched includes various attributes of the carriers and airports, which are then saved into a `.jsonl` file for further analysis or use.

## Features
- Generates all possible combinations of two-letter and three-letter codes.
- Fetches data using the generated codes from specific IATA publication URLs.
- Parses HTML responses to extract relevant table data.
- Saves the extracted data in a JSON Lines format for easy consumption by downstream systems.

## Requirements
This project is managed with Poetry to handle dependencies and environments. You will need:
- Python 3.8 or higher
- Poetry for dependency management

## Setup Instructions

1. **Install Poetry**: Install Poetry by following the instructions on the [official Poetry website](https://python-poetry.org/docs/).

2. **Clone the Repository**: Clone this repository to your local machine.

3. **Install Dependencies**: Navigate to the project directory and run the following command to install the necessary dependencies:
   ```bash
   poetry install
   ```

## Usage

To start data extraction, use the following commands:
```bash
cd iata_code_fetcher  # Navigate to the project directory
poetry run python iata_code_fetcher/fetcher.py
```
The script will begin processing and will save the data to `.jsonl` files named `carrier_data_full.jsonl` and `airport_data_full.jsonl` for carrier and airport data, respectively. 

The script includes rate limiting to prevent excessive requests to the IATA server, with a 1-second sleep interval between requests.

## Output
Output files will be generated in the `iata_code_fetcher` directory:
- `carrier_data_full.jsonl`: Contains data fetched for airline carriers.
- `airport_data_full.jsonl`: Contains data fetched for airports.

Each line in the `.jsonl` file represents a JSON object containing data for one carrier or airport. 

Note that these files may contain duplicate entries. To remove duplicates, you can use the following command in a Unix-like shell:

```bash
cat carrier_data_full.jsonl | sort | uniq > carrier_data_full_unique.jsonl
cat airport_data_full.jsonl | sort | uniq > airport_data_full_unique.jsonl
```

## Notes
Make sure to comply with IATA's terms of service regarding the use of data fetched from their site.