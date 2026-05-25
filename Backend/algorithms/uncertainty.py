import random

class UncertaintyEngine:
    """
    Reasoning Under Uncertainty Module.
    Implements:
    1. Bayesian Reasoning: Updating traffic probability based on weather warnings.
    2. Markov-style State Transitions: Simulating traffic level updates over time steps.
    3. Route Success Probability: Joint probability of safe, delay-free traversals.
    """
    def __init__(self, graph):
        self.graph = graph
        
        # Markov Chain Transition Matrix for Traffic States: [Low, Medium, High]
        # Transition probabilities representing how highway congestion evolves hourly
        self.traffic_transition_matrix = {
            "low":    {"low": 0.70, "medium": 0.20, "high": 0.10},
            "medium": {"low": 0.30, "medium": 0.50, "high": 0.20},
            "high":   {"low": 0.15, "medium": 0.35, "high": 0.50}
        }

    def apply_bayesian_update(self, base_high_traffic_prob, weather_state):
        """
        Applies Bayes' Theorem to update traffic congestion probability given a Weather State:
        
        P(HighTraffic | Weather) = [P(Weather | HighTraffic) * P(HighTraffic)] / P(Weather)
        
        For example:
        If weather_state is 'rain' or 'fog', it increases the likelihood of high traffic.
        """
        p_high_traffic = base_high_traffic_prob  # Prior probability: P(H)
        
        if weather_state == "clear":
            # Clear weather slightly reduces high traffic risk
            return max(0.05, p_high_traffic * 0.8)
            
        elif weather_state == "rain":
            # Probability of rain alert: P(Rain) = 0.20
            # Probability of rain alert GIVEN heavy traffic: P(Rain | HighTraffic) = 0.55
            p_rain = 0.20
            p_rain_given_high_traffic = 0.55
            
            # Bayes formula: P(HighTraffic | Rain) = [P(Rain | HighTraffic) * P(HighTraffic)] / P(Rain)
            posterior = (p_rain_given_high_traffic * p_high_traffic) / p_rain
            return min(0.95, posterior)
            
        elif weather_state == "fog":
            # Probability of fog alert: P(Fog) = 0.15
            # Probability of fog alert GIVEN heavy traffic: P(Fog | HighTraffic) = 0.60
            p_fog = 0.15
            p_fog_given_high_traffic = 0.60
            
            # Bayes formula: P(HighTraffic | Fog) = [P(Fog | HighTraffic) * P(HighTraffic)] / P(Fog)
            posterior = (p_fog_given_high_traffic * p_high_traffic) / p_fog
            return min(0.95, posterior)
            
        return p_high_traffic

    def simulate_traffic_markov(self, initial_state="low", hours=3):
        """
        Simulates traffic congestion changes along the trip using a Markov Chain.
        Computes the probability distribution of traffic states after N hours.
        """
        state_distribution = {"low": 0.0, "medium": 0.0, "high": 0.0}
        state_distribution[initial_state] = 1.0
        
        for _ in range(hours):
            next_distribution = {"low": 0.0, "medium": 0.0, "high": 0.0}
            for current_state, prob_in_state in state_distribution.items():
                if prob_in_state > 0:
                    transitions = self.traffic_transition_matrix[current_state]
                    for next_state, transition_prob in transitions.items():
                        next_distribution[next_state] += prob_in_state * transition_prob
            state_distribution = next_distribution
            
        return state_distribution

    def compute_route_success_probability(self, path, current_weather="clear"):
        """
        Computes the dynamic Success Probability of traversing a complete route path.
        Success is defined as: No severe weather disruptions AND no severe traffic gridlock.
        
        P(Success) = Product of P(Edge Success) for all edges in the path.
        where P(Edge Success) = 1.0 - (Bayesian High Traffic Prob * 0.4 + Weather Risk Prob * 0.3)
        """
        if not path or len(path) < 2:
            return 1.0

        joint_probability = 1.0
        
        for i in range(len(path) - 1):
            curr_loc = self.graph.get_location(path[i])
            conn = curr_loc.get_connection(path[i+1]) if curr_loc else None
            
            if conn:
                # 1. Base probabilities from dataset
                base_high_traffic = conn.traffic_prob.get("high", 0.2)
                
                # 2. Bayesian update for dynamic traffic risk under current weather warning
                updated_high_traffic = self.apply_bayesian_update(base_high_traffic, current_weather)
                
                # 3. Dynamic weather risk based on weather warning condition
                weather_risk = 0.0
                if current_weather == "rain":
                    weather_risk = conn.weather_prob.get("rain", 0.1)
                elif current_weather == "fog":
                    weather_risk = conn.weather_prob.get("fog", 0.15)
                else:
                    weather_risk = 0.02  # Minor residual baseline risk
                
                # Edge failure is a weighted function of heavy traffic risk and storm risk
                edge_failure_prob = (updated_high_traffic * 0.5) + (weather_risk * 0.4)
                edge_success_prob = max(0.1, 1.0 - edge_failure_prob)
                
                # Joint probability (edges are modeled as conditionally independent events)
                joint_probability *= edge_success_prob
                
        return round(joint_probability, 4)

    def estimate_dynamic_travel_time(self, distance, base_time, weather_state, initial_traffic="low", hours_elapsed=1):
        """
        Estimates actual travel time adjusting for traffic and weather congestion.
        Applies Markov State transitions to predict the traffic state, then adjusts.
        """
        # Predict traffic state distribution after hours elapsed
        traffic_dist = self.simulate_traffic_markov(initial_traffic, int(hours_elapsed))
        
        # Calculate expected delay multipliers
        # Low traffic: no delay, Medium traffic: +20% delay, High traffic: +50% delay
        traffic_multiplier = (
            traffic_dist["low"] * 1.0 +
            traffic_dist["medium"] * 1.25 +
            traffic_dist["high"] * 1.55
        )
        
        # Weather delay multiplier
        # Rain: +15% delay, Fog: +35% delay, Clear: no delay
        weather_multiplier = 1.0
        if weather_state == "rain":
            weather_multiplier = 1.15
        elif weather_state == "fog":
            weather_multiplier = 1.35
            
        adjusted_time = base_time * traffic_multiplier * weather_multiplier
        return round(adjusted_time, 1)

    def apply_environmental_factors(self, weather_state, traffic_state):
        """
        Iterates through the entire state-space graph and dynamically updates the travel time 
        (and potentially cost) based on the environmental uncertainty parameters.
        """
        for loc in self.graph.get_all_locations():
            for conn in loc.connections:
                conn.base_time = self.estimate_dynamic_travel_time(
                    distance=conn.distance,
                    base_time=conn.base_time,
                    weather_state=weather_state,
                    initial_traffic=traffic_state,
                    hours_elapsed=1
                )
