import polars as pl
import sys
import os


def process_airport_data(file_path):
    df = pl.read_ndjson(file_path)

    df_deduplicated = df.unique()

    result = df_deduplicated.rename(
        {"3-letter location code": "iata", "City Name": "city_name", "Airport Name": "airport_name"}
    )

    result = result.sort(["iata", "city_name"])

    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_jsonl_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        sys.exit(1)

    result = process_airport_data(file_path)

    output_path = os.path.splitext(file_path)[0] + "_processed.jsonl"
    result.write_ndjson(output_path)
    print(f"Processed data saved to {output_path}")


if __name__ == "__main__":
    main()
