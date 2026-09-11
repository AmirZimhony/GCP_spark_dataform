#!/usr/bin/env python3
"""Generate reproducible users.csv and addresses.csv."""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

START_TS = datetime(2026, 9, 1, 10, 0, 0)

FIRST_NAMES = [
    "Amir",
    "Dana",
    "Noa",
    "Yael",
    "Avi",
    "Maya",
    "Omri",
    "Tamar",
    "Itay",
    "Shira",
    "Yonatan",
    "Michal",
    "Eitan",
    "Lior",
    "Adi",
    "Gal",
    "Nir",
    "Tal",
    "Ron",
    "Or",
    "Bar",
    "Eden",
    "Yuval",
    "Rotem",
    "Neta",
    "Hila",
    "Lihi",
    "Maayan",
    "Shahar",
    "Idan",
    "Alon",
    "Omer",
    "Tom",
    "Guy",
    "Dan",
    "Elad",
    "Ido",
    "Asaf",
    "Chen",
    "Inbar",
    "Keren",
    "Noga",
    "Roni",
    "Stav",
    "Talia",
    "Yaara",
    "Ziv",
    "Amit",
    "Ariel",
    "Nadav",
    "Shai",
    "Yossi",
    "Rina",
    "Dalia",
    "Mor",
    "Nitzan",
    "Ofir",
    "Gil",
    "Noam",
    "Shaked",
]

LAST_NAMES = [
    "Cohen",
    "Levi",
    "Mizrahi",
    "Peretz",
    "Biton",
    "Dahan",
    "Avraham",
    "Friedman",
    "Azulay",
    "Malka",
    "Katz",
    "David",
    "Ben David",
    "Gabay",
    "Amar",
    "Ohayon",
    "Sharabi",
    "Hadad",
    "Yosef",
    "Shapiro",
    "Goldstein",
    "Rosenberg",
    "Baruch",
    "Maimon",
    "Ashkenazi",
    "Ben Haim",
    "Dayan",
    "Ezra",
    "Golan",
    "Hazan",
    "Israeli",
    "Klein",
    "Meir",
    "Nagar",
    "Oren",
    "Sabag",
    "Tzur",
    "Weiss",
    "Zohar",
    "Aharoni",
]

STREETS = [
    "Dizengoff",
    "Allenby",
    "Rothschild",
    "Herzl",
    "Ben Gurion",
    "Weizmann",
    "Jabotinsky",
    "Begin",
    "Ibn Gabirol",
    "King George",
    "HaYarkon",
    "Nordau",
    "Bialik",
    "Sokolov",
    "Arlozorov",
    "Trumpeldor",
    "HaNassi",
    "HaShalom",
    "HaAtzmaut",
    "HaPalmach",
    "HaHistadrut",
    "HaGalil",
    "HaCarmel",
    "HaNassi Ben Zvi",
    "Kaplan",
    "Namir",
    "Yitzhak Sadeh",
    "Shenkin",
    "Frishman",
    "Gordon",
]

# Other cities (excluding Tel Aviv) with rough population weights.
OTHER_CITIES: list[tuple[str, int]] = [
    ("Jerusalem", 970),
    ("Haifa", 285),
    ("Rishon LeZion", 258),
    ("Petah Tikva", 252),
    ("Ashdod", 226),
    ("Netanya", 224),
    ("Beer Sheva", 211),
    ("Bnei Brak", 212),
    ("Holon", 197),
    ("Ramat Gan", 169),
    ("Ashkelon", 149),
    ("Rehovot", 147),
    ("Beit Shemesh", 143),
    ("Bat Yam", 129),
    ("Kfar Saba", 110),
    ("Herzliya", 103),
    ("Hadera", 100),
    ("Modiin", 97),
    ("Lod", 85),
    ("Ramla", 78),
    ("Ra'anana", 78),
    ("Nazareth", 78),
    ("Rahat", 75),
    ("Rosh HaAyin", 72),
    ("Hod Hasharon", 65),
    ("Givatayim", 61),
    ("Kiryat Gat", 60),
    ("Kiryat Ata", 60),
    ("Nahariya", 60),
    ("Afula", 59),
    ("Umm al-Fahm", 57),
    ("Yavne", 55),
    ("Eilat", 53),
    ("Acre", 50),
    ("Elad", 50),
    ("Ness Ziona", 50),
    ("Ramat Hasharon", 48),
    ("Tiberias", 47),
    ("Carmiel", 47),
    ("Tayibe", 44),
    ("Pardes Hanna-Karkur", 44),
    ("Kiryat Motzkin", 43),
    ("Kiryat Bialik", 43),
    ("Shefar'am", 43),
    ("Kiryat Ono", 42),
    ("Netivot", 40),
    ("Kiryat Yam", 40),
    ("Or Yehuda", 37),
    ("Safed", 37),
    ("Dimona", 35),
    ("Tamra", 35),
    ("Ofakim", 34),
    ("Sakhnin", 32),
    ("Yehud", 31),
    ("Sderot", 30),
    ("Gedera", 30),
    ("Arad", 28),
    ("Givat Shmuel", 28),
    ("Tira", 27),
    ("Migdal HaEmek", 26),
    ("Arraba", 26),
    ("Kiryat Malakhi", 25),
    ("Kfar Yona", 25),
    ("Kafr Qasim", 25),
    ("Yokneam", 24),
    ("Nesher", 24),
    ("Zichron Yaakov", 24),
    ("Gan Yavne", 24),
    ("Qalansawe", 24),
    ("Kiryat Shmona", 23),
    ("Kafr Kanna", 23),
    ("Ma'alot-Tarshiha", 22),
    ("Tirat Carmel", 22),
    ("Kadima-Zoran", 22),
    ("Shoham", 22),
    ("Or Akiva", 20),
    ("Reineh", 19),
    ("Kiryat Tivon", 19),
    ("Yafa an-Naseriyye", 19),
    ("Daliyat al-Karmel", 18),
]


def assign_cities(n_users: int, rng: random.Random) -> list[str]:
    n_tel_aviv = n_users // 2
    n_other = n_users - n_tel_aviv
    names = [name for name, _ in OTHER_CITIES]
    weights = [w for _, w in OTHER_CITIES]
    total_w = sum(weights)
    counts = [n_other * w // total_w for w in weights]
    remainder = n_other - sum(counts)
    for i in range(remainder):
        counts[i] += 1

    cities = ["Tel Aviv"] * n_tel_aviv
    for name, count in zip(names, counts, strict=True):
        cities.extend([name] * count)
    rng.shuffle(cities)
    return cities


def generate(n_users: int, seed: int, output_dir: Path) -> None:
    rng = random.Random(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    cities = assign_cities(n_users, rng)

    users_path = output_dir / "users.csv"
    addresses_path = output_dir / "addresses.csv"

    with users_path.open("w", newline="", encoding="utf-8") as users_file, addresses_path.open(
        "w", newline="", encoding="utf-8"
    ) as addresses_file:
        users_writer = csv.writer(users_file, lineterminator="\n")
        addresses_writer = csv.writer(addresses_file, lineterminator="\n")
        users_writer.writerow(["user_id", "name", "email", "updated_at"])
        addresses_writer.writerow(["address_id", "user_id", "city", "street", "updated_at"])

        n_first = len(FIRST_NAMES)
        n_last = len(LAST_NAMES)
        n_streets = len(STREETS)

        for user_id in range(1, n_users + 1):
            first = FIRST_NAMES[(user_id - 1) % n_first]
            last = LAST_NAMES[rng.randrange(n_last)]
            name = f"{first} {last}"
            email = f"{first.lower()}{user_id}@example.com"
            updated_at = (START_TS + timedelta(seconds=user_id - 1)).strftime("%Y-%m-%dT%H:%M:%S")
            street = f"{STREETS[rng.randrange(n_streets)]} {rng.randint(1, 200)}"
            city = cities[user_id - 1]

            users_writer.writerow([user_id, name, email, updated_at])
            addresses_writer.writerow([user_id, user_id, city, street, updated_at])

    counts = Counter(cities)
    tel_aviv = counts["Tel Aviv"]
    other_cities = len(counts) - (1 if tel_aviv else 0)
    print(f"Wrote {n_users} users to {users_path}")
    print(f"Wrote {n_users} addresses to {addresses_path}")
    print(f"Tel Aviv: {tel_aviv}")
    print(f"Other cities: {n_users - tel_aviv} rows across {other_cities} cities")
    print(f"Distinct cities: {len(counts)}")
    print(f"Seed: {seed}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate users.csv and addresses.csv")
    parser.add_argument("--n-users", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.n_users < 1:
        raise SystemExit("--n-users must be at least 1")
    generate(args.n_users, args.seed, args.output_dir)


if __name__ == "__main__":
    main()
