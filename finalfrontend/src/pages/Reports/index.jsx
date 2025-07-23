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
  const [reportData, setReportData] = useState({
    appointments: {
      total: 0,
      completed: 0,
      cancelled: 0,
      pending: 0,
      conversionRate: 0
    },
    procedures: {
      total: 0,
      byType: [],
      mostRequested: []
    },
    units: {
      total: 0,
      byUnit: [],
      mostPopular: []
    },
    transfers: {
      total: 0,
      botToHuman: 0,
      queueTime: 0,
      efficiency: 0
    },
    trends: {
      daily: [],
      weekly: [],
      monthly: []
    }
  });

  // Dados carregados instantaneamente
  useEffect(() => {
    setReportData({
          appointments: {
            total: 156,
            completed: 132,
            cancelled: 8,
            pending: 16,
            conversionRate: 84.6
          },
          procedures: {
            total: 156,
            byType: [
              { name: 'Consulta Médica', count: 89, percentage: 57.1 },
              { name: 'Exame Laboratorial', count: 34, percentage: 21.8 },
              { name: 'Exame de Imagem', count: 18, percentage: 11.5 },
              { name: 'Procedimento Cirúrgico', count: 15, percentage: 9.6 }
            ],
            mostRequested: [
              { name: 'Consulta Clínica Geral', count: 45 },
              { name: 'Exame de Sangue', count: 28 },
              { name: 'Ultrassom', count: 12 },
              { name: 'Consulta Cardiologia', count: 10 }
            ]
          },
          units: {
            total: 8,
            byUnit: [
              { name: 'Unidade Centro', appointments: 67, percentage: 42.9 },
              { name: 'Unidade Norte', appointments: 45, percentage: 28.8 },
              { name: 'Unidade Sul', appointments: 34, percentage: 21.8 },
              { name: 'Unidade Leste', appointments: 10, percentage: 6.5 }
            ],
            mostPopular: [
              { name: 'Unidade Centro', appointments: 67 },
              { name: 'Unidade Norte', appointments: 45 },
              { name: 'Unidade Sul', appointments: 34 },
              { name: 'Unidade Leste', appointments: 10 }
            ]
          },
          transfers: {
            total: 24,
            botToHuman: 24,
            queueTime: 8.5,
            efficiency: 92.3
          },
          trends: {
            daily: [
              { date: '2024-01-01', appointments: 12, transfers: 3 },
              { date: '2024-01-02', appointments: 15, transfers: 4 },
              { date: '2024-01-03', appointments: 18, transfers: 5 },
              { date: '2024-01-04', appointments: 22, transfers: 6 },
              { date: '2024-01-05', appointments: 19, transfers: 4 },
              { date: '2024-01-06', appointments: 16, transfers: 3 },
              { date: '2024-01-07', appointments: 24, transfers: 7 }
            ],
            weekly: [
              { week: 'Semana 1', appointments: 87, transfers: 25 },
              { week: 'Semana 2', appointments: 94, transfers: 28 },
              { week: 'Semana 3', appointments: 102, transfers: 31 },
              { week: 'Semana 4', appointments: 89, transfers: 26 }
            ],
            monthly: [
              { month: 'Jan', appointments: 342, transfers: 98 },
              { month: 'Fev', appointments: 378, transfers: 112 },
              { month: 'Mar', appointments: 401, transfers: 125 }
            ]
          }
        });
  }, [selectedPeriod, selectedFilter, selectedAgent, dateRange]);

  // Funções de exportação
  const exportToCSV = () => {
    const csvData = reportData.trends.daily.map(day => ({
      Data: day.date,
      'Agendamentos': day.appointments,
      'Transferidos': day.transfers,
      'Taxa de Conversão': `${Math.round((day.appointments / (day.appointments + day.transfers)) * 100)}%`,
      'Eficiência': `${Math.round((day.appointments / day.appointments) * 100)}%`
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
        { 'Métrica': 'Agendamentos Totais', 'Valor': reportData.appointments.total },
        { 'Métrica': 'Agendamentos Realizados', 'Valor': reportData.appointments.completed },
        { 'Métrica': 'Agendamentos Cancelados', 'Valor': reportData.appointments.cancelled },
        { 'Métrica': 'Taxa de Conversão', 'Valor': `${reportData.appointments.conversionRate}%` }
      ],
      'Procedimentos': [
        { 'Métrica': 'Total', 'Valor': reportData.procedures.total },
        { 'Métrica': 'Consulta Médica', 'Valor': reportData.procedures.byType[0]?.count || 0 },
        { 'Métrica': 'Exame Laboratorial', 'Valor': reportData.procedures.byType[1]?.count || 0 },
        { 'Métrica': 'Exame de Imagem', 'Valor': reportData.procedures.byType[2]?.count || 0 }
      ],
      'Dados Diários': reportData.trends.daily.map(day => ({
        'Data': day.date,
        'Agendamentos': day.appointments,
        'Transferidos': day.transfers,
        'Taxa de Conversão': `${Math.round((day.appointments / (day.appointments + day.transfers)) * 100)}%`,
        'Eficiência': `${Math.round((day.appointments / day.appointments) * 100)}%`
      }))
    };

    // Simular download
    alert('Exportação Excel simulada - em produção seria implementada com biblioteca xlsx');
  };

  const exportToPDF = () => {
    // Simular exportação PDF (em produção usaria uma biblioteca como jsPDF)
    const pdfData = {
      title: 'Relatório de Agendamentos',
      period: selectedPeriod,
      filter: selectedFilter,
      metrics: reportData.appointments,
      trends: reportData.trends.daily.slice(-7),
      procedures: reportData.procedures.byType,
      units: reportData.units.byUnit
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

  const UnitPerformanceCard = ({ unit }) => (
    <div className="agent-card">
      <div className="agent-info">
        <div className="agent-avatar">
          <span>{unit.name.split(' ').map(n => n[0]).join('')}</span>
        </div>
        <div className="agent-details">
          <h4>{unit.name}</h4>
          <p>{unit.appointments} agendamentos</p>
        </div>
      </div>
      <div className="agent-metrics">
        <div className="metric">
          <Activity size={14} />
          {unit.percentage}%
        </div>
        <div className="metric">
          <Target size={14} />
          {unit.appointments} total
        </div>
      </div>
    </div>
  );



  return (
    <div className="reports-container">
      {/* Header */}
      <div className="reports-header">
        <div className="header-content">
          <p>Relatórios de Agendamentos e Procedimentos Médicos</p>
        </div>
        <div className="header-actions">
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
                <label>Procedimento</label>
                <select 
                  value={selectedAgent} 
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">Todos os procedimentos</option>
                  <option value="consulta">Consulta Médica</option>
                  <option value="laboratorio">Exame Laboratorial</option>
                  <option value="imagem">Exame de Imagem</option>
                  <option value="cirurgico">Procedimento Cirúrgico</option>
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
          title="Agendamentos Totais"
          value={reportData.appointments.total}
          subtitle="Período selecionado"
          color="blue"
          trend={12}
        />
        <MetricCard
          icon={CheckCircle}
          title="Agendamentos Realizados"
          value={reportData.appointments.completed}
          subtitle="Concluídos com sucesso"
          color="green"
          trend={8}
        />
        <MetricCard
          icon={Activity}
          title="Taxa de Conversão"
          value={`${reportData.appointments.conversionRate}%`}
          subtitle="Contatos → Agendamentos"
          color="purple"
          trend={5}
        />
        <MetricCard
          icon={Users}
          title="Transferidos para Humano"
          value={reportData.transfers.botToHuman}
          subtitle="Conversas complexas"
          color="orange"
          trend={15}
        />
      </div>

      {/* Filtros */}
      <div className="reports-filters">
        <div className="filter-group">
          <Filter size={16} />
                      <select 
              value={selectedFilter} 
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">Todos os Agendamentos</option>
              <option value="completed">Agendamentos Realizados</option>
              <option value="cancelled">Agendamentos Cancelados</option>
              <option value="pending">Agendamentos Pendentes</option>
              <option value="transferred">Transferidos para Humano</option>
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
      </div>

      {/* Gráficos e Análises */}
      <div className="charts-grid">
        {/* Agendamentos por Período */}
        <ChartCard 
          title="Evolução de Agendamentos" 
          className="chart-large" 
          icon="📊"
          description="Gráfico de agendamentos por período"
        >
          <div className="chart-data">
            {reportData.trends.daily.slice(-7).map((day, index) => (
              <div key={index} className="data-point">
                <span className="date">{day.date}</span>
                <span className="value">{day.appointments} agendamentos</span>
              </div>
            ))}
          </div>
        </ChartCard>

        {/* Distribuição de Procedimentos */}
        <ChartCard 
          title="Distribuição de Procedimentos" 
          icon="🏥"
          description="Tipos de procedimentos mais solicitados"
        >
          <div className="distribution-stats">
            {reportData.procedures.byType.slice(0, 4).map((procedure, index) => (
              <div key={index} className="stat-item">
                <span className="stat-label">{procedure.name}</span>
                <span className="stat-value">{procedure.count}</span>
            </div>
            ))}
          </div>
        </ChartCard>

        {/* Performance das Unidades */}
        <ChartCard title="Performance das Unidades" className="chart-large">
          <div className="agents-list">
            {reportData.units.byUnit.map((unit, index) => (
              <UnitPerformanceCard key={index} unit={unit} />
            ))}
          </div>
        </ChartCard>

        {/* Eficiência da Fila Global */}
        <ChartCard title="Eficiência da Fila Global">
          <div className="response-time-card">
            <div className="time-display">
              <Clock size={32} />
              <span className="time-value">{reportData.transfers.efficiency}%</span>
            </div>
            <p className="time-description">Taxa de resolução da fila</p>
            <div className="queue-stats">
              <span>Tempo médio na fila: {reportData.transfers.queueTime} min</span>
            </div>
          </div>
        </ChartCard>
      </div>

      {/* Tabela de Dados Detalhados */}
      <div className="detailed-data">
        <div className="data-header">
          <h2>Dados Detalhados de Agendamentos</h2>
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
                <th>Agendamentos</th>
                <th>Transferidos</th>
                <th>Taxa de Conversão</th>
                <th>Eficiência</th>
              </tr>
            </thead>
            <tbody>
              {reportData.trends.daily.slice(-7).map((day, index) => (
                <tr key={index}>
                  <td>{day.date}</td>
                  <td>{day.appointments}</td>
                  <td>{day.transfers}</td>
                  <td>{Math.round((day.appointments / (day.appointments + day.transfers)) * 100)}%</td>
                  <td>{Math.round((day.appointments / day.appointments) * 100)}%</td>
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