import { useState, useRef } from 'react';
import { Search, MoreVertical, Filter, RefreshCw, Wifi, WifiOff, Bot, Users, MessageSquare, X } from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import GlobalQueue from '../Chat/BotQueue/index';
import './Sidebar.css';

const Sidebar = () => {
  const { conversations, selectedConversation, selectConversation, unreadCounts, refreshConversations, socketConnected } = useChat();
  const [searchTerm, setSearchTerm] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [filterType, setFilterType] = useState('all'); // Mudança: 'all' como padrão
  const [showGlobalQueue, setShowGlobalQueue] = useState(false); // Estado para mostrar fila global
  const dropdownRef = useRef(null);

  console.log('📱 Sidebar renderizado - conversas:', conversations.length);
  console.log('📱 Conversas:', conversations);

  // Filtrar conversas baseado no tipo
  const getFilteredConversations = () => {
    let filtered = conversations;
    
    // Filtrar por tipo (bot vs humano)
    if (filterType === 'bot') {
      // Conversas do bot: NÃO transferidas para humano
      filtered = conversations.filter(conv => !conv.transferido_humano);
    } else if (filterType === 'human') {
      // Conversas de atendimento humano: transferidas para humano E atribuídas a alguém
      filtered = conversations.filter(conv => conv.transferido_humano && conv.atribuido_para);
    } else if (filterType === 'all') {
      // Todas as conversas
      filtered = conversations;
    }
    
    // Filtrar por termo de busca
    return filtered.filter(conv =>
      conv.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      conv.phone.includes(searchTerm)
    );
  };

  const filteredConversations = getFilteredConversations();

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



  const getFilterStats = () => {
    // Conversas do bot: NÃO transferidas para humano
    const botCount = conversations.filter(conv => !conv.transferido_humano).length;
    
    // Conversas de atendimento humano: transferidas E atribuídas a alguém
    const humanCount = conversations.filter(conv => conv.transferido_humano && conv.atribuido_para).length;
    
    // Conversas na fila global: transferidas mas NÃO atribuídas
    const globalQueueCount = conversations.filter(conv => 
      conv.transferido_humano && !conv.atribuido_para
    ).length;
    
    return { botCount, humanCount, globalQueueCount };
  };

  const stats = getFilterStats();
  
  // Log apenas quando as conversas mudarem
  console.log('📊 Estatísticas de filtro:', {
    total: conversations.length,
    bot: stats.botCount,
    human: stats.humanCount,
    globalQueue: stats.globalQueueCount,
    conversas: conversations.map(c => ({
      id: c.id,
      transferido_humano: c.transferido_humano,
      atribuido_para: c.atribuido_para
    }))
  });

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
        {/* Removidos todos os botões de ação do header */}
      </div>

      {/* Search */}
      <div className="search-container">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Pesquisar conversas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button
              className="clear-search"
              onClick={() => setSearchTerm('')}
              title="Limpar pesquisa"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Filter Container */}
      <div className="filter-container">
        <div className="filter-row">
          <select 
            ref={dropdownRef}
            value={filterType} 
            onChange={(e) => setFilterType(e.target.value)}
            className="filter-dropdown"
          >
            <option value="all">
              📋 Todas as conversas ({conversations.length})
            </option>
            <option value="human">
              👥 Atendimento Humano ({stats.humanCount})
            </option>
            <option value="bot">
              🤖 Bot ({stats.botCount})
            </option>
          </select>
          
          {/* Global Queue Button */}
          <button 
            className={`global-queue-button ${showGlobalQueue ? 'active' : ''}`}
            onClick={() => setShowGlobalQueue(!showGlobalQueue)}
            title="Fila Global de Conversas"
          >
            <Users size={16} />
            <span className="global-queue-count">{stats.globalQueueCount}</span>
          </button>
        </div>
      </div>

      {/* Global Queue Modal */}
      <GlobalQueue 
        isVisible={showGlobalQueue}
        onClose={() => setShowGlobalQueue(false)}
        onAssignConversation={(conversationId) => {
          console.log('Conversa atribuída:', conversationId);
          setShowGlobalQueue(false);
          // Aqui você pode adicionar lógica para atualizar a lista de conversas
        }}
      />

      {/* Conversations List */}
      <div className="conversations-list">
        {filteredConversations.length > 0 ? (
          filteredConversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`conversation-item ${
                selectedConversation?.id === conversation.id ? 'active' : ''
              } ${conversation.transferido_humano ? 'transferred' : ''}`}
              onClick={() => selectConversation(conversation)}
            >
              <div className="conversation-avatar">
                <img src={conversation.avatar} alt={conversation.name} />
                {unreadCounts[conversation.id] > 0 && (
                  <div className="unread-badge">{unreadCounts[conversation.id]}</div>
                )}
                {conversation.transferido_humano && (
                  <div className="transfer-indicator" title="Transferido para atendimento humano">
                    <Users size={12} />
                  </div>
                )}
              </div>
              <div className="conversation-content">
                <div className="conversation-header">
                  <h4 className="conversation-name">
                    {conversation.name}
                    {conversation.transferido_humano && (
                      <span className="transfer-badge">👥</span>
                    )}
                  </h4>
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