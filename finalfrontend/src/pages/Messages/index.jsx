import { useEffect, useState } from 'react';
import ChatWindow from '../../components/Chat/ChatWindow';
import MessageInput from '../../components/Chat/MessageInput';
import GlobalQueue from '../../components/Chat/BotQueue';
import { useChat } from '../../context/ChatContext';
import { Search, Filter, Users, MessageSquare, X, Menu } from 'lucide-react';
import './Messages.css';

const Messages = () => {
  const { conversations, selectedConversation, selectConversation, unreadCounts, refreshConversations, socketConnected } = useChat();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('human');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showGlobalQueue, setShowGlobalQueue] = useState(false);

  // Recarregar conversas quando a página for acessada
  useEffect(() => {
    console.log('📱 Página Messages carregada - recarregando conversas...');
    refreshConversations();
  }, []);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Calcular conversas na fila global (transferidas mas não atribuídas)
  const globalQueueCount = conversations.filter(conv => 
    conv.transferido_humano && !conv.atribuido_para
  ).length;

  // Log para debug do contador
  console.log('📊 Contador da fila global:', globalQueueCount, 'de', conversations.length, 'conversas');
  console.log('📊 Conversas transferidas:', conversations.filter(c => c.transferido_humano).length);
  console.log('📊 Conversas atribuídas:', conversations.filter(c => c.atribuido_para).length);

  const handleGlobalQueueClick = () => {
    console.log('🔄 Botão da fila global clicado! Contador:', globalQueueCount);
    console.log('📊 Conversas na fila global:', conversations.filter(conv => 
      conv.transferido_humano && !conv.atribuido_para
    ));
    setShowGlobalQueue(true);
  };

  // Função para pegar conversa da fila global
  const [assigningId, setAssigningId] = useState(null);
  const handleAssignConversation = async (conversationId) => {
    setAssigningId(conversationId);
    try {
      const response = await fetch('/api/assign-conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversationId,
          userId: 'current-user-id'
        })
      });
      if (response.ok) {
        console.log('✅ Conversa atribuída:', conversationId);
        await refreshConversations();
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Erro ao atribuir conversa:', response.status, response.statusText, errorData);
      }
    } catch (error) {
      console.error('❌ Erro de rede ao atribuir conversa:', error);
    } finally {
      setAssigningId(null);
    }
  };

  const getFilteredConversations = () => {
    let filtered = conversations;
    
    if (filterType === 'bot') {
      filtered = conversations.filter(conv => !conv.transferido_humano);
    } else if (filterType === 'human') {
      filtered = conversations.filter(conv => conv.transferido_humano && conv.atribuido_para);
    } else if (filterType === 'fila-global') {
      filtered = conversations.filter(conv => conv.transferido_humano && !conv.atribuido_para);
    }
    
    return filtered.filter(conv =>
      conv.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      conv.phone.includes(searchTerm)
    );
  };

  const filteredConversations = getFilteredConversations();

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

  return (
    <div className="messages-page">
      {/* Sidebar Lateral */}
      <div className={`messages-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        {/* Header da Sidebar */}
        <div className="sidebar-header">
          <div className="sidebar-title">
            <h3>Conversas</h3>
            <div className="connection-status">
              <div className={`status-dot ${socketConnected ? 'connected' : 'disconnected'}`} />
              <span>{socketConnected ? 'Conectado' : 'Desconectado'}</span>
            </div>
          </div>
          <button className="close-sidebar-btn" onClick={toggleSidebar} aria-label="Fechar lista de conversas">
            <X size={20} />
          </button>
        </div>

        {/* Barra de Pesquisa */}
        <div className="search-section">
          <div className="search-box">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              placeholder="Pesquisar conversas..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {searchTerm && (
              <button className="clear-search" onClick={() => setSearchTerm('')} aria-label="Limpar busca">
                <X size={14} />
              </button>
            )}
          </div>
        </div>

        {/* Filtros */}
        <div className="filters-section">
          <div className="filter-row">
            <select 
              value={filterType} 
              onChange={(e) => setFilterType(e.target.value)}
              className="filter-dropdown"
            >
              <option value="bot">Bot ({conversations.filter(c => !c.transferido_humano).length})</option>
              <option value="human">Humano ({conversations.filter(c => c.transferido_humano && c.atribuido_para).length})</option>
              <option value="fila-global">Fila Global ({conversations.filter(c => c.transferido_humano && !c.atribuido_para).length})</option>
            </select>
            <button 
              className={`queue-button ${globalQueueCount > 0 ? 'has-items' : ''}`} 
              aria-label="Fila global de conversas" 
              onClick={handleGlobalQueueClick}
            >
              <Users size={16} />
              <span className="queue-count">{globalQueueCount}</span>
            </button>
          </div>
        </div>

        {/* Lista de Conversas */}
        <div className="conversations-list">
          {filteredConversations.length === 0 ? (
            <div className="no-conversations">
              <MessageSquare size={48} />
              <p>Nenhuma conversa encontrada</p>
            </div>
          ) : (
            filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`conversation-item ${selectedConversation?.id === conversation.id ? 'active' : ''} ${conversation.transferido_humano ? 'transferred' : ''}`}
                onClick={() => selectConversation(conversation)}
              >
                <div className="conversation-avatar">
                  <div className="avatar">
                    {conversation.name.charAt(0).toUpperCase()}
                  </div>
                  {unreadCounts[conversation.id] > 0 && (
                    <div className="unread-badge">
                      {unreadCounts[conversation.id]}
                    </div>
                  )}
                </div>
                <div className="conversation-content">
                  <div className="conversation-header">
                    <span className="conversation-name">{conversation.name}</span>
                    <span className="conversation-time">{formatTime(new Date(conversation.lastMessageTime || Date.now()))}</span>
                  </div>
                  <div className="conversation-preview">
                    <span className="last-message">{conversation.lastMessage || 'Nenhuma mensagem'}</span>
                    {unreadCounts[conversation.id] > 0 && (
                      <div className="unread-indicator" />
                    )}
                  </div>
                  {/* Area indicator na lista */}
                  {(() => {
                    if (!conversation.transferido_humano) {
                      return <span className="area-indicator bot">🤖 Bot</span>;
                    } else if (conversation.transferido_humano && conversation.atribuido_para) {
                      return <span className="area-indicator human">👥 Humano</span>;
                    } else if (conversation.transferido_humano && !conversation.atribuido_para) {
                      return <span className="area-indicator fila-global">🟠 Fila Global</span>;
                    }
                    return null;
                  })()}
                  {/* Botão Pegar só para fila global */}
                  {filterType === 'fila-global' && conversation.transferido_humano && !conversation.atribuido_para && (
                    <button
                      className={`assign-button${assigningId === conversation.id ? ' loading' : ''}`}
                      onClick={e => { e.stopPropagation(); handleAssignConversation(conversation.id); }}
                      title="Pegar conversa"
                      disabled={assigningId === conversation.id}
                    >
                      {assigningId === conversation.id ? 'Pegando...' : (<><MessageSquare size={16} /> Pegar</>)}
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Botão Toggle Sidebar */}
      {!sidebarOpen && (
        <button className="open-sidebar-btn" onClick={toggleSidebar} aria-label="Abrir lista de conversas">
          <Menu size={20} />
        </button>
      )}

      {/* Área de Chat */}
      <div className="chat-area">
        {selectedConversation ? (
          <>
            <ChatWindow />
            <MessageInput />
          </>
        ) : (
          <div className="empty-chat">
            <MessageSquare size={64} />
            <h3>Nenhuma conversa selecionada</h3>
            <p>Escolha uma conversa na lista para começar a conversar</p>
          </div>
        )}
      </div>

      {/* Overlay para mobile */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={toggleSidebar} />
      )}

      {/* Modal da Fila Global */}
      <GlobalQueue 
        isVisible={showGlobalQueue}
        onClose={() => setShowGlobalQueue(false)}
        onAssignConversation={(conversationId) => {
          console.log('🔄 Conversa atribuída:', conversationId);
          setShowGlobalQueue(false);
          refreshConversations();
        }}
      />
    </div>
  );
};

export default Messages; 