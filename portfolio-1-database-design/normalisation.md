# MivaDB: Normalisation

## The problem with one flat table

To see why I split MivaDB into eight tables, imagine it as a single flat table with these columns: student name, matric no, email, programme name, level, course code, course title, units, semester, lecturer name, lecturer email, department, capacity, CA score, exam score and total. Every row would be one student taking one course, and four problems follow.

- **Redundancy.** A student's name, email and programme would repeat on every course row they take. Five courses means five copies.
- **Update anomaly.** If a lecturer's email changes, I would have to correct it in hundreds of rows. Missing one leaves the data contradicting itself.
- **Insert anomaly.** I couldn't record a new course until a student enrolled in it, because the course only exists inside a student's row.
- **Delete anomaly.** If the only student on a course leaves, deleting that row also deletes the course's title, units and lecturer.

## 1NF: atomic values, no repeating groups

A student taking five courses must not have them crammed into one cell. In MivaDB each enrolment is its own row in `enrolments`, every column holds a single value, and every table has a primary key (`student_id`, `course_id`, `enrolment_id` and so on). Names are split into `first_name` and `last_name` rather than stored as one string.

## 2NF: no partial dependencies

In the flat table the natural key would be student + course + semester. But course title and units depend only on the course, and student name depends only on the student, so they depend on part of the key. I moved them out: `students`, `courses` and `semesters` are their own tables, and `enrolments` only links a student to an offering.

The clearest example is the split between `courses` and `course_offerings`. A course (its code, title and credit units) never changes. An offering is that course in a particular semester, with a lecturer and a capacity, and that changes every term. Without the split I would repeat the course details every semester, and a title correction would have to be made in many places.

The design also enforces its own rules. `enrolments` has a unique constraint on student and offering, so a student can't enrol in the same offering twice, and `course_offerings` is unique on course and semester.

## 3NF: no transitive dependencies

Every non-key column should depend on the key and nothing else.

- `students.programme_id` determines the programme name and level, so those live in `programmes` and the student row only holds the foreign key.
- `course_offerings.lecturer_id` determines the lecturer's name, email and department, so those live in `lecturers`.

Now a lecturer's email is stored once, and changing it is a single update.

## Two deliberate choices

**Calculated values.** `results.total` is derived from CA score plus exam score, so a purist could argue it breaks 3NF. I made it a generated column so the database computes it and it can never drift out of sync with its inputs. Grade (A, B, C) is not stored at all and is worked out in a query when needed.

**A deliberate denormalisation.** `course_offerings.seats_taken` could be derived by counting rows in `enrolments`. I kept it anyway so the capacity check in Phase 3 is a fast lock on a single row instead of a count under contention. It is a trade-off I made on purpose, to keep the seat race safe and quick. The cost is that every enrolment must update `seats_taken` in the same transaction, or the number drifts. I handle this in Portfolio 3.
