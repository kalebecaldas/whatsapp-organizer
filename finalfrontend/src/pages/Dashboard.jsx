import { useState, useEffect } from 'react';
import { Users, MessageSquare, Clock, CheckCircle, TrendingUp, Activity, BarChart3, ArrowRight, Settings, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState({
    totalConversations: 0,
    queueConversations: 0,
    onlineUsers: 0,
    closedToday: 0
  });

  const [onlineUsers, setOnlineUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Simular dados para demonstração
  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      
      // Simular chamada da API
      setTimeout(() => {
        setMetrics({
          totalConversations: 24,
          queueConversations: 8,
          onlineUsers: 3,
          closedToday: 12
        });

        setOnlineUsers([
          {
            id: 1,
            name: 'João Silva',
            avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=JS&backgroundColor=25D366&textColor=FFFFFF',
            status: 'online',
            activeConversations: 4,
            avgResponseTime: '2m',
            closedToday: 5
          },
          {
            id: 2,
            name: 'Maria Santos',
            avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=MS&backgroundColor=8B5CF6&textColor=FFFFFF',
            status: 'online',
            activeConversations: 3,
            avgResponseTime: '1m',
            closedToday: 7
          },
          {
            id: 3,
            name: 'Pedro Costa',
            avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=PC&backgroundColor=EF4444&textColor=FFFFFF',
            status: 'online',
            activeConversations: 2,
            avgResponseTime: '3m',
            closedToday: 3
          }
        ]);

        setIsLoading(false);
      }, 1000);
    };

    fetchDashboardData();
  }, []);

  const MetricCard = ({ icon: Icon, title, value, subtitle, color = 'blue' }) => (
    <div className={`metric-card metric-card-${color}`}>
      <div className="metric-icon">
        <Icon size={24} />
      </div>
      <div className="metric-content">
        <h3 className="metric-value">{value}</h3>
        <p className="metric-title">{title}</p>
        {subtitle && <p className="metric-subtitle">{subtitle}</p>}
      </div>
    </div>
  );

  const UserCard = ({ user }) => (
    <div className="user-card">
      <div className="user-avatar">
        <img src={user.avatar} alt={user.name} />
        <div className={`status-indicator ${user.status}`} />
      </div>
      <div className="user-info">
        <h4 className="user-name">{user.name}</h4>
        <div className="user-metrics">
          <span className="metric">
            <MessageSquare size={14} />
            {user.activeConversations} conversas
          </span>
          <span className="metric">
            <Clock size={14} />
            {user.avgResponseTime}
          </span>
          <span className="metric">
            <CheckCircle size={14} />
            {user.closedToday} hoje
          </span>
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Carregando dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <p>Visão geral do sistema de atendimento</p>
        </div>
        <div className="header-actions">
          <button className="action-button">
            <BarChart3 size={20} />
            Relatórios
          </button>
        </div>
      </div>

      {/* Métricas Principais */}
      <div className="metrics-grid">
        <MetricCard
          icon={MessageSquare}
          title="Conversas Ativas"
          value={metrics.totalConversations}
          subtitle="Bot + Humano"
          color="blue"
        />
        <MetricCard
          icon={Users}
          title="Em Fila Global"
          value={metrics.queueConversations}
          subtitle="Aguardando atendimento"
          color="orange"
        />
        <MetricCard
          icon={Activity}
          title="Usuários Online"
          value={metrics.onlineUsers}
          subtitle="Atendendo agora"
          color="green"
        />
        <MetricCard
          icon={CheckCircle}
          title="Encerradas Hoje"
          value={metrics.closedToday}
          subtitle="Total do dia"
          color="purple"
        />
      </div>

      {/* Conteúdo Principal */}
      <div className="dashboard-content-grid">
        {/* Atendentes Online */}
        <div className="section">
          <div className="section-header">
            <h2>Atendentes Online</h2>
            <span className="section-count">{onlineUsers.length} ativos</span>
          </div>
          <div className="users-grid">
            {onlineUsers.map(user => (
              <UserCard key={user.id} user={user} />
            ))}
          </div>
        </div>

        {/* Gráficos e Relatórios */}
        <div className="section">
          <div className="section-header">
            <h2>Atividade Hoje</h2>
            <div className="chart-controls">
              <button className="chart-button active">24h</button>
              <button className="chart-button">7d</button>
              <button className="chart-button">30d</button>
            </div>
          </div>
          <div className="charts-container">
            <div className="chart-card">
              <h3>Conversas por Hora</h3>
              <div className="chart-placeholder">
                <TrendingUp size={48} />
                <p>Gráfico de conversas</p>
              </div>
            </div>
            <div className="chart-card">
              <h3>Distribuição</h3>
              <div className="chart-placeholder">
                <BarChart3 size={48} />
                <p>Bot vs Humano</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 