import React, { useState } from 'react';
import { Settings, Play, SlidersHorizontal, CloudRain, Car, Cpu, Target } from 'lucide-react';

const SidebarControls = ({ locations, onPlanRoute, isLoading }) => {
  const [params, setParams] = useState({
    start_id: "loc_01",
    goal_id: "loc_10",
    algorithm: "astar",
    metric: "distance",
    max_budget: "",
    max_time: "",
    weather: "clear",
    traffic: "low",
    compare_algorithms: true
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setParams(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitParams = { ...params };
    if (submitParams.max_budget) submitParams.max_budget = parseInt(submitParams.max_budget);
    else submitParams.max_budget = null;
    
    if (submitParams.max_time) submitParams.max_time = parseInt(submitParams.max_time);
    else submitParams.max_time = null;

    onPlanRoute(submitParams);
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-6 text-sm">
      <div className="flex items-center gap-2 pb-4 border-b border-white/10">
        <Settings className="w-5 h-5 text-blue-400" />
        <h3 className="text-lg font-semibold tracking-wide">Mission Parameters</h3>
      </div>

      {/* Waypoints */}
      <div className="space-y-4">
        <div>
          <label className="block text-gray-400 mb-1.5 uppercase text-xs tracking-wider font-semibold">Origin</label>
          <select 
            name="start_id" 
            value={params.start_id} 
            onChange={handleChange}
            className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none transition"
          >
            {locations.map(loc => (
              <option key={loc.id} value={loc.id}>{loc.name}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-gray-400 mb-1.5 uppercase text-xs tracking-wider font-semibold">Destination</label>
          <select 
            name="goal_id" 
            value={params.goal_id} 
            onChange={handleChange}
            className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-purple-500 outline-none transition"
          >
            {locations.map(loc => (
              <option key={loc.id} value={loc.id}>{loc.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Algorithm Config */}
      <div className="space-y-4 p-4 bg-white/5 rounded-xl border border-white/5">
        <div>
          <label className="flex items-center gap-2 text-gray-400 mb-2 uppercase text-xs tracking-wider font-semibold">
            <Cpu className="w-4 h-4" /> Core Engine
          </label>
          <select 
            name="algorithm" 
            value={params.algorithm} 
            onChange={handleChange}
            className="w-full bg-black/60 border border-white/10 rounded-lg p-2 text-white outline-none"
          >
            <option value="astar">A* Search (Optimal & Informed)</option>
            <option value="ucs">Uniform Cost Search (Dijkstra)</option>
            <option value="bfs">Breadth-First Search (Uninformed)</option>
            <option value="dfs">Depth-First Search (Uninformed)</option>
          </select>
        </div>

        <div>
          <label className="flex items-center gap-2 text-gray-400 mb-2 uppercase text-xs tracking-wider font-semibold">
            <Target className="w-4 h-4" /> Objective Metric
          </label>
          <select 
            name="metric" 
            value={params.metric} 
            onChange={handleChange}
            className="w-full bg-black/60 border border-white/10 rounded-lg p-2 text-white outline-none"
          >
            <option value="distance">Minimize Distance</option>
            <option value="time">Minimize Travel Time</option>
            <option value="cost">Minimize Travel Cost</option>
            <option value="utility">Multi-Attribute Utility (Smart)</option>
          </select>
        </div>
      </div>

      {/* Constraints */}
      <div className="space-y-4">
        <label className="flex items-center gap-2 text-gray-400 uppercase text-xs tracking-wider font-semibold">
          <SlidersHorizontal className="w-4 h-4" /> CSP Limits (Optional)
        </label>
        <div className="grid grid-cols-2 gap-3">
          <input 
            type="number"
            name="max_budget"
            value={params.max_budget}
            onChange={handleChange}
            placeholder="Max Cost (₹)"
            className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white outline-none"
          />
          <input 
            type="number"
            name="max_time"
            value={params.max_time}
            onChange={handleChange}
            placeholder="Max Time (m)"
            className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white outline-none"
          />
        </div>
      </div>

      {/* Environment */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="flex items-center gap-2 text-gray-400 mb-1.5 uppercase text-xs tracking-wider font-semibold">
            <CloudRain className="w-3 h-3" /> Weather
          </label>
          <select 
            name="weather" 
            value={params.weather} 
            onChange={handleChange}
            className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white outline-none text-xs"
          >
            <option value="clear">Clear</option>
            <option value="rain">Rain (Delays)</option>
            <option value="fog">Fog (Hazard)</option>
          </select>
        </div>
        <div>
          <label className="flex items-center gap-2 text-gray-400 mb-1.5 uppercase text-xs tracking-wider font-semibold">
            <Car className="w-3 h-3" /> Traffic
          </label>
          <select 
            name="traffic" 
            value={params.traffic} 
            onChange={handleChange}
            className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white outline-none text-xs"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High (Severe Delays)</option>
          </select>
        </div>
      </div>

      {/* Execute */}
      <div className="mt-auto pt-4">
        <label className="flex items-center gap-2 text-gray-400 mb-4 text-xs cursor-pointer">
          <input 
            type="checkbox" 
            name="compare_algorithms"
            checked={params.compare_algorithms}
            onChange={handleChange}
            className="accent-blue-500 rounded bg-black/40"
          />
          Generate Engine Telemetry (Benchmarking)
        </label>
        
        <button 
          type="submit" 
          disabled={isLoading}
          className="w-full py-3.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-colors shadow-[0_0_20px_rgba(59,130,246,0.3)] flex justify-center items-center gap-2"
        >
          {isLoading ? 'Processing...' : 'Execute Calculation'} <Play className="w-4 h-4" />
        </button>
      </div>
    </form>
  );
};

export default SidebarControls;
