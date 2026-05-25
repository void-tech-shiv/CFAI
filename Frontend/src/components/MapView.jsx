import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { 
  Maximize2, Minimize2, Play, RefreshCw, Layers, ShieldCheck, 
  MapPin, Activity, Clock, IndianRupee, Sliders, AlertTriangle
} from 'lucide-react';

// Color map for algorithms
const ALG_METRIC_STYLES = {
  "BFS": { color: "#22d3ee", shadow: "rgba(34, 211, 238, 0.8)", label: "BFS (Min Hops)", pathClass: "glow-path-cyan", width: 3 },
  "DFS": { color: "#f97316", shadow: "rgba(249, 115, 22, 0.8)", label: "DFS (Deep Winding)", pathClass: "glow-path-orange", width: 3 },
  "UCS": { color: "#22c55e", shadow: "rgba(34, 197, 94, 0.8)", label: "UCS (Economic Cost)", pathClass: "glow-path-green", width: 3 },
  "ASTAR": { color: "#a855f7", shadow: "rgba(168, 85, 247, 0.8)", label: "A* Search (Smart Utility)", pathClass: "glow-path-purple", width: 3 }
};

// 1. Custom Leaflet HTML glowing markers (divIcon)
const getCustomMarkerIcon = (type, color = "#22d3ee", pulse = false) => {
  let content = "";
  
  if (type === "start") {
    content = `
      <div class="relative flex items-center justify-center w-8 h-8">
        <span class="absolute inline-flex h-8 w-8 rounded-full bg-green-500/40 animate-ping"></span>
        <span class="absolute inline-flex h-6 w-6 rounded-full bg-green-500/20 marker-ripple"></span>
        <span class="relative inline-flex rounded-full h-4 w-4 bg-green-400 border-2 border-white shadow-[0_0_15px_#22c55e]"></span>
      </div>
    `;
  } else if (type === "goal") {
    content = `
      <div class="relative flex items-center justify-center w-8 h-8">
        <span class="absolute inline-flex h-8 w-8 rounded-full bg-red-500/40 animate-ping"></span>
        <span class="absolute inline-flex h-6 w-6 rounded-full bg-red-500/20 marker-ripple"></span>
        <span class="relative inline-flex rounded-full h-4 w-4 bg-red-500 border-2 border-white shadow-[0_0_15px_#ef4444]"></span>
      </div>
    `;
  } else if (type === "explored") {
    content = `
      <div class="relative flex items-center justify-center w-6 h-6 animate-pulse">
        <span class="absolute inline-flex h-6 w-6 rounded-full bg-yellow-500/30 marker-ripple"></span>
        <span class="relative inline-flex rounded-full h-3 w-3 bg-yellow-500 border border-white shadow-[0_0_10px_#eab308]"></span>
      </div>
    `;
  } else if (type === "crowded") {
    content = `
      <div class="relative flex items-center justify-center w-7 h-7">
        <span class="absolute inline-flex h-7 w-7 rounded-full bg-orange-500/20 hazard-glow-red"></span>
        <span class="relative inline-flex rounded-full h-3 w-3 bg-orange-500 border border-white shadow-[0_0_10px_#f97316]"></span>
      </div>
    `;
  } else if (type === "route") {
    content = `
      <div class="relative flex items-center justify-center w-7 h-7">
        <span class="absolute inline-flex h-5 w-5 rounded-full" style="background-color: ${color}33"></span>
        <span class="relative inline-flex rounded-full h-3.5 w-3.5 border-2 border-white" style="background-color: ${color}; box-shadow: 0 0 12px ${color}"></span>
      </div>
    `;
  } else {
    // Normal Unvisited node (Obsidian center with cyan halo)
    content = `
      <div class="relative flex items-center justify-center w-6 h-6 group">
        <span class="absolute inline-flex h-4 w-4 rounded-full bg-cyan-500/10 group-hover:bg-cyan-500/30 transition"></span>
        <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-zinc-950 border-2 border-cyan-400 shadow-[0_0_8px_#22d3ee] transition group-hover:scale-125"></span>
      </div>
    `;
  }

  return L.divIcon({
    className: 'custom-div-icon',
    html: content,
    iconSize: [32, 32],
    iconAnchor: [16, 16]
  });
};

// 2. Perpendicular Bezier curved coordinates generator for parallel spacing
const getBezierCurvePoints = (p1, p2, offsetIdx = 0, routeCount = 1) => {
  const [lat1, lon1] = p1;
  const [lat2, lon2] = p2;
  
  // Calculate perpendicular unit vector for parallel offsets
  const dLat = lat2 - lat1;
  const dLon = lon2 - lon1;
  const len = Math.sqrt(dLat * dLat + dLon * dLon) || 1;
  const pLat = -dLon / len;
  const pLon = dLat / len;
  
  // Horizontal spacing offset (around 2km to avoid overlapping roads)
  let shift = 0;
  if (routeCount > 1) {
    shift = (offsetIdx - (routeCount - 1) / 2) * 0.018; 
  }
  
  const lat1_shifted = lat1 + pLat * shift;
  const lon1_shifted = lon1 + pLon * shift;
  const lat2_shifted = lat2 + pLat * shift;
  const lon2_shifted = lon2 + pLon * shift;
  
  // Curvature height (bends based on Euclidean distance)
  const midLat = (lat1_shifted + lat2_shifted) / 2;
  const midLon = (lon1_shifted + lon2_shifted) / 2;
  const curvature = 0.08 * len; 
  
  const controlLat = midLat + pLat * curvature;
  const controlLon = midLon + pLon * curvature;
  
  // Interpolate quadratic bezier points (16 coordinates)
  const points = [];
  for (let t = 0; t <= 1; t += 0.0625) {
    const lat = (1 - t) * (1 - t) * lat1_shifted + 2 * (1 - t) * t * controlLat + t * t * lat2_shifted;
    const lon = (1 - t) * (1 - t) * lon1_shifted + 2 * (1 - t) * t * controlLon + t * t * lon2_shifted;
    points.push([lat, lon]);
  }
  return points;
};

// Component to handle dynamic map bounds auto-fitting
const MapBounds = ({ locations, routeResult, compareMode, allRoutes }) => {
  const map = useMap();
  
  useEffect(() => {
    if (compareMode && allRoutes && Object.keys(allRoutes).length > 0) {
      // Fit to all active comparisons coordinates combined
      const coords = [];
      Object.values(allRoutes).forEach(r => {
        if (r?.path_nodes) {
          r.path_nodes.forEach(n => coords.push([n.y, n.x]));
        }
      });
      if (coords.length > 0) {
        map.flyToBounds(L.latLngBounds(coords), { padding: [50, 50], duration: 1.5 });
      }
    } else if (routeResult?.path_nodes && routeResult.path_nodes.length > 0) {
      const bounds = L.latLngBounds(routeResult.path_nodes.map(loc => [loc.y, loc.x]));
      map.flyToBounds(bounds, { padding: [60, 60], duration: 1.5 });
    } else if (locations && locations.length > 0) {
      const bounds = L.latLngBounds(locations.map(loc => [loc.y, loc.x]));
      map.fitBounds(bounds, { padding: [30, 30] });
    }
  }, [locations, routeResult, compareMode, allRoutes, map]);

  return null;
};

const MapView = ({ locations, routeResult }) => {
  const [compareMode, setCompareMode] = useState(false);
  const [focusAlg, setFocusAlg] = useState("ASTAR");
  const [opacity, setOpacity] = useState(0.85);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Real-time sequential animation states
  const [exploredStep, setExploredStep] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  
  const mapRef = useRef(null);

  // Compile all comparisons path nodes for simultaneous comparison overlay
  const [allRoutes, setAllRoutes] = useState({});

  useEffect(() => {
    if (routeResult?.comparisons && locations) {
      const routesMap = {};
      routeResult.comparisons.forEach(comp => {
        const algName = comp.algorithm; // BFS, DFS, UCS, ASTAR
        const pathIds = comp.path;
        if (pathIds && pathIds.length > 0) {
          const path_nodes = pathIds.map(id => locations.find(loc => loc.id === id)).filter(Boolean);
          routesMap[algName] = {
            path: pathIds,
            path_nodes,
            metrics: {
              distance: comp.distance,
              cost: comp.cost,
              time: comp.time,
              explored_count: comp.explored_nodes
            }
          };
        }
      });
      setAllRoutes(routesMap);
    }
  }, [routeResult, locations]);

  // Hook up animation trigger whenever a new route gets planned
  useEffect(() => {
    if (routeResult?.explored && routeResult.explored.length > 0) {
      setIsAnimating(true);
      setExploredStep(0);
    } else {
      setIsAnimating(false);
      setExploredStep(0);
    }
  }, [routeResult]);

  useEffect(() => {
    if (isAnimating && routeResult?.explored) {
      const timer = setTimeout(() => {
        if (exploredStep < routeResult.explored.length) {
          setExploredStep(prev => prev + 1);
        } else {
          setIsAnimating(false);
        }
      }, 70); // 70ms tick per explored node blip!
      return () => clearTimeout(timer);
    }
  }, [isAnimating, exploredStep, routeResult]);

  const toggleFullscreen = () => {
    const mapContainer = document.getElementById('map-fullscreen-container');
    if (!isFullscreen) {
      if (mapContainer.requestFullscreen) mapContainer.requestFullscreen();
      setIsFullscreen(true);
    } else {
      if (document.exitFullscreen) document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Compute selected routing data for glassmorphism stats cards
  const getActiveStats = () => {
    if (compareMode) {
      return allRoutes[focusAlg]?.metrics || null;
    }
    return routeResult?.metrics || null;
  };

  const activeStats = getActiveStats();
  const startCityId = routeResult?.path?.[0];
  const goalCityId = routeResult?.path?.[routeResult.path.length - 1];

  // List of active algorithms for layout spacing offset
  const activeAlgs = ["BFS", "DFS", "UCS", "ASTAR"];

  return (
    <div id="map-fullscreen-container" className={`relative w-full h-full ${isFullscreen ? 'h-screen w-screen z-[9999]' : ''}`}>
      
      {/* --------------------------------------------------------
          FLOATING ELEMENT 1: Glassmorphic Mission Control (Top-Left)
         -------------------------------------------------------- */}
      <div className="absolute top-4 left-4 z-[1000] glass-overlay rounded-xl p-4 w-72 text-gray-200 text-xs flex flex-col gap-3 font-sans">
        <div className="flex items-center justify-between border-b border-white/10 pb-2">
          <div className="flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span className="font-bold text-gray-100 uppercase tracking-widest font-mono">Mission Control</span>
          </div>
          <button onClick={toggleFullscreen} className="p-1 hover:bg-white/10 rounded transition text-gray-400 hover:text-white">
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Comparison vs Focus Mode select */}
        {allRoutes && Object.keys(allRoutes).length > 0 && (
          <div className="flex flex-col gap-1">
            <span className="text-gray-500 font-mono">ROUTING DISPLAY MODE</span>
            <div className="grid grid-cols-2 bg-zinc-950/80 rounded-lg p-0.5 border border-white/5 font-mono text-center">
              <button 
                onClick={() => setCompareMode(false)}
                className={`py-1.5 rounded-md transition ${!compareMode ? 'bg-cyan-500/20 text-cyan-400 font-semibold border border-cyan-400/20' : 'text-gray-400 hover:text-white'}`}
              >
                SINGLE FOCUS
              </button>
              <button 
                onClick={() => setCompareMode(true)}
                className={`py-1.5 rounded-md transition ${compareMode ? 'bg-cyan-500/20 text-cyan-400 font-semibold border border-cyan-400/20' : 'text-gray-400 hover:text-white'}`}
              >
                COMPARE ALL
              </button>
            </div>
          </div>
        )}

        {/* Algorithm focus switcher */}
        <div className="flex flex-col gap-1">
          <span className="text-gray-500 font-mono">SELECTED ALGORITHM</span>
          <div className="grid grid-cols-4 bg-zinc-950/80 rounded-lg p-0.5 border border-white/5 font-mono text-center">
            {activeAlgs.map(alg => (
              <button
                key={alg}
                disabled={!compareMode && routeResult?.metrics && algorithmNameMapping(routeResult.algorithm) !== alg}
                onClick={() => setFocusAlg(alg)}
                className={`py-1 rounded-md text-[10px] transition ${
                  (compareMode ? focusAlg === alg : algorithmNameMapping(routeResult?.algorithm) === alg)
                    ? `bg-[${ALG_METRIC_STYLES[alg].color}]/20 text-white font-bold border` 
                    : 'text-gray-500 cursor-not-allowed'
                }`}
                style={{
                  borderColor: (compareMode ? focusAlg === alg : algorithmNameMapping(routeResult?.algorithm) === alg) ? ALG_METRIC_STYLES[alg].color : 'transparent',
                  color: (compareMode ? focusAlg === alg : algorithmNameMapping(routeResult?.algorithm) === alg) ? ALG_METRIC_STYLES[alg].color : ''
                }}
              >
                {alg}
              </button>
            ))}
          </div>
        </div>

        {/* Glow Opacity Slider */}
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-gray-500 font-mono">
            <span>TRAJECTORY GLOW</span>
            <span className="text-gray-300 font-bold">{(opacity * 100).toFixed(0)}%</span>
          </div>
          <div className="flex items-center gap-2">
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            <input 
              type="range" 
              min="0.3" 
              max="1.0" 
              step="0.05"
              value={opacity}
              onChange={(e) => setOpacity(parseFloat(e.target.value))}
              className="flex-1 accent-cyan-400 bg-zinc-950/80 rounded h-1 cursor-pointer border border-white/5"
            />
          </div>
        </div>

        {/* Live Exploration Replay Trigger */}
        {routeResult?.explored && (
          <button 
            onClick={() => {
              setIsAnimating(true);
              setExploredStep(0);
            }}
            disabled={isAnimating}
            className="w-full flex items-center justify-center gap-1.5 py-2 bg-cyan-500 hover:bg-cyan-400 disabled:bg-zinc-800 text-zinc-950 disabled:text-gray-500 rounded-lg font-mono font-bold tracking-wider transition"
          >
            {isAnimating ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                EXPLORING FRONTIER...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-zinc-950" />
                REPLAY SEARCH FRONTIER
              </>
            )}
          </button>
        )}
      </div>

      {/* --------------------------------------------------------
          FLOATING ELEMENT 2: Floating Glass Legend (Top-Right)
         -------------------------------------------------------- */}
      <div className="absolute top-4 right-4 z-[1000] glass-overlay rounded-xl p-3 w-52 text-gray-200 text-xs flex flex-col gap-2 font-sans font-mono">
        <div className="flex items-center gap-1 border-b border-white/10 pb-1.5">
          <Layers className="w-3.5 h-3.5 text-purple-400" />
          <span className="font-bold tracking-widest text-[10px] text-gray-300">COLOR LEGEND</span>
        </div>
        <div className="flex flex-col gap-1.5 text-[10px]">
          {Object.entries(ALG_METRIC_STYLES).map(([key, style]) => (
            <div key={key} className="flex items-center justify-between">
              <span className="text-gray-400">{style.label}</span>
              <span 
                className="w-3 h-1.5 rounded-full shadow-[0_0_6px_currentColor]" 
                style={{ backgroundColor: style.color, color: style.color }}
              ></span>
            </div>
          ))}
          <div className="border-t border-white/10 pt-1.5 mt-0.5 flex flex-col gap-1">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">High Crowd Hazard</span>
              <span className="w-2.5 h-2.5 rounded-full bg-orange-500 shadow-[0_0_6px_#f97316] animate-pulse"></span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Weather Warnings</span>
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_6px_#3b82f6]"></span>
            </div>
          </div>
        </div>
      </div>

      {/* --------------------------------------------------------
          FLOATING ELEMENT 3: Glassmorphism Real-Time Telemetry (Bottom-Left)
         -------------------------------------------------------- */}
      {activeStats && (
        <div className="absolute bottom-4 left-4 z-[1000] glass-overlay rounded-xl p-4 w-80 text-gray-300 font-mono text-[11px] flex flex-col gap-2">
          <div className="flex items-center justify-between border-b border-white/10 pb-1.5">
            <div className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-yellow-400" />
              <span className="font-bold text-gray-200">REAL-TIME TELEMETRY</span>
            </div>
            <span className="text-[10px] bg-cyan-500/10 text-cyan-400 border border-cyan-400/20 px-1.5 py-0.5 rounded uppercase">
              {compareMode ? `${focusAlg} Mode` : `${algorithmNameMapping(routeResult?.algorithm)} Active`}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-x-4 gap-y-2 mt-1">
            <div className="flex flex-col">
              <span className="text-gray-500 text-[9px]">TOTAL TRAJECTORY DISTANCE</span>
              <span className="text-sm font-bold text-gray-200 flex items-center gap-0.5">
                <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                {activeStats.distance.toFixed(1)} km
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-500 text-[9px]">ESTIMATED TRAVEL COST</span>
              <span className="text-sm font-bold text-gray-200 flex items-center">
                <IndianRupee className="w-3.5 h-3.5 text-green-400" />
                {activeStats.cost.toFixed(0)} INR
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-500 text-[9px]">ESTIMATED COGNITIVE TIME</span>
              <span className="text-sm font-bold text-gray-200 flex items-center gap-0.5">
                <Clock className="w-3.5 h-3.5 text-yellow-400" />
                {activeStats.time.toFixed(0)} mins
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-500 text-[9px]">FRONTIER STATES EXPLORED</span>
              <span className="text-sm font-bold text-gray-200 flex items-center gap-0.5">
                <ShieldCheck className="w-3.5 h-3.5 text-orange-400" />
                {activeStats.explored_count || 0} nodes
              </span>
            </div>
          </div>
          
          {/* Dynamic weather warnings and hazard states */}
          <div className="border-t border-white/10 pt-2 mt-1 flex items-center gap-2 text-orange-400 text-[10px]">
            <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
            <span>Bayesian weather adjustments and Markov delays integrated.</span>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------
          MAIN MAP CONTROLLER container
         -------------------------------------------------------- */}
      <MapContainer 
        center={[26.4498, 74.6399]} 
        zoom={6.5} 
        className="w-full h-full border border-white/10 rounded-2xl overflow-hidden shadow-2xl"
        zoomControl={false}
        whenCreated={(map) => { mapRef.current = map; }}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        
        <MapBounds 
          locations={locations} 
          routeResult={routeResult} 
          compareMode={compareMode}
          allRoutes={allRoutes}
        />

        {/* --------------------------------------------------------
            LAYER 1: Static connection lines (base highway network)
           -------------------------------------------------------- */}
        {locations.map(loc => {
          return loc.connections.map(conn => {
            const target = locations.find(l => l.id === conn.to_id);
            if (!target) return null;
            
            // Highlight connections with weather/traffic delays dynamically
            const isHighTraffic = conn.traffic_prob?.high > 0.3;
            const isBadWeather = conn.weather_prob?.rain > 0.2 || conn.weather_prob?.fog > 0.2;
            
            return (
              <Polyline 
                key={`${loc.id}-${conn.to_id}`}
                positions={[[loc.y, loc.x], [target.y, target.x]]}
                color={isHighTraffic ? "#ef4444" : isBadWeather ? "#3b82f6" : "#27272a"}
                weight={isHighTraffic || isBadWeather ? 2.5 : 1.2}
                opacity={0.3}
                className={isHighTraffic ? "hazard-glow-red" : isBadWeather ? "hazard-glow-blue" : ""}
              />
            );
          });
        })}

        {/* --------------------------------------------------------
            LAYER 2: Live search animation blinking frontier nodes
           -------------------------------------------------------- */}
        {isAnimating && routeResult?.explored && (
          routeResult.explored.slice(0, exploredStep).map(nodeId => {
            const loc = locations.find(l => l.id === nodeId);
            if (!loc || nodeId === startCityId || nodeId === goalCityId) return null;
            return (
              <Marker
                key={`explored-${nodeId}`}
                position={[loc.y, loc.x]}
                icon={getCustomMarkerIcon("explored")}
              />
            );
          })
        )}

        {/* --------------------------------------------------------
            LAYER 3: Path Polyline Curve overlays
           -------------------------------------------------------- */}
        {!isAnimating && (
          compareMode ? (
            // Compare All Mode: Overlay all 4 curves parallel to each other
            Object.entries(allRoutes).map(([algName, routeData], idx) => {
              if (!routeData?.path_nodes || routeData.path_nodes.length < 2) return null;
              
              const curveSegments = [];
              for (let i = 0; i < routeData.path_nodes.length - 1; i++) {
                const p1 = [routeData.path_nodes[i].y, routeData.path_nodes[i].x];
                const p2 = [routeData.path_nodes[i+1].y, routeData.path_nodes[i+1].x];
                const segmentPoints = getBezierCurvePoints(p1, p2, idx, 4);
                curveSegments.push(segmentPoints);
              }

              return curveSegments.map((segment, segIdx) => (
                <React.Fragment key={`curve-${algName}-${segIdx}`}>
                  {/* Glowing outer shadow line */}
                  <Polyline 
                    positions={segment}
                    color={ALG_METRIC_STYLES[algName].color}
                    weight={ALG_METRIC_STYLES[algName].width + 3}
                    opacity={opacity * 0.4}
                    className={ALG_METRIC_STYLES[algName].pathClass}
                  />
                  {/* Crawling crawling dashed particle core */}
                  <Polyline 
                    positions={segment}
                    color={ALG_METRIC_STYLES[algName].color}
                    weight={ALG_METRIC_STYLES[algName].width}
                    opacity={opacity}
                    className="flow-line"
                  />
                </React.Fragment>
              ));
            })
          ) : (
            // Single Focus Mode: Render only active selected path curves
            routeResult?.path_nodes && routeResult.path_nodes.length >= 2 && (() => {
              const activeAlgName = algorithmNameMapping(routeResult.algorithm);
              const curveSegments = [];
              for (let i = 0; i < routeResult.path_nodes.length - 1; i++) {
                const p1 = [routeResult.path_nodes[i].y, routeResult.path_nodes[i].x];
                const p2 = [routeResult.path_nodes[i+1].y, routeResult.path_nodes[i+1].x];
                // Offset index 2, single route
                const segmentPoints = getBezierCurvePoints(p1, p2, 0, 1);
                curveSegments.push(segmentPoints);
              }

              return curveSegments.map((segment, segIdx) => (
                <React.Fragment key={`active-curve-${segIdx}`}>
                  {/* Glowing background halo */}
                  <Polyline 
                    positions={segment}
                    color={ALG_METRIC_STYLES[activeAlgName]?.color || "#22d3ee"}
                    weight={6}
                    opacity={opacity * 0.4}
                    className={ALG_METRIC_STYLES[activeAlgName]?.pathClass || "glow-path-cyan"}
                  />
                  {/* Glowing crawling dash core */}
                  <Polyline 
                    positions={segment}
                    color={ALG_METRIC_STYLES[activeAlgName]?.color || "#22d3ee"}
                    weight={3.5}
                    opacity={opacity}
                    className="flow-line"
                  />
                </React.Fragment>
              ));
            })()
          )
        )}

        {/* --------------------------------------------------------
            LAYER 4: Interactive nodes & popups
           -------------------------------------------------------- */}
        {locations.map(loc => {
          const isStart = loc.id === startCityId;
          const isGoal = loc.id === goalCityId;
          const isRouteNode = !isAnimating && routeResult?.path?.includes(loc.id);
          const isCrowded = loc.crowd_level > 0.75;
          
          let markerType = "normal";
          if (isStart) markerType = "start";
          else if (isGoal) markerType = "goal";
          else if (isRouteNode) markerType = "route";
          else if (isCrowded) markerType = "crowded";

          const activeAlgName = compareMode ? focusAlg : algorithmNameMapping(routeResult?.algorithm);
          const colorHex = ALG_METRIC_STYLES[activeAlgName]?.color || "#22d3ee";

          return (
            <Marker 
              key={loc.id} 
              position={[loc.y, loc.x]}
              icon={getCustomMarkerIcon(markerType, colorHex)}
            >
              <Popup className="custom-popup">
                <div className="font-sans w-56 text-gray-200">
                  <div className="flex items-center justify-between border-b border-white/10 pb-1 mb-1">
                    <h3 className="font-bold text-gray-100 text-sm tracking-wide">{loc.name.split("(")[0].trim()}</h3>
                    <span className="text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-yellow-400 font-bold">⭐ {loc.rating.toFixed(1)}</span>
                  </div>
                  <p className="text-[10.5px] text-gray-400 mb-2 leading-relaxed">{loc.description}</p>
                  
                  <div className="grid grid-cols-2 gap-2 text-[10px] border-t border-white/10 pt-2 font-mono">
                    <div>
                      <span className="text-gray-500 block">CROWD RATIO</span>
                      <span className={`${loc.crowd_level > 0.75 ? 'text-orange-400 font-bold' : 'text-gray-300'}`}>
                        {(loc.crowd_level * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 block">STATUS</span>
                      <span className={`${loc.is_open ? 'text-green-400' : 'text-red-400'} font-bold`}>
                        {loc.is_open ? 'OPEN' : 'CLOSED'}
                      </span>
                    </div>
                  </div>
                  
                  {loc.hotels && loc.hotels.length > 0 && (
                    <div className="mt-2.5 pt-1.5 border-t border-white/10">
                      <span className="text-gray-500 text-[9px] block font-mono uppercase tracking-wider mb-1">Accommodation</span>
                      <div className="text-[10px] text-gray-300 font-semibold truncate">
                        🏨 {loc.hotels[0].name} (₹{loc.hotels[0].price})
                      </div>
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

// Helper utility to translate API backend algorithm names into consistent front keys
const algorithmNameMapping = (backendName) => {
  if (!backendName) return "ASTAR";
  const name = backendName.toUpperCase();
  if (name.includes("BFS")) return "BFS";
  if (name.includes("DFS")) return "DFS";
  if (name.includes("UCS")) return "UCS";
  return "ASTAR";
};

// Helper String clean strip functions
if (!String.prototype.strip) {
  Object.defineProperty(String.prototype, 'strip', {
    get() {
      return this.trim();
    }
  });
}

export default MapView;
