CREATE TABLE programmes (
    programme_id   SERIAL PRIMARY KEY,
    name           VARCHAR(100) NOT NULL UNIQUE,
    level          VARCHAR(20) NOT NULL CHECK (level IN ('Undergraduate', 'Masters'))
);

CREATE TABLE lecturers (
    lecturer_id    SERIAL PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    email          VARCHAR(100) NOT NULL UNIQUE,
    department     VARCHAR(100) NOT NULL
);

CREATE TABLE semesters (
    semester_id    SERIAL PRIMARY KEY,
    name           VARCHAR(30) NOT NULL UNIQUE,
    start_date     DATE NOT NULL,
    end_date       DATE NOT NULL,
    CHECK (end_date > start_date)
);

CREATE TABLE courses (
    course_id      SERIAL PRIMARY KEY,
    course_code    VARCHAR(15) NOT NULL UNIQUE,
    title          VARCHAR(150) NOT NULL,
    credit_units   SMALLINT NOT NULL CHECK (credit_units BETWEEN 1 AND 6)
);

CREATE TABLE students (
    student_id     SERIAL PRIMARY KEY,
    matric_no      VARCHAR(20) NOT NULL UNIQUE,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    email          VARCHAR(100) NOT NULL UNIQUE,
    programme_id   INT NOT NULL REFERENCES programmes(programme_id),
    cohort_year    SMALLINT NOT NULL,
    status         VARCHAR(15) NOT NULL DEFAULT 'active'
                   CHECK (status IN ('active', 'deferred', 'graduated', 'withdrawn')),
    created_at     TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE course_offerings (
    offering_id    SERIAL PRIMARY KEY,
    course_id      INT NOT NULL REFERENCES courses(course_id),
    semester_id    INT NOT NULL REFERENCES semesters(semester_id),
    lecturer_id    INT NOT NULL REFERENCES lecturers(lecturer_id),
    capacity       INT NOT NULL CHECK (capacity > 0),
    seats_taken    INT NOT NULL DEFAULT 0,
    UNIQUE (course_id, semester_id),
    CHECK (seats_taken >= 0 AND seats_taken <= capacity)
);

CREATE TABLE enrolments (
    enrolment_id   SERIAL PRIMARY KEY,
    student_id     INT NOT NULL REFERENCES students(student_id),
    offering_id    INT NOT NULL REFERENCES course_offerings(offering_id),
    enrolled_at    TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (student_id, offering_id)
);

CREATE TABLE results (
    result_id      SERIAL PRIMARY KEY,
    enrolment_id   INT NOT NULL UNIQUE REFERENCES enrolments(enrolment_id),
    ca_score       NUMERIC(5,2) NOT NULL CHECK (ca_score BETWEEN 0 AND 40),
    exam_score     NUMERIC(5,2) NOT NULL CHECK (exam_score BETWEEN 0 AND 60),
    total          NUMERIC(5,2) GENERATED ALWAYS AS (ca_score + exam_score) STORED
);