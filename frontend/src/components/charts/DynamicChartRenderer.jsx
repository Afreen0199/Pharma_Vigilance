import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';

const COLORS = [
  '#0271c7', // brand blue
  '#10B981', // emerald
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#06B6D4', // cyan
];

const DynamicChartRenderer = ({ chartData }) => {
  if (!chartData) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-400 dark:text-slate-600 font-medium text-xs">
        No dataset provided.
      </div>
    );
  }

  const { chart_type, title, data, x_axis, y_axis } = chartData;

  if (!data || data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-400 dark:text-slate-600 font-medium text-xs">
        Chart dataset is empty.
      </div>
    );
  }

  const renderTooltipContent = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900/95 text-white border border-slate-700/50 p-3 rounded-lg text-xs font-semibold shadow-xl">
          <p className="font-bold border-b border-slate-700 pb-1 mb-1.5 uppercase text-slate-300">{label}</p>
          {payload.map((p, idx) => (
            <p key={idx} className="flex justify-between gap-4">
              <span>{p.name}:</span>
              <span className="text-brand-300 font-extrabold">{p.value.toLocaleString()}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderChart = () => {
    switch (chart_type || 'bar') {
      case 'bar':
        // Determine keys dynamically based on dataset
        const xKey = Object.keys(data[0])[0]; // e.g. reaction, outcome
        const yKey = Object.keys(data[0])[1]; // e.g. count
        
        return (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
              <XAxis 
                dataKey={xKey} 
                stroke="#64748B" 
                fontSize={10} 
                tickLine={false} 
                axisLine={false}
                dy={8}
              />
              <YAxis 
                stroke="#64748B" 
                fontSize={10} 
                tickLine={false} 
                axisLine={false}
                dx={-8}
              />
              <Tooltip content={renderTooltipContent} cursor={{ fill: 'rgba(14, 144, 233, 0.04)' }} />
              <Bar dataKey={yKey} fill="#0e90e9" radius={[4, 4, 0, 0]} name="Cases">
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        const nameKey = Object.keys(data[0])[0]; // e.g. name, system
        const valKey = Object.keys(data[0])[1]; // e.g. value, count
        
        return (
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={4}
                dataKey={valKey}
                nameKey={nameKey}
              >
                {data.map((entry, index) => {
                  // Maintain red for serious and emerald for non-serious if naming matches
                  let fill = COLORS[index % COLORS.length];
                  if (entry.name === 'Serious') fill = '#EF4444';
                  if (entry.name === 'Non-Serious') fill = '#10B981';
                  return <Cell key={`cell-${index}`} fill={fill} />;
                })}
              </Pie>
              <Tooltip content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const dataObj = payload[0].payload;
                  return (
                    <div className="bg-slate-900/95 text-white border border-slate-700/50 p-3 rounded-lg text-xs font-semibold shadow-xl">
                      <p className="flex justify-between gap-4">
                        <span>{dataObj[nameKey]}:</span>
                        <span className="text-brand-300 font-extrabold">{dataObj[valKey].toLocaleString()} ({payload[0].percent ? (payload[0].percent * 100).toFixed(1) + '%' : ''})</span>
                      </p>
                    </div>
                  );
                }
                return null;
              }} />
              <Legend 
                verticalAlign="bottom" 
                height={36} 
                iconType="circle" 
                iconSize={8}
                formatter={(value) => <span className="text-xs font-semibold text-slate-600 dark:text-slate-400 capitalize">{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'line':
        const trendXKey = Object.keys(data[0])[0]; // e.g. year
        const trendYKey = Object.keys(data[0])[1]; // e.g. count
        
        return (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" className="dark:stroke-slate-800" />
              <XAxis 
                dataKey={trendXKey} 
                stroke="#64748B" 
                fontSize={10} 
                tickLine={false} 
                axisLine={false}
                dy={8}
              />
              <YAxis 
                stroke="#64748B" 
                fontSize={10} 
                tickLine={false} 
                axisLine={false}
                dx={-8}
              />
              <Tooltip content={renderTooltipContent} />
              <Line 
                type="monotone" 
                dataKey={trendYKey} 
                stroke="#0e90e9" 
                strokeWidth={3} 
                dot={{ r: 4, stroke: '#0e90e9', strokeWidth: 2, fill: '#fff' }}
                activeDot={{ r: 6 }}
                name="Cases"
              />
            </LineChart>
          </ResponsiveContainer>
        );

      default:
        return (
          <div className="h-48 flex items-center justify-center text-slate-400 dark:text-slate-600 font-medium text-xs">
            Unsupported chart configuration.
          </div>
        );
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-xl shadow-sm hover-scale flex flex-col justify-between">
      <div>
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 leading-tight">
          {title || 'Visual Report'}
        </h4>
        <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider mt-1 block">
          FDA SIGNAL DATABASE
        </span>
      </div>
      <div className="mt-6">
        {renderChart()}
      </div>
    </div>
  );
};

export default DynamicChartRenderer;
