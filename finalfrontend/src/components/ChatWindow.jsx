import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { useChat } from '../context/ChatContext';
import { Users, X, RotateCcw, ArrowRight, Upload, Check } from 'lucide-react';
import './ChatWindow.css';

const ChatWindow = () => {
  const { selectedConversation, messages, loading, refreshConversations } = useChat();
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const [isScrolledToBottom, setIsScrolledToBottom] = useState(true);
  const [hasScrolledUp, setHasScrolledUp] = useState(false);
  const [showTypingIndicator, setShowTypingIndicator] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Função para recarregar conversas após ações
  const reloadConversations = async () => {
    try {
      console.log('🔄 Recarregando conversas após ação...');
      
      // Forçar recarregamento completo
      await refreshConversations();
      
      // Aguardar um pouco para garantir que os dados foram atualizados
      await new Promise(resolve => setTimeout(resolve, 200));
      
      console.log('✅ Conversas recarregadas após ação');
      
      // Forçar uma nova renderização do componente
      console.log('🔄 Forçando atualização da interface...');
      
    } catch (error) {
      console.error('❌ Erro ao recarregar conversas:', error);
    }
  };

  const scrollToBottom = useCallback((behavior = 'auto') => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: behavior,
        block: 'end' 
      });
    }
  }, []);

  const checkIfScrolledToBottom = useCallback(() => {
    if (!messagesContainerRef.current) return true;
    
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const threshold = 50;
    return scrollTop + clientHeight >= scrollHeight - threshold;
  }, []);

  const handleScroll = useCallback(() => {
    if (!messagesContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const threshold = 40; // mais tolerante
    const isAtBottom = Math.abs(scrollHeight - scrollTop - clientHeight) < threshold;
    setShowScrollButton(!isAtBottom);
    setIsScrolledToBottom(isAtBottom);
  }, []);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      // Chame handleScroll uma vez para inicializar corretamente
      handleScroll();
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > 0 && isScrolledToBottom) {
      // Use a small delay to ensure DOM is updated
      const timer = setTimeout(() => {
        scrollToBottom();
      }, 10);
      return () => clearTimeout(timer);
    }
  }, [messages, scrollToBottom, isScrolledToBottom]);

  // Optimize typing indicator logic - simplified without isTyping
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      // Show typing indicator only when last message is received and user is active
      if (lastMessage.sender === 'received') {
        setShowTypingIndicator(true);
        // Hide typing indicator after a short delay
        const timer = setTimeout(() => {
          setShowTypingIndicator(false);
        }, 1000);
        return () => clearTimeout(timer);
      } else {
        setShowTypingIndicator(false);
      }
    } else {
      setShowTypingIndicator(false);
    }
  }, [messages]);

  // Always scroll to bottom when conversation changes
  useEffect(() => {
    if (selectedConversation) {
      scrollToBottom();
    }
  }, [selectedConversation, scrollToBottom]);

  const formatTime = useCallback((timestamp) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  }, []);

  // Memoizar as mensagens para evitar re-renders desnecessários
  const orderedMessages = useMemo(() => {
    return [...messages]
      .sort((a, b) => {
        const timestampA = a.timestamp instanceof Date ? a.timestamp : new Date(a.timestamp);
        const timestampB = b.timestamp instanceof Date ? b.timestamp : new Date(b.timestamp);
        if (timestampA.getTime() !== timestampB.getTime()) {
          return timestampA.getTime() - timestampB.getTime();
        }
        // Se os timestamps forem iguais, ordenar pelo id (que inclui o index)
        return a.id.localeCompare(b.id);
      });
  }, [messages]);

  // Botão de scroll para o final
  const handleScrollToBottom = useCallback(() => {
    scrollToBottom('smooth');
    // Pequeno delay para garantir que o scroll foi executado
    setTimeout(() => {
      setIsScrolledToBottom(true);
      setHasScrolledUp(false);
    }, 300);
  }, [scrollToBottom]);

  // Renderizar botão de scroll apenas se o usuário rolou para cima
  const shouldShowScrollButton = showScrollButton && messages.length > 0;

  // Funções de ação para conversas
  const handleTransferConversation = async () => {
    if (!selectedConversation || actionLoading) return;
    
    setActionLoading(true);
    try {
      const response = await fetch('/api/conversation-actions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversationId: selectedConversation.id,
          action: 'transfer',
          targetUserId: 'current-user-id'
        })
      });

      if (response.ok) {
        console.log('Conversa transferida com sucesso');
        // Aqui você pode adicionar lógica para atualizar a interface
        await reloadConversations();
      }
    } catch (error) {
      console.error('Erro ao transferir conversa:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCloseConversation = async () => {
    if (!selectedConversation || actionLoading) return;
    
    setActionLoading(true);
    try {
      const response = await fetch('/api/conversation-actions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversationId: selectedConversation.id,
          action: 'close'
        })
      });

      if (response.ok) {
        console.log('Conversa fechada com sucesso');
        // Aqui você pode adicionar lógica para atualizar a interface
        await reloadConversations();
      }
    } catch (error) {
      console.error('Erro ao fechar conversa:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReturnToQueue = async () => {
    if (!selectedConversation || actionLoading) return;
    
    setActionLoading(true);
    try {
      const response = await fetch('/api/return-to-global-queue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversationId: selectedConversation.id,
          phone: selectedConversation.phone
        })
      });

      if (response.ok) {
        console.log('Conversa retornada para fila global com sucesso');
        // Atualizar a interface - remover atribuição da conversa
        // Aqui você pode adicionar lógica para atualizar a lista de conversas
        // Por exemplo, recarregar as conversas ou atualizar o estado
        await reloadConversations();
      }
    } catch (error) {
      console.error('Erro ao retornar conversa para fila global:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleTakeConversation = async () => {
    console.log('🔄 handleTakeConversation chamado para:', selectedConversation?.id);
    if (!selectedConversation || actionLoading) return;
    
    setActionLoading(true);
    try {
      const response = await fetch('/api/transfer-conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversationId: selectedConversation.id,
          userId: 'current-user-id'
        })
      });

      console.log('📡 Resposta da API transfer-conversation:', response.status, response.statusText);
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Conversa transferida para atendimento humano com sucesso:', result);
        await reloadConversations();
      } else {
        const errorData = await response.json();
        console.error('❌ Erro na resposta:', response.status, response.statusText, errorData);
      }
    } catch (error) {
      console.error('❌ Erro ao transferir conversa para atendimento humano:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddToGlobalQueue = async () => {
    console.log('🔄 handleAddToGlobalQueue chamado para:', selectedConversation?.id);
    if (!selectedConversation || actionLoading) return;
    
    setActionLoading(true);
    try {
      const response = await fetch('/api/add-to-global-queue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversationId: selectedConversation.id,
          phone: selectedConversation.phone || selectedConversation.id
        })
      });

      console.log('📡 Resposta da API add-to-global-queue:', response.status, response.statusText);
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Conversa adicionada à fila global com sucesso:', result);
        await reloadConversations();
      } else {
        const errorData = await response.json();
        console.error('❌ Erro na resposta:', response.status, response.statusText, errorData);
      }
    } catch (error) {
      console.error('❌ Erro ao adicionar conversa à fila global:', error);
    } finally {
      setActionLoading(false);
    }
  };

  // Optimize message rendering with smooth animations
  const renderMessage = (message, index) => {
    return (
      <div
        key={`${message.id}-${message.timestamp}`}
        className={`message ${message.sender === 'received' ? 'received-message' : 'sent-message'}`}
      >
        <div className="message-bubble">
          <div className="message-text">{message.text}</div>
          <div className="message-time">
            {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
        </div>
      </div>
    );
  };

  if (!selectedConversation) {
    return (
      <div className="chat-window">
        <div className="empty-state">
          <div className="empty-icon">💬</div>
          <h3>Nenhuma conversa selecionada</h3>
          <p>Escolha uma conversa na lista para começar a conversar</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-contact-info">
          <div className="contact-avatar">
            {selectedConversation.avatar ? (
              <img src={selectedConversation.avatar} alt={selectedConversation.name} />
            ) : (
              <span>{selectedConversation.name.charAt(0).toUpperCase()}</span>
            )}
          </div>
          <div className="contact-details">
            <h3 className="contact-name">{selectedConversation.name}</h3>
            <span className="contact-status">
              {selectedConversation.isOnline ? 'online' : 'offline'}
            </span>
            {/* Indicador de área */}
            <span className={`area-indicator ${selectedConversation.transferido_humano ? 'human' : 'bot'}`}>
              {selectedConversation.transferido_humano ? '👥 Atendimento Humano' : '🤖 Bot'}
            </span>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="chat-action-buttons">
          {console.log('🔍 Estado da conversa:', {
            id: selectedConversation?.id,
            transferido_humano: selectedConversation?.transferido_humano,
            atribuido_para: selectedConversation?.atribuido_para
          })}
          
          {/* BOT AREA - Botões específicos para conversas do bot */}
          {selectedConversation && !selectedConversation.transferido_humano && (
            <>
              <button 
                className={`action-button transfer-btn ${actionLoading ? 'loading' : ''}`}
                onClick={handleTransferConversation}
                disabled={actionLoading}
                aria-label="Transferir conversa para outro usuário"
              >
                <Users size={20} />
              </button>
              
              <button 
                className={`action-button take-btn ${actionLoading ? 'loading' : ''}`}
                onClick={handleTakeConversation}
                disabled={actionLoading}
                aria-label="Pegar conversa para atendimento humano"
              >
                <ArrowRight size={20} />
              </button>
              
              <button 
                className={`action-button add-to-queue-btn ${actionLoading ? 'loading' : ''}`}
                onClick={handleAddToGlobalQueue}
                disabled={actionLoading}
                aria-label="Enviar conversa para fila global"
              >
                <Upload size={20} />
              </button>
              
              <button 
                className={`action-button close-btn ${actionLoading ? 'loading' : ''}`}
                onClick={handleCloseConversation}
                disabled={actionLoading}
                aria-label="Encerrar conversa"
              >
                <X size={20} />
              </button>
            </>
          )}
          
          {/* HUMAN AREA - Botões específicos para conversas de atendimento humano */}
          {selectedConversation && selectedConversation.transferido_humano && (
            <>
              <button 
                className={`action-button transfer-btn ${actionLoading ? 'loading' : ''}`}
                onClick={handleTransferConversation}
                disabled={actionLoading}
                aria-label="Transferir conversa para outro atendente"
              >
                <Users size={20} />
              </button>
              
              <button 
                className={`action-button return-btn ${actionLoading ? 'loading' : ''}`}
                onClick={handleReturnToQueue}
                disabled={actionLoading}
                aria-label="Retornar conversa para fila global"
              >
                <RotateCcw size={20} />
              </button>
              
              <button 
                className={`action-button close-btn ${actionLoading ? 'loading' : ''}`}
                onClick={handleCloseConversation}
                disabled={actionLoading}
                aria-label="Encerrar conversa"
              >
                <X size={20} />
              </button>
            </>
          )}
          
          {/* Botão de teste - remover depois */}
          <button 
            className="action-button test-btn"
            onClick={() => console.log('🎯 Botão de teste clicado! Estado:', {
              transferido_humano: selectedConversation?.transferido_para,
              atribuido_para: selectedConversation?.atribuido_para
            })}
            aria-label="Botão de teste"
          >
            <Check size={20} />
          </button>
        </div>
        

      </div>

      {/* Messages Container */}
      <div className="messages-container" ref={messagesContainerRef}>
        {loading && (
          <div className="loading-indicator">
            <div className="loading-spinner"></div>
            <span>Carregando mensagens...</span>
          </div>
        )}
        
        {messages.length === 0 && !loading ? (
          <div className="no-messages">
            <div className="no-messages-icon">💬</div>
            <h4>Nenhuma mensagem ainda</h4>
            <p>Inicie uma conversa enviando uma mensagem</p>
          </div>
        ) : (
          <div className="messages-list">
            {orderedMessages.map((message, index) => {
              return renderMessage(message, index);
            })}
            
            <div ref={messagesEndRef} />
          </div>
        )}
        
        <button
          className={`scroll-to-bottom-button ${shouldShowScrollButton ? 'show' : 'hide'}`}
          onClick={handleScrollToBottom}
          title="Ir para o final"
        >
          <span style={{fontSize: 28, lineHeight: 1}}>↓</span>
        </button>
      </div>
    </div>
  );
};

export default ChatWindow; 