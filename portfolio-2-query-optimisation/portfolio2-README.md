# Portfolio 2: Query Optimisation for MivaDB

## Aim

Measure how slow three typical MivaDB queries are on a realistic amount of data, fix them, and show the improvement with `EXPLAIN ANALYZE`.

## Test data

`seed.py` fills the database with fake data using Faker, with a fixed random seed so the data is the same on every run.

| Table | Rows |
|---|---|
| students | 50,000 |
| enrolments | 250,000 |
| results | 208,458 |

Environment: PostgreSQL 18, queried through pgAdmin 4.

## How I measured

Each query was run with `EXPLAIN ANALYZE` and repeated three times. I report the fastest run, because the first run has to warm the cache and single runs varied a lot (query A ranged from 3.3 ms to 11.6 ms before indexing). Times are read from the top node of the plan.

## The three queries

**A: find students by surname**

```sql
SELECT * FROM students WHERE last_name = 'Olugbayila';
```

**B: everyone enrolled in one offering**

```sql
SELECT * FROM enrolments WHERE offering_id = 100;
```

**C: top 10 courses by average score**

```sql
SELECT c.course_code, ROUND(AVG(r.total), 2) AS avg_total
FROM results r
JOIN enrolments e ON e.enrolment_id = r.enrolment_id
JOIN course_offerings o ON o.offering_id = e.offering_id
JOIN courses c ON c.course_id = o.course_id
GROUP BY c.course_code
ORDER BY avg_total DESC
LIMIT 10;
```

## Results

| Query | Fix | Plan before | Plan after | Time before | Time after |
|---|---|---|---|---|---|
| A: students by surname | Index on `last_name` | Seq Scan (49,810 rows discarded) | Bitmap Heap Scan | 3.3 ms | about 0.5 ms |
| B: enrolments by offering | Index on `offering_id` | Parallel Seq Scan | Bitmap Heap Scan | about 235 ms | about 1.2 ms |
| C: top courses | Materialized view | Parallel seq scans and hash joins | Seq Scan on 60 precomputed rows | about 630 ms | about 0.66 ms |

## What I changed

```sql
CREATE INDEX idx_students_last_name ON students (last_name);
CREATE INDEX idx_enrolments_offering_id ON enrolments (offering_id);
ANALYZE;

CREATE MATERIALIZED VIEW course_avg_scores AS
SELECT c.course_code, ROUND(AVG(r.total), 2) AS avg_total
FROM results r
JOIN enrolments e ON e.enrolment_id = r.enrolment_id
JOIN course_offerings o ON o.offering_id = e.offering_id
JOIN courses c ON c.course_id = o.course_id
GROUP BY c.course_code;
```

Query C is now answered with:

```sql
SELECT * FROM course_avg_scores ORDER BY avg_total DESC LIMIT 10;
```

## Findings

**Indexes fix lookups.** A and B each need a handful of rows out of a big table. Without an index Postgres reads every row and throws most of them away. B shows it best: the unique constraint on `(student_id, offering_id)` does not help a search on `offering_id` alone, because `offering_id` is not the first column, and Postgres does not index foreign key columns automatically.

**Why the plan says Bitmap Heap Scan.** Both queries return hundreds of rows, so Postgres first collects the matching row locations from the index and then reads them in page order, which is cheaper than jumping to each row one by one.

**Indexes do not fix aggregations over everything.** Query C averages over all 208,458 results, so it has to read nearly every row whatever indexes exist. The fix was to compute the answer once and store it.

## What these fixes cost

| Cost | Detail |
|---|---|
| Disk space | `idx_students_last_name` is 368 kB and `idx_enrolments_offering_id` is 1,776 kB |
| Slower writes | Every insert or update on those tables now has to update the index too. This matters for the enrolment rush in Portfolio 3 |
| Stale data | The materialized view does not update itself. It shows the averages as of the last refresh |

To bring the view up to date, run:

```sql
REFRESH MATERIALIZED VIEW course_avg_scores;
```

The refresh costs about as much as the original query C, so it should run on a schedule (for example nightly or after results are published), not on every request.

## Files in this folder

- `seed.py`: generates the test data (run with `py seed.py`)
- `screenshots/`: `EXPLAIN ANALYZE` plans before and after each fix
