# Advanced Database Portfolio: MivaDB

**Course:** MIT 8103 Advanced Database Systems (Miva Open University)
**Student:** Moyinoluwa Toluwase Agbo

## Selected case study: MivaDB

- **Organisation / scenario:** MivaDB, a simulated student management and results system modelled on Miva Open University.
- **Nature of the system:** an online university that registers students into programmes and courses each semester, records their results, and delivers teaching through an LMS.
- **Users:** students, lecturers, programme coordinators and registry staff.
- **Major data:** programmes, lecturers, semesters, courses, students, course offerings, enrolments and results (relational data), and LMS activity events such as logins, video views, quiz attempts, forum posts and assignment submissions (document data).
- **Key operations:** register students for course offerings within seat limits, enter and look up results, report average scores per course, and record and query LMS activity.

All five portfolio activities use this same case study. All data is synthetic, generated with Faker and my own Python scripts, so no real student data is used.

## About the project

The five portfolios take the MivaDB case study through the full life of a database: design, performance tuning, transactions, NoSQL, and distribution.

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
| 3 | Without locking, both sessions saw one free seat and only the CHECK constraint stopped overbooking, returning a raw error. With `FOR UPDATE`, the second session waits, sees the offering is full (1204 of 1204) and rolls back cleanly |
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
