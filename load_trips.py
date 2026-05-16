from __future__ import annotations

import argparse
import io
import os
from pathlib import Path

import pandas as pd
import psycopg
import pyarrow.parquet as pq


DEFAULT_DATABASE_URL = "postgresql://localhost/nyc_mobility"
DEFAULT_TRIP_DIR = Path("data/nyc_taxi/trips/2025")

FACT_TABLE = "fact_trips"
MANIFEST_TABLE = "trip_load_manifest"

COLUMN_MAP = {
    "VendorID": "vendor_id",
    "tpep_pickup_datetime": "pickup_datetime",
    "tpep_dropoff_datetime": "dropoff_datetime",
    "PULocationID": "pickup_location_id",
    "DOLocationID": "dropoff_location_id",
    "passenger_count": "passenger_count",
    "trip_distance": "trip_distance",
    "fare_amount": "fare_amount",
    "extra": "extra",
    "mta_tax": "mta_tax",
    "tip_amount": "tip_amount",
    "tolls_amount": "tolls_amount",
    "improvement_surcharge": "improvement_surcharge",
    "total_amount": "total_amount",
    "payment_type": "payment_type",
    "RatecodeID": "rate_code_id",
    "store_and_fwd_flag": "store_and_fwd_flag",
    "congestion_surcharge": "congestion_surcharge",
    "Airport_fee": "airport_fee",
    "cbd_congestion_fee": "cbd_congestion_fee",
}

SOURCE_COLUMNS = list(COLUMN_MAP)
COPY_COLUMNS = list(COLUMN_MAP.values())
INTEGER_COLUMNS = [
    "vendor_id",
    "pickup_location_id",
    "dropoff_location_id",
    "passenger_count",
    "payment_type",
    "rate_code_id",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fast, idempotent loader for NYC TLC yellow taxi Parquet files."
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL),
        help=f"Postgres connection URL. Defaults to {DEFAULT_DATABASE_URL!r}.",
    )
    parser.add_argument(
        "--trip-dir",
        type=Path,
        default=DEFAULT_TRIP_DIR,
        help=f"Directory containing Parquet files. Defaults to {DEFAULT_TRIP_DIR}.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100_000,
        help="Rows per Parquet batch copied into Postgres.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Drop and rebuild fact_trips and the load manifest before loading.",
    )
    parser.add_argument(
        "--no-indexes",
        action="store_true",
        help="Skip creating analytics indexes after loading.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the files that would be loaded without changing Postgres.",
    )
    return parser.parse_args()


def find_trip_files(trip_dir: Path) -> list[Path]:
    return sorted(trip_dir.glob("*.parquet"))


def ensure_schema(conn: psycopg.Connection, replace: bool) -> None:
    with conn.cursor() as cur:
        if replace:
            cur.execute(f"DROP TABLE IF EXISTS {MANIFEST_TABLE};")
            cur.execute(f"DROP TABLE IF EXISTS {FACT_TABLE};")

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {FACT_TABLE} (
                trip_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                vendor_id integer,
                pickup_datetime timestamp without time zone NOT NULL,
                dropoff_datetime timestamp without time zone NOT NULL,
                pickup_location_id integer,
                dropoff_location_id integer,
                passenger_count integer,
                trip_distance double precision,
                fare_amount double precision,
                extra double precision,
                mta_tax double precision,
                tip_amount double precision,
                tolls_amount double precision,
                improvement_surcharge double precision,
                total_amount double precision,
                payment_type integer,
                rate_code_id integer,
                store_and_fwd_flag text,
                congestion_surcharge double precision,
                airport_fee double precision,
                cbd_congestion_fee double precision
            );
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {MANIFEST_TABLE} (
                file_path text PRIMARY KEY,
                file_size_bytes bigint NOT NULL,
                file_modified_at timestamp without time zone NOT NULL,
                file_rows bigint NOT NULL,
                loaded_rows bigint NOT NULL,
                loaded_at timestamp with time zone NOT NULL DEFAULT now()
            );
            """
        )

        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
            """,
            (FACT_TABLE,),
        )
        actual_columns = [row[0] for row in cur.fetchall()]

    expected_columns = ["trip_id", *COPY_COLUMNS]
    if actual_columns != expected_columns:
        raise SystemExit(
            f"{FACT_TABLE} already exists with a different schema.\n"
            "Run with --replace to rebuild it from the local Parquet files."
        )


def create_indexes(conn: psycopg.Connection) -> None:
    statements = [
        f"CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime ON {FACT_TABLE} (pickup_datetime);",
        f"CREATE INDEX IF NOT EXISTS idx_trips_pickup_location ON {FACT_TABLE} (pickup_location_id);",
        f"CREATE INDEX IF NOT EXISTS idx_trips_dropoff_location ON {FACT_TABLE} (dropoff_location_id);",
        f"CREATE INDEX IF NOT EXISTS idx_trips_payment_type ON {FACT_TABLE} (payment_type);",
    ]
    with conn.cursor() as cur:
        for statement in statements:
            cur.execute(statement)


def loaded_file_status(
    conn: psycopg.Connection, path: Path
) -> tuple[bool, str | None]:
    stat = path.stat()
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT file_size_bytes, file_modified_at
            FROM {MANIFEST_TABLE}
            WHERE file_path = %s;
            """,
            (str(path),),
        )
        row = cur.fetchone()

    if row is None:
        return False, None

    loaded_size, loaded_modified_at = row
    current_modified_at = pd.Timestamp.fromtimestamp(stat.st_mtime).to_pydatetime()
    if loaded_size != stat.st_size or loaded_modified_at != current_modified_at:
        return True, "changed"

    return True, None


def prepare_batch(batch: object) -> pd.DataFrame:
    df = batch.to_pandas()
    missing_columns = set(SOURCE_COLUMNS) - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Parquet file is missing required columns: {missing}")

    df = df.rename(columns=COLUMN_MAP)
    df = df[COPY_COLUMNS]

    for column in INTEGER_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

    return df


def copy_dataframe(
    conn: psycopg.Connection,
    df: pd.DataFrame,
) -> None:
    csv_buffer = io.StringIO()
    df.to_csv(
        csv_buffer,
        index=False,
        header=False,
        na_rep="",
        date_format="%Y-%m-%d %H:%M:%S",
    )
    csv_buffer.seek(0)

    column_list = ", ".join(COPY_COLUMNS)
    copy_sql = (
        f"COPY {FACT_TABLE} ({column_list}) "
        "FROM STDIN WITH (FORMAT CSV, NULL '')"
    )
    with conn.cursor() as cur:
        with cur.copy(copy_sql) as copy:
            copy.write(csv_buffer.getvalue())


def load_file(conn: psycopg.Connection, path: Path, batch_size: int) -> int:
    parquet_file = pq.ParquetFile(path)
    expected_rows = parquet_file.metadata.num_rows
    loaded_rows = 0

    print(f"Loading {path} ({expected_rows:,} rows)", flush=True)

    with conn.transaction():
        for batch in parquet_file.iter_batches(
            batch_size=batch_size,
            columns=SOURCE_COLUMNS,
        ):
            df = prepare_batch(batch)
            copy_dataframe(conn, df)
            loaded_rows += len(df)
            print(
                f"  copied {loaded_rows:,}/{expected_rows:,} rows",
                flush=True,
            )

        stat = path.stat()
        modified_at = pd.Timestamp.fromtimestamp(stat.st_mtime).to_pydatetime()
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {MANIFEST_TABLE}
                    (file_path, file_size_bytes, file_modified_at, file_rows, loaded_rows)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (str(path), stat.st_size, modified_at, expected_rows, loaded_rows),
            )

    return loaded_rows


def main() -> None:
    args = parse_args()
    trip_files = find_trip_files(args.trip_dir)
    if not trip_files:
        raise SystemExit(f"No Parquet files found in {args.trip_dir}")

    print("Trip files:")
    for path in trip_files:
        print(f"  {path}")

    if args.dry_run:
        return

    with psycopg.connect(args.database_url) as conn:
        ensure_schema(conn, replace=args.replace)

        total_loaded = 0
        for path in trip_files:
            already_loaded, reason = loaded_file_status(conn, path)
            if already_loaded and reason == "changed":
                raise SystemExit(
                    f"{path} was loaded before, but the local file changed.\n"
                    "Run with --replace to rebuild from the current files."
                )
            if already_loaded:
                print(f"Skipping already-loaded file: {path}", flush=True)
                continue

            total_loaded += load_file(conn, path, args.batch_size)

        if not args.no_indexes:
            print("Creating indexes", flush=True)
            create_indexes(conn)

    print(f"Done. Loaded {total_loaded:,} new rows.", flush=True)


if __name__ == "__main__":
    main()
