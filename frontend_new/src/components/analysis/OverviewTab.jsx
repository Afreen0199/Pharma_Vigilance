import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';

const Section = ({ title, data }) => {
  if (!data || (Array.isArray(data) && data.length === 0) || (typeof data === 'object' && Object.keys(data).length === 0)) {
    return null;
  }
  
  // Format the title from camelCase or snake_case to Title Case
  const formattedTitle = title
    .replace(/([A-Z])/g, ' $1')
    .replace(/_/g, ' ')
    .replace(/^./, str => str.toUpperCase());

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>{formattedTitle}</CardTitle>
      </CardHeader>
      <CardContent>
        {typeof data === 'string' || typeof data === 'number' ? (
          <p className="text-slate-700 whitespace-pre-wrap">{data}</p>
        ) : Array.isArray(data) ? (
          <ul className="list-disc pl-5 space-y-1">
            {data.map((item, i) => (
              <li key={i} className="text-slate-700 break-words">
                {typeof item === 'object' ? JSON.stringify(item, null, 2) : item}
              </li>
            ))}
          </ul>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data).map(([key, value]) => {
              if (value === null || value === undefined) return null;
              return (
                <div key={key} className="break-words border-b border-slate-100 pb-2">
                  <dt className="text-xs font-bold text-slate-500 uppercase tracking-wider">{key.replace(/_/g, ' ')}</dt>
                  <dd className="mt-1 text-sm text-slate-900 font-medium">
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </dd>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const OverviewTab = ({ reportData }) => {
  if (!reportData || Object.keys(reportData).length === 0) {
    return <div className="text-slate-500 italic mt-6">No data available for this report.</div>;
  }

  // Filter out internal/visual fields that shouldn't be rendered as simple blocks
  const excludedKeys = ['timeline', 'visualizations', 'fda_signal', 'status', 'analysis_id', 'created_at'];
  
  const sections = Object.entries(reportData).filter(([key]) => !excludedKeys.includes(key));

  // Split into two columns for better UI layout
  const midPoint = Math.ceil(sections.length / 2);
  const leftCol = sections.slice(0, midPoint);
  const rightCol = sections.slice(midPoint);

  return (
    <div className="space-y-6 mt-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <div className="space-y-6">
          {leftCol.map(([key, value]) => (
            <Section key={key} title={key} data={value} />
          ))}
        </div>
        <div className="space-y-6">
          {rightCol.map(([key, value]) => (
            <Section key={key} title={key} data={value} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default OverviewTab;
