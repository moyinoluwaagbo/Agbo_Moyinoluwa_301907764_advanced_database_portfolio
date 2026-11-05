# Advanced Database Portfolio: MivaDB

**Course:** MIT 8103 Advanced Database Systems (Miva Open University)
**Student:** Moyinoluwa Toluwase Agbo

## About the project

MivaDB is a simulated student management and results system modelled on a university like Miva. The five portfolios take one case study through the full life of a database: design, performance tuning, transactions, NoSQL, and distribution.

The data is synthetic, generated with scripts in this repository. No real student data is used.

## Repository structure

| Folder | Topic | What it shows |
|---|---|---|
| `portfolio-1-database-design` | Design and normalisation | Schema for programmes, lecturers, semesters, courses, students, course offerings, enrolments and results, an ER diagram, and a normalisation write-up |
| `portfolio-2-query-optimisation` | Indexing and query tuning | 50,000 students and 250,000 enrolments seeded, with `EXPLAIN ANALYZE` before and after indexes and a materialized view |
| `portfolio-3-transactions-concurrency` | Transactions and concurrency | Commit, rollback, and a two-session seat-booking race fixed with `SELECT ... FOR UPDATE` |
| `portfolio-4-nosql` | MongoDB | 100,000 LMS activity events in MongoDB Atlas, five queries, and an index comparison |
| `portfolio-5-distributed-cloud` | Replication and sharding | PostgreSQL primary and replica in Docker, proof of replication, and a discussion of sharding by cohort |

Each folder has its own README with the method, evidence and screenshots.

## Headline results

| Portfolio | Result |
|---|---|
| 2 | Enrolments by offering: about 235 ms before an index, about 1.2 ms after. Top courses by average score: about 630 ms before, about 0.66 ms with a materialized view |
| 3 | Without row locking, two students could take the last seat. With `FOR UPDATE`, the second session waits and is correctly refused |
| 4 | Student activity lookup in MongoDB: full scan of 100,000 documents in 89 ms, versus 4 documents examined in 1 ms with a compound index |
| 5 | The replica streams changes from the primary and refuses direct writes |

## Technology

- PostgreSQL 18 with pgAdmin (Portfolios 1 to 3)
- Python 3.15 with Faker, psycopg2 and pymongo (data generation and queries)
- MongoDB Atlas with Compass (Portfolio 4)
- Docker and Docker Compose with PostgreSQL 16 (Portfolio 5)
- Git and GitHub for version control

## Running the projects

Each portfolio folder explains how to reproduce its results. No passwords or connection strings are stored in this repository: the MongoDB connection string is read from the `MONGO_URI` environment variable, and the Docker setup uses throwaway demo credentials for local testing only.
