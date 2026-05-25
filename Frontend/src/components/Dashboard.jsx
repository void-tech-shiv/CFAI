import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Loader2 } from 'lucide-react';
import SidebarControls from './SidebarControls';
import MapView from './MapView';
import StatsPanel from './StatsPanel';

const API_BASE = "http://127.0.0.1:8000/api";

const Dashboard = ({ onBack }) => {
  const [locations, setLocations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [routeResult, setRouteResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch locations
    fetch(`${API_BASE}/locations`)
      .then(res => res.json())
      .then(data => setLocations(data.locations || []))
      .catch(err => console.error("Failed to fetch locations:", err));
  }, []);

  const handlePlanRoute = async (planParams) => {
    setIsLoading(true);
    setError(null);
    setRouteResult(null);

    try {
      const response = await fetch(`${API_BASE}/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(planParams)
      });
      
      const data = await response.json();
      if (!response.ok || data.error) {
        setError(data.detail || data.error || "Failed to plan route.");
      } else {
        setRouteResult(data);
      }
    } catch (err) {
      setError("Network error. Is the backend running?");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 1.05 }}
      transition={{ duration: 0.5 }}
      className="h-screen w-full flex flex-col p-4 gap-4 z-10 relative"
    >
      {/* Header */}
      <header className="flex items-center justify-between glass-panel px-6 py-4 rounded-2xl">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="p-2 hover:bg-white/10 rounded-full transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            AI Operations Center
          </h2>
        </div>
        <div className="flex items-center gap-3 text-sm font-mono text-gray-400">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          SYSTEM ONLINE
        </div>
      </header>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 overflow-hidden">
        {/* Left Sidebar */}
        <div className="lg:col-span-1 glass-panel rounded-2xl overflow-y-auto">
          <SidebarControls 
            locations={locations} 
            onPlanRoute={handlePlanRoute}
            isLoading={isLoading}
          />
        </div>

        {/* Center/Right Area */}
        <div className="lg:col-span-3 flex flex-col gap-4 overflow-hidden">
          {/* Map Area */}
          <div className="flex-1 glass-panel rounded-2xl relative overflow-hidden">
            {locations.length > 0 ? (
              <MapView locations={locations} routeResult={routeResult} />
            ) : (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
              </div>
            )}
            
            {/* Loading Overlay */}
            {isLoading && (
              <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex flex-col items-center justify-center z-[1000]">
                <Loader2 className="w-12 h-12 animate-spin text-blue-500 mb-4" />
                <p className="text-lg font-mono text-blue-400">Calculating optimal trajectory...</p>
              </div>
            )}

            {/* Error Toast */}
            {error && (
              <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-red-900/80 border border-red-500 text-red-100 px-6 py-3 rounded-full backdrop-blur-md z-[1000] shadow-2xl shadow-red-500/20">
                {error}
              </div>
            )}
          </div>

          {/* Stats Area (conditionally shown) */}
          {routeResult && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              className="glass-panel rounded-2xl p-4 shrink-0"
            >
              <StatsPanel routeResult={routeResult} />
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
