"""
queries_mongo.py - Portfolio 4 (NoSQL)
Runs 5 queries on mivadb_logs.lms_activity and compares the student lookup
before and after adding an index. Reads the connection string from MONGO_URI.
"""
import os
import time

from pymongo import MongoClient

uri = os.environ.get("MONGO_URI")
if not uri:
    raise SystemExit("MONGO_URI is not set.")

client = MongoClient(uri)
db = client["mivadb_logs"]
col = db["lms_activity"]

STUDENT = 12345


def explain_student_lookup():
    """Explain the 'one student's activity' query with execution stats."""
    res = db.command({
        "explain": {
            "find": "lms_activity",
            "filter": {"student_id": STUDENT},
            "sort": {"timestamp": -1},
        },
        "verbosity": "executionStats",
    })
    stats = res["executionStats"]
    plan = str(res["queryPlanner"]["winningPlan"])
    scan = "COLLSCAN (full scan)" if "COLLSCAN" in plan else "IXSCAN (uses index)"
    print(f"  Plan: {scan}")
    print(f"  Docs examined: {stats['totalDocsExamined']:,}")
    print(f"  Docs returned: {stats['nReturned']:,}")
    print(f"  Time: {stats['executionTimeMillis']} ms")


def timed(label, pipeline):
    start = time.perf_counter()
    rows = list(col.aggregate(pipeline))
    ms = (time.perf_counter() - start) * 1000
    print(f"\n{label}  ({ms:.0f} ms)")
    for r in rows:
        print("  ", r)


print("=" * 60)
print("Total documents:", f"{col.count_documents({}):,}")

# ---- BEFORE INDEX ----
col.drop_indexes()  # removes all indexes except the default _id index
print("\nQ1 BEFORE index: all activity for one student, newest first")
explain_student_lookup()

# ---- Q2 to Q5: aggregation queries ----
timed("Q2: Events per type", [
    {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
])

timed("Q3: Average quiz score per course", [
    {"$match": {"event_type": "quiz_attempt"}},
    {"$group": {"_id": "$course_code",
                "avg_score": {"$avg": "$details.score"},
                "attempts": {"$sum": 1}}},
    {"$sort": {"avg_score": -1}},
])

timed("Q4: Top 5 most active students", [
    {"$group": {"_id": "$student_id", "events": {"$sum": 1}}},
    {"$sort": {"events": -1}},
    {"$limit": 5},
])

timed("Q5: Late assignment submissions per course", [
    {"$match": {"event_type": "assignment_submit", "details.late": True}},
    {"$group": {"_id": "$course_code", "late_submissions": {"$sum": 1}}},
    {"$sort": {"late_submissions": -1}},
])

# ---- AFTER INDEX ----
print("\nCreating index on (student_id, timestamp)...")
col.create_index([("student_id", 1), ("timestamp", -1)], name="idx_student_time")

print("\nQ1 AFTER index: all activity for one student, newest first")
explain_student_lookup()

print("\nIndexes now on the collection:")
for name in col.index_information():
    print("  -", name)
