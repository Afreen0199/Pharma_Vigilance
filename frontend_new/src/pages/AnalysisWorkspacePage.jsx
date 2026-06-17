import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Download, ShieldCheck, FileText, Clock, Activity, AlertTriangle,
  AlertCircle, ChevronRight, Users, Info, Loader2, ArrowLeft,
  Pill, User, FlaskConical, FileBarChart, MessageSquare, Brain,
  CheckCircle, Database, LayoutDashboard, Stethoscope, FileSearch, Eye,
  ChevronDown, ChevronUp, FileCode, Server
} from 'lucide-react';
import { reportApi } from '../api/reportApi';
import ChatbotPanel from '../components/analysis/ChatbotPanel';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend, AreaChart, Area
} from 'recharts';

const COLORS = ['#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899'];

/* ─── Helper: Section Card ─── */
const Panel = ({ title, icon: Icon, children, className = '' }) => (
  <div className={`bg-slate-900 border border-slate-800 rounded-xl overflow-hidden ${className}`}>
    {title && (
      <div className="flex items-center gap-2 px-5 py-3.5 border-b border-slate-800 bg-slate-950/50">
        {Icon && <Icon className="h-4 w-4 text-violet-400" />}
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">{title}</h3>
      </div>
    )}
    <div className="p-5">{children}</div>
  </div>
);

const Badge = ({ children, variant = 'default', className = '' }) => {
  const vars = {
    default: 'bg-slate-700 text-slate-300',
    success: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
    danger: 'bg-red-500/10 text-red-400 border border-red-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
    violet: 'bg-violet-500/10 text-violet-400 border border-violet-500/20',
    cyan: 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20',
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold capitalize ${vars[variant]} ${className}`}>
      {children}
    </span>
  );
};

const DataRow = ({ label, value }) => (
  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-2 border-b border-slate-800/50 last:border-0 gap-1">
    <span className="text-xs font-medium text-slate-500 capitalize">{label.replace(/_/g, ' ')}</span>
    <span className="text-sm font-semibold text-slate-200 text-left sm:text-right">
      {value !== undefined && value !== null && value !== '' ? String(value) : 'Not Specified'}
    </span>
  </div>
);

/* ─── Patient & Case Information ─── */
const PatientCasePanel = ({ data }) => {
  const caseInfo = data.case_information || {};
  const patient = data.patient_demographic || data.patient_information || data.patient_details || {};
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Panel title="Case Information" icon={FileText}>
        <div className="space-y-1">
          <DataRow label="Case ID" value={caseInfo.case_id} />
          <DataRow label="Report Type" value={caseInfo.report_type} />
          <DataRow label="Report Date" value={caseInfo.report_date} />
          <DataRow label="Case Status" value={caseInfo.case_status} />
          <DataRow label="Seriousness" value={caseInfo.seriousness} />
        </div>
      </Panel>
      <Panel title="Patient Information" icon={User}>
        <div className="space-y-1">
          <DataRow label="Age" value={patient.age} />
          <DataRow label="Age Group" value={patient.age_group?.meaning || patient.age_group?.code || patient.age_group} />
          <DataRow label="Gender" value={patient.gender} />
          <DataRow label="Weight" value={patient.weight || patient.patient_weight} />
          <DataRow label="Medical History" value={patient.medical_history} />
        </div>
      </Panel>
    </div>
  );
};

/* ─── Drug Information ─── */
const DrugPanel = ({ data }) => {
  const drug = data.drug_information || {};
  const suspected = data.suspected_drug_information || {};
  const therapy = data.therapy_information || {};

  return (
    <Panel title="Drug Information" icon={Pill}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
        <DataRow label="Drug Name" value={suspected.drug_name || drug.product_active_ingredient} />
        <DataRow label="Active Ingredient" value={drug.product_active_ingredient} />
        <DataRow label="Drug Role" value={drug.drug_role?.meaning || drug.drug_role?.code || drug.drug_role} />
        <DataRow label="Indication" value={suspected.indication} />
        <DataRow label="Dosage" value={suspected.dosage || therapy.dose_amount} />
        <DataRow label="Dose Unit" value={therapy.dose_unit} />
        <DataRow label="Frequency" value={therapy.dose_frequency} />
        <DataRow label="Route" value={suspected.route || therapy.route} />
        <DataRow label="Therapy Duration" value={therapy.therapy_duration} />
        <DataRow label="Therapy Start Date" value={suspected.therapy_start_date} />
        <DataRow label="Therapy End Date" value={suspected.therapy_end_date} />
        <DataRow label="Dose Form" value={therapy.dose_form} />
      </div>
    </Panel>
  );
};

/* ─── Drug Batch Details & Reporter ─── */
const BatchReporterPanel = ({ data }) => {
  const batch = data.drug_batch_details || {};
  const reporter = data.reporter_information || {};

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Panel title="Drug Batch Information" icon={Database}>
        <div className="space-y-1">
          <DataRow label="Manufacturer" value={batch.manufacturer} />
          <DataRow label="Lot Number" value={batch.lot_number} />
          <DataRow label="Batch Number" value={batch.batch_number} />
          <DataRow label="Expiry Date" value={batch.expiry_date} />
        </div>
      </Panel>
      <Panel title="Reporter Information" icon={Users}>
        <div className="space-y-1">
          <DataRow label="Occupation" value={reporter.occupation?.meaning || reporter.occupation?.code || reporter.occupation} />
          <DataRow label="Reporter Type" value={reporter.reporter_type} />
        </div>
      </Panel>
    </div>
  );
};

/* ─── Insights Panels ─── */
const InsightCard = ({ insight, type }) => {
  const isSafety = type === 'safety';
  const isMedical = type === 'medical';
  const isObservation = type === 'observation';

  const Icon = isSafety ? ShieldCheck : isMedical ? Stethoscope : Eye;
  const color = isSafety ? 'violet' : isMedical ? 'cyan' : 'amber';
  const bgClass = isSafety ? 'bg-violet-900/10 border-violet-800/30' : isMedical ? 'bg-cyan-900/10 border-cyan-800/30' : 'bg-amber-900/10 border-amber-800/30';
  const iconColor = isSafety ? 'text-violet-400' : isMedical ? 'text-cyan-400' : 'text-amber-400';
  const badgeLabel = isSafety ? 'AI Safety' : isMedical ? 'Medical Review' : 'Recommendation';

  return (
    <div className={`flex items-start gap-3 p-4 rounded-xl border ${bgClass}`}>
      <div className={`mt-1 p-1.5 rounded-lg bg-slate-900/50 ${iconColor}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1">
        <p className="text-sm text-slate-200 leading-relaxed">{insight}</p>
      </div>
      <Badge variant={color} className="shrink-0">{badgeLabel}</Badge>
    </div>
  );
};

const InsightsPanel = ({ data }) => {
  const safetyInsights = data.ai_safety_insights || [];
  const medicalInsights = data.medical_insights || [];
  const observations = data.safety_observations || [];

  return (
    <div className="space-y-6">
      <Panel title="Clinical AI Safety Insights" icon={Brain}>
        {safetyInsights.length === 0 ? <p className="text-slate-500 text-sm italic">Not Specified</p> : (
          <div className="space-y-3">
            {safetyInsights.map((item, i) => <InsightCard key={i} insight={item} type="safety" />)}
          </div>
        )}
      </Panel>
      <Panel title="Medical Review Insights" icon={Stethoscope}>
        {medicalInsights.length === 0 ? <p className="text-slate-500 text-sm italic">Not Specified</p> : (
          <div className="space-y-3">
            {medicalInsights.map((item, i) => <InsightCard key={i} insight={item} type="medical" />)}
          </div>
        )}
      </Panel>
      <Panel title="Safety Observations" icon={Eye}>
         {observations.length === 0 ? <p className="text-slate-500 text-sm italic">Not Specified</p> : (
          <div className="space-y-3">
            {observations.map((item, i) => <InsightCard key={i} insight={item} type="observation" />)}
          </div>
        )}
      </Panel>
    </div>
  );
};

/* ─── FDA Signals Panel ─── */
const FDAPanel = ({ fdaData, visualizations }) => {
  const vis = visualizations || {};
  const sig = fdaData || {};

  const stats = [
    { label: 'Total Cases', value: sig.total_cases ?? sig.api_total_cases ?? sig.local_total_cases ?? 'Not Specified' },
    { label: 'API Cases', value: sig.api_total_cases ?? 'Not Specified' },
    { label: 'Local Cases', value: sig.local_total_cases ?? 'Not Specified' },
    { label: 'Serious Cases', value: sig.serious_cases ?? 'Not Specified' },
    { label: 'Hospitalizations', value: sig.hospitalizations ?? 'Not Specified' },
    { label: 'Signal Score', value: sig.signal_score ?? 'Not Specified' },
  ];
  
  const hasVisualizations = vis && Object.keys(vis).length > 0;

  return (
    <div className="space-y-6">
      {/* Stats bar */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {stats.map(s => (
          <div key={s.label} className="bg-slate-800 border border-slate-700 rounded-xl p-3 text-center">
            <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">{s.label}</p>
            <p className="text-lg font-bold text-white mt-1">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Recent FDA Cases */}
      {sig.recent_cases && sig.recent_cases.length > 0 && (
         <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Recent FDA Cases</h4>
            <div className="flex flex-wrap gap-2">
               {sig.recent_cases.map((rc, i) => (
                  <div key={i} className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-lg text-xs text-slate-300">
                     {typeof rc === 'string' ? rc : JSON.stringify(rc)}
                  </div>
               ))}
            </div>
         </div>
      )}
      
      {/* Top Reactions */}
      {sig.top_reactions && sig.top_reactions.length > 0 && (
         <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Top FDA Reported Reactions</h4>
            <div className="flex flex-wrap gap-2">
               {sig.top_reactions.map((reaction, i) => {
                   const name = reaction.term || reaction.name || reaction;
                   const count = reaction.count ? ` (${reaction.count})` : '';
                   return (
                      <Badge key={i} variant="violet" className="text-xs py-1 px-3">
                        {name}{count}
                      </Badge>
                   );
               })}
            </div>
         </div>
      )}

      {/* Dynamic Charts from visualizations */}
      {hasVisualizations ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {Object.entries(vis).map(([chartKey, chartData], index) => {
             let type = 'bar';
             if (chartKey.includes('pie') || chartKey.includes('distribution')) type = 'pie';
             if (chartKey.includes('trend') || chartKey.includes('line')) type = 'line';
             
             let dataToRender = [];
             if (Array.isArray(chartData)) {
                 dataToRender = chartData;
             } else if (chartData && typeof chartData === 'object') {
                 if (Array.isArray(chartData.data)) {
                     dataToRender = chartData.data;
                 } else {
                     // Chart data is a direct key-value object
                     dataToRender = Object.entries(chartData)
                         .filter(([k]) => k !== 'type' && k !== 'title')
                         .map(([k, v]) => ({ name: k, value: v }));
                 }
             }

             const chartType = chartData?.type || type;
             const chartTitle = chartData?.title || chartKey.replace(/_/g, ' ');

             if (!dataToRender || dataToRender.length === 0) return null;

             const mappedData = dataToRender.map(item => {
                 // Already correctly formatted from Object.entries fallback above
                 if (item.name !== undefined && item.value !== undefined) return item;
                 
                 const possibleNameKeys = ['label', 'name', 'term', 'reaction', 'organ_system', 'outcome', 'year', 'category', 'status', 'seriousness'];
                 const possibleValueKeys = ['count', 'value', 'cases', 'amount', 'total'];
                 
                 let name = undefined;
                 let value = undefined;

                 for (const k of possibleNameKeys) {
                     if (item[k] !== undefined) { name = item[k]; break; }
                 }
                 for (const k of possibleValueKeys) {
                     if (item[k] !== undefined) { value = item[k]; break; }
                 }

                 // Fallback: sniff by type if exact keys weren't found
                 if (name === undefined || value === undefined) {
                     for (const [k, v] of Object.entries(item)) {
                         if (typeof v === 'string' && name === undefined) name = v;
                         if (typeof v === 'number' && value === undefined) value = v;
                     }
                 }

                 return {
                     name: name !== undefined ? String(name) : 'Unknown',
                     value: value !== undefined ? Number(value) : 0
                 };
             });

             const CustomTooltip = ({ active, payload }) => {
                 if (active && payload && payload.length) {
                     const data = payload[0].payload;
                     return (
                         <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl z-50 relative max-w-xs">
                             <p className="text-xs text-slate-200 font-bold uppercase tracking-wider leading-relaxed">{data.name}</p>
                             <p className="text-sm text-violet-400 font-semibold mt-1">— {data.value?.toLocaleString()} cases</p>
                         </div>
                     );
                 }
                 return null;
             };

             // Customizing labels based on chartTitle
             const lowerTitle = chartTitle.toLowerCase();
             let numAxisLabel = 'Value';
             let catAxisLabel = 'Category';

             if (chartType === 'line') {
                 catAxisLabel = 'Year';
                 numAxisLabel = 'Number of FDA Reports';
             } else if (chartType === 'bar') {
                 numAxisLabel = 'Reported Cases';
                 catAxisLabel = lowerTitle.includes('organ') ? 'Organ System' :
                                lowerTitle.includes('reaction') ? 'Adverse Reaction' :
                                lowerTitle.includes('outcome') ? 'Outcome' :
                                lowerTitle.includes('serious') ? 'Seriousness' : 'Category';
             }

             // Truncate function for long labels
             const truncateTick = (tick) => (tick && typeof tick === 'string' && tick.length > 18 ? `${tick.substring(0, 18)}...` : tick);

             return (
                <Panel key={index} title={chartTitle}>
                  <ResponsiveContainer width="100%" height={320}>
                    {chartType === 'pie' ? (
                      <PieChart margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                        <Pie data={mappedData} cx="50%" cy="45%" innerRadius={65} outerRadius={95} paddingAngle={3} dataKey="value" nameKey="name" label={false}>
                          {mappedData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                        </Pie>
                        <Legend layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ paddingTop: '20px' }} formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 11 }}>{v}</span>} />
                        <Tooltip content={<CustomTooltip />} />
                      </PieChart>
                    ) : chartType === 'line' ? (
                      <AreaChart data={mappedData} margin={{ top: 20, right: 30, left: 30, bottom: 20 }}>
                        <defs>
                          <linearGradient id={`grad-${index}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={COLORS[index % COLORS.length]} stopOpacity={0.4} />
                            <stop offset="95%" stopColor={COLORS[index % COLORS.length]} stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} tickMargin={12} label={{ value: catAxisLabel, position: 'insideBottom', offset: -15, fill: '#94a3b8', fontSize: 12, fontWeight: 600 }} />
                        <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickMargin={12} label={{ value: numAxisLabel, angle: -90, position: 'insideLeft', offset: -15, fill: '#94a3b8', fontSize: 12, fontWeight: 600 }} />
                        <Tooltip content={<CustomTooltip />} />
                        <Area type="monotone" dataKey="value" stroke={COLORS[index % COLORS.length]} fill={`url(#grad-${index})`} strokeWidth={2} />
                      </AreaChart>
                    ) : (
                      <BarChart data={mappedData} layout={mappedData.length > 5 ? "vertical" : "horizontal"} margin={mappedData.length > 5 ? { top: 20, right: 30, left: 20, bottom: 20 } : { top: 20, right: 30, left: 30, bottom: 50 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={mappedData.length <= 5} vertical={mappedData.length > 5} />
                        {mappedData.length > 5 ? (
                           <>
                             <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} tickMargin={12} label={{ value: numAxisLabel, position: 'insideBottom', offset: -15, fill: '#94a3b8', fontSize: 12, fontWeight: 600 }} />
                             <YAxis dataKey="name" type="category" width={140} tickFormatter={truncateTick} tick={{ fill: '#94a3b8', fontSize: 11 }} tickMargin={12} label={{ value: catAxisLabel, angle: -90, position: 'insideLeft', offset: -5, fill: '#94a3b8', fontSize: 12, fontWeight: 600 }} />
                           </>
                        ) : (
                           <>
                             <XAxis dataKey="name" tickFormatter={truncateTick} angle={-35} textAnchor="end" height={80} tick={{ fill: '#64748b', fontSize: 11 }} tickMargin={12} label={{ value: catAxisLabel, position: 'insideBottom', offset: -35, fill: '#94a3b8', fontSize: 12, fontWeight: 600 }} />
                             <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickMargin={12} label={{ value: numAxisLabel, angle: -90, position: 'insideLeft', offset: -15, fill: '#94a3b8', fontSize: 12, fontWeight: 600 }} />
                           </>
                        )}
                        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#1e293b', opacity: 0.4 }} />
                        <Bar dataKey="value" fill={COLORS[index % COLORS.length]} radius={[4, 4, 4, 4]} />
                      </BarChart>
                    )}
                  </ResponsiveContainer>
                </Panel>
             );
          })}
        </div>
      ) : (
        <div className="text-center py-10 text-slate-500 text-sm">
          <Activity className="h-8 w-8 text-slate-600 mx-auto mb-2" />
          No data available
        </div>
      )}
    </div>
  );
};

/* ─── Regulatory Alerts Panel ─── */
const RegAlertsPanel = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="text-center py-10 text-slate-500 text-sm">
        <ShieldCheck className="h-8 w-8 text-emerald-500 mx-auto mb-2" />
        No regulatory alerts detected.
      </div>
    );
  }
  return (
    <div className="space-y-3">
      {alerts.map((alert, i) => {
        const message = typeof alert === 'string' ? alert : (alert.alert || alert.message || JSON.stringify(alert));
        const source = alert.source;
        const severity = alert.severity;
        const reason = alert.reason;
        
        return (
          <div key={i} className="flex items-start gap-3 p-4 bg-red-900/10 border border-red-700/40 rounded-xl">
            <AlertTriangle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-red-300">{message}</p>
              {reason && <p className="text-sm text-slate-300 mt-1">{reason}</p>}
              <div className="flex items-center gap-3 mt-2">
                {source && <span className="text-xs text-slate-400 flex items-center gap-1"><Info className="h-3 w-3"/> Source: {source}</span>}
                {severity && <Badge variant={severity.toLowerCase() === 'high' ? 'danger' : 'warning'}>{severity}</Badge>}
              </div>
            </div>
            <Badge variant="danger" className="shrink-0">Alert</Badge>
          </div>
        );
      })}
    </div>
  );
};

/* ─── Missing Information Panel ─── */
const MissingInfoPanel = ({ missing }) => {
  if (!missing || missing.length === 0) {
    return (
      <div className="text-center py-10 text-slate-500 text-sm">
        <CheckCircle className="h-8 w-8 text-emerald-500 mx-auto mb-2" />
        No critical missing information detected.
      </div>
    );
  }
  const len = missing.length;
  const impact = len >= 6 ? 'High' : len >= 3 ? 'Medium' : 'Low';
  const impactColor = { High: 'danger', Medium: 'warning', Low: 'success' }[impact];
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between p-4 bg-amber-900/10 border border-amber-700/30 rounded-xl">
        <div>
          <p className="text-xs font-bold text-amber-400 uppercase tracking-wider">Impact on Assessment</p>
          <p className="text-sm text-slate-300 mt-1">{len} missing field{len !== 1 ? 's' : ''} detected</p>
        </div>
        <Badge variant={impactColor}>{impact} Impact</Badge>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {missing.map((item, i) => (
          <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg">
            <AlertCircle className="h-4 w-4 text-amber-400 shrink-0" />
            <span className="text-sm text-slate-300 font-medium">{typeof item === 'string' ? item : JSON.stringify(item)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ─── ADR Timeline Panel ─── */
const TimelinePanel = ({ timeline }) => {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="text-center py-10 text-slate-500 text-sm">
        <Clock className="h-8 w-8 text-slate-600 mx-auto mb-2" />
        No timeline events available for this case.
      </div>
    );
  }
  return (
    <div className="relative border-l-2 border-violet-800/50 ml-4 space-y-6 py-2">
      {timeline.map((event, i) => {
        const displayDate = event.timestamp || event.date;
        return (
          <div key={i} className="relative pl-8">
            <span className="absolute -left-3 flex h-6 w-6 items-center justify-center rounded-full bg-violet-700 ring-4 ring-slate-900">
              <Clock className="h-3.5 w-3.5 text-white" />
            </span>
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-1">
                {displayDate && <span className="text-xs font-bold text-violet-400">{displayDate}</span>}
                {event.related_drugs?.map((d, j) => (
                  <Badge key={j} variant="violet">{d}</Badge>
                ))}
              </div>
              <h4 className="text-sm font-bold text-slate-200">{event.event || event.description}</h4>
              {event.description && event.event && event.description !== event.event && (
                  <p className="text-xs text-slate-400 mt-1">{event.description}</p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  );
};

/* ─── OCR Metadata Section ─── */
const OCRMetadata = ({ ocr }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  if (!ocr || Object.keys(ocr).length === 0) return null;

  return (
    <div className="border border-slate-800 rounded-xl bg-slate-900/50 overflow-hidden mt-6">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 hover:bg-slate-800/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <FileSearch className="h-4 w-4 text-slate-400" />
          <span className="text-sm font-bold text-slate-300 uppercase tracking-wider">OCR Metadata</span>
        </div>
        {isOpen ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
      </button>
      {isOpen && (
        <div className="p-4 border-t border-slate-800 bg-slate-950/30">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <DataRow label="Source Type" value={ocr.source_type} />
            <DataRow label="OCR Used" value={ocr.ocr_used ? 'Yes' : 'No'} />
            <DataRow label="Confidence" value={ocr.ocr_confidence} />
            <DataRow label="Patient Index" value={ocr.patient_index} />
            <DataRow label="Parent Doc ID" value={ocr.parent_document_id} />
          </div>
        </div>
      )}
    </div>
  );
};

/* ─── Verification Section ─── */
const VerificationSection = ({ data }) => {
  const sources = data.evidence_sources || [];
  const hasFDA = data.fda_signal && Object.keys(data.fda_signal).length > 0;
  const hasMilvus = data.retrieved_chunks && data.retrieved_chunks.length > 0;
  
  return (
    <Panel title="Verification Sources" icon={CheckCircle}>
      <div className="flex flex-wrap gap-3">
        <div className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg">
           <CheckCircle className="h-4 w-4 text-emerald-500" />
           <span className="text-sm font-semibold text-slate-200">Clinical Report</span>
        </div>
        {hasFDA && (
           <div className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg">
             <CheckCircle className="h-4 w-4 text-emerald-500" />
             <span className="text-sm font-semibold text-slate-200">FDA API</span>
          </div>
        )}
        {sources.some(s => s.source_type === 'FAERS_LOCAL') && (
           <div className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg">
             <CheckCircle className="h-4 w-4 text-emerald-500" />
             <span className="text-sm font-semibold text-slate-200">Local FAERS Dataset</span>
          </div>
        )}
        {hasMilvus && (
           <div className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg">
             <CheckCircle className="h-4 w-4 text-emerald-500" />
             <span className="text-sm font-semibold text-slate-200">Milvus Knowledge Base</span>
          </div>
        )}
      </div>
    </Panel>
  );
};

/* ─── Case Metadata Footer ─── */
const MetadataFooter = ({ data, id }) => {
  return (
    <div className="mt-8 pt-6 border-t border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-500">
      <div className="flex items-center gap-4 flex-wrap">
        <span className="flex items-center gap-1.5"><Server className="h-3.5 w-3.5" /> Analysis ID: <span className="text-slate-300 font-mono">{id}</span></span>
        <span className="flex items-center gap-1.5"><FileCode className="h-3.5 w-3.5" /> Report ID: <span className="text-slate-300 font-mono">{data.case_information?.case_id || 'N/A'}</span></span>
        <span>Status: <span className="text-slate-300 capitalize">{data.status || 'Completed'}</span></span>
        {data.cached && <span>Cached: <span className="text-slate-300">True</span></span>}
      </div>
      <div className="flex items-center gap-2">
        <span>Generated Formats:</span>
        <Badge variant="default">PDF</Badge>
        <Badge variant="default">Excel</Badge>
        <Badge variant="default">JSON</Badge>
      </div>
    </div>
  );
};

/* ─── Multi-case Tab Selector ─── */
const CaseTabs = ({ cases, activeIdx, onSelect }) => (
  <div className="flex gap-2 flex-wrap mb-4">
    {cases.map((c, i) => (
      <button
        key={i}
        onClick={() => onSelect(i)}
        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all border ${i === activeIdx ? 'bg-violet-600 text-white border-violet-600' : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200 hover:border-slate-600'}`}
      >
        Case {i + 1}{c.drug_entities?.[0] ? ` — ${c.drug_entities[0]}` : ''}
      </button>
    ))}
  </div>
);

/* ─── Main Workspace Page ─── */
const AnalysisWorkspacePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [bundleData, setBundleData] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [activeCaseIdx, setActiveCaseIdx] = useState(0);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await reportApi.generateReport(id);
        
        if (data.cases && Array.isArray(data.cases) && data.cases.length > 1) {
           setBundleData(data);
           const firstCaseId = data.cases[0].analysis_id;
           const firstCaseData = await reportApi.generateReport(firstCaseId);
           setReport(firstCaseData);
           setActiveCaseIdx(0);
        } else {
           setBundleData(null);
           setReport(data);
        }
      } catch (e) {
        setError(e.response?.data?.detail || e.message || 'Failed to load analysis.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const handleCaseSelect = async (idx) => {
    if (!bundleData || !bundleData.cases[idx]) return;
    setActiveCaseIdx(idx);
    setLoading(true);
    setError(null);
    try {
      const caseId = bundleData.cases[idx].analysis_id;
      const caseData = await reportApi.generateReport(caseId);
      setReport(caseData);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Failed to load case report.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (format) => {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const downloadId = report?.analysis_id || id;
    window.open(`${base}/report/download/${downloadId}?format=${format}`, '_blank');
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="h-10 w-10 text-violet-500 animate-spin" />
        <p className="text-slate-400 text-sm font-medium">Loading Analysis Workspace...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <AlertCircle className="h-10 w-10 text-red-500" />
        <p className="text-slate-300 font-semibold">{error}</p>
        <button onClick={() => navigate('/')} className="text-violet-400 hover:text-violet-300 text-sm font-semibold flex items-center gap-1">
          <ArrowLeft className="h-4 w-4" /> Return to Dashboard
        </button>
      </div>
    );
  }

  if (!report) return null;

  const isMultiCase = bundleData !== null;
  const activeCase = report;
  const activeCaseId = report.analysis_id || id;

  const drug = activeCase?.drug_information?.product_active_ingredient
    || activeCase?.drug_entities?.[0]
    || activeCase?.suspected_drug_information?.drug_name
    || 'Unknown Drug';

  const alerts = activeCase?.regulatory_alerts || [];
  const missing = activeCase?.missing_information || activeCase?.missing_data || [];
  const timeline = activeCase?.timeline || [];
  const fdaSignal = activeCase?.fda_signal || {};
  const visualizations = activeCase?.visualizations || fdaSignal?.visualizations || {};

  const TABS = [
    { id: 'overview', label: 'Case Overview', icon: FileText },
    { id: 'timeline', label: 'ADR Timeline', icon: Clock },
    { id: 'fda', label: 'FDA Signals', icon: Activity },
    { id: 'alerts', label: `Regulatory Alerts ${alerts.length > 0 ? `(${alerts.length})` : ''}`, icon: ShieldCheck },
    { id: 'missing', label: `Missing Info ${missing.length > 0 ? `(${missing.length})` : ''}`, icon: AlertCircle },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <button onClick={() => navigate('/')} className="text-xs text-slate-500 hover:text-violet-400 flex items-center gap-1 mb-2 transition-colors">
            <ArrowLeft className="h-3.5 w-3.5" /> Back to Dashboard
          </button>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-xl font-bold text-white">{id.substring(0, 18)}...</h1>
            <Badge variant={report.status === 'completed' ? 'success' : 'warning'}>{report.status || 'completed'}</Badge>
            {isMultiCase && bundleData && <Badge variant="cyan">{bundleData.cases.length} cases</Badge>}
          </div>
          <p className="text-slate-400 text-sm mt-1">Primary: <span className="font-semibold text-slate-200 capitalize">{drug}</span></p>
        </div>
        <div className="flex flex-wrap gap-2">
          {[['PDF', 'pdf'], ['Excel', 'xlsx'], ['JSON', 'json']].map(([label, fmt]) => (
            <button key={fmt} onClick={() => handleDownload(fmt)} className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold rounded-xl transition-all">
              <Download className="h-3.5 w-3.5" /> {label}
            </button>
          ))}
          <button
            onClick={() => setActiveTab('alerts')}
            className="flex items-center gap-1.5 px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-xs font-bold rounded-xl shadow-lg shadow-violet-600/20 transition-all"
          >
            <ShieldCheck className="h-4 w-4" /> Verify Drug
          </button>
        </div>
      </div>

      {/* Multi-case tabs */}
      {isMultiCase && bundleData && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-4 w-4 text-cyan-400" />
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Multi-Patient Document — Select Case</span>
          </div>
          <CaseTabs cases={bundleData.cases} activeIdx={activeCaseIdx} onSelect={handleCaseSelect} />
          <div className="text-xs text-slate-500">Each case has separate report, AI context, and download.</div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-slate-800">
        <nav className="-mb-px flex gap-1 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all ${activeTab === tab.id ? 'border-violet-500 text-violet-400' : 'border-transparent text-slate-500 hover:text-slate-300 hover:border-slate-700'}`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="pb-24">
        {activeTab === 'overview' && (
           <div className="space-y-6">
              {activeCase.final_case_classification && (
                <div className="bg-gradient-to-r from-violet-900/40 to-slate-900 border border-violet-800/50 rounded-xl p-5 flex items-center justify-between">
                  <div>
                    <h3 className="text-xs font-bold text-violet-400 uppercase tracking-wider mb-1">Final Case Classification</h3>
                    <p className="text-lg font-bold text-white">{activeCase.final_case_classification}</p>
                  </div>
                  <ShieldCheck className="h-10 w-10 text-violet-500/50" />
                </div>
              )}
              
              {(activeCase.ai_generated_summary || activeCase.ai_generated_narrative_summary || activeCase.summary) && (
                <Panel title="AI Narrative Summary" icon={Brain}>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    {activeCase.ai_generated_summary || activeCase.ai_generated_narrative_summary || activeCase.summary}
                  </p>
                </Panel>
              )}

              <PatientCasePanel data={activeCase} />
              <DrugPanel data={activeCase} />
              <BatchReporterPanel data={activeCase} />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Panel title="Seriousness Assessment" icon={AlertTriangle}>
                  {(!activeCase.seriousness_assessment || Object.keys(activeCase.seriousness_assessment).length === 0) ? (
                    <p className="text-slate-500 text-sm italic">Not Specified</p>
                  ) : (
                    <div className="space-y-2">
                      {Object.entries(activeCase.seriousness_assessment).map(([k, v]) => (
                        <DataRow key={k} label={k} value={v} />
                      ))}
                    </div>
                  )}
                </Panel>
                <Panel title="Causality Assessment" icon={ShieldCheck}>
                  {(!activeCase.causality_assessment || Object.keys(activeCase.causality_assessment).length === 0) ? (
                     <p className="text-slate-500 text-sm italic">Not Specified</p>
                  ) : (
                    <div className="space-y-2">
                      {Object.entries(activeCase.causality_assessment).map(([k, v]) => (
                         <DataRow key={k} label={k} value={v} />
                      ))}
                    </div>
                  )}
                </Panel>
              </div>

              <InsightsPanel data={activeCase} />
              <VerificationSection data={activeCase} />
              <OCRMetadata ocr={activeCase.ocr_metadata} />
           </div>
        )}
        
        {activeTab === 'timeline' && <TimelinePanel timeline={timeline} />}
        {activeTab === 'fda' && <FDAPanel fdaData={fdaSignal} visualizations={visualizations} />}
        {activeTab === 'alerts' && <Panel title="Regulatory Alerts" icon={ShieldCheck}><RegAlertsPanel alerts={alerts} /></Panel>}
        {activeTab === 'missing' && <Panel title="Missing Information Review" icon={AlertCircle}><MissingInfoPanel missing={missing} /></Panel>}
        
        <MetadataFooter data={activeCase} id={id} />
      </div>

      {/* AI Chatbot — tied to the active case ID */}
      <ChatbotPanel analysisId={activeCaseId} />
    </div>
  );
};

export default AnalysisWorkspacePage;
