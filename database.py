import sqlite3
from datetime import datetime

DB_NAME = "foodwaste.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            price REAL NOT NULL,
            reason TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_record(food_name, category, quantity, unit, price, reason, date=None):
    conn = connect()
    cursor = conn.cursor()

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO waste_records
        (food_name, category, quantity, unit, price, reason, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (food_name, category, quantity, unit, price, reason, date))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return new_id


def get_records():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, food_name, category, quantity,
               unit, price, reason, date
        FROM waste_records
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    conn.close()

    return records


def get_record_by_id(record_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, food_name, category, quantity,
               unit, price, reason, date
        FROM waste_records
        WHERE id = ?
    """, (record_id,))

    record = cursor.fetchone()
    conn.close()

    return record


def delete_record(record_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM waste_records WHERE id = ?",
        (record_id,)
    )

    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted


def get_timeline_data():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, SUM(quantity), SUM(quantity * price), COUNT(*)
        FROM waste_records
        GROUP BY date
        ORDER BY date ASC
    """)

    result = cursor.fetchall()
    conn.close()

    return result


def get_summary():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COALESCE(SUM(quantity), 0),
            COALESCE(SUM(quantity * price), 0),
            COUNT(*)
        FROM waste_records
    """)

    result = cursor.fetchone()
    conn.close()

    return result


def get_category_data():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(quantity)
        FROM waste_records
        GROUP BY category
    """)

    result = cursor.fetchall()
    conn.close()

    return result


def get_reason_data():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reason, COUNT(*)
        FROM waste_records
        GROUP BY reason
        ORDER BY COUNT(*) DESC
    """)

    result = cursor.fetchall()
    conn.close()

    return result


def get_food_frequency():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT food_name, COUNT(*), SUM(quantity)
        FROM waste_records
        GROUP BY food_name
        ORDER BY COUNT(*) DESC
    """)

    result = cursor.fetchall()
    conn.close()

    return result