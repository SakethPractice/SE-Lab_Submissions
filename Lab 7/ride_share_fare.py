import math


def parse_trip(text):
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    cab, distance = parts
    cab = cab.strip()
    if not cab:
        return None
    try:
        km = float(distance)
    except ValueError:
        return None
    if not math.isfinite(km) or km < 0:
        return None
    return cab.title(), km

def fare_average(fares_csv):
    if not isinstance(fares_csv, str):
        return None
    try:
        values = [int(value.strip()) for value in fares_csv.split(',')]
    except ValueError:
        return None
    if not values or any(value < 0 for value in values):
        return None
    return sum(values) // len(values)

def payable_fare(text):
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    try:
        fare, promo = (float(value) for value in parts)
    except ValueError:
        return None
    if (
        not math.isfinite(fare)
        or not math.isfinite(promo)
        or fare < 0
        or promo < 0
    ):
        return None
    total = fare * 1.18 - promo
    if not math.isfinite(total):
        return None
    return max(total, 0)

def main():
    print("==== Running parse_trip ====")
    user_input = input("Enter cab:distance in km (e.g. sedan:12): ")
    result = parse_trip(user_input)
    print("Cab and Distance:", result)

    print("\n==== Running fare_average ====")
    user_input = input("Enter fares as CSV (e.g. 120,95,210): ")
    result = fare_average(user_input)
    print("Average Fare:", result)

    print("\n==== Running payable_fare ====")
    user_input = input("Enter fare|promo (e.g. 250|30): ")
    result = payable_fare(user_input)
    print("Payable Fare:", result)

if __name__ == "__main__":
    main()
