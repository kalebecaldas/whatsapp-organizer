import { useState, useEffect } from 'react';
import { LayoutDashboard, Users, Settings, MessageCircle, BarChart3 } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import './Menu.css';

const menuItems = [
  { key: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={24} />, path: '/' },
  { key: 'messages', label: 'Mensagens', icon: <MessageCircle size={24} />, path: '/messages' },
  { key: 'reports', label: 'Relatórios', icon: <BarChart3 size={24} />, path: '/reports' },
  { key: 'users', label: 'Usuários', icon: <Users size={24} />, path: '/users' },
  { key: 'settings', label: 'Configurações', icon: <Settings size={24} />, path: '/settings' },
];

const Menu = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [active, setActive] = useState('dashboard');

  useEffect(() => {
    // Determine active menu item based on current path
    const currentPath = location.pathname;
    const activeItem = menuItems.find(item => item.path === currentPath) || menuItems[0];
    setActive(activeItem.key);
  }, [location.pathname]);

  const handleMenuClick = (item) => {
    setActive(item.key);
    navigate(item.path);
  };

  return (
    <nav className="menu">
      <div className="menu-logo">
        <img src="/vite.svg" alt="Logo" />
      </div>
      <ul className="menu-list">
        {menuItems.map((item) => (
          <li
            key={item.key}
            className={`menu-item${active === item.key ? ' active' : ''}`}
            onClick={() => handleMenuClick(item)}
            title={item.label}
          >
            {item.icon}
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Menu; 