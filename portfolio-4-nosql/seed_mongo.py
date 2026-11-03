"""
seed_mongo.py - Portfolio 4 (NoSQL)
Seeds MongoDB Atlas with LMS activity logs for MivaDB.

The connection string is read from the MONGO_URI environment variable,
so no password is ever stored in this file or pushed to GitHub.
"""
import os
import random
from datetime import datetime, timedelta

from pymongo import MongoClient

TOTAL_EVENTS = 100_000   # change this if you want more or fewer
NUM_STUDENTS = 50_000    # matches the 50,000 students seeded in Postgres
BATCH_SIZE = 5_000

uri = os.environ.get("MONGO_URI")
if not uri:
    raise SystemExit("MONGO_URI is not set. See instructions.")

client = MongoClient(uri)
col = client["mivadb_logs"]["lms_activity"]

random.seed(42)

COURSES = ["CSC101", "CSC201", "MTH101", "PHY101", "BUS201",
           "ECO101", "ENG101", "STA201", "CSC301", "IFT201"]
EVENT_TYPES = ["login", "video_view", "quiz_attempt", "forum_post", "assignment_submit"]
EVENT_WEIGHTS = [30, 30, 15, 10, 15]
DEVICES = ["android", "windows", "iphone", "mac"]
FORUM_SNIPPETS = ["Can someone explain this?", "Thanks, that helped",
                  "Is the deadline extended?", "Sharing my notes"]


def make_event():
    event_type = random.choices(EVENT_TYPES, EVENT_WEIGHTS)[0]
    ts = datetime.utcnow() - timedelta(
        days=random.randint(0, 90),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    doc = {
        "student_id": random.randint(1, NUM_STUDENTS),
        "event_type": event_type,
        "timestamp": ts,
        "course_code": random.choice(COURSES),
    }
    # Each event type carries different fields - this is why MongoDB fits.
    if event_type == "login":
        doc["details"] = {"device": random.choice(DEVICES),
                          "session_minutes": random.randint(1, 180)}
    elif event_type == "video_view":
        doc["details"] = {"video_id": f"VID{random.randint(1, 200):03d}",
                          "minutes_watched": random.randint(1, 60)}
    elif event_type == "quiz_attempt":
        doc["details"] = {"quiz_id": f"QZ{random.randint(1, 50):02d}",
                          "score": random.randint(0, 10), "out_of": 10}
    elif event_type == "forum_post":
        doc["details"] = {"thread_id": random.randint(1, 500),
                          "message": random.choice(FORUM_SNIPPETS)}
    else:  # assignment_submit
        doc["details"] = {"assignment_id": f"AS{random.randint(1, 30):02d}",
                          "late": random.random() < 0.15}
    return doc


print("Clearing old data...")
col.delete_many({})

inserted = 0
while inserted < TOTAL_EVENTS:
    batch = [make_event() for _ in range(min(BATCH_SIZE, TOTAL_EVENTS - inserted))]
    col.insert_many(batch)
    inserted += len(batch)
    print(f"Inserted {inserted:,} / {TOTAL_EVENTS:,}")

print("Done. Total documents:", col.count_documents({}))
