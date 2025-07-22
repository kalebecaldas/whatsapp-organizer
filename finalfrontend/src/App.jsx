import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Messages from './pages/Messages';
import Settings from './pages/Settings';
import Reports from './pages/Reports';
import Login from './pages/Login';
import Users from './pages/Users';
import Layout from './components/Layout';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';
import BotTest from './pages/BotTest';

// Componente para rotas protegidas
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div>Carregando...</div>;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Componente para rotas públicas (como login)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div>Carregando...</div>;
  }
  
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Rotas públicas */}
      <Route path="/login" element={
        <PublicRoute>
          <Login />
        </PublicRoute>
      } />
      
      {/* Rotas protegidas */}
      <Route path="/" element={
        <ProtectedRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/messages" element={
        <ProtectedRoute>
          <Layout>
            <Messages />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/reports" element={
        <ProtectedRoute>
          <Layout>
            <Reports />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/users" element={
        <ProtectedRoute>
          <Layout>
            <Users />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/settings" element={
        <ProtectedRoute>
          <Layout>
            <Settings />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/bottest" element={
        <ProtectedRoute>
          <Layout>
            <BotTest />
          </Layout>
        </ProtectedRoute>
      } />
    </Routes>
  );
}

function App() {
  console.log('🚀 App.jsx renderizado');
  
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
