import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Layouts
import AuthLayout from './layouts/AuthLayout';
import DashboardLayout from './layouts/DashboardLayout';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import UploadCasePage from './pages/UploadCasePage';
import AnalysisWorkspacePage from './pages/AnalysisWorkspacePage';
import PreviousAnalysesPage from './pages/PreviousAnalysesPage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';

// Simple Auth Guard
const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  if (loading) return null;
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>

        {/* Protected Routes */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/upload" element={<UploadCasePage />} />
          <Route path="/kb" element={<KnowledgeBasePage />} />
          <Route path="/analyses" element={<PreviousAnalysesPage />} />
          <Route path="/analysis/:id" element={<AnalysisWorkspacePage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
