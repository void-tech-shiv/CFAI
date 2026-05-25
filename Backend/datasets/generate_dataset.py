import json
import os

# Define the 26 cities (nodes) with metadata
locations_data = [
    {"id": "delhi", "name": "Delhi (National Capital)", "rating": 4.5, "crowd": 0.85, "x": 77.2090, "y": 28.6139, "desc": "Historical monuments, Red Fort, Qutub Minar, and street food."},
    {"id": "gurugram", "name": "Gurugram (Cyber City)", "rating": 4.1, "crowd": 0.75, "x": 77.0266, "y": 28.4595, "desc": "Modern corporate hub with high-end shopping and dining like CyberHub."},
    {"id": "alwar", "name": "Alwar (Sariska & Forts)", "rating": 4.2, "crowd": 0.40, "x": 76.6346, "y": 27.5530, "desc": "Ancient city featuring Sariska Tiger Reserve and Bhangarh ruins."},
    {"id": "bharatpur", "name": "Bharatpur (Bird Park)", "rating": 4.3, "crowd": 0.35, "x": 77.5030, "y": 27.2152, "desc": "UNESCO World Heritage Keoladeo National Park, hosting rare birds."},
    {"id": "agra", "name": "Agra (Taj Mahal City)", "rating": 4.9, "crowd": 0.95, "x": 78.0081, "y": 27.1767, "desc": "Home of the iconic Taj Mahal, Agra Fort, and exquisite Mughlai crafts."},
    {"id": "mathura", "name": "Mathura (Sacred Heritage)", "rating": 4.6, "crowd": 0.88, "x": 77.6737, "y": 27.4924, "desc": "The divine birthplace of Lord Krishna on the Yamuna river ghats."},
    {"id": "jaipur", "name": "Jaipur (The Pink City)", "rating": 4.8, "crowd": 0.82, "x": 75.7873, "y": 26.9124, "desc": "Capital of Rajasthan, famous for Hawa Mahal, Amer Fort, and markets."},
    {"id": "pushkar", "name": "Pushkar (Holy Town)", "rating": 4.4, "crowd": 0.55, "x": 74.5511, "y": 26.4897, "desc": "Serene holy lake, rare Lord Brahma Temple, and camel desert fairs."},
    {"id": "ajmer", "name": "Ajmer (Sufi Shrine)", "rating": 4.3, "crowd": 0.78, "x": 74.6399, "y": 26.4498, "desc": "Home to the revered Khwaja Garib Nawaz Dargah and Ana Sagar Lake."},
    {"id": "ranthambore", "name": "Ranthambore (Tigers)", "rating": 4.7, "crowd": 0.48, "x": 76.3865, "y": 25.9928, "desc": "Tiger Reserve offering majestic wildlife safaris and ancient fort."},
    {"id": "bikaner", "name": "Bikaner (Desert Oasis)", "rating": 4.3, "crowd": 0.38, "x": 73.3119, "y": 28.0166, "desc": "Junagarh Fort, Karni Mata (Rat) temple, and spicy Bikaneri bhujia."},
    {"id": "jodhpur", "name": "Jodhpur (The Blue City)", "rating": 4.7, "crowd": 0.72, "x": 73.0243, "y": 26.2389, "desc": "Mehrangarh Fort overlooking blue houses, delicious traditional sweets."},
    {"id": "jaisalmer", "name": "Jaisalmer (Golden City)", "rating": 4.8, "crowd": 0.62, "x": 70.9083, "y": 26.9157, "desc": "Sandstone fort rising from Thar Desert, camel safaris, and sand dunes."},
    {"id": "udaipur", "name": "Udaipur (City of Lakes)", "rating": 4.9, "crowd": 0.80, "x": 73.7125, "y": 24.5854, "desc": "Romantic destination with grand Lake Palace floating on Lake Pichola."},
    {"id": "chittorgarh", "name": "Chittorgarh (Fort of Valor)", "rating": 4.4, "crowd": 0.30, "x": 74.6269, "y": 24.8887, "desc": "Massive hilltop fort, Vijay Stambha, and legends of Rajput bravery."},
    {"id": "mandawa", "name": "Mandawa (Haveli Museum)", "rating": 4.2, "crowd": 0.25, "x": 75.1415, "y": 28.0553, "desc": "Open-air art gallery famous for beautifully painted heritage Havelis."},
    {"id": "mount_abu", "name": "Mount Abu (Hill Station)", "rating": 4.5, "crowd": 0.68, "x": 72.7156, "y": 24.5925, "desc": "Lush oasis in the Aravalli range, Nakki Lake, and Dilwara Temples."},
    {"id": "kumbhalgarh", "name": "Kumbhalgarh (Great Wall)", "rating": 4.6, "crowd": 0.35, "x": 73.5874, "y": 25.1487, "desc": "Massive fort featuring the second longest continuous wall in the world."},
    {"id": "ranakpur", "name": "Ranakpur (Jain Temples)", "rating": 4.5, "crowd": 0.28, "x": 73.4735, "y": 25.1170, "desc": "Intricately carved 1444 marble pillars Jain Temple in Aravalli valleys."},
    {"id": "kota", "name": "Kota (River Palaces)", "rating": 4.0, "crowd": 0.50, "x": 75.8304, "y": 25.1768, "desc": "Lies on Chambal River banks, popular for palaces, gardens, and stone."},
    {"id": "bundi", "name": "Bundi (Stepwells City)", "rating": 4.3, "crowd": 0.22, "x": 75.6429, "y": 25.4417, "desc": "Charming town with ornate stepwells, Taragarh Fort, and miniature art."},
    {"id": "jhunjhunu", "name": "Jhunjhunu (Shekhawati Capital)", "rating": 4.1, "crowd": 0.24, "x": 75.3995, "y": 28.1299, "desc": "Grand Havelis, Rani Sati Temple, and rich brass arts."},
    {"id": "jhalawar", "name": "Jhalawar (Fort of Orchards)", "rating": 4.0, "crowd": 0.15, "x": 76.1610, "y": 24.5973, "desc": "Unique fort, ancient sun temple, and orange orchards."},
    {"id": "osian", "name": "Osian (Ancient Temples)", "rating": 4.2, "crowd": 0.20, "x": 73.0076, "y": 26.7244, "desc": "Brahmanical and Jain temples dating from 8th to 12th centuries."},
    {"id": "abhaneri", "name": "Abhaneri (Stepwell Wonder)", "rating": 4.4, "crowd": 0.32, "x": 76.6033, "y": 27.0073, "desc": "Famous Chand Baori stepwell, one of the deepest and largest in India."},
    {"id": "fatehpur_sikri", "name": "Fatehpur Sikri (Mughal Glory)", "rating": 4.5, "crowd": 0.58, "x": 77.6679, "y": 27.0945, "desc": "Emperor Akbar's sandstone palace complex and towering Buland Darwaza."}
]

# Base hotel lists for rendering in UI
hotels_db = {
    "luxury": [{"name": "The Oberoi Grand Palace", "price": 24000, "rating": 4.9}, {"name": "Taj Heritage Resort", "price": 18000, "rating": 4.8}],
    "standard": [{"name": "Royal Mansion Hotel", "price": 5500, "rating": 4.3}, {"name": "Heritage Haveli Suites", "price": 4200, "rating": 4.1}],
    "budget": [{"name": "Tourist Inn Guest House", "price": 1800, "rating": 3.9}, {"name": "Backpackers Paradise Hostel", "price": 950, "rating": 4.0}]
}

# Unique undirected edges to create a complex connected graph (at least 60+ unique edges)
# Format: (node1, node2, distance, base_time, toll, fuel_cost, traffic_delay, weather_impact)
edges_raw = [
    # Golden Triangle & Capital Connectors
    ("delhi", "gurugram", 32, 45, 80, 200, 20, 1.3),
    ("delhi", "mathura", 145, 160, 240, 900, 30, 1.2),
    ("delhi", "alwar", 165, 210, 120, 1050, 15, 1.1),
    ("delhi", "jhunjhunu", 180, 240, 150, 1150, 10, 1.1),
    
    ("gurugram", "alwar", 135, 180, 120, 850, 15, 1.1),
    ("gurugram", "jaipur", 238, 270, 360, 1500, 45, 1.2),
    ("gurugram", "jhunjhunu", 155, 210, 150, 950, 10, 1.1),
    
    ("alwar", "mathura", 110, 150, 80, 700, 10, 1.1),
    ("alwar", "bharatpur", 115, 150, 90, 750, 10, 1.1),
    ("alwar", "jaipur", 150, 190, 180, 950, 20, 1.1),
    ("alwar", "jhunjhunu", 140, 180, 100, 900, 10, 1.1),
    
    ("mathura", "bharatpur", 40, 50, 40, 250, 10, 1.2),
    ("mathura", "agra", 56, 70, 90, 350, 20, 1.2),
    ("mathura", "fatehpur_sikri", 45, 60, 60, 300, 10, 1.1),
    
    ("bharatpur", "agra", 58, 75, 80, 360, 20, 1.2),
    ("bharatpur", "abhaneri", 95, 120, 90, 600, 10, 1.1),
    ("bharatpur", "fatehpur_sikri", 25, 35, 30, 180, 5, 1.1),
    ("bharatpur", "jaipur", 185, 220, 240, 1150, 25, 1.1),
    
    ("agra", "fatehpur_sikri", 36, 45, 50, 240, 15, 1.2),
    ("agra", "ranthambore", 290, 360, 320, 1850, 20, 1.1),
    
    ("fatehpur_sikri", "abhaneri", 75, 90, 70, 450, 10, 1.1),
    
    # Jaipur Heart & Shekhawati Circuit
    ("jaipur", "abhaneri", 95, 110, 120, 600, 25, 1.1),
    ("jaipur", "mandawa", 168, 210, 150, 1050, 15, 1.1),
    ("jaipur", "jhunjhunu", 175, 220, 150, 1100, 15, 1.1),
    ("jaipur", "ajmer", 135, 140, 180, 850, 25, 1.2),
    ("jaipur", "pushkar", 142, 150, 180, 900, 20, 1.1),
    ("jaipur", "ranthambore", 160, 180, 150, 1000, 15, 1.1),
    ("jaipur", "bundi", 205, 260, 220, 1300, 15, 1.1),
    
    ("mandawa", "jhunjhunu", 28, 40, 30, 180, 5, 1.1),
    ("mandawa", "bikaner", 190, 240, 140, 1200, 10, 1.1),
    
    ("jhunjhunu", "bikaner", 230, 280, 180, 1450, 10, 1.1),
    
    # Central and East (Ajmer, Pushkar, Ranthambore)
    ("pushkar", "ajmer", 15, 30, 0, 100, 15, 1.3),
    ("pushkar", "jodhpur", 185, 220, 160, 1150, 10, 1.1),
    
    ("ajmer", "jodhpur", 200, 240, 200, 1250, 15, 1.1),
    ("ajmer", "udaipur", 265, 300, 280, 1650, 20, 1.2),
    ("ajmer", "bundi", 165, 210, 150, 1050, 10, 1.1),
    ("ajmer", "ranthambore", 215, 270, 180, 1350, 15, 1.1),
    
    ("ranthambore", "bundi", 145, 190, 110, 900, 10, 1.1),
    ("ranthambore", "chittorgarh", 240, 300, 220, 1500, 10, 1.1),
    ("ranthambore", "kota", 130, 170, 120, 800, 15, 1.1),
    
    # West Desert (Bikaner, Jodhpur, Jaisalmer, Osian)
    ("bikaner", "jodhpur", 250, 270, 220, 1550, 15, 1.1),
    ("bikaner", "jaisalmer", 330, 340, 240, 2050, 5, 1.1),
    ("bikaner", "osian", 210, 230, 150, 1300, 5, 1.1),
    
    ("jodhpur", "jaisalmer", 285, 300, 220, 1750, 10, 1.1),
    ("jodhpur", "osian", 65, 75, 40, 400, 5, 1.1),
    ("jodhpur", "ranakpur", 160, 200, 120, 1000, 10, 1.2),
    ("jodhpur", "mount_abu", 260, 310, 240, 1600, 10, 1.1),
    ("jodhpur", "kumbhalgarh", 180, 240, 150, 1100, 10, 1.2),
    
    ("jaisalmer", "osian", 240, 260, 160, 1500, 5, 1.1),
    
    # South Mewar (Udaipur, Mount Abu, Kumbhalgarh, Ranakpur, Chittorgarh)
    ("udaipur", "mount_abu", 165, 190, 180, 1050, 15, 1.2),
    ("udaipur", "kumbhalgarh", 85, 120, 60, 500, 10, 1.3),
    ("udaipur", "ranakpur", 95, 130, 80, 600, 10, 1.3),
    ("udaipur", "chittorgarh", 115, 130, 120, 700, 15, 1.1),
    ("udaipur", "jhalawar", 290, 360, 260, 1800, 10, 1.1),
    ("udaipur", "kota", 270, 340, 240, 1650, 15, 1.1),
    
    ("mount_abu", "ranakpur", 155, 210, 120, 950, 10, 1.2),
    
    ("kumbhalgarh", "ranakpur", 50, 75, 40, 300, 5, 1.3),
    ("kumbhalgarh", "chittorgarh", 165, 220, 140, 1050, 10, 1.2),
    
    ("ranakpur", "chittorgarh", 180, 230, 150, 1100, 10, 1.2),
    
    ("chittorgarh", "bundi", 140, 180, 110, 850, 10, 1.1),
    ("chittorgarh", "kota", 110, 140, 100, 680, 15, 1.1),
    ("chittorgarh", "jhalawar", 190, 240, 160, 1200, 10, 1.1),
    
    # East Hadoti (Kota, Bundi, Jhalawar)
    ("bundi", "kota", 38, 45, 40, 240, 15, 1.2),
    ("bundi", "jhalawar", 120, 160, 100, 750, 10, 1.1),
    
    ("kota", "jhalawar", 85, 110, 80, 550, 10, 1.1)
]

# Assert that we have at least 60 unique edges
print(f"Constructed graph with {len(locations_data)} nodes and {len(edges_raw)} unique edges.")

# Build bidirectional symmetrical JSON database
locations_output = []

for loc in locations_data:
    connections = []
    
    # Find all connections associated with this node (bidirectional)
    for edge in edges_raw:
        u, v, dist, time, toll, fuel, delay, weather = edge
        if u == loc["id"] or v == loc["id"]:
            target_id = v if u == loc["id"] else u
            
            # Weighted attributes structure
            connections.append({
                "to": target_id,
                "distance": dist,
                # Cost is total of Toll + Fuel Cost (represents extremely realistic weight)
                "cost": toll + fuel,
                "base_time": time,
                "toll": toll,
                "fuel_cost": fuel,
                "traffic_delay": delay,
                "weather_impact": weather,
                # Random traffic and weather warning state distributions
                "traffic_prob": {
                    "low": 0.5,
                    "medium": 0.3,
                    "high": 0.2
                },
                "weather_prob": {
                    "clear": 0.8,
                    "rain": 0.1,
                    "fog": 0.1
                }
            })
            
    # Assemble Location Node
    locations_output.append({
        "id": loc["id"],
        "name": loc["name"],
        "description": loc["desc"],
        "rating": loc["rating"],
        "crowd_level": loc["crowd"],
        "is_open": True,
        "x": loc["x"],
        "y": loc["y"],
        "hotels": [
            {"name": f"{loc['name'].split('(')[0].strip()} {h['name']}", "price": h["price"], "rating": h["rating"]}
            for h in (hotels_db["luxury"] if loc["rating"] >= 4.7 else hotels_db["standard"] if loc["rating"] >= 4.3 else hotels_db["budget"])
        ],
        "connections": connections
    })

# Format and write to locations.json
db_path = r"d:\HONORS CLASS\term3\CFAI\pg byme\Backend\datasets\locations.json"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

with open(db_path, "w", encoding="utf-8") as f:
    json.dump({"locations": locations_output}, f, indent=2, ensure_ascii=False)

print(f"Dataset successfully compiled and saved to {db_path}!")
