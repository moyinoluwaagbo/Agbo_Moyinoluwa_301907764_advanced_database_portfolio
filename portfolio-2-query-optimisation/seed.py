"""
seed.py - fills the MivaDB PostgreSQL database with fake data.

Creates: 8 programmes, 6 semesters, 40 lecturers, 60 courses,
360 course offerings, 50,000 students, ~250,000 enrolments and results.

Usage:
    python seed.py            (fails if tables already have data)
    python seed.py --reset    (empties all tables first, then reseeds)
"""

import random
import sys
import time
from datetime import date
from getpass import getpass

import psycopg2
from faker import Faker
from psycopg2.extras import execute_values

# ---- settings you may want to change -------------------------------------
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "mivadb"
DB_USER = "postgres"

N_STUDENTS = 50_000
N_LECTURERS = 40
N_COURSES = 60
ENROLMENTS_PER_STUDENT = 5
RANDOM_SEED = 42  # same seed = same data every run
# ---------------------------------------------------------------------------

random.seed(RANDOM_SEED)

try:
    fake = Faker(["yo_NG", "ig_NG", "ha_NG"])  # Nigerian names
except Exception:
    fake = Faker()  # fallback if those locales are not installed
Faker.seed(RANDOM_SEED)

PROGRAMMES = [
    ("BSc Computer Science", "Undergraduate"),
    ("BSc Cybersecurity", "Undergraduate"),
    ("BSc Business Administration", "Undergraduate"),
    ("BSc Accounting", "Undergraduate"),
    ("BSc Economics", "Undergraduate"),
    ("MSc Information Technology", "Masters"),
    ("MSc Data Science", "Masters"),
    ("MBA", "Masters"),
]

SEMESTERS = [
    ("Feb 2024", date(2024, 2, 1), date(2024, 7, 15)),
    ("Aug 2024", date(2024, 8, 1), date(2024, 12, 20)),
    ("Feb 2025", date(2025, 2, 1), date(2025, 7, 15)),
    ("Aug 2025", date(2025, 8, 1), date(2025, 12, 20)),
    ("Feb 2026", date(2026, 2, 1), date(2026, 7, 15)),
    ("Aug 2026", date(2026, 8, 1), date(2026, 12, 20)),  # current, no results yet
]

DEPARTMENTS = [
    "Computing", "Cybersecurity", "Business", "Accounting",
    "Economics", "Mathematics", "General Studies",
]
COURSE_PREFIXES = ["CSC", "CYB", "BUS", "ACC", "ECO", "MTH", "GST", "MIT"]
COHORT_YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
COHORT_WEIGHTS = [8, 12, 18, 24, 22, 16]


def step(msg):
    print(f"  {msg}...", flush=True)


def main():
    reset = "--reset" in sys.argv
    password = getpass(f"Password for {DB_USER}: ")

    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=password
    )
    conn.autocommit = False
    cur = conn.cursor()
    started = time.time()

    # ---- safety check ----
    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] > 0:
        if reset:
            step("Emptying existing data")
            cur.execute(
                "TRUNCATE results, enrolments, course_offerings, students, "
                "courses, lecturers, semesters, programmes RESTART IDENTITY CASCADE"
            )
        else:
            print("Tables already contain data. Run with --reset to start over.")
            conn.close()
            return

    # ---- programmes ----
    step("Programmes")
    execute_values(cur, "INSERT INTO programmes (name, level) VALUES %s", PROGRAMMES)
    cur.execute("SELECT programme_id FROM programmes ORDER BY programme_id")
    programme_ids = [r[0] for r in cur.fetchall()]

    # ---- semesters ----
    step("Semesters")
    execute_values(
        cur, "INSERT INTO semesters (name, start_date, end_date) VALUES %s", SEMESTERS
    )
    cur.execute("SELECT semester_id FROM semesters ORDER BY start_date")
    semester_ids = [r[0] for r in cur.fetchall()]
    current_semester_id = semester_ids[-1]

    # ---- lecturers ----
    step("Lecturers")
    lecturers = []
    for i in range(1, N_LECTURERS + 1):
        first, last = fake.first_name(), fake.last_name()
        email = f"{first}.{last}{i}@miva.edu.ng".lower().replace(" ", "")
        lecturers.append((first, last, email, random.choice(DEPARTMENTS)))
    execute_values(
        cur,
        "INSERT INTO lecturers (first_name, last_name, email, department) VALUES %s",
        lecturers,
    )
    cur.execute("SELECT lecturer_id FROM lecturers ORDER BY lecturer_id")
    lecturer_ids = [r[0] for r in cur.fetchall()]

    # ---- courses ----
    step("Courses")
    courses, used_codes = [], set()
    while len(courses) < N_COURSES:
        code = f"{random.choice(COURSE_PREFIXES)}{random.choice([1, 2, 3, 4, 8])}{random.randint(0, 9)}{random.randint(1, 9)}"
        if code in used_codes:
            continue
        used_codes.add(code)
        title = f"Introduction to {fake.word().title()} {random.choice(['Systems', 'Methods', 'Theory', 'Practice', 'Analysis'])}"
        courses.append((code, title, random.choice([2, 3, 3, 4])))
    execute_values(
        cur, "INSERT INTO courses (course_code, title, credit_units) VALUES %s", courses
    )
    cur.execute("SELECT course_id FROM courses ORDER BY course_id")
    course_ids = [r[0] for r in cur.fetchall()]

    # ---- course offerings (every course in every semester) ----
    step("Course offerings")
    offerings = [
        (c, s, random.choice(lecturer_ids), random.randint(1000, 1500))
        for c in course_ids
        for s in semester_ids
    ]
    execute_values(
        cur,
        "INSERT INTO course_offerings (course_id, semester_id, lecturer_id, capacity) VALUES %s",
        offerings,
    )
    cur.execute("SELECT offering_id, semester_id FROM course_offerings ORDER BY offering_id")
    offering_rows = cur.fetchall()
    offering_ids = [r[0] for r in offering_rows]
    offering_semester = {r[0]: r[1] for r in offering_rows}

    # ---- students ----
    step(f"{N_STUDENTS:,} students")
    students = []
    for i in range(1, N_STUDENTS + 1):
        first, last = fake.first_name(), fake.last_name()
        cohort = random.choices(COHORT_YEARS, COHORT_WEIGHTS)[0]
        matric = f"MIV/{cohort}/{i:06d}"
        email = f"{first}.{last}{i}@student.miva.edu.ng".lower().replace(" ", "")
        status = random.choices(
            ["active", "deferred", "graduated", "withdrawn"], [80, 4, 12, 4]
        )[0]
        students.append(
            (matric, first, last, email, random.choice(programme_ids), cohort, status)
        )
    execute_values(
        cur,
        "INSERT INTO students (matric_no, first_name, last_name, email, "
        "programme_id, cohort_year, status) VALUES %s",
        students,
        page_size=10_000,
    )
    cur.execute("SELECT student_id FROM students ORDER BY student_id")
    student_ids = [r[0] for r in cur.fetchall()]

    # ---- enrolments ----
    step(f"~{N_STUDENTS * ENROLMENTS_PER_STUDENT:,} enrolments")
    enrolments = []
    for sid in student_ids:
        for oid in random.sample(offering_ids, ENROLMENTS_PER_STUDENT):
            enrolments.append((sid, oid))
    execute_values(
        cur,
        "INSERT INTO enrolments (student_id, offering_id) VALUES %s",
        enrolments,
        page_size=20_000,
    )

    # ---- results (none for the current semester) ----
    step("Results")
    cur.execute("SELECT enrolment_id, offering_id FROM enrolments")
    results = []
    for enrolment_id, offering_id in cur.fetchall():
        if offering_semester[offering_id] == current_semester_id:
            continue
        ca = round(min(40, max(0, random.gauss(25, 7))), 2)
        exam = round(min(60, max(0, random.gauss(36, 12))), 2)
        results.append((enrolment_id, ca, exam))
    execute_values(
        cur,
        "INSERT INTO results (enrolment_id, ca_score, exam_score) VALUES %s",
        results,
        page_size=20_000,
    )

    # ---- keep seats_taken in sync with real enrolments ----
    step("Syncing seats_taken")
    cur.execute(
        """
        UPDATE course_offerings o
        SET seats_taken = c.n
        FROM (SELECT offering_id, COUNT(*) AS n FROM enrolments GROUP BY offering_id) c
        WHERE o.offering_id = c.offering_id
        """
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nDone in {time.time() - started:.1f} seconds.")


if __name__ == "__main__":
    main()
