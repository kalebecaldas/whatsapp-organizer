import { useState } from 'react';
import { Search, MoreVertical, Filter, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { useChat } from '../context/ChatContext';
import './Sidebar.css';

const Sidebar = () => {
  const { conversations, selectedConversation, selectConversation, unreadCounts, refreshConversations, socketConnected } = useChat();
  const [searchTerm, setSearchTerm] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  console.log('📱 Sidebar renderizado - conversas:', conversations.length);
  console.log('📱 Conversas:', conversations);

  const filteredConversations = conversations.filter(conv =>
    conv.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.phone.includes(searchTerm)
  );

  console.log('🔍 Conversas filtradas:', filteredConversations.length);

  const formatTime = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) return `${minutes}m`;
    if (hours < 24) return `${hours}h`;
    return `${days}d`;
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await refreshConversations();
    setRefreshing(false);
  };

  return (
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <div className="profile-section">
          <div className="profile-avatar">
            <img src="https://api.dicebear.com/7.x/initials/svg?seed=AG&backgroundColor=25D366&textColor=FFFFFF" alt="Agent" />
          </div>
          <div className="profile-info">
            <h3>WhatsApp Organizer</h3>
            <div className="status-container">
              <span className={`status ${socketConnected ? 'online' : 'offline'}`}>
                {socketConnected ? 'Online' : 'Offline'}
              </span>
              <div className={`connection-indicator ${socketConnected ? 'connected' : 'disconnected'}`}>
                {socketConnected ? <Wifi size={12} /> : <WifiOff size={12} />}
              </div>
            </div>
          </div>
        </div>
        <div className="header-actions">
          <button 
            className="icon-button" 
            onClick={handleRefresh}
            disabled={refreshing}
            title="Atualizar conversas"
          >
            <RefreshCw size={20} className={refreshing ? 'spinning' : ''} />
          </button>
          <button className="icon-button">
            <Filter size={20} />
          </button>
          <button className="icon-button">
            <MoreVertical size={20} />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="search-container">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Pesquisar ou iniciar nova conversa"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="conversations-list">
        {filteredConversations.length > 0 ? (
          filteredConversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`conversation-item ${
                selectedConversation?.id === conversation.id ? 'active' : ''
              }`}
              onClick={() => selectConversation(conversation)}
            >
              <div className="conversation-avatar">
                <img src={conversation.avatar} alt={conversation.name} />
                {unreadCounts[conversation.id] > 0 && (
                  <div className="unread-badge">{unreadCounts[conversation.id]}</div>
                )}
              </div>
              <div className="conversation-content">
                <div className="conversation-header">
                  <h4 className="conversation-name">{conversation.name}</h4>
                  <span className="conversation-time">
                    {formatTime(conversation.timestamp)}
                  </span>
                </div>
                <div className="conversation-preview">
                  <p className="last-message">{conversation.lastMessage}</p>
                  {unreadCounts[conversation.id] > 0 && (
                    <div className="unread-indicator" />
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="no-conversations">
            <p>{searchTerm ? 'Nenhuma conversa encontrada' : 'Nenhuma conversa disponível'}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar; 