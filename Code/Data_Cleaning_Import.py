import os
import pickle
import xmlrpc.client
from datetime import datetime

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from tqdm import tqdm


def parse_time(timestamp):
    """
    Parse various time formats to datetime.
    """
    if isinstance(timestamp, xmlrpc.client.DateTime):
        return pd.to_datetime(timestamp.value)
    if isinstance(timestamp, pd._libs.tslibs.timestamps.Timestamp) or isinstance(
        timestamp, datetime
    ):
        return pd.Timestamp(timestamp)
    return None


def get_table_columns(conn, table):
    """
    Get the column names and type codes of the table from the given PostgreSQL connection object and table name.
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    table_columns = {desc[0]: desc[1] for desc in cursor.description}
    cursor.close()
    return table_columns


def create_database(dbname="bugzilla", password="123456"):
    """
    Create a PostgreSQL database named 'bugzilla'.
    """
    try:
        conn = psycopg2.connect(
            f"host=localhost user=postgres password={password}")
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {dbname}")
    except psycopg2.Error as error:
        print(error)
    finally:
        cursor.close()
        conn.close()


def connect_database(dbname="bugzilla", password="123456"):
    """
    Connect to the PostgreSQL database named 'bugzilla'.
    """
    try:
        conn = psycopg2.connect(
            f"host=localhost dbname={dbname} user=postgres password={password}"
        )
    except psycopg2.Error as error:
        print(error)
    return conn


def run_query(conn, query):
    """
    Execute the query using the specified connection.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except psycopg2.Error as error:
        print(error)
        cursor.execute("END TRANSACTION")
    finally:
        conn.commit()
        cursor.close()


# Create database
create_database(dbname="bugzilla", password="123456")
# Connect to database
conn = connect_database(dbname="bugzilla", password="123456")
# Set up tables
run_query(conn, open("DBMS_session.sql").read())


# Setup insert queries
users_insert_sql = """
INSERT INTO users (id, email, name, nick, real_name)
VALUES
(%(id)s, %(email)s, %(name)s, %(nick)s, %(real_name)s)
ON CONFLICT (id) DO NOTHING
"""

report_columns = get_table_columns(conn, "reports")
report_insert_sql = (
    """
INSERT INTO reports
VALUES
("""
    + ", ".join([f"%({col})s" for col in report_columns])
    + ") ON CONFLICT DO NOTHING"
)

comment_columns = get_table_columns(conn, "comments")
comment_insert_sql = (
    """
INSERT INTO comments
VALUES
("""
    + ", ".join([f"%({col})s" for col in comment_columns])
    + ") ON CONFLICT DO NOTHING"
)

changes_columns = get_table_columns(conn, "changes_history")
changes_insert_sql = (
    """
INSERT INTO changes_history
VALUES
("""
    + ", ".join([f"%({col})s" for col in changes_columns])
    + ") ON CONFLICT DO NOTHING"
)

flag_columns = get_table_columns(conn, "flags")
flag_insert_sql = (
    """
INSERT INTO flags
VALUES
("""
    + ", ".join([f"%({col})s" for col in flag_columns])
    + ") ON CONFLICT DO NOTHING"
)

custom_fields_columns = get_table_columns(conn, "custom_fields")
custom_fields_insert_sql = (
    """
INSERT INTO custom_fields
VALUES
("""
    + ", ".join([f"%({col})s" for col in custom_fields_columns])
    + ")"
)

user_fields = [
    "assigned_to_detail",
    "cc_detail",
    "qa_contact_detail",
    "creator_detail",
]

timestamp_fields = [
    "last_change_time",
    "cf_last_resolved",
    "creation_time",
    "last_change_time",
]

for pklfiles in tqdm(os.listdir(".bugs")):

    # Skip if not a pickle file
    if not pklfiles.endswith(".pickle"):
        continue

    try:
        with open(os.path.join(".bugs", pklfiles), "rb") as f:
            bug_report = pickle.load(f)
    except Exception as e:
        print(f"Error while reading {pklfiles}: {e}")
        continue

    # Skip if the bug is an error
    if bug_report.get("err"):
        continue

    cursor = conn.cursor()

    # 1. ------------- Convert timestamps
    # 1.1. ----- Timestamps columns
    for timestamp_field in timestamp_fields:
        timestamp_str = bug_report.get(timestamp_field)

        if timestamp_str is not None:
            bug_report[timestamp_field] = parse_time(timestamp_str)

    # 1.2. ----- Comments
    # Skip if there's no comments
    if bug_report.get("comments") is not None:
        for comment in bug_report["comments"]:
            for comment_time_field in ["creation_time", "time"]:
                comment[comment_time_field] = parse_time(
                    comment[comment_time_field]
                )

    # 1.3. ----- History
    bugs = bug_report.get("bugs")

    # Skip if bug report is empty
    if bugs:
        history = bugs[0].get("history")

        for change in history:
            change["when"] = parse_time(change["when"])

    # 2. ------------- Users table
    user_info_to_insert = []

    # 2.1. -------- Gather user info
    for user_field in user_fields:
        # Skip if the field does not exist or empty
        if bug_report.get(user_field) is None:
            continue

        if user_field in ["cc_detail"]:
            for user_info in bug_report[user_field]:
                user_info_to_insert.append(user_info)
        else:
            user_info_to_insert.append(bug_report[user_field])

    # 2.2. --------- Insert
    execute_batch(cursor, users_insert_sql, user_info_to_insert)

    # 3. ----------------- Reports
    # 3.1. -------- Impute missing values

    # Impute values in case of missing values
    impute_values = {
        16: False,  # Boolean
        23: 0,  # Integer
        25: "",  # String
        1007: [],  # list of integers
        1009: [],  # list of strings
        1114: None,  # Timestamp
    }

    # 3.2. --------- Insert

    data = {}
    for col in report_columns:
        data[col] = bug_report.get(col, impute_values[report_columns[col]])

    data["bug_id"] = bug_report["id"]

    data["assigned_to_id"] = bug_report["assigned_to_detail"]["id"]
    data["creator_id"] = bug_report["creator_detail"]["id"]

    try:
        data["qa_contact_id"] = bug_report["qa_contact_detail"]["id"]
    except KeyError:
        data["qa_contact_id"] = None

    data["cc_id"] = [cc_detail["id"] for cc_detail in bug_report["cc_detail"]]

    try:
        data["mentors_id"] = [
            mentors["id"] for mentors in bug_report["mentors_detail"]
        ]
    except KeyError:
        data["mentors_id"] = None

    cursor.execute(report_insert_sql, data)

    # 4. ----------------- Comments
    comments_to_insert = []
    for comment in bug_report["comments"]:
        comments_to_insert.append(comment)

    execute_batch(cursor, comment_insert_sql, comments_to_insert)

    # 5. ----------------- Changes history
    change_history_to_insert = []

    for history in bug_report["bugs"][0]["history"]:
        for change in history["changes"]:
            change_history_to_insert.append(
                {
                    "when": history["when"],
                    "who": history["who"],
                    "field_name": change["field_name"],
                    "added": str(change.get("added")),
                    "removed": str(change.get("removed")),
                    "bug_id": bug_report["id"],
                }
            )

    execute_batch(cursor, changes_insert_sql, change_history_to_insert)

    # 5. ----------------- Flags
    if bug_report.get("flags"):
        flag_to_insert = []

        for flag in bug_report["flags"]:
            flag["creation_date"] = parse_time(flag["creation_date"])
            flag["modification_date"] = parse_time(flag["modification_date"])
            flag["bug_id"] = bug_report["id"]

            flag_to_insert.append(flag)

        execute_batch(cursor, flag_insert_sql, flag_to_insert)

    # 6. ----------------- Custom fields
    custom_fields_to_insert = []
    for field in bug_report.keys():
        if field.startswith("cf_"):
            custom_fields_to_insert.append(
                {
                    "bug_id": bug_report["id"],
                    "cf_field_name": field,
                    "value": bug_report[field],
                }
            )

    execute_batch(
        cursor,
        custom_fields_insert_sql,
        custom_fields_to_insert,
    )

    # End
    cursor.close()
    conn.commit()

print("Done")
