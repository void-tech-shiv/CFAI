class DecisionEngine:
    """
    Decision-Making Module implementing Multi-Attribute Utility Theory (MAUT).
    Computes a combined Utility Score for paths:
    
    Utility = w_d * Distance_norm + w_c * Cost_norm + w_t * Traffic_Risk_norm - w_r * Rating_norm
    
    Since we want to MINIMIZE Generalized Cost (Distance, Cost, Traffic Risk) 
    and MAXIMIZE Tourist Rating (which is subtracted, thus lowering generalized cost),
    the path with the MINIMUM utility score represents the mathematically OPTIMAL decision!
    """
    def __init__(self, graph):
        self.graph = graph

    def normalize_metrics(self, distance, cost, traffic_risk, avg_rating):
        """
        Normalizes metrics to a [0, 1] scale relative to domain maxima.
        Assists in multi-attribute comparison without dimensional bias.
        """
        # Maximum expected limits for normalization
        MAX_DIST = 1500.0  # Max circuit scale in km
        MAX_COST = 8000.0  # Max travel cost in INR
        MAX_RATING = 5.0   # Highest rating possible
        
        d_norm = min(distance / MAX_DIST, 1.0)
        c_norm = min(cost / MAX_COST, 1.0)
        t_risk_norm = min(traffic_risk, 1.0)  # Already [0, 1] probability
        r_norm = min(avg_rating / MAX_RATING, 1.0)
        
        return d_norm, c_norm, t_risk_norm, r_norm

    def compute_utility(self, distance, cost, traffic_risk, avg_rating, weights=None):
        """
        Computes the integrated utility score.
        Lower utility value is better (treated as an integrated cost penalty).
        """
        if not weights:
            weights = {
                "distance": 0.3,
                "cost": 0.3,
                "traffic": 0.2,
                "rating": 0.2
            }
            
        d_norm, c_norm, t_risk_norm, r_norm = self.normalize_metrics(
            distance, cost, traffic_risk, avg_rating
        )
        
        # Apply utility weight equation (subtracted rating reward)
        utility_score = (
            weights.get("distance", 0.3) * d_norm +
            weights.get("cost", 0.3) * c_norm +
            weights.get("traffic", 0.2) * t_risk_norm -
            weights.get("rating", 0.2) * r_norm
        )
        
        return utility_score

    def rank_routes(self, candidate_routes, weights=None):
        """
        Ranks a list of candidate routes and selects the optimal one.
        Each candidate in candidate_routes is a dictionary containing:
        - "path": List of node IDs
        - "distance": float
        - "cost": float
        - "time": float
        
        Returns a list of ranked candidate routes, sorted by utility score ascending (best first),
        with utility calculations and rankings injected.
        """
        if not candidate_routes:
            return []

        ranked_results = []
        for route in candidate_routes:
            if not route or not route.get("path"):
                continue
                
            path = route["path"]
            
            # Calculate path-level average rating and cumulative traffic risk
            total_rating = 0.0
            total_edges = 0
            cumulative_traffic_risk = 0.0
            
            for i, loc_id in enumerate(path):
                loc = self.graph.get_location(loc_id)
                if loc:
                    total_rating += loc.rating
                    
                if i < len(path) - 1:
                    curr_loc = self.graph.get_location(loc_id)
                    conn = curr_loc.get_connection(path[i+1]) if curr_loc else None
                    if conn:
                        # High traffic probability is the risk factor
                        cumulative_traffic_risk += conn.traffic_prob.get("high", 0.2)
                        total_edges += 1
            
            avg_rating = total_rating / len(path) if path else 4.0
            avg_traffic_risk = cumulative_traffic_risk / total_edges if total_edges > 0 else 0.2
            
            score = self.compute_utility(
                route["distance"], 
                route["cost"], 
                avg_traffic_risk, 
                avg_rating, 
                weights
            )
            
            # Create a rich detailed dictionary
            ranked_route = dict(route)
            ranked_route["average_rating"] = round(avg_rating, 2)
            ranked_route["average_traffic_risk"] = round(avg_traffic_risk, 2)
            ranked_route["utility_score"] = round(score, 4)
            ranked_results.append(ranked_route)
            
        # Sort ascending: lower score is best
        ranked_results.sort(key=lambda x: x["utility_score"])
        
        # Inject numerical rank
        for index, item in enumerate(ranked_results):
            item["rank"] = index + 1
            
        return ranked_results
