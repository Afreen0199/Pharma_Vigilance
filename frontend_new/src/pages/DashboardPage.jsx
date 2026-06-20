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
    violet: 'from-violet-600/10 to-violet-600/5 dark:from-violet-600/20 dark:to-violet-600/5 border-violet-200 dark:border-violet-600/30 text-violet-600 dark:text-violet-400',
    emerald: 'from-emerald-600/10 to-emerald-600/5 dark:from-emerald-600/20 dark:to-emerald-600/5 border-emerald-200 dark:border-emerald-600/30 text-emerald-600 dark:text-emerald-400',
    amber: 'from-amber-600/10 to-amber-600/5 dark:from-amber-600/20 dark:to-amber-600/5 border-amber-200 dark:border-amber-600/30 text-amber-600 dark:text-amber-400',
    red: 'from-red-600/10 to-red-600/5 dark:from-red-600/20 dark:to-red-600/5 border-red-200 dark:border-red-600/30 text-red-600 dark:text-red-400',
    cyan: 'from-cyan-600/10 to-cyan-600/5 dark:from-cyan-600/20 dark:to-cyan-600/5 border-cyan-200 dark:border-cyan-600/30 text-cyan-600 dark:text-cyan-400',
  };
  return (
    <div className={`bg-gradient-to-br bg-white dark:bg-transparent ${colorMap[color]} border rounded-xl p-5 flex items-center gap-4 shadow-sm dark:shadow-none`}>
      <div className={`p-3 rounded-lg bg-white/50 dark:bg-slate-900/60 ${colorMap[color]}`}>
        <Icon className="h-6 w-6" />
      </div>
      <div>
        <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{label}</p>
        {loading ? (
          <div className="h-7 w-16 bg-slate-200 dark:bg-slate-700 animate-pulse rounded mt-1" />
        ) : (
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-0.5">{value ?? '—'}</p>
        )}
        {sub && <p className="text-[11px] text-slate-500 dark:text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
};

const ChartCard = ({ title, children }) => (
  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm dark:shadow-none">
    <h3 className="text-sm font-bold text-slate-800 dark:text-slate-300 mb-4 uppercase tracking-wider">{title}</h3>
    {children}
  </div>
);

const DashboardPage = () => {
  const navigate = useNavigate();
  const [data, setData] = useState({
    statistics: { total_cases: 0, completed: 0, processing: 0, failed: 0, high_risk: 0, single_case_documents: 0, multi_case_documents: 0 },
    submission_trend: [],
    seriousness_distribution: { serious: 0, non_serious: 0 },
    recent_uploads: [],
    all_analyses: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const dashboardData = await analysisApi.getDashboard();
        setData(dashboardData);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const stats = data.statistics;
  const trendData = data.submission_trend || [];
  const seriosnessData = [
    { name: 'Serious', value: data.seriousness_distribution?.serious || 0 },
    { name: 'Non-Serious', value: data.seriousness_distribution?.non_serious || 0 }
  ].filter(d => d.value > 0);
  const recent = data.recent_uploads || [];
  const allAnalyses = data.all_analyses || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Pharmacovigilance Dashboard</h1>
          <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">Real-time AI safety intelligence overview.</p>
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
      <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4">
        <StatCard icon={FileText} label="Total Cases" value={stats.total_cases} color="violet" loading={loading} />
        <StatCard icon={CheckCircle} label="Completed" value={stats.completed} color="emerald" loading={loading} />
        <StatCard icon={ShieldAlert} label="High Risk" value={stats.high_risk} sub="Regulatory alerts" color="red" loading={loading} />
        <StatCard icon={Activity} label="Processing" value={stats.processing} color="amber" loading={loading} />
        <StatCard icon={AlertTriangle} label="Failed" value={stats.failed} color="red" loading={loading} />
        <StatCard icon={Database} label="Multi-case" value={stats.multi_case_documents} color="cyan" loading={loading} />
        <StatCard icon={FileText} label="Single-case" value={stats.single_case_documents} color="cyan" loading={loading} />
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
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.5} className="dark:stroke-slate-800" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: 8, color: '#f8fafc', fontSize: 12, boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                <Area type="monotone" dataKey="count" stroke="#8b5cf6" fill="url(#violetGrad)" strokeWidth={2} dot={{ r: 3, fill: '#8b5cf6' }} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-44 flex items-center justify-center text-slate-500 text-sm">No data yet</div>
          )}
        </ChartCard>

        <ChartCard title="Seriousness Distribution">
          {seriosnessData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={seriosnessData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false} stroke="none">
                  {seriosnessData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: 8, color: '#f8fafc', fontSize: 12, boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-44 flex items-center justify-center text-slate-500 text-sm">No data yet</div>
          )}
        </ChartCard>

        {/* Recent Uploads mini-list */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm dark:shadow-none">
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-300 mb-4 uppercase tracking-wider">Recent Uploads</h3>
          <div className="space-y-3">
            {loading ? (
              Array(4).fill(0).map((_, i) => <div key={i} className="h-10 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-lg" />)
            ) : recent.length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-6">No cases yet</p>
            ) : recent.map((item, i) => {
              return (
                <div
                  key={i}
                  onClick={() => navigate(`/analysis/${item.analysis_id}`)}
                  className="flex items-center gap-3 p-2.5 bg-slate-50 hover:bg-slate-100 dark:bg-slate-800/50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700/50 rounded-lg cursor-pointer transition-all"
                >
                  <div className={`h-2 w-2 rounded-full shrink-0 ${item.status.toLowerCase() === 'completed' ? 'bg-emerald-500' : item.status.toLowerCase() === 'failed' ? 'bg-red-500' : 'bg-amber-500'}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-slate-900 dark:text-slate-200 truncate">{item.primary_drug || 'Unknown Drug'}</p>
                    <p className="text-[10px] text-slate-500 truncate">{item.analysis_id?.substring(0, 16)}...</p>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full capitalize ${item.status.toLowerCase() === 'completed' ? 'bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400' : 'bg-amber-100 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400'}`}>{item.status}</span>
                </div>
              );
            })}
          </div>
          {!loading && allAnalyses.length > 5 && (
            <button onClick={() => navigate('/analyses')} className="mt-3 w-full text-xs text-violet-600 hover:text-violet-700 dark:text-violet-400 dark:hover:text-violet-300 font-semibold text-center">
              View all {allAnalyses.length} cases →
            </button>
          )}
        </div>
      </div>

      {/* Full Cases Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm dark:shadow-none">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-300 uppercase tracking-wider">All Case Analyses</h3>
          <span className="text-xs text-slate-500">{stats.total_cases} total</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-[11px] text-slate-500 uppercase bg-slate-50 dark:bg-slate-950/50 border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="px-6 py-3 font-bold tracking-wider">Analysis ID</th>
                <th className="px-6 py-3 font-bold tracking-wider">Date</th>
                <th className="px-6 py-3 font-bold tracking-wider">Primary Drug</th>
                <th className="px-6 py-3 font-bold tracking-wider">Status</th>
                <th className="px-6 py-3 font-bold tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {loading ? (
                Array(4).fill(0).map((_, i) => (
                  <tr key={i}>
                    {Array(5).fill(0).map((__, j) => (
                      <td key={j} className="px-6 py-4"><div className="h-4 bg-slate-100 dark:bg-slate-800 animate-pulse rounded" /></td>
                    ))}
                  </tr>
                ))
              ) : allAnalyses.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-slate-500">
                    No analyses found. Click <strong className="text-violet-600 dark:text-violet-400">New Analysis</strong> to get started.
                  </td>
                </tr>
              ) : allAnalyses.map((row) => {
                const s = row.status.toLowerCase();
                return (
                  <tr key={row.analysis_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer" onClick={() => navigate(`/analysis/${row.analysis_id}`)}>
                    <td className="px-6 py-4 font-mono text-xs text-slate-600 dark:text-slate-300">{row.analysis_id?.substring(0, 20)}...</td>
                    <td className="px-6 py-4 text-slate-500 dark:text-slate-400 text-xs">{row.created_at ? new Date(row.created_at).toLocaleDateString() : '—'}</td>
                    <td className="px-6 py-4 text-slate-900 dark:text-slate-300 font-medium capitalize">{row.primary_drug || 'Unknown'}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold capitalize ${s === 'completed' ? 'bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20' : s === 'failed' ? 'bg-red-100 dark:bg-red-500/10 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-500/20' : 'bg-amber-100 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20'}`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${s === 'completed' ? 'bg-emerald-500 dark:bg-emerald-400' : s === 'failed' ? 'bg-red-500 dark:bg-red-400' : 'bg-amber-500 dark:bg-amber-400 animate-pulse'}`} />
                        {row.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-xs text-violet-700 dark:text-violet-400 hover:text-violet-800 dark:hover:text-violet-300 font-semibold px-3 py-1.5 bg-violet-100 hover:bg-violet-200 dark:bg-violet-600/10 dark:hover:bg-violet-600/20 rounded-lg transition-all">
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
