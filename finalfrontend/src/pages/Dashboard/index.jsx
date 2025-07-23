import React, { useState, useEffect } from 'react';
import { 
  Users, 
  MessageSquare, 
  TrendingUp, 
  Clock, 
  AlertCircle,
  CheckCircle,
  Activity,
  BarChart3,
  Settings,
  Bell
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user, getDashboardConfig } = useAuth();
  const [stats, setStats] = useState({});
  const [recentMessages, setRecentMessages] = useState([]);
  const [userActivity, setUserActivity] = useState([]);
  const [systemStatus, setSystemStatus] = useState({});
  const [pendingTasks, setPendingTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  const dashboardConfig = getDashboardConfig();

  useEffect(() => {
    // Simular carregamento de dados
    const loadDashboardData = async () => {
      setLoading(true);
      
      // Simular delay de API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Dados simulados baseados no perfil
      const mockData = {
        stats: {
          totalUsers: 45,
          activeChats: 12,
          messagesToday: 156,
          responseTime: '2.3min'
        },
        recentMessages: [
          { id: 1, user: 'João Silva', message: 'Preciso de ajuda com meu pedido', time: '2 min atrás', status: 'pending' },
          { id: 2, user: 'Maria Santos', message: 'Obrigada pelo atendimento!', time: '5 min atrás', status: 'resolved' },
          { id: 3, user: 'Pedro Costa', message: 'Quando chega meu produto?', time: '8 min atrás', status: 'pending' }
        ],
        userActivity: [
          { user: 'Ana Silva', action: 'Respondeu mensagem', time: '1 min atrás' },
          { user: 'Carlos Lima', action: 'Transferiu conversa', time: '3 min atrás' },
          { user: 'Fernanda Costa', action: 'Finalizou atendimento', time: '5 min atrás' }
        ],
        systemStatus: {
          whatsapp: 'online',
          api: 'online',
          database: 'online',
          notifications: 'enabled'
        },
        pendingTasks: [
          { id: 1, title: 'Revisar relatório mensal', priority: 'high', due: 'Hoje' },
          { id: 2, title: 'Configurar novos usuários', priority: 'medium', due: 'Amanhã' },
          { id: 3, title: 'Atualizar documentação', priority: 'low', due: 'Próxima semana' }
        ]
      };
      
      setStats(mockData.stats);
      setRecentMessages(mockData.recentMessages);
      setUserActivity(mockData.userActivity);
      setSystemStatus(mockData.systemStatus);
      setPendingTasks(mockData.pendingTasks);
      setLoading(false);
    };

    loadDashboardData();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return '#10b981';
      case 'offline': return '#ef4444';
      case 'warning': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Carregando dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>Bem-vindo, {user?.name}!</h1>
          <p>Dashboard personalizado para {user?.role === 'admin' ? 'Administrador' : user?.role === 'supervisor' ? 'Supervisor' : 'Atendente'}</p>
        </div>
        <div className="header-actions">
          <button className="notification-btn">
            <Bell size={20} />
            <span className="notification-badge">3</span>
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Estatísticas - Visível para Admin e Supervisor */}
        {dashboardConfig.showStats && (
          <div className="stats-section">
            <h2>Estatísticas Gerais</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">
                  <Users size={24} />
                </div>
                <div className="stat-info">
                  <h3>{stats.totalUsers}</h3>
                  <p>Usuários Ativos</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">
                  <MessageSquare size={24} />
                </div>
                <div className="stat-info">
                  <h3>{stats.activeChats}</h3>
                  <p>Chats Ativos</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">
                  <TrendingUp size={24} />
                </div>
                <div className="stat-info">
                  <h3>{stats.messagesToday}</h3>
                  <p>Mensagens Hoje</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">
                  <Clock size={24} />
                </div>
                <div className="stat-info">
                  <h3>{stats.responseTime}</h3>
                  <p>Tempo Médio</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="dashboard-grid">
          {/* Mensagens Recentes - Visível para todos */}
          {dashboardConfig.showRecentMessages && (
            <div className="dashboard-card">
              <div className="card-header">
                <h3>Mensagens Recentes</h3>
                <button className="view-all-btn">Ver todas</button>
              </div>
              <div className="card-content">
                {recentMessages.map((message) => (
                  <div key={message.id} className="message-item">
                    <div className="message-info">
                      <h4>{message.user}</h4>
                      <p>{message.message}</p>
                      <span className="message-time">{message.time}</span>
                    </div>
                    <div className={`message-status ${message.status}`}>
                      {message.status === 'pending' ? <AlertCircle size={16} /> : <CheckCircle size={16} />}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Atividade de Usuários - Apenas Admin */}
          {dashboardConfig.showUserActivity && (
            <div className="dashboard-card">
              <div className="card-header">
                <h3>Atividade da Equipe</h3>
                <Activity size={20} />
              </div>
              <div className="card-content">
                {userActivity.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-user">{activity.user}</div>
                    <div className="activity-action">{activity.action}</div>
                    <div className="activity-time">{activity.time}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Status do Sistema - Admin e Supervisor */}
          {dashboardConfig.showSystemStatus && (
            <div className="dashboard-card">
              <div className="card-header">
                <h3>Status do Sistema</h3>
                <Settings size={20} />
              </div>
              <div className="card-content">
                <div className="status-grid">
                  <div className="status-item">
                    <span className="status-label">WhatsApp</span>
                    <div className="status-indicator" style={{ backgroundColor: getStatusColor(systemStatus.whatsapp) }}></div>
                    <span className="status-text">{systemStatus.whatsapp}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">API</span>
                    <div className="status-indicator" style={{ backgroundColor: getStatusColor(systemStatus.api) }}></div>
                    <span className="status-text">{systemStatus.api}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Database</span>
                    <div className="status-indicator" style={{ backgroundColor: getStatusColor(systemStatus.database) }}></div>
                    <span className="status-text">{systemStatus.database}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Notificações</span>
                    <div className="status-indicator" style={{ backgroundColor: getStatusColor(systemStatus.notifications) }}></div>
                    <span className="status-text">{systemStatus.notifications}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tarefas Pendentes - Admin e Supervisor */}
          {dashboardConfig.showPendingTasks && (
            <div className="dashboard-card">
              <div className="card-header">
                <h3>Tarefas Pendentes</h3>
                <BarChart3 size={20} />
              </div>
              <div className="card-content">
                {pendingTasks.map((task) => (
                  <div key={task.id} className="task-item">
                    <div className="task-info">
                      <h4>{task.title}</h4>
                      <span className="task-due">Vence: {task.due}</span>
                    </div>
                    <div 
                      className="task-priority" 
                      style={{ backgroundColor: getPriorityColor(task.priority) }}
                    >
                      {task.priority}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Ações Rápidas - Visível para todos */}
          {dashboardConfig.showQuickActions && (
            <div className="dashboard-card">
              <div className="card-header">
                <h3>Ações Rápidas</h3>
              </div>
              <div className="card-content">
                <div className="quick-actions">
                  <button className="quick-action-btn">
                    <MessageSquare size={20} />
                    <span>Nova Mensagem</span>
                  </button>
                  <button className="quick-action-btn">
                    <Users size={20} />
                    <span>Transferir Chat</span>
                  </button>
                  <button className="quick-action-btn">
                    <BarChart3 size={20} />
                    <span>Ver Relatórios</span>
                  </button>
                  <button className="quick-action-btn">
                    <Settings size={20} />
                    <span>Configurações</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 