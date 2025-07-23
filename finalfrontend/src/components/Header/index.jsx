import { LogOut } from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Header.css';

const mockUser = {
  name: 'Agente Demo',
  email: 'agente@demo.com',
  avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=AG&backgroundColor=25D366&textColor=FFFFFF',
};

const Header = () => {
  const { selectedConversation } = useChat();
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  // Pages that should show conversation info
  const pagesWithConversations = ['/', '/dashboard', '/messages'];
  const shouldShowConversation = pagesWithConversations.includes(location.pathname) && selectedConversation;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="header">
      <div className="header-content">
        <div className="page-title">
          <h2>
            {location.pathname === '/settings' && 'Configurações'}
            {location.pathname === '/reports' && 'Relatórios'}
            {location.pathname === '/users' && 'Usuários'}
            {location.pathname === '/messages' && 'Mensagens'}
            {location.pathname === '/' && 'Dashboard'}
          </h2>
        </div>
        <div className="header-actions">
          <button className="logout-button" title="Sair" onClick={handleLogout}>
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Header; 