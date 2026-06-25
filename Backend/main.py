from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from models.location import TouristGraph
from algorithms.search import SearchManager
from algorithms.csp import ItineraryCSP
from algorithms.decision import DecisionEngine
from algorithms.uncertainty import UncertaintyEngine

app = FastAPI(title="Tourist Route Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global graph and managers
graph = TouristGraph()
search_manager = SearchManager(graph)
uncertainty_model = UncertaintyEngine(graph)

class PlanRequest(BaseModel):
    start_id: str
    goal_id: str
    algorithm: str = "astar"  # bfs, dfs, dfs_recursive, ucs, astar, minimax, alphabeta, min_conflicts
    metric: str = "distance"  # distance, cost, time, utility
    max_budget: Optional[int] = None
    max_time: Optional[int] = None
    weather: str = "clear"  # clear, rain, fog
    traffic: str = "low"  # low, medium, high
    compare_algorithms: bool = True
    avoid_tolls: bool = False
    avoid_highways: bool = False
    wheelchair: bool = False

@app.get("/api/locations")
def get_locations():
    locations = graph.get_all_locations()
    return {"locations": [loc.__dict__ for loc in locations]}

@app.post("/api/plan")
def plan_route(req: PlanRequest):
    # Reset graph to base state to prevent compounding/exponential environmental multipliers
    graph.load_graph()

    if not graph.get_location(req.start_id) or not graph.get_location(req.goal_id):
        raise HTTPException(status_code=404, detail="Start or Goal location not found")

    # 1. Update Graph Edge Weights based on Uncertainty (Weather/Traffic)
    uncertainty_model.apply_environmental_factors(req.weather, req.traffic)

    # 2. CSP Filtering for Budget/Time Constraints
    csp_status = {"valid": True, "message": "No constraints provided or constraints met."}
    if req.max_budget is not None or req.max_time is not None:
        csp = ItineraryCSP(graph, req.start_id, [req.goal_id], max_stops=1, max_budget=req.max_budget, max_time=req.max_time)
        csp_result = csp.solve()
        if not csp_result:
            csp_status = {"valid": False, "message": "No path satisfies the budget and time constraints."}

    # 3. Main Algorithm Execution
    algo = req.algorithm.lower()
    main_result = None
    
    if algo == "bfs":
        main_result = search_manager.bfs(req.start_id, req.goal_id)
    elif algo == "dfs":
        main_result = search_manager.dfs(req.start_id, req.goal_id)
    elif algo == "dfs_recursive":
        main_result = search_manager.dfs_recursive(req.start_id, req.goal_id)
    elif algo == "ucs":
        main_result = search_manager.ucs(req.start_id, req.goal_id, metric_type="cost")
    elif algo == "astar":
        main_result = search_manager.a_star(req.start_id, req.goal_id, metric_type="utility")
    elif algo == "minimax":
        main_result = search_manager.minimax(req.start_id, req.goal_id)
    elif algo == "alphabeta":
        main_result = search_manager.alphabeta(req.start_id, req.goal_id)
    elif algo == "min_conflicts":
        from algorithms.csp import MinConflictsLocalSearch
        target_pool = [loc.id for loc in graph.get_all_locations() if loc.is_open][:10] 
        if req.goal_id not in target_pool: target_pool.append(req.goal_id)
        solver = MinConflictsLocalSearch(graph, req.start_id, target_pool, max_stops=3)
        res = solver.solve(max_iterations=100)
        if res:
            main_result = {
                "path": res["itinerary"],
                "distance": res["distance"],
                "cost": res["cost"],
                "time": res["time"],
                "explored": [],
                "execution_time_ns": res["execution_time_ns"],
                "memory_usage_kb": 5.0,
                "nodes_explored": res["explored_nodes"],
                "efficiency": 100.0
            }
        else:
            main_result = {"path": None}
    else:
        raise HTTPException(status_code=400, detail="Invalid algorithm selected")

    if not main_result or not main_result.get("path"):
        return {"error": "No path found between the selected locations.", "csp_status": csp_status}

    # 4. Multi-Attribute Utility Theory (Decision Making)
    utility_engine = DecisionEngine(graph)
    ranked = utility_engine.rank_routes([main_result])
    utility_score = ranked[0]["utility_score"] if ranked else 0.0

    # 4b. Prediction Confidence & Fuel Cost
    prediction_confidence = 1.0
    if len(main_result.get("path", [])) > 1:
        _, hmm_conf = uncertainty_model.hmm_viterbi_predict(initial_state=req.traffic, observations=[req.weather] * len(main_result["path"]))
        prediction_confidence = hmm_conf

    # 5. Algorithm Comparison (Optional)
    comparisons = []
    if req.compare_algorithms:
        algos_to_run = ["bfs", "dfs", "dfs_recursive", "ucs", "astar", "minimax", "alphabeta", "min_conflicts"]
        for a in algos_to_run:
            try:
                if a == algo:
                    res = main_result
                else:
                    if a == "bfs": res = search_manager.bfs(req.start_id, req.goal_id)
                    elif a == "dfs": res = search_manager.dfs(req.start_id, req.goal_id)
                    elif a == "dfs_recursive": res = search_manager.dfs_recursive(req.start_id, req.goal_id)
                    elif a == "ucs": res = search_manager.ucs(req.start_id, req.goal_id, metric_type="cost")
                    elif a == "astar": res = search_manager.a_star(req.start_id, req.goal_id, metric_type="utility")
                    elif a == "minimax": res = search_manager.minimax(req.start_id, req.goal_id)
                    elif a == "alphabeta": res = search_manager.alphabeta(req.start_id, req.goal_id)
                    elif a == "min_conflicts":
                        from algorithms.csp import MinConflictsLocalSearch
                        target_pool = [loc.id for loc in graph.get_all_locations() if loc.is_open][:10] 
                        if req.goal_id not in target_pool: target_pool.append(req.goal_id)
                        solver = MinConflictsLocalSearch(graph, req.start_id, target_pool, max_stops=3)
                        mres = solver.solve(max_iterations=100)
                        if mres:
                            res = {
                                "path": mres["itinerary"],
                                "distance": mres["distance"],
                                "cost": mres["cost"],
                                "time": mres["time"],
                                "explored": [],
                                "execution_time_ns": mres["execution_time_ns"],
                                "memory_usage_kb": 5.0,
                                "nodes_explored": mres["explored_nodes"],
                                "efficiency": 100.0
                            }
                        else:
                            res = {"path": None}
                
                if res and res.get("path"):
                    comparisons.append({
                        "algorithm": a.upper(),
                        "execution_time_ns": res.get("execution_time_ns", 0),
                        "distance": res.get("distance", 0),
                        "cost": res.get("cost", 0),
                        "time": res.get("time", 0),
                        "explored_nodes": res.get("nodes_explored", len(res.get("explored", []))),
                        "memory_usage_kb": res.get("memory_usage_kb", 0),
                        "success_rate": 100.0 if res.get("path") else 0.0,
                        "path": res.get("path", [])
                    })
            except Exception as e:
                print(f"Error running {a}: {e}")

    # Hydrate path with actual location objects for UI
    path_nodes = [graph.get_location(loc_id).__dict__ for loc_id in main_result["path"]]

    return {
        "path": main_result["path"],
        "path_nodes": path_nodes,
        "explored": main_result.get("explored", []),
        "metrics": {
            "distance": main_result.get("distance", 0),
            "cost": main_result.get("cost", 0),
            "time": main_result.get("time", 0),
            "explored_count": len(main_result.get("explored", [])),
            "execution_time_ns": main_result.get("execution_time_ns", 0),
            "utility_score": utility_score,
            "prediction_confidence": prediction_confidence,
            "memory_usage_kb": main_result.get("memory_usage_kb", 0.0)
        },
        "csp_status": csp_status,
        "comparisons": comparisons
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
