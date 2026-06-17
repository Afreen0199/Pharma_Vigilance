import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisApi } from '../api/analysisApi';
import { 
  FolderHeart, 
  Upload, 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  ChevronRight,
  TrendingUp,
  FileText,
  AlertTriangle,
  Loader2,
  RefreshCw,
  Database
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell
} from 'recharts';

const COLORS = ['#0271c7', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

const Dashboard = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAnalyses = async (showRefreshIndicator = false) => {
    if (showRefreshIndicator) setRefreshing(true);
    else setLoading(true);
    setError(null);
    try {
      const data = await analysisApi.listAnalyses();
      setAnalyses(data || []);
    } catch (err) {
      console.error('List analyses error:', err);
      setError('Failed to fetch case analyses. Ensure backend FastAPI server is running.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, []);

  // Compute metrics
  const totalCases = analyses.length;
  const completedCases = analyses.filter(a => a.status === 'completed').length;
  const pendingCases = analyses.filter(a => a.status === 'pending').length;
  
  const highRiskCases = analyses.filter(a => {
    let isSerious = false;
    // Check in seriousness_assessment flags
    if (a.seriousness_assessment) {
      const flags = a.seriousness_assessment;
      if (
        String(flags.hospitalization).toLowerCase() === 'yes' ||
        String(flags.life_threatening).toLowerCase() === 'yes' ||
        String(flags.disability).toLowerCase() === 'yes' ||
        String(flags.death).toLowerCase() === 'yes'
      ) {
        isSerious = true;
      }
    }
    // Check in ai_summary json if parsed
    if (!isSerious && a.ai_summary) {
      try {
        const summary = typeof a.ai_summary === 'string' ? JSON.parse(a.ai_summary) : a.ai_summary;
        const ser = String(summary?.case_information?.seriousness || summary?.adverse_event_details?.severity || '').toLowerCase();
        if (ser.includes('serious') || ser.includes('high')) isSerious = true;
      } catch (e) {}
    }
    return isSerious;
  }).length;

  // Aggregate drug counts for charts
  const getChartData = () => {
    const drugCounts = {};
    analyses.forEach(a => {
      let drug = 'Unknown';
      if (a.drug_entities && a.drug_entities.length > 0) {
        drug = a.drug_entities[0];
      } else if (a.ai_summary) {
        try {
          const summary = typeof a.ai_summary === 'string' ? JSON.parse(a.ai_summary) : a.ai_summary;
          drug = summary?.drug_information?.product_active_ingredient || summary?.suspect_drug || 'Unknown';
        } catch (e) {}
      }
      drug = drug.charAt(0).toUpperCase() + drug.slice(1).toLowerCase();
      drugCounts[drug] = (drugCounts[drug] || 0) + 1;
    });

    return Object.keys(drugCounts)
      .map(name => ({ name, count: drugCounts[name] }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  };

  const chartData = getChartData();

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Welcome header & refresh trigger */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-800 dark:text-white tracking-tight">
            Safety Dashboard
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
            Overview of clinical pharmacovigilance reports and openFDA safety metrics.
          </p>
        </div>
        <button
          onClick={() => fetchAnalyses(true)}
          disabled={refreshing || loading}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-200 dark:border-slate-850 hover:bg-slate-100 dark:hover:bg-slate-850 rounded-lg text-xs font-bold text-slate-700 dark:text-slate-350 cursor-pointer transition-all disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>{refreshing ? 'Syncing...' : 'Sync Database'}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50 rounded-xl text-xs font-semibold text-red-650 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          { label: 'Total Ingestions', val: totalCases, icon: Database, color: 'text-brand-500 bg-brand-50 dark:bg-brand-950/30' },
          { label: 'Completed Cases', val: completedCases, icon: CheckCircle2, color: 'text-emerald-500 bg-emerald-50 dark:bg-emerald-950/30' },
          { label: 'Pending Processing', val: pendingCases, icon: Clock, color: 'text-amber-500 bg-amber-50 dark:bg-amber-950/30' },
          { label: 'High-Risk Signals', val: highRiskCases, icon: ShieldAlert, color: 'text-red-500 bg-red-50 dark:bg-red-950/30' }
        ].map((c, idx) => {
          const Icon = c.icon;
          return (
            <div key={idx} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-xl shadow-sm hover-scale">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-slate-450 dark:text-slate-400 font-bold uppercase tracking-wider block">
                  {c.label}
                </span>
                <div className={`p-2 rounded-lg ${c.color}`}>
                  <Icon className="h-4 w-4" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-2xl font-black text-slate-800 dark:text-white">
                  {loading ? '...' : c.val}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Grid: Case List (2/3) and Chart stats (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Recent Cases list table */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider">
              Recent Pharmacovigilance Logs
            </h3>
            <button
              onClick={() => navigate('/upload')}
              className="text-xs text-brand-600 dark:text-brand-400 font-bold hover:underline cursor-pointer flex items-center gap-0.5"
            >
              <span>Ingest Case</span>
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-150 dark:border-slate-800 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-2">Document</th>
                  <th className="py-3 px-2">Drugs Detected</th>
                  <th className="py-3 px-2">Status</th>
                  <th className="py-3 px-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
                {loading ? (
                  <tr>
                    <td colSpan="4" className="py-8 text-center text-slate-450">
                      <Loader2 className="h-6 w-6 animate-spin text-brand-500 mx-auto" />
                      <span className="mt-2 block font-semibold">Loading case records...</span>
                    </td>
                  </tr>
                ) : analyses.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="py-8 text-center text-slate-400 font-semibold italic">
                      No clinical logs found. Please upload a medical record.
                    </td>
                  </tr>
                ) : (
                  analyses.slice(0, 5).map((a) => (
                    <tr key={a.analysis_id || a.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/10 transition-colors">
                      <td className="py-3.5 px-2 font-bold text-slate-800 dark:text-slate-200 max-w-[150px] truncate">
                        {a.filename || 'Pasted Case Text'}
                      </td>
                      <td className="py-3.5 px-2 font-semibold text-slate-500 dark:text-slate-400">
                        {a.drug_entities && a.drug_entities.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {a.drug_entities.map((d, i) => (
                              <span key={i} className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-350 rounded text-[10px] font-bold">
                                {d}
                              </span>
                            ))}
                          </div>
                        ) : (
                          'Not Mapped'
                        )}
                      </td>
                      <td className="py-3.5 px-2">
                        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded font-black text-[9px] uppercase tracking-wider border ${
                          a.status === 'completed'
                            ? 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-450 border-emerald-250 dark:border-emerald-900/40'
                            : 'bg-amber-50 dark:bg-amber-950/20 text-amber-700 dark:text-amber-450 border-amber-250 dark:border-amber-900/40 animate-pulse'
                        }`}>
                          {a.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-2 text-right">
                        <button
                          onClick={() => navigate(`/workspace/${a.analysis_id || a.id}`)}
                          className="px-2.5 py-1 text-[10px] font-bold bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded cursor-pointer transition-colors"
                        >
                          View Workspace
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Side: Recharts Bar Graph representing primary suspect drugs */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider">
              Primary Drug Frequencies
            </h3>
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider mt-1 block">
              Case Count Distribution
            </span>
          </div>

          <div className="h-64 flex items-center justify-center mt-4">
            {loading ? (
              <Loader2 className="h-6 w-6 animate-spin text-brand-500" />
            ) : chartData.length === 0 ? (
              <span className="text-slate-450 font-medium text-xs italic">
                No safety signals indexed yet.
              </span>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                  <XAxis type="number" stroke="#64748B" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis dataKey="name" type="category" stroke="#64748B" fontSize={9} width={80} tickLine={false} axisLine={false} />
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-slate-900 text-white p-2 rounded border border-slate-750 text-[10px] font-bold shadow-xl">
                            <p className="font-extrabold uppercase text-slate-350">{payload[0].payload.name}</p>
                            <p className="flex justify-between gap-4 mt-1">
                              <span>Cases:</span>
                              <span className="text-brand-300 font-black">{payload[0].value}</span>
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="count" fill="#0271c7" radius={[0, 4, 4, 0]} name="Cases">
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
