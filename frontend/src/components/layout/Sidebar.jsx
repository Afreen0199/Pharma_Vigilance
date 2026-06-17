import React from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  LayoutDashboard, 
  Database, 
  Upload, 
  TrendingUp, 
  BookOpen, 
  Settings, 
  LogOut,
  FileText,
  Activity
} from 'lucide-react';

const Sidebar = () => {
  const { logout, userEmail } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Detect if we are currently inspecting a case workspace
  const workspaceMatch = location.pathname.match(/\/workspace\/([^/]+)/);
  const activeAnalysisId = workspaceMatch ? workspaceMatch[1] : null;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
    { to: '/cases', label: 'Safety Database', icon: Database },
    { to: '/upload', label: 'Ingestion Terminal', icon: Upload },
    { to: '/fda-explorer', label: 'FDA Explorer', icon: TrendingUp },
    { to: '/kb-manage', label: 'Knowledge Base', icon: BookOpen },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col border-r border-slate-800 select-none shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center gap-2.5 px-6 border-b border-slate-800 bg-slate-950/40">
        <div className="p-1.5 bg-brand-600 rounded-lg text-white">
          <Activity className="h-5 w-5" />
        </div>
        <div>
          <span className="font-extrabold text-sm tracking-tight text-white block">
            ANTIGRAVITY
          </span>
          <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block -mt-1">
            PV Copilot
          </span>
        </div>
      </div>

      {/* Navigation list */}
      <nav className="flex-1 py-6 px-4 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-lg text-xs font-bold transition-all duration-150 ${
                  isActive
                    ? 'bg-slate-800 text-white border-l-4 border-brand-500'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/30'
                }`
              }
            >
              <Icon className="h-4.5 w-4.5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}

        {/* Dynamic active workspace menu item */}
        {activeAnalysisId && (
          <div className="pt-4 border-t border-slate-800/60 mt-4">
            <span className="px-4 text-[9px] text-slate-500 font-bold uppercase tracking-wider block mb-2">
              Active Session
            </span>
            <NavLink
              to={`/workspace/${activeAnalysisId}`}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-lg text-xs font-bold transition-all duration-150 ${
                  isActive
                    ? 'bg-brand-950/30 text-brand-400 border-l-4 border-brand-500'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/30'
                }`
              }
            >
              <FileText className="h-4.5 w-4.5 text-brand-400" />
              <span className="truncate">Case Workspace</span>
            </NavLink>
          </div>
        )}
      </nav>

      {/* Case Status Widget Card */}
      <div className="mx-4 mb-4 p-4 bg-slate-950/40 border border-slate-800/60 rounded-xl space-y-2">
        <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block">
          Current Case Status
        </span>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${activeAnalysisId ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></span>
          <span className="text-xs font-bold text-slate-200">
            {activeAnalysisId ? 'Analysis Loaded' : 'Idle'}
          </span>
        </div>
        <span className="text-[10px] text-slate-500 block leading-tight">
          {userEmail ? `User: ${userEmail}` : 'Clinical Copilot Session'}
        </span>
      </div>

      {/* Logout button */}
      <div className="p-4 border-t border-slate-800">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-xs font-bold text-red-400 hover:text-red-300 hover:bg-red-500/5 transition-all duration-150 cursor-pointer"
        >
          <LogOut className="h-4.5 w-4.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
