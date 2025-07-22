import { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  MessageSquare, 
  Clock, 
  CheckCircle, 
  Download, 
  Filter,
  Calendar,
  Activity,
  FileText,
  PieChart,
  Target,
  Zap,
  Search,
  X,
  BarChart,
  MessageCircle
} from 'lucide-react';
import './Reports.css';

const Reports = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('24h');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [reportData, setReportData] = useState({
    conversations: {
      total: 0,
      active: 0,
      closed: 0,
      transferred: 0
    },
    messages: {
      total: 0,
      received: 0,
      sent: 0,
      avgResponseTime: '0m'
    },
    agents: {
      online: 0,
      total: 0,
      performance: []
    },
    trends: {
      daily: [],
      weekly: [],
      monthly: []
    }
  });

  // Simular dados para demonstração
  useEffect(() => {
    const fetchReportData = async () => {
      setIsLoading(true);
      
      // Simular chamada da API com filtros
      setTimeout(() => {
        setReportData({
          conversations: {
            total: 156,
            active: 24,
            closed: 132,
            transferred: 18
          },
          messages: {
            total: 2847,
            received: 1423,
            sent: 1424,
            avgResponseTime: '2m 34s'
          },
          agents: {
            online: 3,
            total: 5,
            performance: [
              { name: 'João Silva', conversations: 45, avgTime: '1m 52s', satisfaction: 4.8 },
              { name: 'Maria Santos', conversations: 38, avgTime: '2m 15s', satisfaction: 4.6 },
              { name: 'Pedro Costa', conversations: 32, avgTime: '2m 48s', satisfaction: 4.7 }
            ]
          },
          trends: {
            daily: [
              { date: '2024-01-01', conversations: 12, messages: 89 },
              { date: '2024-01-02', conversations: 15, messages: 112 },
              { date: '2024-01-03', conversations: 18, messages: 134 },
              { date: '2024-01-04', conversations: 22, messages: 167 },
              { date: '2024-01-05', conversations: 19, messages: 145 },
              { date: '2024-01-06', conversations: 16, messages: 123 },
              { date: '2024-01-07', conversations: 24, messages: 189 }
            ],
            weekly: [
              { week: 'Semana 1', conversations: 87, messages: 623 },
              { week: 'Semana 2', conversations: 94, messages: 712 },
              { week: 'Semana 3', conversations: 102, messages: 789 },
              { week: 'Semana 4', conversations: 89, messages: 654 }
            ],
            monthly: [
              { month: 'Jan', conversations: 342, messages: 2456 },
              { month: 'Fev', conversations: 378, messages: 2712 },
              { month: 'Mar', conversations: 401, messages: 2894 }
            ]
          }
        });
        setIsLoading(false);
      }, 1000);
    };

    fetchReportData();
  }, [selectedPeriod, selectedFilter, selectedAgent, dateRange]);

  // Funções de exportação
  const exportToCSV = () => {
    const csvData = reportData.trends.daily.map(day => ({
      Data: day.date,
      'Conversas': day.conversations,
      'Mensagens': day.messages,
      'Tempo Médio': '2m 34s',
      'Satisfação': '4.7/5.0'
    }));

    const headers = Object.keys(csvData[0]);
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n');

    downloadFile(csvContent, 'relatorio_conversas.csv', 'text/csv');
  };

  const exportToExcel = () => {
    // Simular exportação Excel (em produção usaria uma biblioteca como xlsx)
    const excelData = {
      'Métricas Gerais': [
        { 'Métrica': 'Conversas Totais', 'Valor': reportData.conversations.total },
        { 'Métrica': 'Conversas Ativas', 'Valor': reportData.conversations.active },
        { 'Métrica': 'Conversas Encerradas', 'Valor': reportData.conversations.closed },
        { 'Métrica': 'Transferidas', 'Valor': reportData.conversations.transferred }
      ],
      'Dados Diários': reportData.trends.daily.map(day => ({
        'Data': day.date,
        'Conversas': day.conversations,
        'Mensagens': day.messages,
        'Tempo Médio': '2m 34s',
        'Satisfação': '4.7/5.0'
      }))
    };

    // Simular download
    alert('Exportação Excel simulada - em produção seria implementada com biblioteca xlsx');
  };

  const exportToPDF = () => {
    // Simular exportação PDF (em produção usaria uma biblioteca como jsPDF)
    const pdfData = {
      title: 'Relatório de Conversas',
      period: selectedPeriod,
      filter: selectedFilter,
      metrics: reportData.conversations,
      trends: reportData.trends.daily.slice(-7),
      agents: reportData.agents.performance
    };

    // Simular download
    alert('Exportação PDF simulada - em produção seria implementada com biblioteca jsPDF');
  };

  const downloadFile = (content, filename, mimeType) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const clearFilters = () => {
    setSelectedPeriod('24h');
    setSelectedFilter('all');
    setSelectedAgent('all');
    setDateRange({ start: '', end: '' });
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (selectedFilter !== 'all') count++;
    if (selectedAgent !== 'all') count++;
    if (dateRange.start || dateRange.end) count++;
    return count;
  };

  const MetricCard = ({ icon: Icon, title, value, subtitle, color = 'blue', trend = null }) => (
    <div className={`metric-card metric-card-${color}`}>
      <div className="metric-icon">
        <Icon size={24} />
      </div>
      <div className="metric-content">
        <h3 className="metric-value">{value}</h3>
        <p className="metric-title">{title}</p>
        {subtitle && <p className="metric-subtitle">{subtitle}</p>}
        {trend && (
          <div className={`metric-trend ${trend > 0 ? 'positive' : 'negative'}`}>
            <TrendingUp size={14} />
            {Math.abs(trend)}%
          </div>
        )}
      </div>
    </div>
  );

  const ChartCard = ({ title, children, className = '', icon = null, description = '' }) => (
    <div className={`chart-card ${className}`}>
      <div className="chart-header">
        <div className="chart-title">
          {icon && <span className="chart-icon">{icon}</span>}
          <div className="chart-title-content">
            <h3>{title}</h3>
            {description && <p className="chart-description">{description}</p>}
          </div>
        </div>
        <div className="chart-actions">
          <button className="chart-action-btn" onClick={exportToCSV} title="Exportar CSV">
            <Download size={16} />
            <span>CSV</span>
          </button>
        </div>
      </div>
      <div className="chart-content">
        {children}
      </div>
    </div>
  );

  const AgentPerformanceCard = ({ agent }) => (
    <div className="agent-card">
      <div className="agent-info">
        <div className="agent-avatar">
          <span>{agent.name.split(' ').map(n => n[0]).join('')}</span>
        </div>
        <div className="agent-details">
          <h4>{agent.name}</h4>
          <p>{agent.conversations} conversas</p>
        </div>
      </div>
      <div className="agent-metrics">
        <div className="metric">
          <Clock size={14} />
          {agent.avgTime}
        </div>
        <div className="metric">
          <Target size={14} />
          {agent.satisfaction}/5.0
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="reports-loading">
        <div className="loading-spinner"></div>
        <p>Carregando relatórios...</p>
      </div>
    );
  }

  return (
    <div className="reports-container">
      {/* Header */}
      <div className="reports-header">
        <div className="header-content">
          <p>Métricas e análises do sistema de atendimento</p>
        </div>
        <div className="header-actions">
          <div className="filter-group">
            <Filter size={16} />
            <select 
              value={selectedFilter} 
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">Todos</option>
              <option value="bot">Bot</option>
              <option value="human">Humano</option>
              <option value="transferred">Transferidos</option>
            </select>
          </div>
          <div className="period-group">
            <Calendar size={16} />
            <select 
              value={selectedPeriod} 
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="period-select"
            >
              <option value="24h">Últimas 24h</option>
              <option value="7d">Últimos 7 dias</option>
              <option value="30d">Últimos 30 dias</option>
              <option value="90d">Últimos 90 dias</option>
            </select>
          </div>
          <button 
            className={`advanced-filter-btn ${showAdvancedFilters ? 'active' : ''}`}
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
          >
            <Search size={16} />
            Filtros
            {getActiveFiltersCount() > 0 && (
              <span className="filter-badge">{getActiveFiltersCount()}</span>
            )}
          </button>
          <button className="export-button" onClick={exportToCSV}>
            <Download size={16} />
            Exportar
          </button>
        </div>
      </div>

      {/* Filtros Avançados */}
      {showAdvancedFilters && (
        <div className="advanced-filters">
          <div className="filters-header">
            <h3>Filtros Avançados</h3>
            <button className="clear-filters-btn" onClick={clearFilters}>
              <X size={16} />
              Limpar
            </button>
          </div>
          <div className="filters-content">
            <div className="filter-row">
              <div className="filter-item">
                <label>Atendente</label>
                <select 
                  value={selectedAgent} 
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">Todos os atendentes</option>
                  <option value="joao">João Silva</option>
                  <option value="maria">Maria Santos</option>
                  <option value="pedro">Pedro Costa</option>
                </select>
              </div>
              <div className="filter-item">
                <label>Data Início</label>
                <input 
                  type="date" 
                  value={dateRange.start}
                  onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                  className="date-input"
                />
              </div>
              <div className="filter-item">
                <label>Data Fim</label>
                <input 
                  type="date" 
                  value={dateRange.end}
                  onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                  className="date-input"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Métricas Principais */}
      <div className="metrics-grid">
        <MetricCard
          icon={MessageSquare}
          title="Conversas Totais"
          value={reportData.conversations.total}
          subtitle="Período selecionado"
          color="blue"
          trend={12}
        />
        <MetricCard
          icon={Activity}
          title="Conversas Ativas"
          value={reportData.conversations.active}
          subtitle="Em andamento"
          color="green"
          trend={-5}
        />
        <MetricCard
          icon={CheckCircle}
          title="Conversas Encerradas"
          value={reportData.conversations.closed}
          subtitle="Concluídas"
          color="purple"
          trend={8}
        />
        <MetricCard
          icon={Users}
          title="Transferidas"
          value={reportData.conversations.transferred}
          subtitle="Para humano"
          color="orange"
          trend={15}
        />
      </div>

      {/* Gráficos e Análises */}
      <div className="charts-grid">
        {/* Conversas por Período */}
        <ChartCard 
          title="Evolução de Conversas" 
          className="chart-large" 
          icon="📊"
          description="Gráfico de conversas por período"
        >
          <div className="chart-data">
            {reportData.trends.daily.slice(-7).map((day, index) => (
              <div key={index} className="data-point">
                <span className="date">{day.date}</span>
                <span className="value">{day.conversations} conversas</span>
              </div>
            ))}
          </div>
        </ChartCard>

        {/* Distribuição de Mensagens */}
        <ChartCard 
          title="Distribuição de Mensagens" 
          icon="📈"
          description="Bot vs Atendente Humano"
        >
          <div className="distribution-stats">
            <div className="stat-item">
              <span className="stat-label">Recebidas</span>
              <span className="stat-value">{reportData.messages.received}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Enviadas</span>
              <span className="stat-value">{reportData.messages.sent}</span>
            </div>
          </div>
        </ChartCard>

        {/* Performance dos Agentes */}
        <ChartCard title="Performance dos Agentes" className="chart-large">
          <div className="agents-list">
            {reportData.agents.performance.map((agent, index) => (
              <AgentPerformanceCard key={index} agent={agent} />
            ))}
          </div>
        </ChartCard>

        {/* Tempo Médio de Resposta */}
        <ChartCard title="Tempo Médio de Resposta">
          <div className="response-time-card">
            <div className="time-display">
              <Clock size={32} />
              <span className="time-value">{reportData.messages.avgResponseTime}</span>
            </div>
            <p className="time-description">Tempo médio de resposta</p>
          </div>
        </ChartCard>
      </div>

      {/* Tabela de Dados Detalhados */}
      <div className="detailed-data">
        <div className="data-header">
          <h2>Dados Detalhados</h2>
          <div className="data-actions">
            <button className="action-btn" onClick={exportToCSV}>
              <FileText size={16} />
              CSV
            </button>
            <button className="action-btn" onClick={exportToExcel}>
              <Download size={16} />
              Excel
            </button>
            <button className="action-btn" onClick={exportToPDF}>
              <FileText size={16} />
              PDF
            </button>
          </div>
        </div>
        <div className="data-table">
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Conversas</th>
                <th>Mensagens</th>
                <th>Tempo Médio</th>
                <th>Satisfação</th>
              </tr>
            </thead>
            <tbody>
              {reportData.trends.daily.slice(-7).map((day, index) => (
                <tr key={index}>
                  <td>{day.date}</td>
                  <td>{day.conversations}</td>
                  <td>{day.messages}</td>
                  <td>2m 34s</td>
                  <td>4.7/5.0</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Reports; 