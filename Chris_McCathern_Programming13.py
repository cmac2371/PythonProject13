
import sqlite3
import matplotlib.pyplot as plt
import random
from typing import Dict, Tuple, Optional

# ---------- 1. Create the database ----------
def create_database(initials: str) -> sqlite3.Connection:
    """Create SQLite database with a population table."""
    db_name = f"population_{initials}.db"
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS population (
            city TEXT,
            year INTEGER,
            population INTEGER,
            PRIMARY KEY (city, year)
        )
    """)
    conn.commit()
    return conn


# ---------- 2. Insert 2023 data ----------
def insert_2023_data(conn: sqlite3.Connection) -> None:
    """Insert 10 Florida cities with 2023 population data."""
    cities = {
        "Jacksonville": 985000,
        "Miami": 451000,
        "Tampa": 398000,
        "Orlando": 317000,
        "St. Petersburg": 261000,
        "Hialeah": 220000,
        "Tallahassee": 202000,
        "Port St. Lucie": 241000,
        "Cape Coral": 216000,
        "Fort Lauderdale": 184000,
    }
    cur = conn.cursor()
    for city, pop in cities.items():
        cur.execute(
            "INSERT OR IGNORE INTO population (city, year, population) VALUES (?, ?, ?)",
            (city, 2023, pop),
        )
    conn.commit()


# ---------- 3. Simulate population growth ----------
def simulate_growth(conn: sqlite3.Connection,
                    start_year: int = 2024,
                    years: int = 20,
                    rate_min: float = -0.01,
                    rate_max: float = 0.03,
                    rng_seed: int = 42) -> None:
    """
    Simulate growth/decline for the next `years` at random rates each year
    and insert results into the population table.
    """
    cur = conn.cursor()
    cur.execute("SELECT city, population FROM population WHERE year = 2023")
    rows = cur.fetchall()

    random.seed(rng_seed)

    for city, pop in rows:
        population = pop
        for year in range(start_year, start_year + years):
            growth_rate = random.uniform(rate_min, rate_max)  # -1% to +3% default
            population = max(1, int(round(population * (1 + growth_rate))))
            cur.execute(
                "INSERT OR REPLACE INTO population (city, year, population) VALUES (?, ?, ?)",
                (city, year, population),
            )
    conn.commit()


# ---------- 4. Plot one city ----------
def show_city_plot(conn: sqlite3.Connection) -> None:
    """Ask user for a city and show its population growth."""
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT city FROM population ORDER BY city")
    cities = [row[0] for row in cur.fetchall()]

    if not cities:
        print("No cities found. Did you insert the 2023 data?")
        return

    print("\nAvailable cities:")
    for c in cities:
        print("-", c)

    choice = input("\nType a city name exactly as shown: ").strip()
    if choice not in cities:
        print("Invalid city — showing first city instead.")
        choice = cities[0]

    cur.execute(
        "SELECT year, population FROM population WHERE city = ? ORDER BY year",
        (choice,),
    )
    data = cur.fetchall()
    years = [row[0] for row in data]
    pops = [row[1] for row in data]

    plt.figure(figsize=(8, 5))
    plt.plot(years, pops, marker='o')
    plt.title(f"Population Growth for {choice}")
    plt.xlabel("Year")
    plt.ylabel("Population")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ---------- 5. Run everything ----------
def main() -> None:
    initials = input("Enter your initials (e.g., WCM): ").strip() or "CM"
    conn = create_database(initials)
    insert_2023_data(conn)
    simulate_growth(conn)  # you can tweak rate_min/rate_max if needed
    show_city_plot(conn)
    conn.close()


if __name__ == "__main__":
    main()
wcm