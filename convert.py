import sqlite3
from project import network_check, update_db

def get_exchange_rate(cursor, denomination: str) -> float:
    cursor.execute(
        "SELECT todollar FROM currency WHERE denomination = ?",
        (denomination.lower(),)
    )
    result = cursor.fetchone()
    return result[0] if result else None

def main():
    if network_check():
        update_db()
    else:
        print("Network unavailable. Using cached local rates.")

    try:
        amount = float(input("Enter the amount: "))
    except ValueError:
        print("Invalid amount. Please enter a numerical value.")
        return

    primary_currency = input("Enter primary currency (e.g., USD, EUR): ").strip().lower()
    secondary_currency = input("Enter secondary currency (e.g., GBP, NGN): ").strip().lower()

    connector = sqlite3.connect("rates.db")
    cursor = connector.cursor()

    try:
        rate_primary = get_exchange_rate(cursor, primary_currency)
        rate_secondary = get_exchange_rate(cursor, secondary_currency)

        if not rate_primary:
            print(f"Error: Primary currency '{primary_currency.upper()}' not found in database.")
            return
        if not rate_secondary:
            print(f"Error: Secondary currency '{secondary_currency.upper()}' not found in database.")
            return

        converted_amount = (amount / rate_primary) * rate_secondary

        print(f"{amount:,.2f} {primary_currency.upper()} is equal to {converted_amount:,.2f} {secondary_currency.upper()}")

    except sqlite3.OperationalError:
        print("Database error. Ensure 'rates.db' exists and is populated.")
    finally:
        connector.close()

if __name__ == "__main__":
    main()
