-- =====================================================================
-- Portfolio 3: Transactions and Concurrency (MivaDB, PostgreSQL 18)
-- Run in pgAdmin 4 Query Tool. Run one statement at a time unless a
-- block is marked "run together".
-- Demo 3 needs TWO Query Tool tabs (session A and session B).
-- =====================================================================


-- ---------------------------------------------------------------------
-- Step 0: reset any open transaction, then check the starting state
-- (a "no transaction in progress" warning is harmless)
-- ---------------------------------------------------------------------
ROLLBACK;

SELECT offering_id, capacity, seats_taken
FROM course_offerings
WHERE offering_id = 1;          -- expected: capacity 1012, seats_taken 686


-- ---------------------------------------------------------------------
-- DEMO 1: COMMIT (atomic enrolment, student 3 -> offering 1)
-- Run together.
-- ---------------------------------------------------------------------
BEGIN;

INSERT INTO enrolments (student_id, offering_id, enrolled_at)
VALUES (3, 1, now());

UPDATE course_offerings
SET seats_taken = seats_taken + 1
WHERE offering_id = 1;

COMMIT;

-- Checks (run separately)
SELECT seats_taken FROM course_offerings WHERE offering_id = 1;   -- 687
SELECT * FROM enrolments WHERE student_id = 3 AND offering_id = 1; -- 1 row


-- ---------------------------------------------------------------------
-- DEMO 2: ROLLBACK (student 4 -> offering 1)
-- Run the block below together. The transaction stays open.
-- ---------------------------------------------------------------------
BEGIN;

INSERT INTO enrolments (student_id, offering_id, enrolled_at)
VALUES (4, 1, now());

UPDATE course_offerings
SET seats_taken = seats_taken + 1
WHERE offering_id = 1;

SELECT seats_taken FROM course_offerings WHERE offering_id = 1;   -- 688 inside the transaction

-- Now undo everything (run on its own)
ROLLBACK;

-- Checks (run separately)
SELECT seats_taken FROM course_offerings WHERE offering_id = 1;    -- back to 687
SELECT * FROM enrolments WHERE student_id = 4 AND offering_id = 1; -- 0 rows


-- ---------------------------------------------------------------------
-- DEMO 3: THE LAST-SEAT RACE (offering 2, capacity 1204)
-- ---------------------------------------------------------------------

-- Setup (session A): leave exactly one seat
UPDATE course_offerings SET seats_taken = capacity - 1 WHERE offering_id = 2;
SELECT capacity, seats_taken FROM course_offerings WHERE offering_id = 2;  -- 1204, 1203


-- ----- Part 1: WITHOUT locking (the bug) -----
-- Run in this exact order, one statement at a time:
--
-- A: BEGIN;
-- A: SELECT capacity, seats_taken FROM course_offerings WHERE offering_id = 2;   -- sees 1 seat left
-- B: BEGIN;
-- B: SELECT capacity, seats_taken FROM course_offerings WHERE offering_id = 2;   -- also sees 1 seat left
-- A: UPDATE course_offerings SET seats_taken = seats_taken + 1 WHERE offering_id = 2;
-- A: COMMIT;
-- B: UPDATE course_offerings SET seats_taken = seats_taken + 1 WHERE offering_id = 2;
--    -> ERROR: new row for relation "course_offerings" violates check constraint
--       "course_offerings_check"   (the CHECK constraint stops 1205 of 1204)
-- B: ROLLBACK;
--
-- Final check (either session):
-- SELECT capacity, seats_taken FROM course_offerings WHERE offering_id = 2;      -- 1204, 1204


-- ----- Part 2: WITH SELECT ... FOR UPDATE (the fix) -----
-- Reset (session A):
UPDATE course_offerings SET seats_taken = capacity - 1 WHERE offering_id = 2;

-- Then, in this exact order:
--
-- A: BEGIN;
-- A: SELECT capacity, seats_taken FROM course_offerings WHERE offering_id = 2 FOR UPDATE;
-- B: BEGIN;
-- B: SELECT capacity, seats_taken FROM course_offerings WHERE offering_id = 2 FOR UPDATE;
--    -> B WAITS (spinner). Screenshot it now.
-- A: UPDATE course_offerings SET seats_taken = seats_taken + 1 WHERE offering_id = 2;
-- A: COMMIT;
--    -> B's SELECT now finishes and shows 1204 of 1204 (offering full)
-- B: ROLLBACK;   -- B refuses the enrolment cleanly, no overbooking
