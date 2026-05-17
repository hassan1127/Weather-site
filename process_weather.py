


import csv
import time



def read_csv(filename):
    data = []
    try:
        with open(filename, newline="") as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                data.append({
                    "City":        row[0],
                    "Temperature": row[1],
                    "WindSpeed":   row[2],
                    "WeatherCode": row[3],
                    "Time":        row[4]
                })
    except FileNotFoundError:
        print("weather_data.csv not found. Run fetch_weather.py first.")
    return data



class WeatherIterator:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        item = self.data[self.index]
        self.index += 1
        return item



def temperature_generator(data):
    for row in data:
        yield float(row["Temperature"])



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



data = read_csv("weather_data.csv")

if not data:
    exit()



print("\n--- All Cities (using iterator) ---")
for item in WeatherIterator(data):
    print(f"  {item['City']}: {item['Temperature']}C, wind={item['WindSpeed']}km/h")



temps_gen = temperature_generator(data)
all_temps = list(temperature_generator(data))

highest_temp = max(all_temps)
average_temp = sum(all_temps) / len(all_temps)

print(f"\nHighest Temperature : {highest_temp}C")
print(f"Average Temperature : {average_temp:.1f}C")



hot_cities = list(filter(lambda x: float(x["Temperature"]) > 35, data))

print("\n--- Hot Cities (above 35C) ---")
if hot_cities:
    for r in hot_cities:
        print(f"  {r['City']} -> {r['Temperature']}C")
else:
    print("  No hot cities found")



windy_cities = list(filter(lambda x: float(x["WindSpeed"]) > 15, data))

print("\n--- Windy Cities (above 15 km/h) ---")
if windy_cities:
    for r in windy_cities:
        print(f"  {r['City']} -> {r['WindSpeed']} km/h")
else:
    print("  No windy cities found")



city_names = [r["City"]        for r in data]
city_temps  = [r["Temperature"] for r in data]

print("\n--- City -> Temperature (using zip) ---")
for city, temp in zip(city_names, city_temps):
    print(f"  {city} -> {temp}C")



temps = [float(r["Temperature"]) for r in data]
winds = [float(r["WindSpeed"])   for r in data]

hottest = data[temps.index(max(temps))]
coldest = data[temps.index(min(temps))]
fastest = data[winds.index(max(winds))]

print("\n--- Summary Stats ---")
print(f"Hottest city      : {hottest['City']} ({hottest['Temperature']}C)")
print(f"Coldest city      : {coldest['City']} ({coldest['Temperature']}C)")
print(f"Average temp      : {sum(temps)/len(temps):.1f}C")
print(f"Fastest wind city : {fastest['City']} ({fastest['WindSpeed']} km/h)")



with open("report.txt", "w") as f:
    f.write("Weather Report\n")
    f.write("=" * 30 + "\n\n")
    f.write(f"Hottest City       : {hottest['City']}\n")
    f.write(f"Coldest City       : {coldest['City']}\n")
    f.write(f"Average Temperature: {sum(temps)/len(temps):.1f}C\n")
    f.write(f"Fastest Wind City  : {fastest['City']} ({fastest['WindSpeed']} km/h)\n")
    f.write("\nAll Cities:\n")
    for r in data:
        f.write(f"  {r['City']}: {r['Temperature']}C, {r['WindSpeed']}km/h wind\n")

print("\nReport saved to report.txt")


