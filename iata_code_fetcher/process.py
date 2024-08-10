"""
Module for processing airport and carrier data from JSONL files.
"""

import sys
import os
import polars as pl


def process_airport_data(file_path):
    """
    Process airport data from a JSONL file.

    Args:
        file_path (str): Path to the JSONL file containing airport data.

    Returns:
        polars.DataFrame: Processed airport data.
    """
    df = pl.read_ndjson(file_path)

    df_deduplicated = df.unique()

    result = df_deduplicated.rename(
        {"3-letter location code": "iata", "City Name": "city_name", "Airport Name": "airport_name"}
    )

    result = result.sort(["iata", "city_name", "airport_name"])

    return result


def process_carrier_data(file_path):
    """
    Process carrier data from a JSONL file.

    Args:
        file_path (str): Path to the JSONL file containing carrier data.

    Returns:
        polars.DataFrame: Processed carrier data.
    """
    df = pl.read_ndjson(file_path)

    df_deduplicated = df.unique()

    result = df_deduplicated.rename(
        {
            "2-letter code": "iata",
            "Country / Territory": "country_or_territory",
            "Company name": "company_name",
        }
    )

    result = result.sort(["iata", "country_or_territory", "company_name"])

    return result


def main():
    """
    Main function to process the JSONL file based on the given mode (air or carrier).
    """
    if len(sys.argv) != 3:
        print("Usage: python script.py <air|carrier> <path_to_jsonl_file>")
        sys.exit(1)

    mode = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        sys.exit(1)

    if mode == "air":
        result = process_airport_data(file_path)
    elif mode == "carrier":
        result = process_carrier_data(file_path)
    else:
        print("Invalid mode. Use 'air' or 'carrier'.")
        sys.exit(1)

    output_path = os.path.splitext(file_path)[0] + "_processed.jsonl"
    result.write_ndjson(output_path)
    print(f"Processed data saved to {output_path}")


if __name__ == "__main__":
    main()
