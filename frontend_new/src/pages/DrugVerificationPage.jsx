import React, { useState } from 'react';
import { 
  Search, ShieldCheck, AlertTriangle, ShieldAlert, Activity,
  Database, FileText, CheckCircle, Loader2, Hospital, Stethoscope, AlertCircle
} from 'lucide-react';
import { verificationApi } from '../api/verificationApi';

const Card = ({ children, className = '' }) => (
  <div className={`bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm dark:shadow-none ${className}`}>
    {children}
  </div>
);

const Badge = ({ children, variant = 'gray' }) => {
  const styles = {
    success: 'bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20',
    warning: 'bg-amber-100 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20',
    danger: 'bg-rose-100 dark:bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-500/20',
    violet: 'bg-violet-100 dark:bg-violet-500/10 text-violet-700 dark:text-violet-400 border border-violet-200 dark:border-violet-500/20',
    gray: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700',
  };
  
  return (
    <span className={`px-2.5 py-1 text-xs font-bold rounded-lg uppercase tracking-wider ${styles[variant]}`}>
      {children}
    </span>
  );
};

const StatCard = ({ title, value, icon: Icon, color = 'violet' }) => {
  const colorMap = {
    violet: 'text-violet-400 bg-violet-400/10 border-violet-400/20',
    emerald: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
    rose: 'text-rose-400 bg-rose-400/10 border-rose-400/20',
    amber: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
  };

  return (
    <Card className="p-5 flex items-center gap-4 hover:border-slate-700 transition-colors">
      <div className={`p-3 rounded-xl border ${colorMap[color]}`}>
        <Icon className="h-6 w-6" />
      </div>
      <div>
        <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">{title}</p>
        <p className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
      </div>
    </Card>
  );
};

const DrugVerificationPage = () => {
  const [query, setQuery] = useState('');
  const [evidence, setEvidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setEvidence(null);

    try {
      const data = await verificationApi.verifyDrug(query.trim());
      setEvidence(data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('No verification evidence found for this drug.');
      } else {
        setError('An error occurred while verifying the drug.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getSignalLevel = (data) => {
    const total = data.fda_evidence?.total_cases || 0;
    const serious = data.fda_evidence?.serious_cases || 0;
    
    if (total > 100000 || serious > 50000) return { label: 'High Risk', variant: 'danger' };
    if (total > 10000 || serious > 5000) return { label: 'Elevated Risk', variant: 'warning' };
    if (total > 0) return { label: 'Baseline Risk', variant: 'success' };
    return { label: 'Unknown Risk', variant: 'gray' };
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white flex items-center gap-3">
          <ShieldCheck className="h-8 w-8 text-violet-600 dark:text-violet-500" />
          Drug Verification
        </h1>
        <p className="text-slate-600 dark:text-slate-400 text-sm max-w-2xl">
          Search the global pharmacovigilance database, FDA FAERS, and internal knowledge base to verify drug safety profiles, historical signals, and known adverse reactions.
        </p>
      </div>

      <Card className="p-2">
        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
            <input
              type="text"
              placeholder="Enter drug name (e.g. Aspirin, Apratixaban)..."
              className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl py-3 pl-12 pr-4 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-violet-600 dark:focus:border-violet-500 focus:ring-1 focus:ring-violet-600 dark:focus:ring-violet-500 transition-all"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-6 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white font-bold text-sm rounded-xl transition-all flex items-center gap-2 whitespace-nowrap"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldCheck className="h-4 w-4" />}
            Verify Drug
          </button>
        </form>
      </Card>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex gap-3 text-rose-400 items-center">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-4">
          <Loader2 className="h-10 w-10 text-violet-600 dark:text-violet-500 animate-spin" />
          <p className="text-slate-600 dark:text-slate-400 text-sm font-medium animate-pulse">Querying FDA APIs and Global Databases...</p>
        </div>
      )}

      {!loading && !evidence && !error && (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-4 opacity-50">
          <Database className="h-16 w-16 text-slate-400 dark:text-slate-700" />
          <p className="text-slate-600 dark:text-slate-500 text-sm font-medium">Enter a drug name to view evidence.</p>
        </div>
      )}

      {!loading && evidence && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 bg-gradient-to-r from-violet-100 dark:from-violet-600/10 to-indigo-100 dark:to-indigo-600/10 border border-violet-200 dark:border-violet-500/20 rounded-2xl">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white capitalize">{evidence.drug_name}</h2>
                <Badge variant={evidence.verification_status === 'Verified' ? 'success' : 'warning'}>
                  {evidence.verification_status}
                </Badge>
                {evidence.fda_evidence?.total_cases > 0 && (
                  <Badge variant="violet">FDA Verified</Badge>
                )}
                <Badge variant={getSignalLevel(evidence).variant}>
                  {getSignalLevel(evidence).label}
                </Badge>
              </div>
              <p className="text-sm text-slate-700 dark:text-slate-400">
                Found {evidence.supporting_cases?.length || 0} local matching cases and {evidence.fda_evidence?.total_cases?.toLocaleString() || 0} historical FDA reports.
              </p>
            </div>
            <div className="h-12 w-12 rounded-full bg-violet-600/20 flex items-center justify-center shrink-0 border border-violet-500/30">
              <ShieldCheck className="h-6 w-6 text-violet-400" />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard 
              title="Total FDA Cases" 
              value={evidence.fda_evidence?.total_cases || 0} 
              icon={Database} 
              color="violet" 
            />
            <StatCard 
              title="Serious FDA Cases" 
              value={evidence.fda_evidence?.serious_cases || 0} 
              icon={AlertTriangle} 
              color="amber" 
            />
            <StatCard 
              title="Hospitalizations" 
              value={evidence.fda_evidence?.hospitalizations || 0} 
              icon={Hospital} 
              color="rose" 
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Reactions */}
            <Card>
              <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center gap-2">
                <Activity className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                <h3 className="font-bold text-slate-900 dark:text-white text-sm">Top FDA Reported Reactions</h3>
              </div>
              <div className="p-5">
                {evidence.fda_evidence?.top_reactions?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {evidence.fda_evidence.top_reactions.map((reaction, idx) => (
                      <span key={idx} className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg">
                        {reaction}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500 italic">No reactions available.</p>
                )}
              </div>
            </Card>

            {/* Local FAERS Evidence */}
            <Card>
              <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center gap-2">
                <FileText className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                <h3 className="font-bold text-slate-900 dark:text-white text-sm">Local FAERS Dataset Evidence</h3>
              </div>
              <div className="p-0 overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-950">
                    <tr>
                      <th className="px-5 py-3 font-semibold">Reaction</th>
                      <th className="px-5 py-3 font-semibold">Count</th>
                      <th className="px-5 py-3 font-semibold">Source</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                    {evidence.local_faers_evidence?.length > 0 ? (
                      evidence.local_faers_evidence.slice(0, 5).map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                          <td className="px-5 py-3 font-medium text-slate-800 dark:text-slate-300">{row.reaction}</td>
                          <td className="px-5 py-3 text-slate-600 dark:text-slate-400">{row.count.toLocaleString()}</td>
                          <td className="px-5 py-3">
                            <span className="px-2 py-1 bg-indigo-100 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20 text-[10px] uppercase font-bold rounded">
                              {row.source}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="3" className="px-5 py-4 text-slate-500 italic text-center">No local FAERS records found.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>

          {/* Supporting Internal Cases */}
          <Card>
            <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-violet-600 dark:text-violet-400" />
              <h3 className="font-bold text-slate-900 dark:text-white text-sm">Internal Verified Cases</h3>
            </div>
            <div className="p-5">
              {evidence.supporting_cases?.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                  {evidence.supporting_cases.slice(0, 6).map((c, idx) => (
                    <div key={idx} className="p-4 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl flex items-start gap-3 shadow-sm dark:shadow-none">
                      <CheckCircle className="h-5 w-5 text-emerald-600 dark:text-emerald-500 shrink-0 mt-0.5" />
                      <div>
                        <p className="text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">Case: {c.case_id}</p>
                        <p className="text-sm font-medium text-slate-900 dark:text-white">{c.reaction}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500 italic">No supporting internal cases found.</p>
              )}
            </div>
          </Card>

        </div>
      )}
    </div>
  );
};

export default DrugVerificationPage;
