import React, { useState } from 'react';
import { Users, Clock, MessageSquare } from 'lucide-react';
import { useChat } from '../../../context/ChatContext';
import './BotQueue.css';

const GlobalQueue = ({ isVisible, onClose, onAssignConversation }) => {
  const { conversations, refreshConversations } = useChat();
  const [loading, setLoading] = useState(false);
  const [removingId, setRemovingId] = useState(null);

  // Filtrar conversas que estão na fila global (transferidas mas não atribuídas)
  const globalQueueConversations = conversations.filter(conv => 
    conv.transferido_humano && !conv.atribuido_para
  );

  const handleAssignConversation = async (conversationId) => {
    setRemovingId(conversationId);
    // Espera a animação (400ms)
    setTimeout(async () => {
      setLoading(true);
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
          onAssignConversation(conversationId);
          await refreshConversations();
        }
      } catch (error) {
        // erro
      } finally {
        setLoading(false);
        setRemovingId(null);
      }
    }, 400);
  };

  if (!isVisible) return null;

  return (
    <div className="global-queue-overlay" onClick={onClose}>
      <div className="global-queue-modal" onClick={e => e.stopPropagation()}>
        <div className="global-queue-header">
          <div className="global-queue-title">
            <Users size={20} />
            <h3>Fila Global de Conversas</h3>
            <span className="queue-count">{globalQueueConversations.length}</span>
          </div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="global-queue-content">
          {loading && <div className="loading">Carregando...</div>}
          {globalQueueConversations.length > 0 ? (
            globalQueueConversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`bot-queue-item${removingId === conversation.id ? ' removing' : ''}`}
              >
                <div className="queue-item-avatar">
                  <img src={conversation.avatar} alt={conversation.name} />
                </div>
                <div className="queue-item-content">
                  <div className="queue-item-header">
                    <h4>{conversation.name}</h4>
                    <span className="queue-time">
                      <Clock size={12} />
                      {/* timestamp pode ser melhorado */}
                      {conversation.timestamp ? new Date(conversation.timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : ''}
                    </span>
                  </div>
                  <p className="queue-last-message">{conversation.lastMessage}</p>
                  {conversation.dados_transferencia && (
                    <div className="transfer-info">
                      <Users size={12} />
                      <span>Paciente cadastrado - Dados completos disponíveis</span>
                    </div>
                  )}
                </div>
                <div className="queue-item-actions">
                  <button
                    className="assign-button"
                    onClick={() => handleAssignConversation(conversation.id)}
                    title="Pegar conversa"
                    disabled={loading || removingId === conversation.id}
                  >
                    <MessageSquare size={16} />
                    Pegar
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-queue">
              <Users size={48} />
              <p>Nenhuma conversa na fila global</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GlobalQueue; 