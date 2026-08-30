import urllib.request
import csv

def fetch_cities(state_abbr):
    url = "https://raw.githubusercontent.com/kelvins/US-Cities-Database/main/csv/us_cities.csv"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            lines = [line.decode('utf-8') for line in response.readlines()]
            reader = csv.DictReader(lines)
            cities = []
            for row in reader:
                if row['STATE_CODE'].lower() == state_abbr.lower():
                    cities.append(row['CITY'])
            
            # Deduplicate and sort
            cities = sorted(list(set(cities)))
            print(f"Found {len(cities)} cities for {state_abbr.upper()}.")
            print(cities[:20])
    except Exception as e:
        print(f"Error: {e}")

fetch_cities('al')
