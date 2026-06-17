import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisApi } from '../api/analysisApi';
import { 
  FolderHeart, 
  Search, 
  Loader2, 
  CheckCircle2, 
  Clock, 
  AlertTriangle,
  ChevronRight,
  Filter
} from 'lucide-react';

const CasesPage = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'completed' | 'pending'

  useEffect(() => {
    const fetchAnalyses = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await analysisApi.listAnalyses();
        setAnalyses(data || []);
      } catch (err) {
        console.error('List analyses error:', err);
        setError('Failed to fetch case history records.');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalyses();
  }, []);

  // Filter logic
  const filteredAnalyses = analyses.filter(item => {
    const matchesSearch = 
      item.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.drugs?.some(d => d.toLowerCase().includes(searchTerm.toLowerCase())) ||
      item.symptoms?.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            Safety Case Database
          </h1>
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase mt-0.5 tracking-wider">
            Search, Filter, and Manage Ingested Pharmacovigilance Records
          </p>
        </div>
        <div className="text-xs font-extrabold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-lg flex items-center gap-1">
          <FolderHeart className="h-4.5 w-4.5 text-brand-600 dark:text-brand-400" />
          <span>Total Records: {analyses.length}</span>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50 rounded-xl text-xs font-bold text-red-600 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Filter and Search Bar Control */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        
        {/* Search */}
        <div className="relative w-full md:max-w-md">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Search className="h-4 w-4" />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by suspect drug, reaction term, or file name..."
            className="block w-full pl-9 pr-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-semibold placeholder-slate-400 focus:outline-none focus:border-brand-500 text-slate-800 dark:text-white"
          />
        </div>

        {/* Filter dropdown */}
        <div className="flex gap-2 w-full md:w-auto">
          <div className="flex items-center gap-1.5 px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-400 font-semibold w-full md:w-auto">
            <Filter className="h-3.5 w-3.5" />
            <span>Filter Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent text-slate-700 dark:text-slate-300 font-bold border-none focus:outline-none cursor-pointer pl-1 text-xs"
            >
              <option value="all">All Cases</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>
      </div>

      {/* Database table list */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm p-6">
        {loading ? (
          <div className="h-60 flex flex-col items-center justify-center text-slate-400">
            <Loader2 className="h-8 w-8 animate-spin text-brand-500 mb-2" />
            <span className="text-xs font-semibold">Retrieving case safety database records...</span>
          </div>
        ) : filteredAnalyses.length === 0 ? (
          <div className="h-60 flex flex-col items-center justify-center text-center p-6 text-slate-400">
            <FolderHeart className="h-10 w-10 text-slate-300 dark:text-slate-700 mb-2.5" />
            <p className="text-xs font-bold text-slate-600 dark:text-slate-400">No matching case records</p>
            <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">
              Modify your filter criteria or try searching for another suspect drug term.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 text-[10px] text-slate-400 dark:text-slate-500 font-extrabold uppercase">
                  <th className="pb-3">Analysis Ref</th>
                  <th className="pb-3">Ingested Document Name</th>
                  <th className="pb-3">Suspect Drugs</th>
                  <th className="pb-3">Clinical Adverse Events</th>
                  <th className="pb-3 text-center">Pipeline Status</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/50 text-xs">
                {filteredAnalyses.map((caseItem) => (
                  <tr key={caseItem.analysis_id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-all font-medium">
                    <td className="py-3.5 font-bold text-slate-400 uppercase text-[10px]">
                      {caseItem.analysis_id.slice(0, 8)}
                    </td>
                    <td className="py-3.5 font-semibold text-slate-700 dark:text-slate-300 max-w-[200px] truncate" title={caseItem.filename}>
                      {caseItem.filename}
                    </td>
                    <td className="py-3.5">
                      <div className="flex flex-wrap gap-1">
                        {caseItem.drugs && caseItem.drugs.length > 0 ? (
                          caseItem.drugs.map((d, i) => (
                            <span key={i} className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold rounded text-[10px]">
                              {d}
                            </span>
                          ))
                        ) : (
                          <span className="text-slate-400">None</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 text-slate-600 dark:text-slate-400 max-w-[200px] truncate" title={caseItem.symptoms?.join(', ')}>
                      {caseItem.symptoms && caseItem.symptoms.length > 0 ? caseItem.symptoms.join(', ') : 'None'}
                    </td>
                    <td className="py-3.5 text-center">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 font-bold rounded-full text-[10px] ${
                        caseItem.status === 'completed'
                          ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400'
                          : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 animate-pulse'
                      }`}>
                        {caseItem.status === 'completed' ? 'Completed' : 'Pending'}
                      </span>
                    </td>
                    <td className="py-3.5 text-right">
                      <button
                        onClick={() => navigate(`/workspace/${caseItem.analysis_id}`)}
                        className="px-3 py-1 bg-brand-600 hover:bg-brand-700 text-white rounded-md font-bold text-[10px] transition-all inline-flex items-center gap-1"
                      >
                        <span>Workspace</span>
                        <ChevronRight className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default CasesPage;
