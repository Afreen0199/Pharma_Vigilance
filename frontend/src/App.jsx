import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/layout/Sidebar';
import Topbar from './components/layout/Topbar';

// Pages
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import CasesPage from './pages/CasesPage';
import UploadCasePage from './pages/UploadCasePage';
import AnalysisWorkspace from './pages/AnalysisWorkspace';
import FDAExplorer from './pages/FDAExplorer';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import Settings from './pages/Settings';

// Protected Route Guard
const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 text-slate-400">
        <div className="animate-pulse font-bold text-xs">VERIFYING ACCESS...</div>
      </div>
    );
  }
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Private Layout containing Sidebar and Topbar
const PrivateLayout = ({ children }) => {
  const location = useLocation();
  
  // Resolve Topbar title based on active path
  const getTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path === '/cases') return 'Safety Case Database';
    if (path === '/upload') return 'Case Ingestion & Upload';
    if (path.startsWith('/workspace/')) return 'Clinical Evaluation Workspace';
    if (path === '/fda-explorer') return 'FDA openFDA Explorer';
    if (path === '/kb-manage') return 'Regulatory Knowledge Base';
    if (path === '/settings') return 'Platform Settings';
    return 'Safety Copilot';
  };

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 font-sans transition-all duration-200">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar title={getTitle()} />
        <main className="flex-1 overflow-y-auto p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Auth Endpoint */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Clinical Workspace Routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <PrivateLayout>
                <Dashboard />
              </PrivateLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/cases" element={
            <ProtectedRoute>
              <PrivateLayout>
                <CasesPage />
              </PrivateLayout>
            </ProtectedRoute>
          } />

          <Route path="/upload" element={
            <ProtectedRoute>
              <PrivateLayout>
                <UploadCasePage />
              </PrivateLayout>
            </ProtectedRoute>
          } />

          <Route path="/workspace/:analysisId" element={
            <ProtectedRoute>
              <PrivateLayout>
                <AnalysisWorkspace />
              </PrivateLayout>
            </ProtectedRoute>
          } />

          <Route path="/fda-explorer" element={
            <ProtectedRoute>
              <PrivateLayout>
                <FDAExplorer />
              </PrivateLayout>
            </ProtectedRoute>
          } />

          <Route path="/kb-manage" element={
            <ProtectedRoute>
              <PrivateLayout>
                <KnowledgeBasePage />
              </PrivateLayout>
            </ProtectedRoute>
          } />

          <Route path="/settings" element={
            <ProtectedRoute>
              <PrivateLayout>
                <Settings />
              </PrivateLayout>
            </ProtectedRoute>
          } />

          {/* Fallback to Dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
