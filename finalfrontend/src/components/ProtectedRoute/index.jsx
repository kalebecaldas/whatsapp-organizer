import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const ProtectedRoute = ({ children, requiredPermission = null, requiredAction = 'read' }) => {
  const { isAuthenticated, hasPermission, loading } = useAuth();
  const location = useLocation();

  // Mostrar loading enquanto verifica autenticação
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Carregando...
      </div>
    );
  }

  // Se não está autenticado, redirecionar para login
  if (!isAuthenticated()) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Se não há permissão específica requerida, permitir acesso
  if (!requiredPermission) {
    return children;
  }

  // Verificar se o usuário tem a permissão necessária
  if (!hasPermission(requiredPermission, requiredAction)) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        textAlign: 'center',
        padding: '20px'
      }}>
        <h2 style={{ color: '#dc2626', marginBottom: '16px' }}>
          Acesso Negado
        </h2>
        <p style={{ color: '#666', marginBottom: '24px' }}>
          Você não tem permissão para acessar esta página.
        </p>
        <button 
          onClick={() => window.history.back()}
          style={{
            padding: '12px 24px',
            backgroundColor: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Voltar
        </button>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute; 