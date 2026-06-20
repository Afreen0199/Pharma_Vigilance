import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, Loader2, AlertCircle, CheckCircle, ListChecks,
  Activity, Database, Search
} from 'lucide-react';
import { verificationApi } from '../../api/verificationApi';

const Card = ({ children, className = '' }) => (
  <div className={`bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm dark:shadow-none ${className}`}>
    {children}
  </div>
);

const VerificationPanel = ({ analysisId, report }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVerification = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await verificationApi.verifyAnalysis(analysisId);
        setData(response);
      } catch (err) {
        setError('Failed to load verification evidence for this analysis.');
      } finally {
        setLoading(false);
      }
    };
    if (analysisId) fetchVerification();
  }, [analysisId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <Loader2 className="h-8 w-8 text-violet-500 animate-spin" />
        <p className="text-slate-400 text-sm font-medium animate-pulse">Running AI Verification Checks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center justify-center gap-3 text-rose-400">
        <AlertCircle className="h-6 w-6" />
        <p className="font-semibold">{error}</p>
      </div>
    );
  }

  if (!data) return null;

  const score = Math.round((data.confidence_score || 0) * 100);
  let statusColor = 'text-emerald-600 dark:text-emerald-400';
  let statusBg = 'bg-emerald-50 dark:bg-emerald-400/10 border-emerald-200 dark:border-emerald-400/20';
  let statusText = 'Highly Confident';

  if (score < 50) {
    statusColor = 'text-rose-600 dark:text-rose-400';
    statusBg = 'bg-rose-50 dark:bg-rose-400/10 border-rose-200 dark:border-rose-400/20';
    statusText = 'Low Confidence / Flagged';
  } else if (score < 80) {
    statusColor = 'text-amber-600 dark:text-amber-400';
    statusBg = 'bg-amber-50 dark:bg-amber-400/10 border-amber-200 dark:border-amber-400/20';
    statusText = 'Requires Review';
  }

  const evidenceSources = report?.evidence_sources || [];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Verification Summary */}
      <div className={`p-6 border-slate-200 dark:border-slate-800 border rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6 ${statusBg}`}>
        <div className="flex items-center gap-5">
          <div className="relative h-20 w-20 shrink-0">
            {/* Radial Progress Simulation */}
            <svg className="h-full w-full" viewBox="0 0 36 36">
              <path
                className="text-slate-200 dark:text-slate-800"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
              />
              <path
                className={statusColor}
                strokeDasharray={`${score}, 100`}
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`text-xl font-bold ${statusColor}`}>{score}%</span>
            </div>
          </div>
          <div>
            <h2 className={`text-2xl font-bold ${statusColor} mb-1`}>{statusText}</h2>
            <p className="text-sm text-slate-700 dark:text-slate-300">AI Copilot Confidence Score</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <ShieldCheck className={`h-8 w-8 ${statusColor}`} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Causality Reasoning */}
        <Card>
          <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center gap-2">
            <ListChecks className="h-5 w-5 text-violet-600 dark:text-violet-400" />
            <h3 className="font-bold text-slate-900 dark:text-white text-sm">Causality Reasoning Checklist</h3>
          </div>
          <div className="p-5 space-y-3">
            {data.causality_reasoning?.length > 0 ? (
              data.causality_reasoning.map((item, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-emerald-600 dark:text-emerald-500 shrink-0 mt-0.5" />
                  <p className="text-sm text-slate-700 dark:text-slate-300">{item}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500 italic">No causality reasoning available.</p>
            )}
          </div>
        </Card>

        {/* Seriousness Reasoning */}
        <Card>
          <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-rose-600 dark:text-rose-400" />
            <h3 className="font-bold text-slate-900 dark:text-white text-sm">Seriousness Reasoning Checklist</h3>
          </div>
          <div className="p-5 space-y-3">
            {data.seriousness_reasoning?.length > 0 ? (
              data.seriousness_reasoning.map((item, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-rose-600 dark:text-rose-500 shrink-0 mt-0.5" />
                  <p className="text-sm text-slate-700 dark:text-slate-300">{item}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500 italic">No seriousness reasoning available.</p>
            )}
          </div>
        </Card>
      </div>

      {/* Verified Claims */}
      <Card>
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center gap-2">
          <Search className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
          <h3 className="font-bold text-slate-900 dark:text-white text-sm">Verified Claims</h3>
        </div>
        <div className="p-5">
          {data.verified_claims?.length > 0 ? (
            <div className="space-y-4">
              {data.verified_claims.map((claim, idx) => (
                <div key={idx} className="p-4 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl">
                  <p className="font-bold text-slate-800 dark:text-slate-200 text-sm mb-2">Claim: <span className="font-medium text-slate-900 dark:text-slate-300">{claim.claim}</span></p>
                  <p className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold mb-1 uppercase tracking-wider">Verified From: {claim.verified_from}</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{claim.supporting_evidence}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 italic">No specific claims verified for this report.</p>
          )}
        </div>
      </Card>

      {/* Evidence Sources Table */}
      <Card>
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center gap-2">
          <Database className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
          <h3 className="font-bold text-slate-900 dark:text-white text-sm">Evidence Sources</h3>
        </div>
        <div className="p-0 overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-950">
              <tr>
                <th className="px-5 py-3 font-semibold">Source Type</th>
                <th className="px-5 py-3 font-semibold w-2/3">Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {evidenceSources.length > 0 ? (
                evidenceSources.map((source, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                    <td className="px-5 py-4">
                      <span className="px-2.5 py-1 text-[10px] font-bold uppercase rounded-lg bg-indigo-100 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
                        {source.source_type}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-slate-800 dark:text-slate-300 font-medium">{source.evidence}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="2" className="px-5 py-6 text-slate-500 italic text-center">No external evidence sources referenced.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

    </div>
  );
};

export default VerificationPanel;
