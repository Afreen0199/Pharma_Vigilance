import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, Eye } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Skeleton from '../components/ui/Skeleton';

const PreviousAnalysesPage = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  useEffect(() => {
    setTimeout(() => {
      setAnalyses([
        { id: 'REP-2026-001', date: '2026-06-17', drug: 'Aspirin', adr: 'Nausea, Bleeding', status: 'completed' },
        { id: 'REP-2026-002', date: '2026-06-16', drug: 'Lisinopril', adr: 'Cough', status: 'processing' },
        { id: 'REP-2026-003', date: '2026-06-15', drug: 'Metformin', adr: 'Lactic Acidosis', status: 'failed' },
        { id: 'REP-2026-004', date: '2026-06-14', drug: 'Atorvastatin', adr: 'Muscle Pain', status: 'completed' },
        { id: 'REP-2026-005', date: '2026-06-10', drug: 'Amoxicillin', adr: 'Rash', status: 'completed' },
      ]);
      setIsLoading(false);
    }, 1000);
  }, []);

  const filteredAnalyses = analyses.filter(a => {
    const matchesSearch = a.id.toLowerCase().includes(search.toLowerCase()) || 
                          a.drug.toLowerCase().includes(search.toLowerCase()) ||
                          a.adr.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter ? a.status === statusFilter : true;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Previous Analyses</h1>
        <p className="text-slate-500 mt-1">Review and search through all historical pharmacovigilance reports.</p>
      </div>

      <Card>
        <CardHeader className="pb-4">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="relative w-full sm:w-96">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search by ID, Drug, or ADR..."
                className="w-full pl-10 pr-4 py-2 rounded-md border border-slate-300 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex gap-2 w-full sm:w-auto">
              <div className="relative w-full sm:w-auto">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <select
                  className="w-full pl-10 pr-8 py-2 rounded-md border border-slate-300 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm appearance-none bg-white"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="completed">Completed</option>
                  <option value="processing">Processing</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-y border-slate-200">
                <tr>
                  <th className="px-6 py-4 font-medium">Analysis ID</th>
                  <th className="px-6 py-4 font-medium">Date</th>
                  <th className="px-6 py-4 font-medium">Primary Drug</th>
                  <th className="px-6 py-4 font-medium">Key ADRs</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {isLoading ? (
                  Array(5).fill(0).map((_, i) => (
                    <tr key={i}>
                      <td className="px-6 py-4"><Skeleton className="h-4 w-24" /></td>
                      <td className="px-6 py-4"><Skeleton className="h-4 w-20" /></td>
                      <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                      <td className="px-6 py-4"><Skeleton className="h-4 w-40" /></td>
                      <td className="px-6 py-4"><Skeleton className="h-6 w-20 rounded-full" /></td>
                      <td className="px-6 py-4 text-right"><Skeleton className="h-8 w-20 ml-auto" /></td>
                    </tr>
                  ))
                ) : filteredAnalyses.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-slate-500">
                      No analyses found matching your filters.
                    </td>
                  </tr>
                ) : (
                  filteredAnalyses.map((row) => (
                    <tr key={row.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-900">{row.id}</td>
                      <td className="px-6 py-4 text-slate-500">{row.date}</td>
                      <td className="px-6 py-4 text-slate-700">{row.drug}</td>
                      <td className="px-6 py-4 text-slate-600 truncate max-w-xs">{row.adr}</td>
                      <td className="px-6 py-4">
                        <Badge 
                          variant={row.status === 'completed' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'}
                        >
                          {row.status}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Button variant="outline" size="sm" onClick={() => navigate(`/analysis/${row.id}`)} className="gap-2">
                          <Eye className="h-4 w-4" /> Open Report
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PreviousAnalysesPage;
