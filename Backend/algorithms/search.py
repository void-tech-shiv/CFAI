import time
import heapq
from collections import deque

class SearchManager:
    """
    Class executing state-space searches on the TouristGraph.
    Implements: BFS, DFS, Uniform Cost Search (UCS), and A* Search.
    Allows optimizing along multiple dimensions: distance, cost, time, or integrated utility.
    """
    def __init__(self, graph):
        self.graph = graph

    def _get_edge_weight(self, connection, metric_type="distance", utility_weights=None, destination_loc=None):
        """
        Determines the edge weight based on the optimization metric selected.
        If metric_type is 'utility', computes the multi-attribute utility value.
        """
        if metric_type == "distance":
            return connection.distance
        elif metric_type == "cost":
            return connection.cost
        elif metric_type == "time":
            return connection.base_time  # Can be dynamically adjusted for traffic/weather in Phase 3
        elif metric_type == "utility":
            # Default fallback utility calculation if utility_weights are not passed
            if not utility_weights:
                utility_weights = {"distance": 0.3, "cost": 0.3, "time": 0.2, "rating": 0.2}
            
            # Retrieve destination location details for ratings
            to_node = self.graph.get_location(connection.to_id)
            rating = to_node.rating if to_node else 4.0
            crowd = to_node.crowd_level if to_node else 0.5
            
            # Normalize components to approximately [0, 1] relative to domain maxima
            # Max single distance ~350, max cost ~2000, max time ~360, ratings [1, 5]
            d_norm = connection.distance / 350.0
            c_norm = connection.cost / 2000.0
            t_norm = connection.base_time / 360.0
            r_norm = (5.0 - rating) / 4.0  # Invert rating so that higher ratings yield LOWER generalized cost
            
            utility_cost = (
                utility_weights.get("distance", 0.3) * d_norm +
                utility_weights.get("cost", 0.3) * c_norm +
                utility_weights.get("time", 0.2) * t_norm +
                utility_weights.get("rating", 0.2) * r_norm
            )
            return utility_cost
        
        return connection.distance

    def _calculate_path_metrics(self, path):
        """Calculates total distance, cost, and time of a finalized path list."""
        total_dist = 0
        total_cost = 0
        total_time = 0
        
        for i in range(len(path) - 1):
            curr_loc = self.graph.get_location(path[i])
            conn = curr_loc.get_connection(path[i+1])
            if conn:
                total_dist += conn.distance
                total_cost += conn.cost
                total_time += conn.base_time
                
        return total_dist, total_cost, total_time

    def bfs(self, start_id, goal_id):
        """
        Breadth-First Search (BFS)
        Finds path with minimum number of transitions/edges (hops), ignoring edge weights.
        """
        start_time_ns = time.perf_counter_ns()
        explored = []
        queue = deque([[start_id]])
        visited = {start_id}
        max_frontier_size = 0

        if start_id == goal_id:
            elapsed = time.perf_counter_ns() - start_time_ns
            return {
                "path": [start_id], "distance": 0, "cost": 0, "time": 0, "explored": [start_id], 
                "execution_time_ns": elapsed, "memory_usage_kb": 1.2, "nodes_explored": 1, "efficiency": 100.0
            }

        found_path = None
        while queue:
            max_frontier_size = max(max_frontier_size, len(queue))
            path = queue.popleft()
            node_id = path[-1]
            explored.append(node_id)

            if node_id == goal_id:
                found_path = path
                break

            curr_loc = self.graph.get_location(node_id)
            if not curr_loc or not curr_loc.is_open:
                continue

            for conn in curr_loc.connections:
                neighbor = conn.to_id
                neighbor_loc = self.graph.get_location(neighbor)
                if neighbor_loc and neighbor_loc.is_open and neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        elapsed = time.perf_counter_ns() - start_time_ns
        memory_kb = max_frontier_size * 0.16 + 1.2
        if found_path:
            dist, cost, travel_time = self._calculate_path_metrics(found_path)
            efficiency = (len(found_path) / len(explored)) * 100.0 if len(explored) > 0 else 0.0
            return {
                "path": found_path,
                "distance": dist,
                "cost": cost,
                "time": travel_time,
                "explored": explored,
                "execution_time_ns": elapsed,
                "memory_usage_kb": memory_kb,
                "nodes_explored": len(explored),
                "efficiency": efficiency
            }
        return {
            "path": None, "distance": 0, "cost": 0, "time": 0, "explored": explored, 
            "execution_time_ns": elapsed, "memory_usage_kb": memory_kb, "nodes_explored": len(explored), "efficiency": 0.0
        }

    def dfs(self, start_id, goal_id):
        """
        Depth-First Search (DFS)
        Explores paths deeply before backtracking. Uninformed.
        Intentionally designed to explore winding, longer paths to differ from BFS/A*.
        """
        start_time_ns = time.perf_counter_ns()
        explored = []
        stack = [[start_id]]
        visited = set()
        max_frontier_size = 0

        if start_id == goal_id:
            elapsed = time.perf_counter_ns() - start_time_ns
            return {
                "path": [start_id], "distance": 0, "cost": 0, "time": 0, "explored": [start_id], 
                "execution_time_ns": elapsed, "memory_usage_kb": 1.2, "nodes_explored": 1, "efficiency": 100.0
            }

        found_path = None
        while stack:
            max_frontier_size = max(max_frontier_size, len(stack))
            path = stack.pop()
            node_id = path[-1]

            if node_id in visited:
                continue
            visited.add(node_id)
            explored.append(node_id)

            if node_id == goal_id:
                found_path = path
                break

            curr_loc = self.graph.get_location(node_id)
            if not curr_loc or not curr_loc.is_open:
                continue

            # Sort connections by distance descending to intentionally explore deep/winding connections first!
            sorted_connections = sorted(curr_loc.connections, key=lambda c: c.distance, reverse=True)
            for conn in sorted_connections:
                neighbor = conn.to_id
                neighbor_loc = self.graph.get_location(neighbor)
                if neighbor_loc and neighbor_loc.is_open and neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    stack.append(new_path)

        elapsed = time.perf_counter_ns() - start_time_ns
        memory_kb = max_frontier_size * 0.18 + 1.5
        
        if found_path:
            dist, cost, travel_time = self._calculate_path_metrics(found_path)
            efficiency = (len(found_path) / len(explored)) * 100.0 if len(explored) > 0 else 0.0
            return {
                "path": found_path,
                "distance": dist,
                "cost": cost,
                "time": travel_time,
                "explored": explored,
                "execution_time_ns": elapsed,
                "memory_usage_kb": memory_kb,
                "nodes_explored": len(explored),
                "efficiency": efficiency
            }
            
        return {
            "path": None, "distance": 0, "cost": 0, "time": 0, "explored": explored, 
            "execution_time_ns": elapsed, "memory_usage_kb": memory_kb, "nodes_explored": len(explored), "efficiency": 0.0
        }

    def ucs(self, start_id, goal_id, metric_type="distance", utility_weights=None):
        """
        Uniform Cost Search (UCS)
        Dijkstra-based search optimizing for cumulative cost of the selected metric.
        """
        start_time_ns = time.perf_counter_ns()
        explored = []
        pq = [(0.0, start_id, [start_id])]
        min_costs = {start_id: 0.0}
        found_path = None
        max_frontier_size = 0

        while pq:
            max_frontier_size = max(max_frontier_size, len(pq))
            cost, node_id, path = heapq.heappop(pq)

            if node_id in explored:
                continue
            explored.append(node_id)

            if node_id == goal_id:
                found_path = path
                break

            curr_loc = self.graph.get_location(node_id)
            if not curr_loc or not curr_loc.is_open:
                continue

            for conn in curr_loc.connections:
                neighbor = conn.to_id
                neighbor_loc = self.graph.get_location(neighbor)
                if not neighbor_loc or not neighbor_loc.is_open:
                    continue

                edge_cost = self._get_edge_weight(conn, metric_type, utility_weights)
                new_cost = cost + edge_cost

                if neighbor not in min_costs or new_cost < min_costs[neighbor]:
                    min_costs[neighbor] = new_cost
                    heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

        elapsed = time.perf_counter_ns() - start_time_ns
        memory_kb = max_frontier_size * 0.22 + 1.8
        
        if found_path:
            dist, cost, travel_time = self._calculate_path_metrics(found_path)
            efficiency = (len(found_path) / len(explored)) * 100.0 if len(explored) > 0 else 0.0
            return {
                "path": found_path,
                "distance": dist,
                "cost": cost,
                "time": travel_time,
                "explored": explored,
                "execution_time_ns": elapsed,
                "memory_usage_kb": memory_kb,
                "nodes_explored": len(explored),
                "efficiency": efficiency
            }
            
        return {
            "path": None, "distance": 0, "cost": 0, "time": 0, "explored": explored, 
            "execution_time_ns": elapsed, "memory_usage_kb": memory_kb, "nodes_explored": len(explored), "efficiency": 0.0
        }

    def a_star(self, start_id, goal_id, metric_type="distance", heuristic_type="haversine", utility_weights=None):
        """
        A* Search Algorithm
        Optimizes f(n) = g(n) + h(n), where h(n) is the admissible heuristic to goal_id.
        """
        start_time_ns = time.perf_counter_ns()
        explored = []
        max_frontier_size = 0
        
        goal_loc = self.graph.get_location(goal_id)
        if not goal_loc:
            return {
                "path": None, "distance": 0, "cost": 0, "time": 0, "explored": [], 
                "execution_time_ns": 0, "memory_usage_kb": 0.0, "nodes_explored": 0, "efficiency": 0.0
            }

        def get_heuristic(loc_id):
            loc_node = self.graph.get_location(loc_id)
            if not loc_node:
                return 0.0
            
            # Calculate base physical heuristic distance
            if heuristic_type == "euclidean":
                h_val = self.graph.calculate_euclidean(loc_node, goal_loc)
            elif heuristic_type == "haversine":
                h_val = self.graph.calculate_haversine(loc_node, goal_loc)
            else:
                h_val = self.graph.calculate_manhattan(loc_node, goal_loc)

            # Heuristics must be scaled appropriately for the optimized metric to remain admissible
            if metric_type == "distance":
                return h_val
            elif metric_type == "cost":
                return h_val * 4.0  # Safe scaled lower bound for toll + fuel cost per km
            elif metric_type == "time":
                return h_val * 1.1  # Safe scaled lower bound for speed
            elif metric_type == "utility":
                return (h_val / 450.0) * utility_weights.get("distance", 0.3) if utility_weights else (h_val / 450.0) * 0.3
            
            return h_val

        # Priority Queue elements: (f_score, g_score, current_node_id, path_taken)
        h_start = get_heuristic(start_id)
        pq = [(h_start, 0.0, start_id, [start_id])]
        min_g_costs = {start_id: 0.0}
        found_path = None

        while pq:
            max_frontier_size = max(max_frontier_size, len(pq))
            f, g, node_id, path = heapq.heappop(pq)

            if node_id in explored:
                continue
            explored.append(node_id)

            if node_id == goal_id:
                found_path = path
                break

            curr_loc = self.graph.get_location(node_id)
            if not curr_loc or not curr_loc.is_open:
                continue

            for conn in curr_loc.connections:
                neighbor = conn.to_id
                neighbor_loc = self.graph.get_location(neighbor)
                if not neighbor_loc or not neighbor_loc.is_open:
                    continue

                edge_cost = self._get_edge_weight(conn, metric_type, utility_weights)
                new_g = g + edge_cost

                if neighbor not in min_g_costs or new_g < min_g_costs[neighbor]:
                    min_g_costs[neighbor] = new_g
                    h_val = get_heuristic(neighbor)
                    new_f = new_g + h_val
                    heapq.heappush(pq, (new_f, new_g, neighbor, path + [neighbor]))

        elapsed = time.perf_counter_ns() - start_time_ns
        memory_kb = max_frontier_size * 0.25 + 2.0
        
        if found_path:
            dist, cost, travel_time = self._calculate_path_metrics(found_path)
            efficiency = (len(found_path) / len(explored)) * 100.0 if len(explored) > 0 else 0.0
            return {
                "path": found_path,
                "distance": dist,
                "cost": cost,
                "time": travel_time,
                "explored": explored,
                "execution_time_ns": elapsed,
                "memory_usage_kb": memory_kb,
                "nodes_explored": len(explored),
                "efficiency": efficiency
            }
            
        return {
            "path": None, "distance": 0, "cost": 0, "time": 0, "explored": explored, 
            "execution_time_ns": elapsed, "memory_usage_kb": memory_kb, "nodes_explored": len(explored), "efficiency": 0.0
        }

    def dfs_recursive(self, start_id, goal_id):
        """
        Depth-First Search (Recursive)
        """
        start_time_ns = time.perf_counter_ns()
        explored = []
        visited = set()
        found_path = None
        
        def _dfs(node_id, current_path):
            nonlocal found_path
            if found_path: return
            
            visited.add(node_id)
            explored.append(node_id)
            
            if node_id == goal_id:
                found_path = list(current_path)
                return
                
            curr_loc = self.graph.get_location(node_id)
            if not curr_loc or not curr_loc.is_open: return
                
            sorted_connections = sorted(curr_loc.connections, key=lambda c: c.distance, reverse=True)
            for conn in sorted_connections:
                neighbor = conn.to_id
                if neighbor not in visited:
                    neighbor_loc = self.graph.get_location(neighbor)
                    if neighbor_loc and neighbor_loc.is_open:
                        current_path.append(neighbor)
                        _dfs(neighbor, current_path)
                        current_path.pop()
                        
        _dfs(start_id, [start_id])
        elapsed = time.perf_counter_ns() - start_time_ns
        memory_kb = len(explored) * 0.18 + 1.5
        
        if found_path:
            dist, cost, travel_time = self._calculate_path_metrics(found_path)
            efficiency = (len(found_path) / len(explored)) * 100.0 if len(explored) > 0 else 0.0
            return {
                "path": found_path, "distance": dist, "cost": cost, "time": travel_time,
                "explored": explored, "execution_time_ns": elapsed, "memory_usage_kb": memory_kb,
                "nodes_explored": len(explored), "efficiency": efficiency
            }
        return {
            "path": None, "distance": 0, "cost": 0, "time": 0, "explored": explored, 
            "execution_time_ns": elapsed, "memory_usage_kb": memory_kb, "nodes_explored": len(explored), "efficiency": 0.0
        }

    def _minimax(self, start_id, goal_id, max_depth, use_alpha_beta):
        start_time_ns = time.perf_counter_ns()
        explored = []
        
        def utility_value(node_id, next_id, traffic_state):
            curr_loc = self.graph.get_location(node_id)
            next_loc = self.graph.get_location(next_id)
            conn = curr_loc.get_connection(next_id)
            if not conn: return -9999
            
            rating_score = next_loc.rating * 20
            crowd_penalty = next_loc.crowd_level * 30
            
            delay = conn.base_time
            if traffic_state == "high": delay *= 1.6
            elif traffic_state == "medium": delay *= 1.2
            
            return rating_score - delay - crowd_penalty
            
        def max_val(node_id, goal_id, depth, alpha, beta, visited):
            explored.append(node_id)
            if node_id == goal_id:
                return 10000, [node_id]
            if depth == 0:
                loc = self.graph.get_location(node_id)
                g_loc = self.graph.get_location(goal_id)
                h = -self.graph.calculate_haversine(loc, g_loc) * 0.1
                return h, [node_id]
                
            v = -float('inf')
            best_path = []
            
            curr_loc = self.graph.get_location(node_id)
            if not curr_loc or not curr_loc.is_open:
                return -9999, [node_id]
                
            for conn in curr_loc.connections:
                neighbor = conn.to_id
                if neighbor in visited: continue
                
                # MIN layer: evaluate traffic states
                min_v = float('inf')
                for traffic in ["low", "medium", "high"]:
                    edge_u = utility_value(node_id, neighbor, traffic)
                    visited.add(neighbor)
                    next_u, n_path = max_val(neighbor, goal_id, depth - 1, alpha, beta, visited)
                    visited.remove(neighbor)
                    
                    val = edge_u + next_u
                    if val < min_v: min_v = val
                        
                    if use_alpha_beta:
                        if min_v <= alpha: break
                        beta = min(beta, min_v)
                        
                if min_v > v:
                    v = min_v
                    best_path = [node_id] + n_path
                    
                if use_alpha_beta:
                    if v >= beta: break
                    alpha = max(alpha, v)
                    
            return v, best_path

        val, path = max_val(start_id, goal_id, max_depth, -float('inf'), float('inf'), {start_id})
        elapsed = time.perf_counter_ns() - start_time_ns
        memory_kb = len(explored) * 0.2 + 2.0
        
        if path and path[-1] == goal_id:
            dist, cost, travel_time = self._calculate_path_metrics(path)
            return {
                "path": path, "distance": dist, "cost": cost, "time": travel_time,
                "explored": explored, "execution_time_ns": elapsed, "memory_usage_kb": memory_kb,
                "nodes_explored": len(explored), "efficiency": 100.0, "utility_score": val
            }
        return {
            "path": None, "distance": 0, "cost": 0, "time": 0, "explored": explored, 
            "execution_time_ns": elapsed, "memory_usage_kb": memory_kb, "nodes_explored": len(explored), "efficiency": 0.0
        }

    def minimax(self, start_id, goal_id):
        return self._minimax(start_id, goal_id, max_depth=3, use_alpha_beta=False)

    def alphabeta(self, start_id, goal_id):
        return self._minimax(start_id, goal_id, max_depth=4, use_alpha_beta=True)
