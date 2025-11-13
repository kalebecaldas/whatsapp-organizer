import { useState, useEffect } from 'react';
import { X, Clock, MessageSquare, CheckCircle, Circle } from 'lucide-react';
import { sessionsAPI } from '../../../utils/api';
import './SessionsModal.css';

const SessionsModal = ({ isVisible, onClose, phone }) => {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [sessionMessages, setSessionMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);

  useEffect(() => {
    if (isVisible && phone) {
      loadSessions();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isVisible, phone]);

  const loadSessions = async () => {
    if (!phone) return;
    
    setLoading(true);
    try {
      const response = await sessionsAPI.getSessions(phone);
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Erro ao carregar sessões:', error);
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  const loadSessionMessages = async (sessionId) => {
    if (!phone || !sessionId) return;
    
    setLoadingMessages(true);
    try {
      const response = await sessionsAPI.getSessionMessages(phone, sessionId);
      setSessionMessages(response.data.messages || []);
      setSelectedSession(sessionId);
    } catch (error) {
      console.error('Erro ao carregar mensagens da sessão:', error);
      setSessionMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m atrás`;
    if (diffHours < 24) return `${diffHours}h atrás`;
    return `${diffDays}d atrás`;
  };

  if (!isVisible) return null;

  return (
    <div className="sessions-modal-overlay" onClick={onClose}>
      <div className="sessions-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="sessions-modal-header">
          <h2>Sessões de Conversa</h2>
          <button className="sessions-modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="sessions-modal-body">
          {loading ? (
            <div className="sessions-loading">
              <p>Carregando sessões...</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="sessions-empty">
              <MessageSquare size={48} />
              <p>Nenhuma sessão encontrada</p>
            </div>
          ) : (
            <div className="sessions-layout">
              <div className="sessions-list">
                <h3>Sessões ({sessions.length})</h3>
                <div className="sessions-list-content">
                  {sessions.map((session) => (
                    <div
                      key={session.id}
                      className={`session-item ${selectedSession === session.id ? 'active' : ''}`}
                      onClick={() => loadSessionMessages(session.id)}
                    >
                      <div className="session-item-header">
                        <div className="session-status">
                          {session.status === 'active' ? (
                            <Circle size={12} className="status-active" />
                          ) : (
                            <CheckCircle size={12} className="status-finished" />
                          )}
                          <span className="session-status-text">
                            {session.status === 'active' ? 'Ativa' : 'Finalizada'}
                          </span>
                        </div>
                        <span className="session-time">
                          {formatTimeAgo(session.end_time)}
                        </span>
                      </div>
                      <div className="session-preview">
                        {session.preview || session.last_message || 'Sem mensagens'}
                      </div>
                      <div className="session-meta">
                        <span className="session-message-count">
                          <MessageSquare size={14} />
                          {session.message_count} mensagens
                        </span>
                        <span className="session-dates">
                          <Clock size={14} />
                          {formatDate(session.start_time)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="sessions-messages">
                {selectedSession ? (
                  <>
                    <h3>Mensagens da Sessão</h3>
                    {loadingMessages ? (
                      <div className="sessions-loading">
                        <p>Carregando mensagens...</p>
                      </div>
                    ) : (
                      <div className="messages-list">
                        {sessionMessages.map((msg) => (
                          <div
                            key={msg.id}
                            className={`message-item ${msg.direction === 'sent' ? 'sent' : 'received'}`}
                          >
                            <div className="message-content">
                              <p>{msg.text}</p>
                              <span className="message-time">
                                {formatDate(msg.timestamp)}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                ) : (
                  <div className="sessions-empty-messages">
                    <MessageSquare size={48} />
                    <p>Selecione uma sessão para ver as mensagens</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SessionsModal;
