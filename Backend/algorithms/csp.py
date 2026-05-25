import time
from algorithms.search import SearchManager

class ItineraryCSP:
    """
    Constraint Satisfaction Problem (CSP) solver for planning multi-stop tourist itineraries.
    
    Variables: [Slot_1, Slot_2, ..., Slot_N] where N is the limited number of destinations.
    Domains: Operational tourist locations.
    
    Constraints:
    1. Budget limit (cumulative path cost).
    2. Travel time limit (cumulative travel time).
    3. Crowd level constraints (individual node crowd index <= tolerance).
    4. Operational status constraint (must be Open).
    5. Uniqueness (avoid visiting the same location twice).
    6. Connectivity (roads must exist/connect slots).
    
    Heuristics:
    - MRV (Minimum Remaining Values): Selects the slot with the fewest valid domains.
    - LCV (Least Constraining Value): Selects values that rule out the fewest options for remaining slots.
    """
    def __init__(self, graph, start_id, target_pool, max_stops=4, max_budget=5000, max_time=600, max_crowd=0.8):
        self.graph = graph
        self.start_id = start_id
        # Pool of locations the user is interested in visiting
        self.target_pool = [t for t in target_pool if t != start_id]
        self.max_stops = min(max_stops, len(self.target_pool))
        
        # Constraints
        self.max_budget = max_budget
        self.max_time = max_time
        self.max_crowd = max_crowd
        
        # Graph searcher to estimate path metrics between slots
        self.searcher = SearchManager(graph)

        # Variables: slots in itinerary [Slot_1, Slot_2, ..., Slot_N]
        self.variables = [f"Slot_{i}" for i in range(1, self.max_stops + 1)]
        
        # Domains: Initialized with target pool locations that meet static constraints
        self.domains = {}
        for var in self.variables:
            self.domains[var] = self._get_initial_domain()

    def _get_initial_domain(self):
        """Returns the set of locations from target pool meeting individual node constraints."""
        valid_domain = []
        for loc_id in self.target_pool:
            loc = self.graph.get_location(loc_id)
            if loc and loc.is_open and loc.crowd_level <= self.max_crowd:
                valid_domain.append(loc_id)
        return valid_domain

    def solve(self):
        """
        Runs backtracking search to find a valid itinerary sequence.
        Returns a dictionary with result path, metrics, and nodes explored or None.
        """
        start_time = time.perf_counter_ns()
        
        # Initial assignment: Slot_0 = start_id (implicit start, not a variable to solve for)
        assignment = {}
        self.nodes_explored_count = 0
        
        success = self._backtrack(assignment)
        
        elapsed_ns = time.perf_counter_ns() - start_time
        
        if success:
            # Reconstruct the full path connecting the slots in the solved assignment
            full_route = [self.start_id]
            for var in self.variables:
                full_route.append(assignment[var])
                
            total_dist, total_cost, total_time = self._calculate_itinerary_metrics(full_route)
            
            return {
                "itinerary": full_route,
                "distance": total_dist,
                "cost": total_cost,
                "time": total_time,
                "explored_nodes": self.nodes_explored_count,
                "execution_time_ns": elapsed_ns
            }
        
        return None

    def _calculate_itinerary_metrics(self, path):
        """Calculates total actual route metrics by finding optimal paths between stops."""
        total_dist = 0
        total_cost = 0
        total_time = 0
        
        for i in range(len(path) - 1):
            res = self.searcher.a_star(path[i], path[i+1], metric_type="distance")
            if res["path"]:
                total_dist += res["distance"]
                total_cost += res["cost"]
                total_time += res["time"]
            else:
                # Fallback if no road path exists between successive selections
                return float('inf'), float('inf'), float('inf')
                
        return total_dist, total_cost, total_time

    def _is_consistent(self, var, val, assignment):
        """Checks if assigning val to var is consistent with current assignments and constraints."""
        # 1. Uniqueness constraint (no duplicate destinations)
        if val in assignment.values():
            return False
            
        # Temporarily apply assignment
        temp_assignment = dict(assignment)
        temp_assignment[var] = val
        
        # Reconstruct sequence of stops
        stops_sequence = [self.start_id]
        for v in self.variables:
            if v in temp_assignment:
                stops_sequence.append(temp_assignment[v])
            else:
                break
                
        # 2. Estimate cumulative cost and time
        tot_dist, tot_cost, tot_time = self._calculate_itinerary_metrics(stops_sequence)
        
        if tot_cost > self.max_budget:
            return False
        if tot_time > self.max_time:
            return False
            
        return True

    def _get_mrv_variable(self, assignment):
        """
        Minimum Remaining Values (MRV) Heuristic
        Selects the unassigned variable (slot) with the smallest remaining domain.
        """
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return None
            
        # Count remaining valid values for each unassigned variable
        mrv_var = min(unassigned, key=lambda var: len(self._get_valid_domain_for_var(var, assignment)))
        return mrv_var

    def _get_valid_domain_for_var(self, var, assignment):
        """Filters domain values that are consistent with the current assignment."""
        return [val for val in self.domains[var] if self._is_consistent(var, val, assignment)]

    def _get_lcv_ordered_values(self, var, assignment):
        """
        Least Constraining Value (LCV) Heuristic
        Sorts domain values based on how many options they leave open for remaining unassigned variables.
        """
        valid_vals = self._get_valid_domain_for_var(var, assignment)
        unassigned_vars = [v for v in self.variables if v not in assignment and v != var]
        
        if not unassigned_vars:
            return valid_vals  # No subsequent variables to constrain
            
        def lcv_score(val):
            # Temporarily assign val to var
            temp_assignment = dict(assignment)
            temp_assignment[var] = val
            
            # Count the total number of remaining choices for all unassigned variables
            choices_left = 0
            for u_var in unassigned_vars:
                choices_left += len(self._get_valid_domain_for_var(u_var, temp_assignment))
            return -choices_left  # Negate so we can sort in ascending order (higher choices left first)
            
        return sorted(valid_vals, key=lcv_score)

    def _backtrack(self, assignment):
        """Recursive backtracking search using MRV and LCV heuristics."""
        self.nodes_explored_count += 1
        
        # If all variables are assigned, we are done
        if len(assignment) == len(self.variables):
            return True
            
        # Select next variable using MRV Heuristic
        var = self._get_mrv_variable(assignment)
        
        # Order domain values using LCV Heuristic
        ordered_values = self._get_lcv_ordered_values(var, assignment)
        
        for val in ordered_values:
            # We already know these values are consistent via LCV domain filtering
            assignment[var] = val
            
            # Recurse
            if self._backtrack(assignment):
                return True
                
            # Backtrack
            del assignment[var]
            
        return False
