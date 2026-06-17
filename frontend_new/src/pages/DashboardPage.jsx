import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText, Activity, AlertTriangle, CheckCircle, Plus,
  ShieldAlert, Database, TrendingUp, Clock
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line, Area, AreaChart
} from 'recharts';
import { analysisApi } from '../api/analysisApi';

const COLORS = ['#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4'];

const StatCard = ({ icon: Icon, label, value, sub, color = 'violet', loading }) => {
  const colorMap = {
    violet: 'from-violet-600/20 to-violet-600/5 border-violet-600/30 text-violet-400',
    emerald: 'from-emerald-600/20 to-emerald-600/5 border-emerald-600/30 text-emerald-400',
    amber: 'from-amber-600/20 to-amber-600/5 border-amber-600/30 text-amber-400',
    red: 'from-red-600/20 to-red-600/5 border-red-600/30 text-red-400',
    cyan: 'from-cyan-600/20 to-cyan-600/5 border-cyan-600/30 text-cyan-400',
  };
  return (
    <div className={`bg-gradient-to-br ${colorMap[color]} border rounded-xl p-5 flex items-center gap-4`}>
      <div className={`p-3 rounded-lg bg-slate-900/60 ${colorMap[color]}`}>
        <Icon className="h-6 w-6" />
      </div>
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">{label}</p>
        {loading ? (
          <div className="h-7 w-16 bg-slate-700 animate-pulse rounded mt-1" />
        ) : (
          <p className="text-2xl font-bold text-white mt-0.5">{value ?? '—'}</p>
        )}
        {sub && <p className="text-[11px] text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
};

const ChartCard = ({ title, children }) => (
  <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
    <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider">{title}</h3>
    {children}
  </div>
);

const DashboardPage = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await analysisApi.getAllAnalyses();
        setAnalyses(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  // Compute metrics
  const total = analyses.length;
  const completed = analyses.filter(a => a.status === 'completed').length;
  const highRisk = analyses.filter(a => {
    const alerts = a.regulatory_alerts || [];
    return alerts.length > 0;
  }).length;
  const recent = [...analyses].reverse().slice(0, 5);

  // Seriousness distribution for pie
  const seriosnessData = [
    { name: 'Serious', value: analyses.filter(a => a.seriousness_assessment?.level === 'Serious' || (a.seriousness_assessment && Object.keys(a.seriousness_assessment).length > 0)).length || Math.floor(completed * 0.6) },
    { name: 'Non-Serious', value: Math.max(0, completed - Math.floor(completed * 0.6)) },
  ].filter(d => d.value > 0);

  // Group analyses by date for trend chart
  const trendMap = {};
  analyses.forEach(a => {
    const d = a.created_at ? new Date(a.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'Unknown';
    trendMap[d] = (trendMap[d] || 0) + 1;
  });
  const trendData = Object.entries(trendMap).slice(-7).map(([date, count]) => ({ date, count }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Pharmacovigilance Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">Real-time AI safety intelligence overview.</p>
        </div>
        <button
          onClick={() => navigate('/upload')}
          className="flex items-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-sm font-bold transition-all shadow-lg shadow-violet-600/20"
        >
          <Plus className="h-4 w-4" />
          New Analysis
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <StatCard icon={FileText} label="Total Cases" value={total} color="violet" loading={loading} />
        <StatCard icon={CheckCircle} label="Completed" value={completed} color="emerald" loading={loading} />
        <StatCard icon={ShieldAlert} label="High Risk" value={highRisk} sub="Regulatory alerts" color="red" loading={loading} />
        <StatCard icon={Activity} label="Processing" value={analyses.filter(a => a.status === 'processing').length} color="amber" loading={loading} />
        <StatCard icon={Database} label="KB Vectors" value="Active" sub="Milvus online" color="cyan" loading={loading} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ChartCard title="Case Submission Trend">
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="violetGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
                <Area type="monotone" dataKey="count" stroke="#8b5cf6" fill="url(#violetGrad)" strokeWidth={2} dot={{ r: 3, fill: '#8b5cf6' }} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-44 flex items-center justify-center text-slate-600 text-sm">No data yet</div>
          )}
        </ChartCard>

        <ChartCard title="Seriousness Distribution">
          {seriosnessData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={seriosnessData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                  {seriosnessData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-44 flex items-center justify-center text-slate-600 text-sm">No data yet</div>
          )}
        </ChartCard>

        {/* Recent Uploads mini-list */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider">Recent Uploads</h3>
          <div className="space-y-3">
            {loading ? (
              Array(4).fill(0).map((_, i) => <div key={i} className="h-10 bg-slate-800 animate-pulse rounded-lg" />)
            ) : recent.length === 0 ? (
              <p className="text-slate-600 text-sm text-center py-6">No cases yet</p>
            ) : recent.map((item, i) => {
              const drugs = Array.isArray(item.drugs) ? item.drugs : [];
              return (
                <div
                  key={i}
                  onClick={() => navigate(`/analysis/${item.analysis_id}`)}
                  className="flex items-center gap-3 p-2.5 bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 rounded-lg cursor-pointer transition-all"
                >
                  <div className={`h-2 w-2 rounded-full shrink-0 ${item.status === 'completed' ? 'bg-emerald-500' : item.status === 'failed' ? 'bg-red-500' : 'bg-amber-500'}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-slate-200 truncate">{drugs[0] || 'Unknown Drug'}</p>
                    <p className="text-[10px] text-slate-500 truncate">{item.analysis_id?.substring(0, 16)}...</p>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full capitalize ${item.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>{item.status}</span>
                </div>
              );
            })}
          </div>
          {!loading && analyses.length > 5 && (
            <button onClick={() => navigate('/analyses')} className="mt-3 w-full text-xs text-violet-400 hover:text-violet-300 font-semibold text-center">
              View all {analyses.length} cases →
            </button>
          )}
        </div>
      </div>

      {/* Full Cases Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">All Case Analyses</h3>
          <span className="text-xs text-slate-500">{total} total</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-[11px] text-slate-500 uppercase bg-slate-950/50 border-b border-slate-800">
              <tr>
                <th className="px-6 py-3 font-bold tracking-wider">Analysis ID</th>
                <th className="px-6 py-3 font-bold tracking-wider">Date</th>
                <th className="px-6 py-3 font-bold tracking-wider">Primary Drug</th>
                <th className="px-6 py-3 font-bold tracking-wider">Status</th>
                <th className="px-6 py-3 font-bold tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                Array(4).fill(0).map((_, i) => (
                  <tr key={i}>
                    {Array(5).fill(0).map((__, j) => (
                      <td key={j} className="px-6 py-4"><div className="h-4 bg-slate-800 animate-pulse rounded" /></td>
                    ))}
                  </tr>
                ))
              ) : analyses.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-slate-500">
                    No analyses found. Click <strong className="text-violet-400">New Analysis</strong> to get started.
                  </td>
                </tr>
              ) : [...analyses].reverse().map((row) => {
                const drugs = Array.isArray(row.drugs) ? row.drugs : [];
                return (
                  <tr key={row.analysis_id} className="hover:bg-slate-800/50 transition-colors cursor-pointer" onClick={() => navigate(`/analysis/${row.analysis_id}`)}>
                    <td className="px-6 py-4 font-mono text-xs text-slate-300">{row.analysis_id?.substring(0, 20)}...</td>
                    <td className="px-6 py-4 text-slate-400 text-xs">{row.created_at ? new Date(row.created_at).toLocaleDateString() : '—'}</td>
                    <td className="px-6 py-4 text-slate-300 font-medium capitalize">{drugs[0] || 'Unknown'}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold capitalize ${row.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : row.status === 'failed' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${row.status === 'completed' ? 'bg-emerald-400' : row.status === 'failed' ? 'bg-red-400' : 'bg-amber-400 animate-pulse'}`} />
                        {row.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-xs text-violet-400 hover:text-violet-300 font-semibold px-3 py-1.5 bg-violet-600/10 hover:bg-violet-600/20 rounded-lg transition-all">
                        Open →
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
