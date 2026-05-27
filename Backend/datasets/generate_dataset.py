import json
import os
import math
import random

# Haversine formula to calculate distance between two lat/long points
def haversine(lon1, lat1, lon2, lat2):
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r

fetched_path = os.path.join(os.path.dirname(__file__), "fetched_locations.json")
if os.path.exists(fetched_path):
    with open(fetched_path, "r", encoding="utf-8") as f:
        locations_data = json.load(f)
else:
    print("Please run fetch_districts.py first to generate the massive dataset.")
    exit(1)

hotels_db = {
    "luxury": [{"name": "Taj Grand Resort", "price": 18000, "rating": 4.9}, {"name": "Oberoi Suites", "price": 15000, "rating": 4.8}],
    "standard": [{"name": "Royal Mansion Hotel", "price": 5500, "rating": 4.3}, {"name": "Heritage Guest House", "price": 4200, "rating": 4.1}],
    "budget": [{"name": "Backpackers Paradise", "price": 950, "rating": 4.0}, {"name": "City Express Inn", "price": 1500, "rating": 3.9}]
}

edges_raw = []
edges_set = set()
# Generate edges by connecting each node to its 4 nearest neighbors
for i, loc1 in enumerate(locations_data):
    distances = []
    for j, loc2 in enumerate(locations_data):
        if i != j:
            dist = haversine(loc1["x"], loc1["y"], loc2["x"], loc2["y"])
            distances.append((dist, loc2["id"]))
    
    # Sort by distance
    distances.sort(key=lambda x: x[0])
    
    # Connect to 4 closest neighbors
    for dist, loc2_id in distances[:4]:
        # Keep consistent order for undirected edges
        u, v = loc1["id"], loc2_id
        if u > v: u, v = v, u
        
        edge_key = (u, v)
        if edge_key not in edges_set:
            edges_set.add(edge_key)
            time_mins = max(10, int((dist / 60) * 60)) # Minimum 10 mins
            toll = int(dist * 1.5)
            fuel = int((dist / 15) * 100)
            delay = random.randint(10, 60)
            weather_imp = round(random.uniform(1.0, 1.4), 1)
            
            edges_raw.append((u, v, round(dist), time_mins, toll, fuel, delay, weather_imp))

print(f"Constructed graph with {len(locations_data)} nodes and {len(edges_raw)} unique edges.")

locations_output = []

for loc in locations_data:
    connections = []
    
    for edge in edges_raw:
        u, v, dist, time, toll, fuel, delay, weather = edge
        if u == loc["id"] or v == loc["id"]:
            target_id = v if u == loc["id"] else u
            
            connections.append({
                "to": target_id,
                "distance": dist,
                "cost": toll + fuel,
                "base_time": time,
                "toll": toll,
                "fuel_cost": fuel,
                "traffic_delay": delay,
                "weather_impact": weather,
                "traffic_prob": {
                    "low": 0.5, "medium": 0.3, "high": 0.2
                },
                "weather_prob": {
                    "clear": 0.8, "rain": 0.1, "fog": 0.1
                }
            })
            
    locations_output.append({
        "id": loc["id"],
        "name": loc["name"],
        "state": loc["state"],
        "description": loc["desc"],
        "rating": loc["rating"],
        "crowd_level": loc["crowd"],
        "is_open": True,
        "x": loc["x"],
        "y": loc["y"],
        "hotels": [
            {"name": f"{loc['name']} {h['name']}", "price": h["price"], "rating": h["rating"]}
            for h in (hotels_db["luxury"] if loc["rating"] >= 4.7 else hotels_db["standard"] if loc["rating"] >= 4.3 else hotels_db["budget"])
        ],
        "connections": connections
    })

db_path = r"d:\HONORS CLASS\term3\CFAI\pg byme\Backend\datasets\locations.json"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

with open(db_path, "w", encoding="utf-8") as f:
    json.dump({"locations": locations_output}, f, indent=2, ensure_ascii=False)

print(f"Dataset successfully compiled and saved to {db_path}!")
