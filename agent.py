import csv
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_core.tools import Tool

load_dotenv()

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "LOG"
COLLECTION_NAME = "LOGGING"
CSV_PATH = "normal_system_logs.csv"


# ---------- MongoDB helper ----------
def _get_collection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME][COLLECTION_NAME]


# ---------- Tool 1: Load CSV into MongoDB (idempotent) ----------
def load_splunk_csv(_: str = "") -> str:
    """Load the Splunk CSV into MongoDB without duplicating rows."""
    try:
        if not os.path.exists(CSV_PATH):
            return f"CSV file not found at {CSV_PATH}"

        collection = _get_collection()
        inserted = 0
        with open(CSV_PATH, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # upsert to avoid duplicates (uses all fields as filter)
                result = collection.update_one(row, {"$setOnInsert": row}, upsert=True)
                if result.upserted_id is not None:
                    inserted += 1
        return f"Loaded CSV. Inserted {inserted} new rows (duplicates skipped)."
    except Exception as e:
        return f"Error loading CSV: {e}"


splunk_csv_load_tool = Tool(
    name="load_splunk_csv",
    description=(
        "Loads the fixed Splunk CSV file into MongoDB. "
        "No arguments needed. Use this once before reading logs."
    ),
    func=load_splunk_csv,
)


# ---------- Tool 2: Read logs from MongoDB ----------
def read_splunk_logs(query: str = "") -> str:
    """
    Read log rows from MongoDB. Optionally filter by a keyword.
    If query is empty, return the most recent 50 rows.
    """
    try:
        collection = _get_collection()
        if query.strip():
            cursor = collection.find(
                {"$or": [
                    {"message": {"$regex": query, "$options": "i"}},
                    {"raw": {"$regex": query, "$options": "i"}},
                ]}
            ).limit(50)
        else:
            cursor = collection.find().sort("_id", -1).limit(50)

        rows = []
        for doc in cursor:
            doc.pop("_id", None)
            rows.append(doc)

        if not rows:
            return "No log rows found."
        return "\n".join(str(r) for r in rows)
    except Exception as e:
        return f"Error reading logs: {e}"


splunk_log_read = Tool(
    name="read_splunk_logs",
    description=(
        "Reads log rows from MongoDB. Optionally pass a keyword to filter. "
        "Returns up to 50 matching rows."
    ),
    func=read_splunk_logs,
)


# ---------- Tool 3: Report anomaly ----------
def report_anomaly(report: str) -> str:
    try:
        with open("anomaly_report.txt", "a", encoding="utf-8") as file:
            file.write(report + "\n---\n")
        return "Anomaly reported successfully."
    except Exception as e:
        return f"Failed to report anomaly: {e}"


report_anomaly_tool = Tool(
    name="report_anomaly",
    description="Writes an anomaly report to anomaly_report.txt. Pass the report text.",
    func=report_anomaly,
)


# ---------- Tool 4: Report error ----------
def report_error(error: str) -> str:
    try:
        with open("error_report.txt", "a", encoding="utf-8") as file:
            file.write(error + "\n---\n")
        return "Error reported successfully."
    except Exception as e:
        return f"Failed to report error: {e}"


report_error_tool = Tool(
    name="report_error",
    description="Writes an error report to error_report.txt. Pass the error text.",
    func=report_error,
)


# ---------- Tool 5: Update Suricata rule ----------
def update_suricata_rule(rule: str) -> str:
    """Append a Suricata rule to the rules file (with basic sanity check)."""
    try:
        if not rule.strip():
            return "No rule provided."
        if not rule.strip().startswith(("alert", "drop", "pass", "reject")):
            return "Invalid Suricata rule: must start with alert/drop/pass/reject."

        with open("suricata_rules.txt", "a", encoding="utf-8") as file:
            file.write(rule.strip() + "\n")
        return "Suricata rule added successfully."
    except Exception as e:
        return f"Failed to update Suricata rule: {e}"


update_suricata_rule_tool = Tool(
    name="update_suricata_rule",
    description=(
        "Appends a Suricata rule to suricata_rules.txt. "
        "The rule must start with alert/drop/pass/reject."
    ),
    func=update_suricata_rule,
)