import React from 'react';
import { 
  Calendar, 
  Pill, 
  AlertTriangle, 
  Activity, 
  CheckCircle,
  HelpCircle,
  FileClock
} from 'lucide-react';

const TimelineUI = ({ timeline }) => {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 rounded-xl text-center space-y-4">
        <FileClock className="h-12 w-12 text-slate-350 dark:text-slate-700 mx-auto" />
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">No Chronology Log Available</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 font-semibold leading-relaxed">
          The ingested case narrative does not contain sufficient dates or sequential clinical markers to compile a chronological safety timeline.
        </p>
      </div>
    );
  }

  // Helper to determine icon and color dynamically
  const getEventIconAndColor = (item) => {
    const desc = String(item.event_description || item.description || '').toLowerCase();
    const type = String(item.event_type || item.type || '').toLowerCase();

    if (type.includes('start') || type.includes('initiate') || desc.includes('started') || desc.includes('began')) {
      return {
        icon: Pill,
        color: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-250 dark:border-emerald-900/40',
        lineColor: 'border-emerald-200 dark:border-emerald-900/30'
      };
    }
    
    if (type.includes('hospital') || type.includes('icu') || desc.includes('admitted') || desc.includes('hospital') || desc.includes('presented to')) {
      return {
        icon: Activity,
        color: 'text-red-650 bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-900/40',
        lineColor: 'border-red-200 dark:border-red-900/30'
      };
    }

    if (type.includes('onset') || type.includes('event') || type.includes('reaction') || desc.includes('developed') || desc.includes('experienced') || desc.includes('symptom')) {
      return {
        icon: AlertTriangle,
        color: 'text-amber-600 bg-amber-50 dark:bg-amber-950/40 border-amber-250 dark:border-amber-900/40',
        lineColor: 'border-amber-200 dark:border-amber-900/30'
      };
    }

    if (type.includes('outcome') || type.includes('recovery') || desc.includes('recovered') || desc.includes('discharged') || desc.includes('resolved') || desc.includes('improved')) {
      return {
        icon: CheckCircle,
        color: 'text-brand-650 bg-brand-50 dark:bg-brand-950/40 border-brand-200 dark:border-brand-900/40',
        lineColor: 'border-brand-200 dark:border-brand-900/30'
      };
    }

    // Default fallback
    return {
      icon: Calendar,
      color: 'text-slate-600 bg-slate-50 dark:bg-slate-805 border-slate-200 dark:border-slate-800',
      lineColor: 'border-slate-200 dark:border-slate-800'
    };
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-xl shadow-sm space-y-8 select-none">
      <div>
        <h3 className="text-sm font-bold text-slate-855 dark:text-white uppercase tracking-wider">
          Patient Adverse Event Chronology
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Step-by-step chronology mapping therapy duration and adverse drug reaction onset.
        </p>
      </div>

      <div className="relative pl-8 border-l border-slate-200 dark:border-slate-800 space-y-6 ml-4">
        {timeline.map((item, idx) => {
          const config = getEventIconAndColor(item);
          const Icon = config.icon;
          
          return (
            <div key={idx} className="relative animate-fadeIn">
              {/* Timeline dot connector */}
              <span className={`absolute -left-12 top-0.5 p-2 rounded-full border cursor-default flex items-center justify-center transition-all ${config.color} hover:scale-110 shadow-sm`}>
                <Icon className="h-4 w-4" />
              </span>

              <div className="space-y-1 bg-slate-50 dark:bg-slate-850/45 p-4 rounded-xl border border-slate-200/50 dark:border-slate-800/80 hover-scale">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                  <span className="text-[10px] text-brand-600 dark:text-brand-400 font-extrabold uppercase tracking-widest">
                    {item.event_type || item.type || 'Clinical Event'}
                  </span>
                  <span className="text-xs font-bold text-slate-500 dark:text-slate-400 flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>{item.event_date || item.date || 'Not Specified'}</span>
                  </span>
                </div>
                
                <p className="text-xs font-semibold text-slate-750 dark:text-slate-350 leading-relaxed pt-1">
                  {item.event_description || item.description || 'No event descriptions compiled.'}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TimelineUI;
