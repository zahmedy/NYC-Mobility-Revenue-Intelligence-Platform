from pathlib import Path
import requests
from tqdm import tqdm


BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

DATA_DIR = Path("data/nyc_taxi")
TRIP_TYPE = "yellow"  # options: yellow, green, fhv, fhvhv


def download_file(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        print(f"Already exists: {output_path}")
        return

    print(f"Downloading: {url}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))

    with open(output_path, "wb") as file, tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        desc=output_path.name,
    ) as progress:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)
                progress.update(len(chunk))


def download_taxi_data(start_year: int, start_month: int, end_year: int, end_month: int) -> None:
    for year in range(start_year, end_year + 1):
        first_month = start_month if year == start_year else 1
        last_month = end_month if year == end_year else 12

        for month in range(first_month, last_month + 1):
            file_name = f"{TRIP_TYPE}_tripdata_{year}-{month:02d}.parquet"
            url = f"{BASE_URL}/{file_name}"
            output_path = DATA_DIR / "trips" / str(year) / file_name

            try:
                download_file(url, output_path)
            except requests.HTTPError:
                print(f"Not available yet or invalid file: {file_name}")


def download_zone_lookup() -> None:
    output_path = DATA_DIR / "lookup" / "taxi_zone_lookup.csv"
    download_file(ZONE_LOOKUP_URL, output_path)


if __name__ == "__main__":
    download_zone_lookup()

    # Example: download January to March 2025 yellow taxi data
    download_taxi_data(
        start_year=2025,
        start_month=1,
        end_year=2025,
        end_month=3,
    )