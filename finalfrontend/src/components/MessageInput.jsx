import { useState, useRef, useEffect } from 'react';
import { Send, Smile, Paperclip, Mic } from 'lucide-react';
import { useChat } from '../context/ChatContext';
import './MessageInput.css';

const MessageInput = () => {
  const { selectedConversation, sendMessage } = useChat();
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
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

  return (
    <div className="message-input-container">
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