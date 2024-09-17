"""
This module contains functionality to fetch and process IATA codes from the IATA website. It supports fetching data
for both carrier and airport codes, processing the data, and saving it in JSONL format.
"""

import json
from string import ascii_uppercase, digits
from itertools import product
from typing import Generator, List, Dict
from enum import Enum
import logging
from time import sleep
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException

# Constants
BASE_URL: str = (
    "https://www.iata.org/PublicationDetails/Search/?currentBlock={block}&currentPage=12572&{type}.search={code}"
)
CARRIER_BLOCK: str = "314383"
AIRPORT_BLOCK: str = "314384"
CARRIER_FILE: str = "carrier_data_full.jsonl"
AIRPORT_FILE: str = "airport_data_full.jsonl"
# Frequency of processing status updates
REPORT_FREQUENCY: int = 100  # report every 100 codes
MAX_RETRIES: int = 3
RETRY_DELAY: int = 15  # seconds
TIMEOUT: int = 20  # seconds

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CodeType(Enum):
    """
    Enum for distinguishing between carrier and airport IATA codes.
    """

    CARRIER = 1
    AIRPORT = 2


def generate_codes(length: int) -> Generator[str, None, None]:
    """
    Generate all possible combinations of IATA codes of a given length.

    :param length: Length of the IATA code (2 for carrier, 3 for airport).
    :return: Generator of code strings.
    """
    return ("".join(letters) for letters in product(ascii_uppercase + digits, repeat=length))


def fetch_and_process_data(code: str, code_type: CodeType) -> List[Dict[str, str]]:
    """
    Fetch and process data from the IATA site based on the code and type.

    :param code: The IATA code.
    :param code_type: The type of the code (CodeType.CARRIER or CodeType.AIRPORT).
    :return: List of dictionaries.
    """
    url = BASE_URL.format(
        block=CARRIER_BLOCK if code_type == CodeType.CARRIER else AIRPORT_BLOCK,
        type="airline" if code_type == CodeType.CARRIER else "airport",
        code=code,
    )

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"class": "datatable"})

            if not table:
                raise ValueError("No record found")

            headers = [th.text.strip() for th in table.find_all("td")]
            rows = []
            for row in table.find("tbody").find_all("tr"):
                cols = [col.text.strip() for col in row.find_all("td")]
                row_data = dict(zip(headers, cols))
                rows.append(row_data)

            return rows

        except RequestException as e:
            if attempt < MAX_RETRIES - 1:
                logging.warning(
                    "Request failed for %s. Retrying in %d seconds... (Attempt %d/%d)",
                    code,
                    RETRY_DELAY,
                    attempt + 1,
                    MAX_RETRIES,
                )
                sleep(RETRY_DELAY)
            else:
                raise RequestException(f"Request failed after {MAX_RETRIES} attempts: {str(e)}") from e

    return []


def process_and_save_data(code_type: CodeType) -> None:
    """
    Process and save data for the given code type.

    :param code_type: The type of the code (CodeType.CARRIER or CodeType.AIRPORT).
    """
    processed: int = 0
    file_path = CARRIER_FILE if code_type == CodeType.CARRIER else AIRPORT_FILE
    for code in generate_codes(2 if code_type == CodeType.CARRIER else 3):
        try:
            result = fetch_and_process_data(code, code_type)
            with open(file_path, "a", encoding="UTF-8") as file:
                for item in result:
                    file.write(json.dumps(item) + "\n")
        except RequestException as e:
            logging.error("For %s: %s", code, e)
        except ValueError as e:
            logging.info("For %s, %s", code, e)

        processed += 1
        if processed % REPORT_FREQUENCY == 0:
            logging.info("Processed %s %s codes so far...", processed, code_type.name.lower())

    logging.info(
        "Data extraction for %ss completed. Results are saved in %s.",
        code_type.name.lower(),
        file_path,
    )


if __name__ == "__main__":
    process_and_save_data(CodeType.CARRIER)
    process_and_save_data(CodeType.AIRPORT)


# Example response for:
# https://www.iata.org/PublicationDetails/Search/?currentBlock=314383&currentPage=12572&airline.search=AA:
# <table class="datatable">
#     <thead>
#     <tr>
#             <td>Company name</td>
#             <td>Country / Territory</td>
#             <td>2-letter code</td>
#     </tr>
#     </thead>
#     <tbody>
#         <tr>
#                 <td>BONZA AVIATION PTY LTD</td>
#                 <td>Australia</td>
#                 <td>AB</td>
#         </tr>
#         <tr>
#                 <td>West Atlantic Sweden AB</td>
#                 <td>Sweden</td>
#                 <td>T2</td>
#         </tr>
#     </tbody>
# </table>

# Example response for:
# https://www.iata.org/PublicationDetails/Search/?currentBlock=314384&currentPage=12572&airport.search=AAA
# <table class="datatable">
#     <thead>
#     <tr>
#             <td>City Name</td>
#             <td>Airport Name</td>
#             <td>3-letter location code</td>
#     </tr>
#     </thead>
#     <tbody>
#         <tr>
#                 <td>Anaa</td>
#                 <td>Anaa Airport</td>
#                 <td>AAA</td>
#         </tr>
#     </tbody>
# </table>
