import React, { useState } from 'react';
import { fdaApi } from '../api/fdaApi';
import DynamicChartRenderer from '../components/charts/DynamicChartRenderer';
import { 
  Search, 
  TrendingUp, 
  AlertTriangle, 
  Activity, 
  Loader2, 
  HelpCircle,
  ShieldAlert,
  BarChart4,
  Heart,
  Skull,
  UserCheck
} from 'lucide-react';

const FDAExplorer = () => {
  const [searchType, setSearchType] = useState('drug'); // 'drug' | 'reaction'
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Results states
  const [drugResults, setDrugResults] = useState(null);
  const [reactionResults, setReactionResults] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setDrugResults(null);
    setReactionResults(null);

    try {
      if (searchType === 'drug') {
        const signalData = await fdaApi.getSignalSummary(query.trim());
        
        // Extract deaths count dynamically from outcome distribution chart if present
        const deathItem = signalData.visualizations?.outcome_distribution_chart?.data?.find(
          item => String(item.outcome).toLowerCase() === 'death' || String(item.name).toLowerCase() === 'death'
        );
        signalData.deaths = deathItem ? (deathItem.count || deathItem.value || 0) : 0;
        
        setDrugResults(signalData);
      } else {
        const reactionData = await fdaApi.searchReaction(query.trim());
        setReactionResults(reactionData.results || []);
      }
    } catch (err) {
      console.error('FDA Search error:', err);
      setError(err.response?.data?.detail || 'No matching regulatory records found for the search query.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-6xl mx-auto">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-black text-slate-800 dark:text-white tracking-tight">
          FDA openFDA Registry Explorer
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Query live FAERS safety records, outcome trends, and drug-reaction signal indexes.
        </p>
      </div>

      {/* Control panel & Search Input */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-6">
        <div className="flex bg-slate-100 dark:bg-slate-950 p-1 rounded-xl max-w-xs">
          <button
            onClick={() => {
              setSearchType('drug');
              setError(null);
            }}
            className={`flex-1 text-center py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
              searchType === 'drug' 
                ? 'bg-white dark:bg-slate-800 text-slate-800 dark:text-white shadow-sm' 
                : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'
            }`}
          >
            Search Suspect Drug
          </button>
          <button
            onClick={() => {
              setSearchType('reaction');
              setError(null);
            }}
            className={`flex-1 text-center py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
              searchType === 'reaction' 
                ? 'bg-white dark:bg-slate-800 text-slate-800 dark:text-white shadow-sm' 
                : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'
            }`}
          >
            Search Adverse Event
          </button>
        </div>

        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Search className="h-4.5 w-4.5" />
            </div>
            <input
              type="text"
              required
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={searchType === 'drug' ? 'Enter active ingredient (e.g., Vancomycin, Methotrexate, Lisinopril)' : 'Enter adverse event symptom (e.g., Thrombosis, Hepatotoxicity, Pruritus)'}
              className="block w-full pl-11 pr-3 py-2.5 bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-750 rounded-xl text-xs font-semibold placeholder-slate-400 focus:outline-none focus:border-brand-500 text-slate-800 dark:text-white"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold shadow-md shadow-brand-600/20 disabled:bg-slate-200 dark:disabled:bg-slate-800 transition-all flex items-center gap-1.5 shrink-0 cursor-pointer"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <span>Search Registry</span>}
          </button>
        </form>

        {error && (
          <div className="p-3.5 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50 rounded-xl text-xs font-bold text-red-650 dark:text-red-400">
            {error}
          </div>
        )}
      </div>

      {/* Loading state spinner */}
      {loading && (
        <div className="h-64 flex flex-col items-center justify-center text-slate-450 dark:text-slate-500">
          <Loader2 className="h-10 w-10 animate-spin text-brand-500 mb-2" />
          <span className="text-xs font-semibold">Querying openFDA regulatory records...</span>
        </div>
      )}

      {/* DRUG TYPE SEARCH RESULTS */}
      {drugResults && !loading && (
        <div className="space-y-6 animate-fadeIn">
          {/* Signal Assessment Indicators */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { label: 'FDA Registered Cases', val: drugResults.api_records_retrieved || drugResults.total_cases, icon: Activity, color: 'text-brand-500 bg-brand-50 dark:bg-brand-950/30' },
              { label: 'Hospitalization Cases', val: `${drugResults.hospitalizations || 0} (${(drugResults.hosp_pct * 100).toFixed(1)}%)`, icon: Heart, color: 'text-emerald-500 bg-emerald-50 dark:bg-emerald-950/30' },
              { label: 'Fatal Outcomes (Deaths)', val: drugResults.deaths || 0, icon: Skull, color: 'text-red-500 bg-red-50 dark:bg-red-950/30' },
              { label: 'Regulatory Risk Level', val: drugResults.safety_signal || 'Low Signal', icon: ShieldAlert, color: drugResults.safety_signal === 'High' ? 'text-red-500 bg-red-50 dark:bg-red-950/30' : 'text-amber-500 bg-amber-50 dark:bg-amber-950/30' }
            ].map((c, idx) => {
              const Icon = c.icon;
              return (
                <div key={idx} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-xl shadow-sm">
                  <span className="text-[10px] text-slate-450 dark:text-slate-400 font-bold uppercase tracking-wider block">
                    {c.label}
                  </span>
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-lg font-black text-slate-800 dark:text-white">
                      {c.val}
                    </span>
                    <div className={`p-2 rounded-lg ${c.color}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {drugResults.visualizations?.outcome_distribution_chart && (
              <DynamicChartRenderer chartData={drugResults.visualizations.outcome_distribution_chart} />
            )}
            {drugResults.visualizations?.top_reactions_chart && (
              <DynamicChartRenderer chartData={drugResults.visualizations.top_reactions_chart} />
            )}
            {drugResults.visualizations?.seriousness_distribution_chart && (
              <DynamicChartRenderer chartData={drugResults.visualizations.seriousness_distribution_chart} />
            )}
            {drugResults.visualizations?.signal_trend_chart && (
              <DynamicChartRenderer chartData={drugResults.visualizations.signal_trend_chart} />
            )}
            {drugResults.visualizations?.organ_system_chart && (
              <DynamicChartRenderer chartData={drugResults.visualizations.organ_system_chart} />
            )}
          </div>
        </div>
      )}

      {/* REACTION TYPE SEARCH RESULTS */}
      {reactionResults && !loading && (
        <div className="space-y-4 animate-fadeIn">
          <h3 className="text-sm font-bold text-slate-855 dark:text-white uppercase tracking-wider">
            FDA Reported Patient Cases ({reactionResults.length})
          </h3>
          
          {reactionResults.length === 0 ? (
            <div className="p-8 text-center text-slate-400 font-medium italic">
              No matching clinical reports found.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {reactionResults.map((r, idx) => (
                <div 
                  key={r.safetyreportid || idx} 
                  className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-850 p-5 rounded-xl shadow-sm flex flex-col justify-between space-y-4"
                >
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] text-brand-600 dark:text-brand-400 font-extrabold uppercase tracking-wider bg-brand-50 dark:bg-brand-950/40 px-2 py-0.5 rounded border border-brand-100/30">
                      Report: {r.safetyreportid}
                    </span>
                    <span className="text-[10px] text-slate-400 font-bold">
                      Date: {r.receivedate ? `${r.receivedate.slice(0,4)}-${r.receivedate.slice(4,6)}-${r.receivedate.slice(6,8)}` : 'N/A'}
                    </span>
                  </div>

                  <div className="space-y-2 text-xs">
                    <p className="font-semibold text-slate-650 dark:text-slate-350">
                      <span className="text-slate-400 block text-[9px] uppercase font-bold tracking-wider">Suspected Drugs</span>
                      <span className="text-slate-800 dark:text-slate-100 font-black">
                        {r.patient?.drug?.map(d => d.medicinalproduct).filter(Boolean).slice(0,3).join(', ') || 'Unknown'}
                      </span>
                    </p>
                    <p className="font-semibold text-slate-650 dark:text-slate-350 mt-2">
                      <span className="text-slate-400 block text-[9px] uppercase font-bold tracking-wider">Reported Reactions</span>
                      <span className="text-slate-850 dark:text-slate-100 font-bold">
                        {r.patient?.reaction?.map(re => re.reactionmeddrapt).filter(Boolean).slice(0,5).join(', ') || 'N/A'}
                      </span>
                    </p>
                  </div>

                  <div className="pt-3 border-t border-slate-100 dark:border-slate-800 grid grid-cols-3 gap-2 text-center text-[10px] font-bold text-slate-500">
                    <div>
                      <span className="text-[9px] text-slate-400 block">Seriousness</span>
                      <span className={r.serious === '1' ? 'text-red-500 font-bold animate-pulse' : 'text-slate-600 dark:text-slate-300'}>
                        {r.serious === '1' ? 'Serious' : 'Non-Serious'}
                      </span>
                    </div>
                    <div>
                      <span className="text-[9px] text-slate-400 block">Reporter</span>
                      <span className="text-slate-600 dark:text-slate-300">
                        {r.primarysource?.reportercountry === 'US' ? 'Professional' : 'Consumer'}
                      </span>
                    </div>
                    <div>
                      <span className="text-[9px] text-slate-400 block">Country</span>
                      <span className="text-slate-600 dark:text-slate-300">{r.occurcountry || 'US'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Display Onboarding Helper if no search result */}
      {!drugResults && !reactionResults && !loading && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 text-center max-w-lg mx-auto space-y-4">
          <HelpCircle className="h-12 w-12 text-slate-300 dark:text-slate-700 mx-auto" />
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">How to use FDA Signal Explorer</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-semibold">
            Input a drug active ingredient name or an adverse reaction key-term above to search openFDA registries. The utility computes risk signals, death statistics, and compiles interactive outcome distribution charts.
          </p>
        </div>
      )}
    </div>
  );
};

export default FDAExplorer;
