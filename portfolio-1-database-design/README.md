# Portfolio 1: Database Design and Modelling for MivaDB

## Case study

MivaDB simulates the student management and results system of a Nigerian online university. It tracks students, the programmes they belong to, the courses offered each semester, who teaches them, who enrolled, and the results they got.

Course seats are limited, so many students can try to register for the same course at the same time. That makes the system a good fit for studying indexing, transactions and concurrency, and scaling in the later portfolios.

## Design

The database has eight tables:

- `programmes`: the degree programmes a student can belong to
- `students`: each student, linked to one programme
- `lecturers`: teaching staff
- `semesters`: academic terms with start and end dates
- `courses`: the course catalogue (code, title, credit units)
- `course_offerings`: a course taught in a specific semester by a specific lecturer, with a seat capacity
- `enrolments`: a student registered on an offering
- `results`: CA and exam scores for an enrolment, with the total calculated by the database

## Contents of this folder

- `schema.sql`: the full PostgreSQL schema with primary keys, foreign keys and constraints
- `er-diagram.png`: the entity relationship diagram generated from the database in pgAdmin
- `normalisation.md`: why the design reaches 3NF, with two deliberate design choices explained

## How to recreate the database

1. Create an empty PostgreSQL database named `mivadb`.
2. Open `schema.sql` in the pgAdmin Query Tool, connected to `mivadb`.
3. Run the whole script. It creates all eight tables.
