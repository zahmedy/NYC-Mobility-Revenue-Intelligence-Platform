SELECT 
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE pickup_datetime IS NULL) AS null_pick_datetime,
    COUNT(*) FILTER (WHERE dropoff_datetime IS NULL) AS null_pick_datetime,
    COUNT(*) FILTER (WHERE passenger_count IS NULL) AS null_passenger_count,
    COUNT(*) FILTER (WHERE trip_distance IS NULL) AS null_trip_distance 
FROM fact_trips;

-- Min/Max Pickup dates
SELECT
    MIN(pickup_datetime) AS earliest_pickup,
    MAX(pickup_datetime) as latest_pickup
FROM fact_trips;

-- Impossible trips
SELECT *
FROM fact_trips
WHERE dropoff_datetime <= pickup_datetime
    OR trip_distance <= 0
    OR fare_amount < 0
    OR passenger_count <= 0;

-- Cleaned fact table
CREATE TABLE fact_trips_clean AS
SELECT
    trip_id,
    pickup_datetime,
    dropoff_datetime,
    passenger_count,
    trip_distance,
    fare_amount,
    tip_amount,
    pickup_location_id,
    dropoff_location_id
FROM fact_trips
WHERE pickup_datetime IS NOT NULL
    AND dropoff_datetime IS NOT NULL
    AND dropoff_datetime > pickup_datetime
    AND trip_distance > 0
    AND fare_amount >= 0
    AND passenger_count > 0;