import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

const FDASignalsTab = ({ fdaData }) => {
  if (!fdaData) {
    return (
      <Card className="mt-6">
        <CardContent className="p-12 text-center text-slate-500">
          No FDA signal data available.
        </CardContent>
      </Card>
    );
  }

  // Map actual backend keys to the expected charting components
  const topReactions = fdaData.top_reactions_chart || fdaData.topReactions || [];
  const reportingTrend = fdaData.signal_trend_chart || fdaData.reportingTrend || [];
  const outcomeDist = fdaData.outcome_distribution_chart || fdaData.outcomeDistribution || [];
  const organSystem = fdaData.organ_system_chart || fdaData.organSystemImpact || [];
  const seriousnessDist = fdaData.seriousness_distribution_chart || fdaData.seriousnessDistribution || [];

  return (
    <div className="space-y-6 mt-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Top Reactions Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Top Reactions</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            {topReactions.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topReactions} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={100} tick={{fontSize: 12}} />
                  <RechartsTooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <div className="h-full flex items-center justify-center text-slate-500">No data</div>}
          </CardContent>
        </Card>

        {/* Reporting Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Reporting Trend</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            {reportingTrend.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={reportingTrend} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : <div className="h-full flex items-center justify-center text-slate-500">No data</div>}
          </CardContent>
        </Card>

        {/* Outcome Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Outcome Distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-80 flex justify-center">
            {outcomeDist.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={outcomeDist}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    fill="#8884d8"
                    paddingAngle={2}
                    dataKey="value"
                    label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {outcomeDist.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : <div className="h-full flex items-center justify-center text-slate-500">No data</div>}
          </CardContent>
        </Card>

        {/* Seriousness Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Seriousness Distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            {seriousnessDist.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={seriousnessDist} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <div className="h-full flex items-center justify-center text-slate-500">No data</div>}
          </CardContent>
        </Card>

      </div>
      
      {/* Organ System Impact */}
      <Card>
        <CardHeader>
          <CardTitle>Organ System Impact</CardTitle>
        </CardHeader>
        <CardContent className="h-96">
          {organSystem.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={organSystem} margin={{ top: 5, right: 30, left: 40, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} interval={0} tick={{fontSize: 11}} />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="h-full flex items-center justify-center text-slate-500">No data</div>}
        </CardContent>
      </Card>
    </div>
  );
};

export default FDASignalsTab;
