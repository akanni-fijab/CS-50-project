import os
import sqlite3

import requests


def main():
    if network_check():
        update_db()
    else:
        print("Network unavailable. Skipping database update.")
        print_stored_data()


def network_check() -> bool:
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


def update_db():
    url: str = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json"

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
        return

    date_updated = data.get("date", "Unknown")
    rates = data.get("usd", {})

    connector = sqlite3.connect("rates.db")
    cursor = connector.cursor()

    create_command = """
    CREATE TABLE IF NOT EXISTS currency(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        denomination TEXT UNIQUE,
        todollar REAL,
        last_updated TEXT
    )
    """
    cursor.execute(create_command)

    # Prepare a list of tuples for insertion
    records_to_insert = []
    for denom, rate in rates.items():
        records_to_insert.append((denom, rate, date_updated))

    upsert_command = """
    INSERT INTO currency (denomination, todollar, last_updated) 
    VALUES (?, ?, ?)
    ON CONFLICT(denomination) DO UPDATE SET 
        todollar = excluded.todollar,
        last_updated = excluded.last_updated;
    """

    cursor.executemany(upsert_command, records_to_insert)  # should be faster
    connector.commit()

    print(
        f"Successfully updated {len(records_to_insert)} currencies for date: {date_updated}"
    )

    cursor.execute(
        "SELECT denomination, todollar FROM currency WHERE denomination IN ('eur', 'gbp', 'ngn', 'jpy')"
    )
    sample_rates = cursor.fetchall()

    for denom, rate in sample_rates:
        print(f"USD to {denom.upper()}: {rate}")

    connector.close()


def print_stored_data():
    """Prints saved currency rates if the network is unavailable."""
    # Check if the database file exists first
    if not os.path.exists("rates.db"):
        print("No local data found. Please connect to the internet first.")
        return

    connector = sqlite3.connect("rates.db")
    cursor = connector.cursor()

    try:
        # Fetch a few major currencies, plus the Nigerian Naira
        cursor.execute("""
            SELECT denomination, todollar, last_updated 
            FROM currency 
            WHERE denomination IN ('eur', 'gbp', 'ngn', 'jpy', 'cad')
        """)
        rows = cursor.fetchall()

        if not rows:
            print("Database is empty.")
            return

        # We can grab the date from the first row since they were updated together
        last_updated = rows[0][2]
        print(f"Showing saved data from: {last_updated}")

        for denom, rate, _ in rows:
            print(f"USD to {denom.upper()}: {rate}")

    except sqlite3.OperationalError:
        print("Database table does not exist yet. run when online to create cache")

    finally:
        connector.close()


if __name__ == "__main__":
    main()
