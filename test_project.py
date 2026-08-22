import os
import sqlite3

from project import network_check, print_stored_data, update_db


def test_network_check():
    assert network_check() == True


def test_update_db():
    update_db()

    assert os.path.exists("rates.db") == True

    connector = sqlite3.connect("rates.db")
    cursor = connector.cursor()

    cursor.execute("SELECT COUNT(*) FROM currency")
    row_count = cursor.fetchone()[0]

    assert row_count > 50

    cursor.execute("SELECT denomination FROM currency WHERE denomination = 'eur'")
    euro_record = cursor.fetchone()

    assert euro_record is not None
    assert euro_record[0] == "eur"

    connector.close()


def test_print_stored_data(capsys):
    # 1. Run update_db() to populate the database
    update_db()

    # 2. CLEAR the captured output so we ignore update_db's prints
    capsys.readouterr()

    # 3. Run the function we actually want to test
    print_stored_data()

    # 4. Capture ONLY the output from print_stored_data
    captured = capsys.readouterr()

    # 5. Check if the expected currencies were printed
    assert "USD to NGN" in captured.out
    assert "USD to EUR" in captured.out
    assert "USD to CAD" in captured.out  # Since we see CAD in your terminal output!
