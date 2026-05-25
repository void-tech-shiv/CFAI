import React from 'react';
import { motion } from 'framer-motion';
import { Map, Zap, Compass, ChevronRight } from 'lucide-react';

const HeroSection = ({ onStart }) => {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, y: -50 }}
      transition={{ duration: 0.8 }}
      className="h-screen w-full flex flex-col items-center justify-center relative z-10 px-4"
    >
      <motion.div 
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2, type: "spring", stiffness: 100 }}
        className="mb-8 p-4 bg-white/5 rounded-3xl border border-white/10 backdrop-blur-md"
      >
        <Map className="w-16 h-16 text-blue-400" />
      </motion.div>

      <motion.h1 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="text-5xl md:text-7xl font-bold text-center tracking-tight mb-6"
      >
        Plan Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">Smart Journey</span><br/> with AI
      </motion.h1>

      <motion.p 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-lg md:text-xl text-gray-400 text-center max-w-2xl mb-12"
      >
        Experience the future of travel. Our intelligent agent analyzes traffic, weather, budget, and multi-attribute utility to build the ultimate itinerary.
      </motion.p>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex gap-4 flex-wrap justify-center"
      >
        <button 
          onClick={onStart}
          className="group relative px-8 py-4 bg-white text-black font-semibold rounded-full overflow-hidden transition-transform hover:scale-105 active:scale-95 flex items-center gap-2"
        >
          <span className="relative z-10">Launch Dashboard</span>
          <ChevronRight className="w-5 h-5 relative z-10 group-hover:translate-x-1 transition-transform" />
          <div className="absolute inset-0 bg-gradient-to-r from-blue-200 to-purple-200 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </button>
      </motion.div>

      {/* Feature Badges */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 1 }}
        className="absolute bottom-12 flex gap-8 text-sm text-gray-500 font-medium"
      >
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-500" /> Real-time A* Search
        </div>
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-blue-500" /> Constraint Satisfaction
        </div>
      </motion.div>
    </motion.div>
  );
};

export default HeroSection;
