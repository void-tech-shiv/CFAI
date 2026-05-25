import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, Clock, ShieldCheck, MapPin } from 'lucide-react';

const StatsPanel = ({ routeResult }) => {
  const { metrics, csp_status, comparisons, path_nodes } = routeResult;

  // Format data for Recharts
  const chartData = comparisons ? comparisons.map(comp => ({
    name: comp.algorithm,
    Time_ms: comp.execution_time_ns / 1000000,
    Distance: comp.distance,
    Cost: comp.cost
  })) : [];

  return (
    <div className="flex flex-col xl:flex-row gap-6 w-full">
      {/* Metrics Summary */}
      <div className="flex-1 space-y-4">
        <div className="flex items-center gap-2 border-b border-white/10 pb-2">
          <Activity className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold text-gray-200">Trajectory Analysis</h3>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-black/40 p-3 rounded-lg border border-white/5">
            <div className="text-gray-500 text-xs mb-1 font-mono">TOTAL DISTANCE</div>
            <div className="text-xl font-bold">{metrics.distance.toFixed(1)} km</div>
          </div>
          <div className="bg-black/40 p-3 rounded-lg border border-white/5">
            <div className="text-gray-500 text-xs mb-1 font-mono">EST COST</div>
            <div className="text-xl font-bold">₹{metrics.cost.toFixed(0)}</div>
          </div>
          <div className="bg-black/40 p-3 rounded-lg border border-white/5">
            <div className="text-gray-500 text-xs mb-1 font-mono">EST TIME</div>
            <div className="text-xl font-bold">{metrics.time.toFixed(0)} min</div>
          </div>
          <div className="bg-black/40 p-3 rounded-lg border border-white/5">
            <div className="text-gray-500 text-xs mb-1 font-mono">UTILITY SCORE</div>
            <div className="text-xl font-bold text-blue-400">{metrics.utility_score.toFixed(3)}</div>
          </div>
        </div>

        {/* CSP & Engine Stats */}
        <div className="flex flex-wrap gap-4 mt-2">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold ${csp_status.valid ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
            <ShieldCheck className="w-4 h-4" /> 
            {csp_status.valid ? 'Constraints Satisfied' : 'Constraint Violation Detected'}
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Clock className="w-4 h-4" />
            Compute: {(metrics.execution_time_ns / 1000000).toFixed(2)} ms
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-orange-500/10 text-orange-400 border border-orange-500/20">
            <MapPin className="w-4 h-4" />
            Nodes Explored: {metrics.explored_count}
          </div>
        </div>
        
        {/* Route Sequence */}
        <div className="mt-4 pt-2 border-t border-white/10">
           <div className="text-gray-500 text-xs mb-2 font-mono">OPTIMAL SEQUENCE</div>
           <div className="flex flex-wrap items-center gap-2 text-sm">
             {path_nodes.map((node, i) => (
               <React.Fragment key={node.id}>
                 <span className="bg-white/10 px-2 py-1 rounded text-gray-300">{node.name}</span>
                 {i < path_nodes.length - 1 && <span className="text-gray-600">→</span>}
               </React.Fragment>
             ))}
           </div>
        </div>
      </div>

      {/* Benchmark Charts */}
      {comparisons && comparisons.length > 0 && (
        <div className="flex-1 bg-black/30 rounded-xl p-4 border border-white/5 h-64">
          <div className="text-gray-500 text-xs mb-4 font-mono">ALGORITHM TELEMETRY (EXECUTION TIME MS)</div>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
              <XAxis dataKey="name" stroke="#888" tick={{fontSize: 12}} />
              <YAxis stroke="#888" tick={{fontSize: 12}} width={40} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', borderRadius: '8px' }}
                itemStyle={{ color: '#e4e4e7' }}
              />
              <Bar dataKey="Time_ms" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default StatsPanel;
