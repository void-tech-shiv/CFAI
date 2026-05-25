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
    algorithm: str = "astar"  # bfs, dfs, ucs, astar
    metric: str = "distance"  # distance, cost, time, utility
    max_budget: Optional[int] = None
    max_time: Optional[int] = None
    weather: str = "clear"  # clear, rain, fog
    traffic: str = "low"  # low, medium, high
    compare_algorithms: bool = True

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
    # The UncertaintyEngine modifies base_time based on weather and traffic.
    uncertainty_model.apply_environmental_factors(req.weather, req.traffic)

    # 2. CSP Filtering for Budget/Time Constraints
    # If constraints are provided, we run CSP to find if a valid route exists
    csp_status = {"valid": True, "message": "No constraints provided or constraints met."}
    if req.max_budget is not None or req.max_time is not None:
        csp = ItineraryCSP(graph, req.start_id, [req.goal_id], max_stops=1, max_budget=req.max_budget, max_time=req.max_time)
        csp_result = csp.solve()
        if not csp_result:
            csp_status = {"valid": False, "message": "No path satisfies the budget and time constraints."}
            # We can still run the regular algorithm to show what *would* be the path

    # 3. Main Algorithm Execution
    algo = req.algorithm.lower()
    main_result = None
    
    if algo == "bfs":
        main_result = search_manager.bfs(req.start_id, req.goal_id)
    elif algo == "dfs":
        main_result = search_manager.dfs(req.start_id, req.goal_id)
    elif algo == "ucs":
        main_result = search_manager.ucs(req.start_id, req.goal_id, metric_type="cost")
    elif algo == "astar":
        main_result = search_manager.a_star(req.start_id, req.goal_id, metric_type="utility")
    else:
        raise HTTPException(status_code=400, detail="Invalid algorithm selected")

    if not main_result["path"]:
        return {"error": "No path found between the selected locations.", "csp_status": csp_status}

    # 4. Multi-Attribute Utility Theory (Decision Making)
    # Calculate utility score for the found path
    utility_engine = DecisionEngine(graph)
    ranked = utility_engine.rank_routes([main_result])
    utility_score = ranked[0]["utility_score"] if ranked else 0.0

    # 5. Algorithm Comparison (Optional)
    comparisons = []
    if req.compare_algorithms:
        algos_to_run = ["bfs", "dfs", "ucs", "astar"]
        for a in algos_to_run:
            if a == algo:
                res = main_result
            else:
                if a == "bfs": res = search_manager.bfs(req.start_id, req.goal_id)
                elif a == "dfs": res = search_manager.dfs(req.start_id, req.goal_id)
                elif a == "ucs": res = search_manager.ucs(req.start_id, req.goal_id, metric_type="cost")
                elif a == "astar": res = search_manager.a_star(req.start_id, req.goal_id, metric_type="utility")
            
            comparisons.append({
                "algorithm": a.upper(),
                "execution_time_ns": res["execution_time_ns"],
                "distance": res["distance"],
                "cost": res["cost"],
                "time": res["time"],
                "explored_nodes": len(res["explored"]),
                "path": res["path"]
            })

    # Hydrate path with actual location objects for UI
    path_nodes = [graph.get_location(loc_id).__dict__ for loc_id in main_result["path"]]

    return {
        "path": main_result["path"],
        "path_nodes": path_nodes,
        "explored": main_result["explored"],
        "metrics": {
            "distance": main_result["distance"],
            "cost": main_result["cost"],
            "time": main_result["time"],
            "explored_count": len(main_result["explored"]),
            "execution_time_ns": main_result["execution_time_ns"],
            "utility_score": utility_score
        },
        "csp_status": csp_status,
        "comparisons": comparisons
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
