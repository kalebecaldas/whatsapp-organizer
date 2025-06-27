import { useEffect, useState } from 'react';
import { useChat } from '../context/ChatContext';
import { RefreshCw, Users, MessageCircle, Clock } from 'lucide-react';
import './Reports.css';

const Reports = () => {
  const { stats, refreshConversations, conversations } = useChat();
  const [loading, setLoading] = useState(false);

  const handleRefresh = async () => {
    setLoading(true);
    await refreshConversations();
    setLoading(false);
  };

  const formatNumber = (num) => {
    return num?.toLocaleString('pt-BR') || '0';
  };

  return (
    <div className="reports-container">
      <div className="reports-content">
        <div className="reports-header">
          <h1>Relatórios</h1>
          <button 
            className="refresh-button" 
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw size={20} className={loading ? 'spinning' : ''} />
            Atualizar
          </button>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">
              <Users size={24} />
            </div>
            <div className="stat-content">
              <h3>Usuários Ativos</h3>
              <p className="stat-value">{formatNumber(stats?.usuarios_ativos_ultimas_8h)}</p>
              <span className="stat-label">Últimas 8 horas</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <MessageCircle size={24} />
            </div>
            <div className="stat-content">
              <h3>Conversas Ativas</h3>
              <p className="stat-value">{formatNumber(conversations?.length)}</p>
              <span className="stat-label">Total de conversas</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Clock size={24} />
            </div>
            <div className="stat-content">
              <h3>Última Atualização</h3>
              <p className="stat-value">{new Date().toLocaleTimeString('pt-BR')}</p>
              <span className="stat-label">Tempo real</span>
            </div>
          </div>
        </div>

        <div className="conversations-summary">
          <h2>Resumo das Conversas</h2>
          {conversations && conversations.length > 0 ? (
            <div className="conversations-list">
              {conversations.slice(0, 5).map((conv) => (
                <div key={conv.id} className="conversation-item">
                  <div className="conversation-info">
                    <h4>{conv.name}</h4>
                    <p>{conv.phone}</p>
                  </div>
                  <div className="conversation-stats">
                    <span>{conv.messages?.length || 0} mensagens</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-data">Nenhuma conversa encontrada</p>
          )}
        </div>

        <div className="reports-footer">
          <p>Dados atualizados automaticamente a cada 5 minutos</p>
        </div>
      </div>
    </div>
  );
};

export default Reports; 