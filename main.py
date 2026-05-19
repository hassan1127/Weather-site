

import argparse
import requests
import csv
import time
import logging

from process_weather import WeatherIterator

cities = [
    ("Lahore",     31.5204, 74.3587),
    ("Karachi",    24.8607, 67.0011),
    ("Islamabad",  33.6844, 73.0479),
    ("Multan",     30.1575, 71.5249),
    ("Peshawar",   34.0151, 71.5249),
]



def log_function(func):
    def wrapper(*args, **kwargs):
        print("Fetching Started...")
        log("Fetching Started...")
        result = func(*args, **kwargs)
        print("Fetching Completed...")
        log("Fetching Completed...")
        return result
    return wrapper

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        log(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@log_function
@timer
def fetch_weather(name, lat, lon, args):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        weather = data["current_weather"]

        temp = weather["temperature"]

        if args.temp_unit.upper() == "F":
            temp = (temp * 9/5) + 32

        return {
            "City":        name,
            "Temperature": temp,
            "WindSpeed":   weather["windspeed"],
            "WeatherCode": weather["weathercode"],
            "Time":        weather["time"]
        }
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        log(f"Error fetching {name}: {e}", level="error")
        return None

def main():
    global log

    parser = argparse.ArgumentParser(description="Bulk Weather Analyzer")

    parser.add_argument("--log", choices=["true", "false"], default="false")
    parser.add_argument("--output-type", choices=["csv", "txt"], default="txt")
    parser.add_argument("--temp-unit", choices=["C", "F"], default="C")
    parser.add_argument("--hot-limit", type=float, default=35.0)
    parser.add_argument("--wind-limit", type=float, default=50.0)

    args = parser.parse_args()


    if not (0 <= args.hot_limit <= 70):
        parser.error("--hot-limit must be between 0 and 70 °C")
    if not (0 <= args.wind_limit <= 200):
        parser.error("--wind-limit must be between 0 and 200 km/h")

    if args.log.lower() == "true":
        logging.basicConfig(
            filename="weather.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        def log(msg, level="info"):
            
            if level == "error":
                logging.error(msg)
            else:
                logging.info(msg)

            if args.output_type.lower() == "csv":
                with open("weather_data.csv", "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([msg])
            else:
                with open("report.txt", "a") as f:
                    f.write(msg + "\n")

    elif args.log.lower() == "false":
        def log(msg, level="info"):
            if args.output_type.lower() == "csv":
                with open("weather_data.csv", "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([msg])
            else:
                with open("report.txt", "a") as f:
                    f.write(msg + "\n")
  
    
    all_data = []

    for name, lat, lon in cities:
        print(f"\nFetching {name} weather...")
        log(f"Fetching started for {name}")

        result = fetch_weather(name, lat, lon, args)

        if result:
            all_data.append(result)
            log(f"{name} fetched successfully - Temp: {result['Temperature']}")
        else:
            log(f"Failed to fetch {name}", level="error")

        time.sleep(0.3)

    if len(all_data) == 0: # if not all_data:
        return None
    else:
        temps = [float(r["Temperature"]) for r in all_data]
        winds = [float(r["WindSpeed"])   for r in all_data]

    hottest = all_data[temps.index(max(temps))]
    coldest = all_data[temps.index(min(temps))]
    fastest = all_data[winds.index(max(winds))]

    hot_cities   = list(filter(lambda x: float(x["Temperature"]) > args.hot_limit,  all_data))
    windy_cities = list(filter(lambda x: float(x["WindSpeed"])   > args.wind_limit, all_data))

    city_names = [r["City"] for r in all_data]
    city_temps = [r["Temperature"] for r in all_data]

    print("\nAll Cities")
    for item in WeatherIterator(all_data):
        print(f"  {item['City']}: {item['Temperature']}{args.temp_unit}, wind={item['WindSpeed']}km/h")

    print("\n City -> Temperature")
    for city, temp in zip(city_names, city_temps):
        print(f"  {city} -> {temp}{args.temp_unit}")

    print(f"\nHot Cities (above {args.hot_limit}{args.temp_unit}) ")
    if hot_cities:
        for r in hot_cities:
            print(f"  {r['City']} -> {r['Temperature']}{args.temp_unit}")
    else:
        print("  No hot cities found")

    print(f"\n Windy Cities (above {args.wind_limit} km/h)")
    if windy_cities:
        for r in windy_cities:
            print(f"  {r['City']} -> {r['WindSpeed']} km/h")
    else:
        print("No windy cities found")

    print("\nSummary Stats")
    print(f"Hottest city      : {hottest['City']} ({hottest['Temperature']}{args.temp_unit})")
    print(f"Coldest city      : {coldest['City']} ({coldest['Temperature']}{args.temp_unit})")
    print(f"Average temp      : {sum(temps)/len(temps):.1f}{args.temp_unit}")
    print(f"Fastest wind city : {fastest['City']} ({fastest['WindSpeed']} km/h)")

    log(f"Hottest city: {hottest['City']} - {hottest['Temperature']}{args.temp_unit}")
    log(f"Coldest city: {coldest['City']} - {coldest['Temperature']}{args.temp_unit}")
    log(f"Average temp: {sum(temps)/len(temps):.1f}{args.temp_unit}")

    if args.output_type.lower() == "csv":
        with open("weather_data.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["City", "Temperature", "WindSpeed", "WeatherCode", "Time"])
            for row in all_data:
                writer.writerow([row["City"], row["Temperature"], row["WindSpeed"], row["WeatherCode"], row["Time"]])
        print("\nData saved to weather_data.csv")
        log("Data saved to weather_data.csv")
    else:
        with open("report.txt", "w") as f:
            f.write("Weather Report\n")
            f.write(f"Hottest City       : {hottest['City']}\n")
            f.write(f"Coldest City       : {coldest['City']}\n")
            f.write(f"Average Temperature: {sum(temps)/len(temps):.1f}{args.temp_unit}\n")
            f.write(f"Fastest Wind City  : {fastest['City']} ({fastest['WindSpeed']} km/h)\n")
            f.write("\nAll Cities:\n")
            for r in all_data:
                f.write(f"  {r['City']}: {r['Temperature']}{args.temp_unit}, {r['WindSpeed']}km/h wind\n")
        log("Report saved to report.txt")


    