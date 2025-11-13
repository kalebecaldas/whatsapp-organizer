import { useState } from 'react';
import { useInternalChat } from '../../context/InternalChatContext';
import { MessageSquare, Plus, Users, Search } from 'lucide-react';
import './InternalChat.css';

const InternalChat = () => {
  const {
    conversations,
    selectedConversation,
    messages,
    selectConversation,
    sendMessage,
    createConversation,
    loading
  } = useInternalChat();

  const [messageText, setMessageText] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newConversationName, setNewConversationName] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageText.trim() || !selectedConversation) return;

    await sendMessage(selectedConversation.id, messageText.trim());
    setMessageText('');
  };

  const handleCreateConversation = async () => {
    if (!newConversationName.trim()) return;

    await createConversation(newConversationName.trim(), 'group', [], '');
    setNewConversationName('');
    setShowCreateModal(false);
  };

  const filteredConversations = conversations.filter(conv =>
    conv.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const currentMessages = selectedConversation
    ? (messages[selectedConversation.id] || [])
    : [];

  return (
    <div className="internal-chat-page">
      {/* Sidebar */}
      <div className="internal-chat-sidebar">
        <div className="sidebar-header">
          <h2>Conversas Internas</h2>
          <button
            className="create-conversation-btn"
            onClick={() => setShowCreateModal(true)}
            title="Criar nova conversa"
          >
            <Plus size={20} />
          </button>
        </div>

        <div className="sidebar-search">
          <Search size={16} />
          <input
            type="text"
            placeholder="Pesquisar conversas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="conversations-list">
          {loading ? (
            <div className="loading">Carregando...</div>
          ) : filteredConversations.length === 0 ? (
            <div className="empty-state">
              <MessageSquare size={48} />
              <p>Nenhuma conversa encontrada</p>
            </div>
          ) : (
            filteredConversations.map((conv) => (
              <div
                key={conv.id}
                className={`conversation-item ${
                  selectedConversation?.id === conv.id ? 'active' : ''
                }`}
                onClick={() => selectConversation(conv)}
              >
                <div className="conversation-avatar">
                  {conv.type === 'group' ? (
                    <Users size={20} />
                  ) : (
                    <MessageSquare size={20} />
                  )}
                </div>
                <div className="conversation-info">
                  <div className="conversation-name">{conv.name}</div>
                  <div className="conversation-preview">
                    {conv.last_message || 'Nenhuma mensagem'}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="internal-chat-area">
        {selectedConversation ? (
          <>
            <div className="chat-header">
              <h3>{selectedConversation.name}</h3>
              <span className="conversation-type">
                {selectedConversation.type === 'group' ? 'Grupo' : 'Direta'}
              </span>
            </div>

            <div className="messages-container">
              {currentMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`message ${
                    msg.sender_id === 'current-user' ? 'sent' : 'received'
                  }`}
                >
                  <div className="message-content">
                    <p>{msg.content}</p>
                    <span className="message-time">
                      {new Date(msg.timestamp).toLocaleTimeString('pt-BR', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <form className="message-input-form" onSubmit={handleSendMessage}>
              <input
                type="text"
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                placeholder="Digite uma mensagem..."
                className="message-input"
              />
              <button type="submit" className="send-button">
                Enviar
              </button>
            </form>
          </>
        ) : (
          <div className="empty-chat">
            <MessageSquare size={64} />
            <h3>Nenhuma conversa selecionada</h3>
            <p>Escolha uma conversa ou crie uma nova</p>
          </div>
        )}
      </div>

      {/* Create Conversation Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Criar Nova Conversa</h3>
            <input
              type="text"
              value={newConversationName}
              onChange={(e) => setNewConversationName(e.target.value)}
              placeholder="Nome da conversa"
              className="modal-input"
            />
            <div className="modal-actions">
              <button onClick={() => setShowCreateModal(false)}>Cancelar</button>
              <button onClick={handleCreateConversation}>Criar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InternalChat;
