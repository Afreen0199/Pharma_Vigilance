import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, UploadCloud, History, LogOut, Shield,
  BookOpen, Settings, ChevronLeft, ChevronRight, Activity, Sun, Moon
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard, exact: true },
  { name: 'Upload Case', path: '/upload', icon: UploadCloud },
  { name: 'Drug Verification', path: '/verify-drug', icon: Shield },
  { name: 'Knowledge Base', path: '/kb', icon: BookOpen },
];

const DashboardLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, userEmail } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex text-slate-900 dark:text-slate-100 transition-colors duration-200">
      {/* Sidebar */}
      <aside
        className={`${collapsed ? 'w-16' : 'w-64'} bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col h-screen sticky top-0 transition-all duration-300 ease-in-out z-30`}
      >
        {/* Logo */}
        <div className={`p-4 flex items-center ${collapsed ? 'justify-center' : 'gap-3'} border-b border-slate-200 dark:border-slate-800 h-16`}>
          <div className="bg-gradient-to-br from-violet-600 to-indigo-600 p-2 rounded-xl shrink-0 shadow-lg shadow-violet-500/20">
            <Activity className="h-5 w-5 text-white" />
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <p className="font-bold text-slate-900 dark:text-white text-sm tracking-tight leading-tight">AI Pharma</p>
              <p className="text-[10px] text-violet-600 dark:text-violet-400 font-medium tracking-wider uppercase leading-tight">Vigilance</p>
            </div>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = item.exact
              ? location.pathname === item.path
              : location.pathname.startsWith(item.path);
            return (
              <NavLink
                key={item.name}
                to={item.path}
                title={collapsed ? item.name : undefined}
                className={`flex items-center ${collapsed ? 'justify-center' : 'gap-3'} px-3 py-2.5 rounded-lg font-medium text-sm transition-all duration-150 group ${
                  isActive
                    ? 'bg-violet-100 dark:bg-violet-600/20 text-violet-700 dark:text-violet-300 border border-violet-200 dark:border-violet-600/30'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100'
                }`}
              >
                <item.icon className={`h-5 w-5 shrink-0 ${isActive ? 'text-violet-600 dark:text-violet-400' : 'text-slate-500 group-hover:text-slate-700 dark:group-hover:text-slate-300'}`} />
                {!collapsed && <span>{item.name}</span>}
              </NavLink>
            );
          })}
        </nav>

        {/* User & Logout */}
        <div className="p-2 border-t border-slate-200 dark:border-slate-800 space-y-1">
          {!collapsed && userEmail && (
            <div className="px-3 py-2">
              <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Signed in as</p>
              <p className="text-xs text-slate-700 dark:text-slate-300 font-medium truncate mt-0.5">{userEmail}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            title="Logout"
            className={`flex items-center ${collapsed ? 'justify-center' : 'gap-3'} px-3 py-2.5 w-full rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-red-50 dark:hover:bg-red-600/10 hover:text-red-600 dark:hover:text-red-400 transition-all`}
          >
            <LogOut className="h-5 w-5 shrink-0" />
            {!collapsed && <span>Logout</span>}
          </button>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className={`flex items-center ${collapsed ? 'justify-center' : 'gap-3'} px-3 py-2 w-full rounded-lg text-xs font-medium text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-700 dark:hover:text-slate-300 transition-all`}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <><ChevronLeft className="h-4 w-4" /><span>Collapse</span></>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-200">
        {/* Top bar */}
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm flex items-center px-6 shrink-0 sticky top-0 z-20">
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-violet-600 dark:text-violet-400" />
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Enterprise AI Safety Platform</span>
          </div>
          <div className="ml-auto flex items-center gap-4">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title="Toggle Theme"
            >
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <div className="flex items-center gap-2 border-l border-slate-200 dark:border-slate-800 pl-4">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-xs text-slate-600 dark:text-slate-500 font-medium">Backend Online</span>
            </div>
          </div>
        </header>
        <div className="flex-1 p-6">
          <div className="max-w-screen-2xl mx-auto">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
