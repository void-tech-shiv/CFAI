import json
import urllib.request
import os
import random

CITIES_URL = "https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json"
ADMIN1_URL = "https://raw.githubusercontent.com/lutangar/cities.json/master/admin1.json"

def fetch_data():
    print("Fetching admin1 states mapping...")
    req = urllib.request.urlopen(ADMIN1_URL)
    admin1_data = json.loads(req.read())
    
    state_mapping = {}
    for entry in admin1_data:
        code = entry.get("code", "")
        if code.startswith("IN."):
            state_mapping[code.split(".")[1]] = entry.get("name")
            
    print("Fetching cities dataset...")
    req = urllib.request.urlopen(CITIES_URL)
    cities_data = json.loads(req.read())
    
    ind_cities = [c for c in cities_data if c.get('country') == 'IN']
    print(f"Found {len(ind_cities)} Indian cities.")
    
    # Group by state
    states_dict = {}
    for city in ind_cities:
        admin_code = city.get("admin1")
        state_name = state_mapping.get(admin_code, "Unknown State")
        
        if state_name not in states_dict:
            states_dict[state_name] = []
        states_dict[state_name].append(city)
        
    final_locations = []
    
    # Cap at ~15 cities per state to prevent massive browser lag, total ~500 nodes
    for state_name, cities in states_dict.items():
        random.seed(42) # Deterministic sampling
        sample_size = min(15, len(cities))
        sampled = random.sample(cities, sample_size)
        
        for c in sampled:
            city_name = c.get("name")
            lat = float(c.get("lat"))
            lng = float(c.get("lng"))
            
            # Formulate the node
            # Generate a consistent ID
            clean_name = "".join(e for e in city_name if e.isalnum()).lower()
            clean_state = "".join(e for e in state_name if e.isalnum()).lower()
            loc_id = f"{clean_name}_{clean_state}"
            
            final_locations.append({
                "id": loc_id,
                "name": city_name,
                "state": state_name,
                "rating": round(random.uniform(3.8, 4.9), 1),
                "crowd": round(random.uniform(0.3, 0.95), 2),
                "x": lng,
                "y": lat,
                "desc": f"Major district in {state_name}. Administrative and cultural center."
            })

    output_path = os.path.join(os.path.dirname(__file__), "fetched_locations.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_locations, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully exported {len(final_locations)} districts to {output_path}")

if __name__ == "__main__":
    fetch_data()
