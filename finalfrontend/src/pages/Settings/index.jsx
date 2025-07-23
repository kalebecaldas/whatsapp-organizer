import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Shield, 
  Users, 
  Key, 
  Bell, 
  Database,
  Server,
  Globe,
  Save,
  Eye,
  EyeOff
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './Settings.css';

const Settings = () => {
  const { user, hasPermission } = useAuth();
  const [activeTab, setActiveTab] = useState('general');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const canEditSettings = hasPermission('settings', 'write');

  const tabs = [
    { id: 'general', label: 'Geral', icon: SettingsIcon },
    { id: 'security', label: 'Segurança', icon: Shield },
    { id: 'permissions', label: 'Permissões', icon: Users },
    { id: 'system', label: 'Sistema', icon: Server }
  ];

  const renderGeneralTab = () => (
    <div className="settings-section">
      <h3>Configurações Gerais</h3>
      
      <div className="setting-group">
        <label className="setting-label">
          <span>Nome da Empresa</span>
          <input 
            type="text" 
            defaultValue="WhatsApp Organizer" 
            disabled={!canEditSettings}
          />
        </label>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Email de Contato</span>
          <input 
            type="email" 
            defaultValue="contato@empresa.com" 
            disabled={!canEditSettings}
          />
        </label>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Fuso Horário</span>
          <select defaultValue="America/Sao_Paulo" disabled={!canEditSettings}>
            <option value="America/Sao_Paulo">Brasília (GMT-3)</option>
            <option value="America/Manaus">Manaus (GMT-4)</option>
            <option value="America/Belem">Belém (GMT-3)</option>
          </select>
        </label>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Idioma</span>
          <select defaultValue="pt-BR" disabled={!canEditSettings}>
            <option value="pt-BR">Português (Brasil)</option>
            <option value="en-US">English (US)</option>
            <option value="es-ES">Español</option>
          </select>
        </label>
      </div>
    </div>
  );

  const renderSecurityTab = () => (
    <div className="settings-section">
      <h3>Configurações de Segurança</h3>
      
      <div className="setting-group">
        <label className="setting-label">
          <span>Autenticação de Dois Fatores</span>
          <div className="toggle-switch">
            <input type="checkbox" id="2fa" disabled={!canEditSettings} />
            <label htmlFor="2fa"></label>
          </div>
        </label>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Tempo de Sessão (minutos)</span>
          <input 
            type="number" 
            defaultValue="30" 
            min="5" 
            max="480"
            disabled={!canEditSettings}
          />
        </label>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Log de Atividades</span>
          <div className="toggle-switch">
            <input type="checkbox" id="activity-log" defaultChecked disabled={!canEditSettings} />
            <label htmlFor="activity-log"></label>
          </div>
        </label>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Notificações de Segurança</span>
          <div className="toggle-switch">
            <input type="checkbox" id="security-notifications" defaultChecked disabled={!canEditSettings} />
            <label htmlFor="security-notifications"></label>
          </div>
        </label>
      </div>
    </div>
  );

  const renderPermissionsTab = () => (
    <div className="settings-section">
      <h3>Configurações de Permissões</h3>
      
      <div className="permissions-info">
        <div className="permission-card">
          <div className="permission-header">
            <Users size={20} />
            <h4>Administrador</h4>
          </div>
          <div className="permission-features">
            <span>✓ Acesso total ao sistema</span>
            <span>✓ Gerenciar usuários</span>
            <span>✓ Configurações avançadas</span>
            <span>✓ Relatórios completos</span>
          </div>
        </div>

        <div className="permission-card">
          <div className="permission-header">
            <Shield size={20} />
            <h4>Supervisor</h4>
          </div>
          <div className="permission-features">
            <span>✓ Relatórios e mensagens</span>
            <span>✓ Visualizar usuários</span>
            <span>✓ Dashboard limitado</span>
            <span>✓ Configurações básicas</span>
          </div>
        </div>

        <div className="permission-card">
          <div className="permission-header">
            <Bell size={20} />
            <h4>Atendente</h4>
          </div>
          <div className="permission-features">
            <span>✓ Mensagens e chat</span>
            <span>✓ Dashboard básico</span>
            <span>✗ Sem acesso a relatórios</span>
            <span>✗ Sem gerenciamento</span>
          </div>
        </div>
      </div>

      {canEditSettings && (
        <div className="setting-group">
          <button className="btn-primary">
            <Save size={16} />
            Configurar Permissões Personalizadas
          </button>
        </div>
      )}
    </div>
  );

  const renderSystemTab = () => (
    <div className="settings-section">
      <h3>Informações do Sistema</h3>
      
      <div className="system-info">
        <div className="info-card">
          <div className="info-header">
            <Database size={20} />
            <h4>Banco de Dados</h4>
          </div>
          <div className="info-content">
            <p><strong>Status:</strong> <span className="status-online">Online</span></p>
            <p><strong>Versão:</strong> PostgreSQL 14.5</p>
            <p><strong>Uso:</strong> 2.3 GB / 10 GB</p>
          </div>
        </div>

        <div className="info-card">
          <div className="info-header">
            <Server size={20} />
            <h4>Servidor</h4>
          </div>
          <div className="info-content">
            <p><strong>Status:</strong> <span className="status-online">Online</span></p>
            <p><strong>CPU:</strong> 45%</p>
            <p><strong>RAM:</strong> 3.2 GB / 8 GB</p>
          </div>
        </div>

        <div className="info-card">
          <div className="info-header">
            <Globe size={20} />
            <h4>WhatsApp API</h4>
          </div>
          <div className="info-content">
            <p><strong>Status:</strong> <span className="status-online">Conectado</span></p>
            <p><strong>Mensagens:</strong> 1,234 hoje</p>
            <p><strong>Taxa de resposta:</strong> 98.5%</p>
          </div>
        </div>
      </div>

      <div className="setting-group">
        <button 
          className="btn-secondary"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? <EyeOff size={16} /> : <Eye size={16} />}
          {showAdvanced ? 'Ocultar' : 'Mostrar'} Configurações Avançadas
        </button>
      </div>

      {showAdvanced && (
        <div className="advanced-settings">
          <h4>Configurações Avançadas</h4>
          
          <div className="setting-group">
            <label className="setting-label">
              <span>Log Level</span>
              <select defaultValue="info" disabled={!canEditSettings}>
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warn">Warning</option>
                <option value="error">Error</option>
              </select>
            </label>
          </div>

          <div className="setting-group">
            <label className="setting-label">
              <span>Backup Automático</span>
              <div className="toggle-switch">
                <input type="checkbox" id="auto-backup" defaultChecked disabled={!canEditSettings} />
                <label htmlFor="auto-backup"></label>
              </div>
            </label>
          </div>

          <div className="setting-group">
            <label className="setting-label">
              <span>Intervalo de Backup (horas)</span>
              <input 
                type="number" 
                defaultValue="24" 
                min="1" 
                max="168"
                disabled={!canEditSettings}
              />
            </label>
          </div>
        </div>
      )}
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralTab();
      case 'security':
        return renderSecurityTab();
      case 'permissions':
        return renderPermissionsTab();
      case 'system':
        return renderSystemTab();
      default:
        return renderGeneralTab();
    }
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>Configurações</h1>
        <p>Gerencie as configurações do sistema</p>
      </div>

      <div className="settings-container">
        <div className="settings-sidebar">
          <nav className="settings-nav">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <Icon size={20} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="settings-content">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default Settings; 