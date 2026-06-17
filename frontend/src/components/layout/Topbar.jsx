import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sun, Moon, Bell, Plus, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Topbar = ({ title }) => {
  const navigate = useNavigate();
  const { userEmail } = useAuth();
  
  // Read theme initial state
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem('theme') === 'dark' || 
    (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
  );

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 z-30 select-none shrink-0 transition-colors duration-200">
      {/* Left side: Route-specific Title */}
      <div className="flex items-center gap-3">
        <h2 className="font-extrabold text-sm text-slate-800 dark:text-white tracking-wide">
          {title || 'Safety Workspace'}
        </h2>
      </div>

      {/* Right side: Global Actions & User Session */}
      <div className="flex items-center gap-4">
        {/* Dark Mode toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-850 rounded-lg transition-colors cursor-pointer"
          title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {darkMode ? <Sun className="h-4.5 w-4.5" /> : <Moon className="h-4.5 w-4.5" />}
        </button>

        {/* Alerts count */}
        <button className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-850 rounded-lg relative transition-colors cursor-pointer">
          <Bell className="h-4.5 w-4.5" />
          <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 bg-red-500 rounded-full animate-ping"></span>
        </button>

        {/* Divider */}
        <div className="h-5 w-px bg-slate-200 dark:bg-slate-800"></div>

        {/* Quick Ingestion Action */}
        <button
          onClick={() => navigate('/upload')}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-bold shadow-md shadow-brand-600/20 transition-all duration-200 cursor-pointer"
        >
          <Plus className="h-4 w-4" />
          <span>New Ingestion</span>
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-2 p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors group cursor-pointer">
          <div className="h-7 w-7 rounded-full bg-brand-100 dark:bg-brand-950/40 flex items-center justify-center text-brand-600 dark:text-brand-400 font-black text-xs border border-brand-200 dark:border-brand-800/40">
            {userEmail ? userEmail.slice(0, 2).toUpperCase() : 'PV'}
          </div>
          <span className="text-xs font-bold text-slate-600 dark:text-slate-350 group-hover:text-slate-950 dark:group-hover:text-white hidden sm:block">
            {userEmail ? userEmail.split('@')[0] : 'Reviewer'}
          </span>
        </div>
      </div>
    </header>
  );
};

export default Topbar;
