


import requests
import csv
import time


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
        result = func(*args, **kwargs)
        print("Fetching Completed...")
        return result
    return wrapper



def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper



@log_function
@timer
def fetch_weather(name, lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        weather = data["current_weather"]
        return {
            "City":        name,
            "Temperature": weather["temperature"],
            "WindSpeed":   weather["windspeed"],
            "WeatherCode": weather["weathercode"],
            "Time":        weather["time"]
        }
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return None



all_data = []

for name, lat, lon in cities:
    print(f"\nFetching {name} weather...")
    result = fetch_weather(name, lat, lon)
    if result:
        all_data.append(result)
    time.sleep(0.3)



with open("weather_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["City", "Temperature", "WindSpeed", "WeatherCode", "Time"])
    for row in all_data:
        writer.writerow([row["City"], row["Temperature"], row["WindSpeed"], row["WeatherCode"], row["Time"]])

print("\nData saved to CSV.")




