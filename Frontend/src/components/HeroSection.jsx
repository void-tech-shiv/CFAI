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
          className="group relative px-8 py-4 bg-white text-black font-semibold rounded-full overflow-hidden transition-transform hover:scale-105 active:scale-95 flex items-center gap-2 cursor-pointer"
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
        className="absolute bottom-12 flex gap-8 flex-wrap justify-center items-center text-sm text-gray-500 font-medium"
      >
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-500" /> Real-time A* Search
        </div>
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-blue-500" /> Constraint Satisfaction
        </div>
        
        {/* Sleek inline LinkedIn dev profile link */}
        <a 
          href="https://www.linkedin.com/in/shivanshu-satyajeet-a52013229/"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-gray-500 hover:text-blue-400 transition-colors cursor-pointer"
          title="Developer's LinkedIn Profile"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2.5" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            className="w-4 h-4"
          >
            <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
            <rect x="2" y="9" width="4" height="12"></rect>
            <circle cx="4" cy="4" r="2"></circle>
          </svg>
          Developer Profile
        </a>

        {/* Sleek inline GitHub profile link */}
        <a 
          href="https://github.com/void-tech-shiv"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-gray-500 hover:text-purple-400 transition-colors cursor-pointer"
          title="Developer's GitHub Profile"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2.5" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            className="w-4 h-4"
          >
            <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path>
            <path d="M9 18c-4.51 2-5-2-7-2"></path>
          </svg>
          Source Code
        </a>
      </motion.div>
    </motion.div>
  );
};

export default HeroSection;
