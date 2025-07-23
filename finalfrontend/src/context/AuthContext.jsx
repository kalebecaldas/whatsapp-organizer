import React, { createContext, useContext, useState, useEffect } from 'react';

// Definição dos níveis de acesso
export const USER_ROLES = {
  ADMIN: 'admin',
  SUPERVISOR: 'supervisor',
  ATTENDANT: 'attendant'
};

// Permissões por nível de acesso
export const PERMISSIONS = {
  [USER_ROLES.ADMIN]: {
    dashboard: 'full',
    messages: 'full',
    reports: 'full',
    users: 'full',
    settings: 'full',
    chat: 'full'
  },
  [USER_ROLES.SUPERVISOR]: {
    dashboard: 'limited',
    messages: 'full',
    reports: 'full',
    users: 'read',
    settings: 'read',
    chat: 'limited'
  },
  [USER_ROLES.ATTENDANT]: {
    dashboard: 'basic',
    messages: 'full',
    reports: 'none',
    users: 'none',
    settings: 'none',
    chat: 'full'
  }
};

// Configurações de dashboard por perfil
export const DASHBOARD_CONFIG = {
  [USER_ROLES.ADMIN]: {
    showStats: true,
    showRecentMessages: true,
    showUserActivity: true,
    showSystemStatus: true,
    showQuickActions: true,
    showPendingTasks: true
  },
  [USER_ROLES.SUPERVISOR]: {
    showStats: true,
    showRecentMessages: true,
    showUserActivity: false,
    showSystemStatus: true,
    showQuickActions: true,
    showPendingTasks: true
  },
  [USER_ROLES.ATTENDANT]: {
    showStats: false,
    showRecentMessages: true,
    showUserActivity: false,
    showSystemStatus: false,
    showQuickActions: true,
    showPendingTasks: false
  }
};

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [permissions, setPermissions] = useState({});
  const [dashboardConfig, setDashboardConfig] = useState({});

  // Verificar se o usuário tem permissão para uma funcionalidade
  const hasPermission = (feature, action = 'read') => {
    if (!user || !permissions[feature]) return false;
    
    const userPermission = permissions[feature];
    if (userPermission === 'full') return true;
    if (userPermission === 'limited' && action === 'read') return true;
    if (userPermission === 'read' && action === 'read') return true;
    
    return false;
  };

  // Verificar se o usuário pode acessar uma página
  const canAccess = (page) => {
    return hasPermission(page, 'read');
  };

  // Obter configuração do dashboard para o usuário
  const getDashboardConfig = () => {
    return dashboardConfig;
  };

  // Login com validação de credenciais
  const login = async (email, password) => {
    try {
      setLoading(true);
      
      // Simular API call - em produção, isso seria uma chamada real
      const response = await simulateLoginAPI(email, password);
      
      if (response.success) {
        const userData = response.user;
        const userPermissions = PERMISSIONS[userData.role] || {};
        const userDashboardConfig = DASHBOARD_CONFIG[userData.role] || {};
        
        setUser(userData);
        setPermissions(userPermissions);
        setDashboardConfig(userDashboardConfig);
        
        // Salvar no localStorage
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('permissions', JSON.stringify(userPermissions));
        localStorage.setItem('dashboardConfig', JSON.stringify(userDashboardConfig));
        
        return { success: true };
      } else {
        return { success: false, error: response.error };
      }
    } catch (error) {
      return { success: false, error: 'Erro de conexão' };
    } finally {
      setLoading(false);
    }
  };

  // Simular API de login com diferentes usuários
  const simulateLoginAPI = async (email, password) => {
    // Simular delay de rede
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const users = {
      'admin@whatsapp.com': {
        id: 1,
        name: 'Administrador',
        email: 'admin@whatsapp.com',
        role: USER_ROLES.ADMIN,
        avatar: null
      },
      'supervisor@whatsapp.com': {
        id: 2,
        name: 'Supervisor',
        email: 'supervisor@whatsapp.com',
        role: USER_ROLES.SUPERVISOR,
        avatar: null
      },
      'atendente@whatsapp.com': {
        id: 3,
        name: 'Atendente',
        email: 'atendente@whatsapp.com',
        role: USER_ROLES.ATTENDANT,
        avatar: null
      }
    };
    
    const user = users[email];
    
    if (user && password === '123456') {
      return { success: true, user };
    } else {
      return { success: false, error: 'Credenciais inválidas' };
    }
  };

  const logout = () => {
    setUser(null);
    setPermissions({});
    setDashboardConfig({});
    localStorage.removeItem('user');
    localStorage.removeItem('permissions');
    localStorage.removeItem('dashboardConfig');
  };

  // Verificar se o usuário está logado
  const isAuthenticated = () => {
    return !!user;
  };

  // Carregar dados do usuário do localStorage
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    const savedPermissions = localStorage.getItem('permissions');
    const savedDashboardConfig = localStorage.getItem('dashboardConfig');
    
    if (savedUser && savedPermissions && savedDashboardConfig) {
      try {
        setUser(JSON.parse(savedUser));
        setPermissions(JSON.parse(savedPermissions));
        setDashboardConfig(JSON.parse(savedDashboardConfig));
      } catch (error) {
        console.error('Erro ao carregar dados do usuário:', error);
        logout();
      }
    }
    
    setLoading(false);
  }, []);

  const value = {
    user,
    loading,
    permissions,
    dashboardConfig,
    login,
    logout,
    isAuthenticated,
    hasPermission,
    canAccess,
    getDashboardConfig,
    USER_ROLES
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 