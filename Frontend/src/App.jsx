import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import HeroSection from './components/HeroSection';
import Dashboard from './components/Dashboard';

function App() {
  const [showDashboard, setShowDashboard] = useState(false);

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      {/* Background glowing effects */}
      <div className="absolute top-0 -left-1/4 w-1/2 h-1/2 bg-blue-900/20 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-0 -right-1/4 w-1/2 h-1/2 bg-purple-900/20 blur-[120px] rounded-full pointer-events-none"></div>

      <AnimatePresence mode="wait">
        {!showDashboard ? (
          <HeroSection key="hero" onStart={() => setShowDashboard(true)} />
        ) : (
          <Dashboard key="dashboard" onBack={() => setShowDashboard(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
