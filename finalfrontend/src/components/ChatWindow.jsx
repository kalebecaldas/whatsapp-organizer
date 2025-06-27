import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { useChat } from '../context/ChatContext';
import './ChatWindow.css';

const ChatWindow = () => {
  const { selectedConversation, messages, loading } = useChat();
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const [isScrolledToBottom, setIsScrolledToBottom] = useState(true);
  const [hasScrolledUp, setHasScrolledUp] = useState(false);
  const [showTypingIndicator, setShowTypingIndicator] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);

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
          </div>
        </div>
        <div className="chat-actions">
          <button className="icon-button" title="Buscar">
            🔍
          </button>
          <button className="icon-button" title="Mais opções">
            ⋮
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