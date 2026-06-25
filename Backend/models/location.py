import json
import os
import math

class Connection:
    """
    OOP class representing a weighted edge (road connection) between two tourist places.
    Includes distance, travel cost, travel time, and risk probabilities.
    """
    def __init__(self, to_id, distance, cost, base_time, traffic_prob, weather_prob, toll=0, fuel_cost=0, traffic_delay=0, weather_impact=1.0):
        self.to_id = to_id
        self.distance = distance
        self.cost = cost
        self.base_time = base_time
        # Probabilities for uncertainty calculations
        self.traffic_prob = traffic_prob    # e.g., {"low": 0.5, "medium": 0.3, "high": 0.2}
        self.weather_prob = weather_prob    # e.g., {"clear": 0.7, "rain": 0.2, "fog": 0.1}
        # Weighted road attributes
        self.toll = toll
        self.fuel_cost = fuel_cost
        self.traffic_delay = traffic_delay
        self.weather_impact = weather_impact


class Location:
    """
    OOP class representing a node (tourist place) in the state-space graph.
    Contains rating, coordinates, crowd indices, operational status, and hotels.
    """
    def __init__(self, id_str, name, state, description, rating, crowd_level, is_open, x, y, hotels, connections_data):
        self.id = id_str
        self.name = name
        self.state = state
        self.description = description
        self.rating = rating
        self.crowd_level = crowd_level
        self.is_open = is_open
        self.x = x
        self.y = y
        self.hotels = hotels
        self.connections = [
            Connection(
                to_id=conn["to"],
                distance=conn["distance"],
                cost=conn["cost"],
                base_time=conn["base_time"],
                traffic_prob=conn["traffic_prob"],
                weather_prob=conn["weather_prob"],
                toll=conn.get("toll", 0),
                fuel_cost=conn.get("fuel_cost", 0),
                traffic_delay=conn.get("traffic_delay", 0),
                weather_impact=conn.get("weather_impact", 1.0)
            )
            for conn in connections_data
        ]

    def get_connection(self, target_id):
        """Returns the connection details to a target location if it exists, otherwise None."""
        for conn in self.connections:
            if conn.to_id == target_id:
                return conn
        return None


class TouristGraph:
    """
    Graph representation representing the state space of tourist destinations.
    """
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets", "locations.json")

    def __init__(self):
        self.locations = {}  # Map: id -> Location object
        self.load_graph()

    def load_graph(self):
        """Loads the graph from locations.json."""
        if not os.path.exists(self.DB_PATH):
            return
        try:
            with open(self.DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for loc_data in data["locations"]:
                    loc_obj = Location(
                        id_str=loc_data["id"],
                        name=loc_data["name"],
                        state=loc_data.get("state", "Unknown"),
                        description=loc_data["description"],
                        rating=loc_data["rating"],
                        crowd_level=loc_data["crowd_level"],
                        is_open=loc_data["is_open"],
                        x=loc_data["x"],
                        y=loc_data["y"],
                        hotels=loc_data["hotels"],
                        connections_data=loc_data["connections"]
                    )
                    self.locations[loc_data["id"]] = loc_obj
        except Exception as e:
            print(f"Error loading graph database: {e}")

    def get_location(self, loc_id):
        """Retrieves a Location object by its ID."""
        return self.locations.get(loc_id)

    def get_all_locations(self):
        """Returns all location objects."""
        return list(self.locations.values())

    @staticmethod
    def calculate_euclidean(loc1, loc2):
        """Calculates Euclidean straight-line distance between two locations (admissible heuristic)."""
        return math.sqrt((loc1.x - loc2.x) ** 2 + (loc1.y - loc2.y) ** 2) * 100.0  # Scaled to approximate km

    @staticmethod
    def calculate_manhattan(loc1, loc2):
        """Calculates Manhattan distance between two locations (admissible/consistent heuristic for grid)."""
        return (abs(loc1.x - loc2.x) + abs(loc1.y - loc2.y)) * 100.0  # Scaled to approximate km

    @staticmethod
    def calculate_haversine(loc1, loc2):
        """Calculates exact earth-surface distance using Haversine formula (admissible heuristic)."""
        R = 6371.0  # Earth radius in kilometers
        lat1, lon1 = math.radians(loc1.y), math.radians(loc1.x)
        lat2, lon2 = math.radians(loc2.y), math.radians(loc2.x)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
