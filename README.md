# NYC Mobility Revenue Intelligence Platform

Build a SQL analytics project that answers:

“Where, when, and why do taxi/FHV trips generate the most revenue, delays, demand spikes, and abnormal patterns?”

This is not just practicing SQL. Treat it like you are an analytics engineer at Uber, Lyft, DoorDash, or a city transportation department.

## Platforms

- PostgreSQL first
- Then DuckDB for fast local analytics
- Optional advanced version: ClickHouse for huge-scale analytical queries

## Skills you will practice

- joins
- window functions
- CTEs
- subqueries
- date/time logic
- percentile analysis
- cohort analysis
- sessionization-style thinking
- anomaly detection in SQL
- data modeling
- indexing
- query optimization
- materialized views
- dimensional modeling
- business reporting

## Dataset structure

### Fact table: `fact_trips`

Columns:

- trip_id
- vendor_id
- pickup_datetime
- dropoff_datetime
- pickup_location_id
- dropoff_location_id
- passenger_count
- trip_distance
- fare_amount
- extra
- mta_tax
- tip_amount
- tolls_amount
- improvement_surcharge
- total_amount
- payment_type
- rate_code_id
- store_and_fwd_flag

### Dimension tables

#### `dim_zone`

- location_id
- borough
- zone
- service_zone

#### `dim_payment_type`

- payment_type_id
- payment_type_name

#### `dim_rate_code`

- rate_code_id
- rate_code_name

### Derived tables

- `daily_zone_metrics`
- `hourly_demand_metrics`
- `driverless_market_kpis`
- `anomaly_trips`
- `route_profitability`

## Daily routine

Do this 5 days per week, 60–90 minutes per day.

Each day:

- Write 3 SQL queries
- Rewrite one query using a different method
- Explain the query in plain English
- Add one metric to a dashboard table
- Optimize one query using `EXPLAIN ANALYZE`

The goal is not to memorize SQL. The goal is to think like this:

“What business question am I answering, what table shape do I need, and what SQL pattern solves it?”

## 8-week SQL project plan

### Week 1: Setup and basic exploration

Goal: become comfortable touching real data.

Tasks:

- Load 1–3 months of yellow taxi data.
- Load taxi zone lookup data.
- Create clean staging tables.
- Check row counts.
- Check null values.
- Check min/max pickup dates.
- Find impossible trips.
- Create a cleaned fact table.

Questions to answer:

1. How many trips are in the dataset?
2. What is the date range?
3. What are the top 10 pickup zones?
4. What are the top 10 dropoff zones?
5. What is the average fare?
6. What is the average trip distance?
7. How many trips have `total_amount <= 0`?
8. How many trips have `trip_distance = 0`?
9. Which payment type is most common?
10. What percentage of trips include a tip?

Important SQL skills:

- `COUNT()`
- `AVG()`
- `MIN()`
- `MAX()`
- `GROUP BY`
- `ORDER BY`
- `LIMIT`
- `CASE WHEN`
- `WHERE`

### Week 2: Time-based analysis

Goal: master dates and time-series SQL.

Questions:

1. Trips by day
2. Trips by hour of day
3. Revenue by day
4. Average fare by weekday
5. Average tip by hour
6. Busiest pickup hour per borough
7. Weekend vs weekday revenue
8. Morning rush vs evening rush
9. Trips grouped into 15-minute windows
10. Day-over-day revenue change

Example task:

```sql
SELECT
    DATE(pickup_datetime) AS trip_date,
    COUNT(*) AS trip_count,
    SUM(total_amount) AS revenue,
    AVG(total_amount) AS avg_order_value
FROM fact_trips
GROUP BY DATE(pickup_datetime)
ORDER BY trip_date;
```

Then rewrite it using a CTE:

```sql
WITH daily_trips AS (
    SELECT
        DATE(pickup_datetime) AS trip_date,
        total_amount
    FROM fact_trips
)
SELECT
    trip_date,
    COUNT(*) AS trip_count,
    SUM(total_amount) AS revenue,
    AVG(total_amount) AS avg_order_value
FROM daily_trips
GROUP BY trip_date
ORDER BY trip_date;
```

Skills:

- `DATE()`
- `EXTRACT()`
- `DATE_TRUNC()`
- `INTERVAL`
- CTEs
- time bucketing

### Week 3: Joins and dimensional analysis

Goal: stop querying one table only.

Questions:

1. Revenue by pickup borough
2. Revenue by dropoff borough
3. Average trip distance by borough pair
4. Most common pickup-dropoff zone pairs
5. Highest revenue routes
6. Highest tip routes
7. Which borough has the longest average trips?
8. Which zones have the highest cash usage?
9. Which zones have the highest credit-card usage?
10. Which borough produces the most airport trips?

Example:

```sql
SELECT
    pickup_zone.borough AS pickup_borough,
    dropoff_zone.borough AS dropoff_borough,
    COUNT(*) AS trips,
    AVG(t.trip_distance) AS avg_distance,
    SUM(t.total_amount) AS total_revenue
FROM fact_trips t
JOIN dim_zone pickup_zone
    ON t.pickup_location_id = pickup_zone.location_id
JOIN dim_zone dropoff_zone
    ON t.dropoff_location_id = dropoff_zone.location_id
GROUP BY
    pickup_zone.borough,
    dropoff_zone.borough
ORDER BY total_revenue DESC;
```

Skills:

- `INNER JOIN`
- `LEFT JOIN`
- self-style dimension joins
- `GROUP BY` multiple columns
- business segmentation

### Week 4: Window functions

This is where you start becoming strong.

Questions:

1. Rank pickup zones by daily revenue
2. Find top 3 zones per borough
3. Calculate 7-day moving average of trips
4. Calculate day-over-day revenue change
5. Calculate percent of total revenue by zone
6. Find each zone's best revenue day
7. Compare each trip fare to zone average
8. Find unusually high fares within each zone
9. Calculate cumulative monthly revenue
10. Rank routes by tip percentage

Example:

```sql
WITH daily_zone_revenue AS (
    SELECT
        DATE(t.pickup_datetime) AS trip_date,
        z.zone,
        SUM(t.total_amount) AS revenue
    FROM fact_trips t
    JOIN dim_zone z
        ON t.pickup_location_id = z.location_id
    GROUP BY DATE(t.pickup_datetime), z.zone
)
SELECT
    trip_date,
    zone,
    revenue,
    RANK() OVER (
        PARTITION BY trip_date
        ORDER BY revenue DESC
    ) AS daily_rank
FROM daily_zone_revenue;
```

Skills:

- `ROW_NUMBER()`
- `RANK()`
- `DENSE_RANK()`
- `LAG()`
- `LEAD()`
- `SUM() OVER`
- `AVG() OVER`
- `PARTITION BY`
- moving averages

### Week 5: Advanced business metrics

Goal: think like a data analyst, not just a SQL student.

Build these metrics:

- `gross_revenue`
- `average_fare`
- `average_tip`
- `tip_rate`
- `tip_percentage`
- `revenue_per_mile`
- `revenue_per_minute`
- `trip_duration_minutes`
- `airport_trip_rate`
- `cash_payment_rate`
- `rush_hour_trip_rate`

Questions:

1. What zones have the highest revenue per mile?
2. What routes are long but low revenue?
3. What routes are short but highly profitable?
4. What hours have the best tip percentage?
5. Do airport trips tip better?
6. Do longer trips produce higher tip percentage?
7. What is the average trip duration by borough?
8. Which pickup zones have poor revenue efficiency?
9. Which zones have demand but low average fare?
10. Which time windows have high demand but low tip rate?

Example:

```sql
SELECT
    z.zone,
    COUNT(*) AS trips,
    SUM(t.total_amount) AS revenue,
    SUM(t.total_amount) / NULLIF(SUM(t.trip_distance), 0) AS revenue_per_mile,
    AVG(t.tip_amount / NULLIF(t.total_amount, 0)) AS avg_tip_percentage
FROM fact_trips t
JOIN dim_zone z
    ON t.pickup_location_id = z.location_id
WHERE t.trip_distance > 0
  AND t.total_amount > 0
GROUP BY z.zone
HAVING COUNT(*) >= 100
ORDER BY revenue_per_mile DESC;
```

Important pattern:

- `NULLIF(value, 0)` to avoid division-by-zero errors.

### Week 6: Data quality and anomaly detection

Goal: become dangerous with messy real data.

Create an `anomaly_trips` table.

Flag trips where:

- `trip_distance <= 0`
- `total_amount <= 0`
- `fare_amount <= 0`
- `trip_duration_minutes <= 0`
- `trip_duration_minutes > 240`
- `trip_distance > 100`
- `fare_amount > 500`
- `tip_amount > total_amount`
- `average_speed_mph > 80`

Questions:

1. What percentage of trips are suspicious?
2. Which vendors have the most anomalies?
3. Which zones have the most zero-distance trips?
4. Are anomalies more common at certain hours?
5. Do cash trips have more suspicious values?
6. What are the most common anomaly types?
7. How much revenue is affected by bad records?
8. Which borough has the highest anomaly rate?
9. Are airport trips more likely to be outliers?
10. What filters should define the clean analytics table?

Example:

```sql
SELECT
    *,
    CASE
        WHEN trip_distance <= 0 THEN 'zero_or_negative_distance'
        WHEN total_amount <= 0 THEN 'zero_or_negative_total'
        WHEN EXTRACT(EPOCH FROM (dropoff_datetime - pickup_datetime)) / 60 <= 0 THEN 'bad_duration'
        WHEN trip_distance > 100 THEN 'extreme_distance'
        WHEN total_amount > 500 THEN 'extreme_amount'
        ELSE 'normal'
    END AS anomaly_type
FROM fact_trips;
```

### Week 7: Performance and optimization

Goal: write SQL that works on big data.

Tasks:

- Run `EXPLAIN ANALYZE` on slow queries
- Add indexes
- Compare query before/after index
- Create materialized views
- Partition by pickup month
- Compare raw table vs aggregate table performance
- Test query speed on 1 month vs 6 months vs 1 year
- Create summary tables
- Avoid `SELECT *`
- Rewrite correlated subqueries as joins

Indexes to try:

```sql
CREATE INDEX idx_trips_pickup_datetime
ON fact_trips (pickup_datetime);

CREATE INDEX idx_trips_pickup_location
ON fact_trips (pickup_location_id);

CREATE INDEX idx_trips_dropoff_location
ON fact_trips (dropoff_location_id);

CREATE INDEX idx_trips_payment_type
ON fact_trips (payment_type);
```

Materialized view:

```sql
CREATE MATERIALIZED VIEW daily_zone_metrics AS
SELECT
    DATE(t.pickup_datetime) AS trip_date,
    z.borough,
    z.zone,
    COUNT(*) AS trips,
    SUM(t.total_amount) AS revenue,
    AVG(t.total_amount) AS avg_fare,
    AVG(t.trip_distance) AS avg_distance
FROM fact_trips t
JOIN dim_zone z
    ON t.pickup_location_id = z.location_id
GROUP BY
    DATE(t.pickup_datetime),
    z.borough,
    z.zone;
```

Then query the materialized view instead of the raw table.

### Week 8: Final capstone

Build a full SQL analytics report:

“NYC Taxi Market Performance Report”

Your final report should answer:

1. What are the highest-revenue pickup zones?
2. What are the highest-growth pickup zones?
3. What hours have the most demand?
4. What hours have the highest revenue efficiency?
5. What borough pairs generate the most money?
6. Which routes have high demand but low revenue?
7. Which zones are declining week over week?
8. Which routes have abnormal fares?
9. What payment types produce the highest tips?
10. What business recommendations would you make?

Deliverables:

- `/sql`
  - `01_schema.sql`
  - `02_load_data.sql`
  - `03_cleaning.sql`
  - `04_basic_eda.sql`
  - `05_time_analysis.sql`
  - `06_zone_analysis.sql`
  - `07_window_functions.sql`
  - `08_anomaly_detection.sql`
  - `09_performance_optimization.sql`
  - `10_final_report.sql`
- `README.md`
- `data_dictionary.md`
- `business_report.md`

This becomes a serious portfolio project.

## Daily question list

Use these as your daily SQL drills.

### Beginner/intermediate daily questions

1. Count total trips
2. Count trips by day
3. Count trips by hour
4. Average fare by day
5. Average distance by day
6. Revenue by payment type
7. Top 10 pickup zones
8. Top 10 dropoff zones
9. Average tip by payment type
10. Weekend vs weekday trips

### Intermediate questions

11. Top zone per borough by revenue
12. Top 3 routes by revenue per borough
13. Average fare by pickup/dropoff borough pair
14. Revenue per mile by route
15. Tip percentage by hour
16. Cash usage by borough
17. Airport trip revenue
18. Rush-hour revenue vs non-rush-hour revenue
19. Longest average routes
20. Shortest high-revenue routes

### Advanced questions

21. 7-day moving average of revenue
22. Day-over-day revenue growth
23. Week-over-week trip growth
24. Rank zones by daily revenue
25. Find each zone's best day
26. Find routes whose revenue dropped 30% week over week
27. Find trips above the 99th percentile fare
28. Find zones with high demand and low tip rate
29. Find unusually fast trips
30. Find unusually slow trips

### Pro-level questions

31. Build a clean fact table from raw data
32. Build a daily aggregate table
33. Build a route-level aggregate table
34. Build anomaly detection rules
35. Build a materialized dashboard table
36. Optimize a slow revenue query
37. Compare CTE vs temp table vs materialized view
38. Partition trips by month
39. Write a query that explains revenue decline
40. Create a final business recommendation report

## Weekly breakdown

### Monday: Exploration

Write 3 queries:

- basic counts
- group by time
- group by zone

Then write 5 bullet insights.

Example:

1. Midtown had the highest pickup volume.
2. Credit card trips had higher average tips.
3. Rush hour had more trips but not always higher revenue per mile.

### Tuesday: Joins

Write 3 queries joining:

- `fact_trips`
- `dim_zone`
- `dim_payment_type`

Focus on borough, zone, and payment analysis.

### Wednesday: Window functions

Write 3 queries using:

- `RANK()`
- `LAG()`
- `AVG() OVER`
- `SUM() OVER`

No basic `GROUP BY` only queries allowed.

### Thursday: Data quality

- Find bad data.
- Create flags.
- Write cleanup rules.
- Compare metrics before and after cleanup.

### Friday: Performance

Pick your slowest query.

Run:

`EXPLAIN ANALYZE`

Then improve it using:

- indexes
- filtering
- materialized views
- better joins
- less `SELECT *`

Make it harder: add a fake business goal.

Pretend the CEO asks:

“We want to know where to focus driver incentives next month.”

Your job is to answer with SQL.

Identify zones with:

- high demand
- low driver supply proxy
- high fare potential
- high wait/time inefficiency
- good revenue per mile
- growth over time

Since you may not have driver supply directly, create proxy metrics:

- `trips_per_hour`
- `revenue_per_trip`
- `revenue_per_mile`
- `avg_duration`
- `growth_rate`
- `repeat route frequency`

Final recommendation:

Prioritize pickup zones where demand is growing, revenue per mile is high, and trip volume is consistent across multiple days.

## Best pro SQL concepts to master from this project

- `WITH cte AS (...)`
- `JOIN`
- `LEFT JOIN`
- `GROUP BY`
- `HAVING`
- `CASE WHEN`
- `DATE_TRUNC`
- `EXTRACT`
- `INTERVAL`
- `NULLIF`
- `COALESCE`
- `ROW_NUMBER`
- `RANK`
- `DENSE_RANK`
- `LAG`
- `LEAD`
- `SUM() OVER`
- `AVG() OVER`
- `PERCENTILE_CONT`
- `CREATE VIEW`
- `CREATE MATERIALIZED VIEW`
- `CREATE INDEX`
- `EXPLAIN ANALYZE`

## Recommendation

Do NYC Taxi Analytics instead of a small Kaggle dataset.

It is closer to real work because it has:

- messy records
- time-series behavior
- location dimensions
- payment behavior
- revenue metrics
- big data performance problems
- real business questions

That is exactly the type of SQL practice that makes you strong enough for Data Analyst, Data Scientist, Analytics Engineer, Data Engineer, and ML Engineer interviews.

JOIN dim_zone dropoff_zone
    ON t.dropoff_location_id = dropoff_zone.location_id
GROUP BY
    pickup_zone.borough,
    dropoff_zone.borough
ORDER BY total_revenue DESC;

Skills:

INNER JOIN
LEFT JOIN
self-style dimension joins
GROUP BY multiple columns
business segmentation
Week 4: Window functions

This is where you start becoming strong.

Questions:

-- 1. Rank pickup zones by daily revenue
-- 2. Find top 3 zones per borough
-- 3. Calculate 7-day moving average of trips
-- 4. Calculate day-over-day revenue change
-- 5. Calculate percent of total revenue by zone
-- 6. Find each zone's best revenue day
-- 7. Compare each trip fare to zone average
-- 8. Find unusually high fares within each zone
-- 9. Calculate cumulative monthly revenue
-- 10. Rank routes by tip percentage

Example:

WITH daily_zone_revenue AS (
    SELECT
        DATE(t.pickup_datetime) AS trip_date,
        z.zone,
        SUM(t.total_amount) AS revenue
    FROM fact_trips t
    JOIN dim_zone z
        ON t.pickup_location_id = z.location_id
    GROUP BY DATE(t.pickup_datetime), z.zone
)
SELECT
    trip_date,
    zone,
    revenue,
    RANK() OVER (
        PARTITION BY trip_date
        ORDER BY revenue DESC
    ) AS daily_rank
FROM daily_zone_revenue;

Skills:

ROW_NUMBER()
RANK()
DENSE_RANK()
LAG()
LEAD()
SUM() OVER
AVG() OVER
PARTITION BY
moving averages
Week 5: Advanced business metrics

Goal: think like a data analyst, not just a SQL student.

Build these metrics:

gross_revenue
average_fare
average_tip
tip_rate
tip_percentage
revenue_per_mile
revenue_per_minute
trip_duration_minutes
airport_trip_rate
cash_payment_rate
rush_hour_trip_rate

Questions:

-- 1. What zones have the highest revenue per mile?
-- 2. What routes are long but low revenue?
-- 3. What routes are short but highly profitable?
-- 4. What hours have the best tip percentage?
-- 5. Do airport trips tip better?
-- 6. Do longer trips produce higher tip percentage?
-- 7. What is the average trip duration by borough?
-- 8. Which pickup zones have poor revenue efficiency?
-- 9. Which zones have demand but low average fare?
-- 10. Which time windows have high demand but low tip rate?

Example:

SELECT
    z.zone,
    COUNT(*) AS trips,
    SUM(t.total_amount) AS revenue,
    SUM(t.total_amount) / NULLIF(SUM(t.trip_distance), 0) AS revenue_per_mile,
    AVG(t.tip_amount / NULLIF(t.total_amount, 0)) AS avg_tip_percentage
FROM fact_trips t
JOIN dim_zone z
    ON t.pickup_location_id = z.location_id
WHERE t.trip_distance > 0
  AND t.total_amount > 0
GROUP BY z.zone
HAVING COUNT(*) >= 100
ORDER BY revenue_per_mile DESC;

Important pattern:

NULLIF(value, 0)

Use it to avoid division-by-zero errors.

Week 6: Data quality and anomaly detection

Goal: become dangerous with messy real data.

Create an anomaly_trips table.

Flag trips where:

trip_distance <= 0
total_amount <= 0
fare_amount <= 0
trip_duration_minutes <= 0
trip_duration_minutes > 240
trip_distance > 100
fare_amount > 500
tip_amount > total_amount
average_speed_mph > 80

Questions:

-- 1. What percentage of trips are suspicious?
-- 2. Which vendors have the most anomalies?
-- 3. Which zones have the most zero-distance trips?
-- 4. Are anomalies more common at certain hours?
-- 5. Do cash trips have more suspicious values?
-- 6. What are the most common anomaly types?
-- 7. How much revenue is affected by bad records?
-- 8. Which borough has the highest anomaly rate?
-- 9. Are airport trips more likely to be outliers?
-- 10. What filters should define the clean analytics table?

Example:

SELECT
    *,
    CASE
        WHEN trip_distance <= 0 THEN 'zero_or_negative_distance'
        WHEN total_amount <= 0 THEN 'zero_or_negative_total'
        WHEN EXTRACT(EPOCH FROM (dropoff_datetime - pickup_datetime)) / 60 <= 0 THEN 'bad_duration'
        WHEN trip_distance > 100 THEN 'extreme_distance'
        WHEN total_amount > 500 THEN 'extreme_amount'
        ELSE 'normal'
    END AS anomaly_type
FROM fact_trips;
Week 7: Performance and optimization

Goal: write SQL that works on big data.

Tasks:

-- 1. Run EXPLAIN ANALYZE on slow queries
-- 2. Add indexes
-- 3. Compare query before/after index
-- 4. Create materialized views
-- 5. Partition by pickup month
-- 6. Compare raw table vs aggregate table performance
-- 7. Test query speed on 1 month vs 6 months vs 1 year
-- 8. Create summary tables
-- 9. Avoid SELECT *
-- 10. Rewrite correlated subqueries as joins

Indexes to try:

CREATE INDEX idx_trips_pickup_datetime
ON fact_trips (pickup_datetime);

CREATE INDEX idx_trips_pickup_location
ON fact_trips (pickup_location_id);

CREATE INDEX idx_trips_dropoff_location
ON fact_trips (dropoff_location_id);

CREATE INDEX idx_trips_payment_type
ON fact_trips (payment_type);

Materialized view:

CREATE MATERIALIZED VIEW daily_zone_metrics AS
SELECT
    DATE(t.pickup_datetime) AS trip_date,
    z.borough,
    z.zone,
    COUNT(*) AS trips,
    SUM(t.total_amount) AS revenue,
    AVG(t.total_amount) AS avg_fare,
    AVG(t.trip_distance) AS avg_distance
FROM fact_trips t
JOIN dim_zone z
    ON t.pickup_location_id = z.location_id
GROUP BY
    DATE(t.pickup_datetime),
    z.borough,
    z.zone;

Then query the materialized view instead of the raw table.

Week 8: Final capstone

Build a full SQL analytics report:

“NYC Taxi Market Performance Report”

Your final report should answer:

-- 1. What are the highest-revenue pickup zones?
-- 2. What are the highest-growth pickup zones?
-- 3. What hours have the most demand?
-- 4. What hours have the highest revenue efficiency?
-- 5. What borough pairs generate the most money?
-- 6. Which routes have high demand but low revenue?
-- 7. Which zones are declining week over week?
-- 8. Which routes have abnormal fares?
-- 9. What payment types produce the highest tips?
-- 10. What business recommendations would you make?

Deliverables:

/sql
  01_schema.sql
  02_load_data.sql
  03_cleaning.sql
  04_basic_eda.sql
  05_time_analysis.sql
  06_zone_analysis.sql
  07_window_functions.sql
  08_anomaly_detection.sql
  09_performance_optimization.sql
  10_final_report.sql

README.md
data_dictionary.md
business_report.md

This becomes a serious portfolio project.

Daily question list

Use these as your daily SQL drills.

Beginner/intermediate daily questions
-- 1. Count total trips
-- 2. Count trips by day
-- 3. Count trips by hour
-- 4. Average fare by day
-- 5. Average distance by day
-- 6. Revenue by payment type
-- 7. Top 10 pickup zones
-- 8. Top 10 dropoff zones
-- 9. Average tip by payment type
-- 10. Weekend vs weekday trips
Intermediate questions
-- 11. Top zone per borough by revenue
-- 12. Top 3 routes by revenue per borough
-- 13. Average fare by pickup/dropoff borough pair
-- 14. Revenue per mile by route
-- 15. Tip percentage by hour
-- 16. Cash usage by borough
-- 17. Airport trip revenue
-- 18. Rush-hour revenue vs non-rush-hour revenue
-- 19. Longest average routes
-- 20. Shortest high-revenue routes
Advanced questions
-- 21. 7-day moving average of revenue
-- 22. Day-over-day revenue growth
-- 23. Week-over-week trip growth
-- 24. Rank zones by daily revenue
-- 25. Find each zone's best day
-- 26. Find routes whose revenue dropped 30% week over week
-- 27. Find trips above the 99th percentile fare
-- 28. Find zones with high demand and low tip rate
-- 29. Find unusually fast trips
-- 30. Find unusually slow trips
Pro-level questions
-- 31. Build a clean fact table from raw data
-- 32. Build a daily aggregate table
-- 33. Build a route-level aggregate table
-- 34. Build anomaly detection rules
-- 35. Build a materialized dashboard table
-- 36. Optimize a slow revenue query
-- 37. Compare CTE vs temp table vs materialized view
-- 38. Partition trips by month
-- 39. Write a query that explains revenue decline
-- 40. Create a final business recommendation report
The exact daily routine I would follow
Monday: Exploration

Write 3 queries:

-- basic counts
-- group by time
-- group by zone

Then write 5 bullet insights.

Example:

1. Midtown had the highest pickup volume.
2. Credit card trips had higher average tips.
3. Rush hour had more trips but not always higher revenue per mile.
Tuesday: Joins

Write 3 queries joining:

fact_trips
dim_zone
dim_payment_type

Focus on borough, zone, and payment analysis.

Wednesday: Window functions

Write 3 queries using:

RANK()
LAG()
AVG() OVER
SUM() OVER

No basic GROUP BY only queries allowed.

Thursday: Data quality

Find bad data.

Create flags.

Write cleanup rules.

Compare metrics before and after cleanup.

Friday: Performance

Pick your slowest query.

Run:

EXPLAIN ANALYZE

Then improve it using:

indexes
filtering
materialized views
better joins
less SELECT *
Make it harder: add a fake business goal

Pretend the CEO asks:

“We want to know where to focus driver incentives next month.”

Your job is to answer with SQL.

You need to identify zones with:

high demand
low driver supply proxy
high fare potential
high wait/time inefficiency
good revenue per mile
growth over time

Since you may not have driver supply directly, create proxy metrics:

trips_per_hour
revenue_per_trip
revenue_per_mile
avg_duration
growth_rate
repeat route frequency

Final recommendation:

Prioritize pickup zones where demand is growing, revenue per mile is high, and trip volume is consistent across multiple days.
Best “pro” SQL concepts to master from this project

By the end, you should be comfortable with:

WITH cte AS (...)
JOIN
LEFT JOIN
GROUP BY
HAVING
CASE WHEN
DATE_TRUNC
EXTRACT
INTERVAL
NULLIF
COALESCE
ROW_NUMBER
RANK
DENSE_RANK
LAG
LEAD
SUM() OVER
AVG() OVER
PERCENTILE_CONT
CREATE VIEW
CREATE MATERIALIZED VIEW
CREATE INDEX
EXPLAIN ANALYZE
My recommendation

Do NYC Taxi Analytics instead of a small Kaggle dataset.

It is closer to real work because it has:

messy records
time-series behavior
location dimensions
payment behavior
revenue metrics
big data performance problems
real business questions

That is exactly the type of SQL practice that makes you strong enough for Data Analyst, Data Scientist, Analytics Engineer, Data Engineer, and ML Engineer interviews.