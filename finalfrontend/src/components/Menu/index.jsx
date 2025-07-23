import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  MessageSquare, 
  BarChart3, 
  Users, 
  Settings, 
  LogOut,
  User,
  ChevronDown
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './Menu.css';

const Menu = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, hasPermission, canAccess } = useAuth();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
      path: '/dashboard',
      permission: 'dashboard'
    },
    {
      id: 'messages',
      label: 'Mensagens',
      icon: MessageSquare,
      path: '/messages',
      permission: 'messages'
    },
    {
      id: 'reports',
      label: 'Relatórios',
      icon: BarChart3,
      path: '/reports',
      permission: 'reports'
    },
    {
      id: 'users',
      label: 'Usuários',
      icon: Users,
      path: '/users',
      permission: 'users'
    },
    {
      id: 'settings',
      label: 'Configurações',
      icon: Settings,
      path: '/settings',
      permission: 'settings'
    }
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleUserMenuToggle = () => {
    setIsUserMenuOpen(!isUserMenuOpen);
  };

  const filteredMenuItems = menuItems.filter(item => canAccess(item.permission));

  return (
    <div className="menu-container">
      <div className="menu-header">
        <h2>WhatsApp Organizer</h2>
      </div>

      <nav className="menu-nav">
        <ul className="menu-list">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.id} className={`menu-item ${isActive ? 'active' : ''}`}>
                <button
                  className="menu-button"
                  onClick={() => navigate(item.path)}
                >
                  <Icon size={20} strokeWidth={2} />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="menu-footer">
        <div className="user-info">
          <button 
            className="user-menu-button"
            onClick={handleUserMenuToggle}
          >
            <div className="user-avatar">
              <User size={20} strokeWidth={2} />
            </div>
            <div className="user-details">
              <span className="user-name">{user?.name || 'Usuário'}</span>
              <span className="user-role">
                {user?.role === 'admin' && 'Administrador'}
                {user?.role === 'supervisor' && 'Supervisor'}
                {user?.role === 'attendant' && 'Atendente'}
              </span>
            </div>
            <ChevronDown 
              size={16} 
              strokeWidth={2} 
              className={`chevron ${isUserMenuOpen ? 'rotated' : ''}`}
            />
          </button>

          {isUserMenuOpen && (
            <div className="user-dropdown">
              <div className="dropdown-item">
                <User size={16} strokeWidth={2} />
                <span>Perfil</span>
              </div>
              <div className="dropdown-divider"></div>
              <button className="dropdown-item logout-button" onClick={handleLogout}>
                <LogOut size={16} strokeWidth={2} />
                <span>Sair</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Menu; 