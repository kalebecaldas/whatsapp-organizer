import { LogOut } from 'lucide-react';
import { useChat } from '../context/ChatContext';
import { useLocation } from 'react-router-dom';
import './Header.css';

const mockUser = {
  name: 'Agente Demo',
  email: 'agente@demo.com',
  avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=AG&backgroundColor=25D366&textColor=FFFFFF',
};

const Header = () => {
  const { selectedConversation } = useChat();
  const location = useLocation();
  
  // Pages that should show conversation info
  const pagesWithConversations = ['/', '/dashboard', '/messages'];
  const shouldShowConversation = pagesWithConversations.includes(location.pathname) && selectedConversation;

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
        <div className="user-info">
          <img className="user-avatar" src={mockUser.avatar} alt={mockUser.name} />
          <div className="user-details">
            <span className="user-name">{mockUser.name}</span>
            <span className="user-email">{mockUser.email}</span>
          </div>
          <button className="logout-button" title="Sair">
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Header; 