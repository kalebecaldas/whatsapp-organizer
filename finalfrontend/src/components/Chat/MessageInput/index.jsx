import { useState, useRef, useEffect } from 'react';
import { Send, Smile, Paperclip, Mic, Users, X, RotateCcw } from 'lucide-react';
import { useChat } from '../../../context/ChatContext';
import './MessageInput.css';

const MessageInput = () => {
  const { selectedConversation, sendMessage } = useChat();
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showActionMenu, setShowActionMenu] = useState(false);
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && selectedConversation) {
      sendMessage(message.trim());
      setMessage('');
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputChange = (e) => {
    setMessage(e.target.value);
    setIsTyping(e.target.value.length > 0);
  };

  const handleConversationAction = async (action) => {
    if (!selectedConversation) return;

    try {
      const response = await fetch('/api/conversation-actions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversationId: selectedConversation.id,
          action: action,
          targetUserId: action === 'transfer' ? 'target-user-id' : null
        })
      });

      if (response.ok) {
        console.log(`Ação ${action} executada com sucesso`);
        setShowActionMenu(false);
      } else {
        console.error(`Erro ao executar ação ${action}`);
      }
    } catch (error) {
      console.error('Erro na requisição:', error);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  if (!selectedConversation) {
    return null;
  }

  // Verificar se a conversa foi atribuída a um usuário
  // const isAssignedConversation = selectedConversation.atribuido_para;

  return (
    <div className="message-input-container">
      {/* Removido bloco de botões de ação duplicados */}
      <form onSubmit={handleSubmit} className="message-input-form">
        <div className="input-wrapper">
          <button type="button" className="icon-button">
            <Smile size={20} />
          </button>
          <button type="button" className="icon-button">
            <Paperclip size={20} />
          </button>
          <div className="text-input-container">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Digite uma mensagem"
              className="message-textarea"
              rows={1}
              maxLength={4096}
            />
          </div>
          {isTyping ? (
            <button type="submit" className="send-button">
              <Send size={20} />
            </button>
          ) : (
            <button type="button" className="icon-button">
              <Mic size={20} />
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default MessageInput; 