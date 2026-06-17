import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisApi } from '../api/analysisApi';
import DynamicReportRenderer from '../components/reports/DynamicReportRenderer';
import MissingDataAlerts from '../components/reports/MissingDataAlerts';
import TimelineUI from '../components/timeline/TimelineUI';
import DynamicChartRenderer from '../components/charts/DynamicChartRenderer';
import SafetyChatbot from '../components/chatbot/SafetyChatbot';
import { 
  FileText, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  Download,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  Loader2,
  CheckCircle2,
  Calendar,
  Activity
} from 'lucide-react';

const AnalysisWorkspace = () => {
  const { analysisId } = useParams();
  const navigate = useNavigate();

  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('report');
  const [isChatOpen, setIsChatOpen] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        // Calls generateReport which will return the completed details
        const data = await analysisApi.generateReport(analysisId);
        setReportData(data);
      } catch (err) {
        console.error('Fetch report error:', err);
        setError('Failed to load case safety assessment report. Make sure backend service is active.');
      } finally {
        setLoading(false);
      }
    };

    if (analysisId) {
      fetchReport();
    }
  }, [analysisId]);

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-slate-450 dark:text-slate-500">
        <Loader2 className="h-10 w-10 animate-spin text-brand-500 mb-3" />
        <span className="text-sm font-semibold">Generating & Compiling Case Safety Assessment...</span>
        <span className="text-xs text-slate-400 mt-1 max-w-xs text-center leading-relaxed font-semibold">
          We are executing RAG context alignment, openFDA verification, and causality scoring.
        </span>
      </div>
    );
  }

  if (error || !reportData) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 rounded-2xl shadow-md text-center max-w-xl mx-auto space-y-4">
        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto" />
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">Failed to Load Safety Workspace</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 font-semibold leading-relaxed">
          {error || 'Make sure the analysis ID is correct and active.'}
        </p>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-bold transition-all cursor-pointer"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const handleDownload = (format) => {
    const url = analysisApi.getDownloadUrl(analysisId, format);
    window.open(url, '_blank');
  };

  const tabs = [
    { id: 'report', label: 'Safety Report', icon: FileText },
    { id: 'timeline', label: 'Case Timeline', icon: Clock },
    { id: 'fda', label: 'FDA Signals', icon: TrendingUp },
    { id: 'alerts', label: 'Missing Fields', icon: AlertTriangle }
  ];

  return (
    <div className="h-[calc(100vh-8rem)] flex overflow-hidden -mx-8 -mb-8 relative border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 transition-colors duration-200">
      
      {/* LEFT PANEL: Report & Details Workspace */}
      <div className={`flex flex-col h-full overflow-y-auto p-6 transition-all duration-300 ${
        isChatOpen ? 'w-2/3 border-r border-slate-200 dark:border-slate-850' : 'w-full'
      }`}>
        
        {/* Workspace Action Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 dark:border-slate-850 pb-4 mb-5 gap-4 bg-transparent">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/')}
              className="p-1.5 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-700 dark:hover:text-white rounded-lg transition-colors cursor-pointer"
              title="Back to Dashboard"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-extrabold text-slate-800 dark:text-white truncate max-w-md">
                  {reportData.filename || `Case ID: ${analysisId.slice(0, 8)}`}
                </h2>
                <span className="px-2 py-0.5 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-450 border border-emerald-100 dark:border-emerald-900/40 font-black text-[9px] uppercase tracking-wider rounded">
                  Active
                </span>
              </div>
              <span className="text-[10px] text-slate-450 font-bold block mt-0.5">
                Ingested ID: {analysisId}
              </span>
            </div>
          </div>

          {/* Export Action Buttons */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => handleDownload('pdf')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-850 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-bold transition-all cursor-pointer border border-slate-200 dark:border-slate-750"
            >
              <Download className="h-3.5 w-3.5" />
              <span>PDF</span>
            </button>
            <button
              onClick={() => handleDownload('excel')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-850 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-bold transition-all cursor-pointer border border-slate-200 dark:border-slate-750"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Excel</span>
            </button>
            <button
              onClick={() => handleDownload('json')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-850 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-bold transition-all cursor-pointer border border-slate-200 dark:border-slate-750"
            >
              <Download className="h-3.5 w-3.5" />
              <span>JSON</span>
            </button>
          </div>
        </div>

        {/* Tab Selection */}
        <div className="flex gap-2 border-b border-slate-200 dark:border-slate-850 pb-px mb-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 border-b-2 text-xs font-extrabold transition-all cursor-pointer -mb-px ${
                  activeTab === tab.id
                    ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                    : 'border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Contents */}
        <div className="flex-1 min-h-0">
          {activeTab === 'report' && (
            <div className="animate-fadeIn">
              <DynamicReportRenderer reportData={reportData} />
            </div>
          )}

          {activeTab === 'timeline' && (
            <div className="animate-fadeIn">
              <TimelineUI timeline={reportData.timeline || []} />
            </div>
          )}

          {activeTab === 'fda' && (
            <div className="space-y-6 animate-fadeIn">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {reportData.visualizations?.outcome_distribution_chart && (
                  <DynamicChartRenderer chartData={reportData.visualizations.outcome_distribution_chart} />
                )}
                {reportData.visualizations?.top_reactions_chart && (
                  <DynamicChartRenderer chartData={reportData.visualizations.top_reactions_chart} />
                )}
                {reportData.visualizations?.seriousness_distribution_chart && (
                  <DynamicChartRenderer chartData={reportData.visualizations.seriousness_distribution_chart} />
                )}
                {reportData.visualizations?.reporting_trend_chart && (
                  <DynamicChartRenderer chartData={reportData.visualizations.reporting_trend_chart} />
                )}
              </div>
            </div>
          )}

          {activeTab === 'alerts' && (
            <div className="animate-fadeIn">
              <MissingDataAlerts 
                missingFields={reportData.missing_data || []} 
                impact={reportData.missing_data_impact || reportData.gaps_impact} 
              />
            </div>
          )}
        </div>
      </div>

      {/* CHATBOT TOGGLE HANDLE */}
      <button
        onClick={() => setIsChatOpen(!isChatOpen)}
        className={`absolute bottom-6 right-6 p-3 rounded-full bg-brand-600 hover:bg-brand-700 text-white shadow-xl hover:scale-105 transition-all duration-300 z-30 cursor-pointer ${
          isChatOpen ? 'hidden' : 'flex items-center justify-center'
        }`}
        title="Open Safety Copilot Chat"
      >
        <MessageSquare className="h-6 w-6" />
      </button>

      {/* RIGHT PANEL: Collapsible Case Chatbot */}
      {isChatOpen && (
        <div className="w-1/3 h-full flex flex-col relative bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-850 shrink-0">
          {/* Collapse Handle Button */}
          <button
            onClick={() => setIsChatOpen(false)}
            className="absolute top-4 -left-3.5 h-7 w-7 rounded-full border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 hover:text-brand-500 flex items-center justify-center shadow-md hover:scale-105 z-20 transition-all cursor-pointer"
            title="Collapse Chat Sidebar"
          >
            <ChevronRight className="h-4.5 w-4.5" />
          </button>

          <div className="h-full min-h-0">
            <SafetyChatbot analysisId={analysisId} />
          </div>
        </div>
      )}

    </div>
  );
};

export default AnalysisWorkspace;
