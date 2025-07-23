import React from 'react';
import { useAuth } from '../../context/AuthContext';
import Menu from '../Menu';
import './Layout.css';

const Layout = ({ children }) => {
  const { isAuthenticated } = useAuth();

  // Se não está autenticado, não renderizar o layout
  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="layout">
      <Menu />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout; 