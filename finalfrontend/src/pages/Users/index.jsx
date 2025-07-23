import React, { useState, useEffect } from 'react';
import { 
  Users as UsersIcon, 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Eye, 
  MoreVertical,
  UserPlus,
  Shield,
  User,
  Mail,
  Phone,
  Calendar,
  CheckCircle,
  XCircle,
  AlertCircle,
  X
} from 'lucide-react';
import './Users.css';

// Dados simulados de usuários
const mockUsers = [
  {
    id: 1,
    name: 'João Silva',
    email: 'joao.silva@empresa.com',
    phone: '(11) 99999-9999',
    role: 'admin',
    status: 'active',
    createdAt: '2024-01-15',
    lastLogin: '2024-01-20 14:30'
  },
  {
    id: 2,
    name: 'Maria Santos',
    email: 'maria.santos@empresa.com',
    phone: '(11) 88888-8888',
    role: 'manager',
    status: 'active',
    createdAt: '2024-01-10',
    lastLogin: '2024-01-20 10:15'
  },
  {
    id: 3,
    name: 'Pedro Costa',
    email: 'pedro.costa@empresa.com',
    phone: '(11) 77777-7777',
    role: 'user',
    status: 'inactive',
    createdAt: '2024-01-05',
    lastLogin: '2024-01-15 16:45'
  },
  {
    id: 4,
    name: 'Ana Oliveira',
    email: 'ana.oliveira@empresa.com',
    phone: '(11) 66666-6666',
    role: 'user',
    status: 'active',
    createdAt: '2024-01-12',
    lastLogin: '2024-01-20 09:20'
  },
  {
    id: 5,
    name: 'Carlos Ferreira',
    email: 'carlos.ferreira@empresa.com',
    phone: '(11) 55555-5555',
    role: 'user',
    status: 'active',
    createdAt: '2024-01-08',
    lastLogin: '2024-01-19 15:30'
  },
  {
    id: 6,
    name: 'Lucia Mendes',
    email: 'lucia.mendes@empresa.com',
    phone: '(11) 44444-4444',
    role: 'manager',
    status: 'active',
    createdAt: '2024-01-06',
    lastLogin: '2024-01-20 11:45'
  },
  {
    id: 7,
    name: 'Roberto Almeida',
    email: 'roberto.almeida@empresa.com',
    phone: '(11) 33333-3333',
    role: 'user',
    status: 'inactive',
    createdAt: '2024-01-03',
    lastLogin: '2024-01-14 09:15'
  },
  {
    id: 8,
    name: 'Fernanda Lima',
    email: 'fernanda.lima@empresa.com',
    phone: '(11) 22222-2222',
    role: 'user',
    status: 'active',
    createdAt: '2024-01-11',
    lastLogin: '2024-01-20 08:30'
  },
  {
    id: 9,
    name: 'Marcos Santos',
    email: 'marcos.santos@empresa.com',
    phone: '(11) 11111-1111',
    role: 'admin',
    status: 'active',
    createdAt: '2024-01-07',
    lastLogin: '2024-01-20 16:20'
  },
  {
    id: 10,
    name: 'Patricia Costa',
    email: 'patricia.costa@empresa.com',
    phone: '(11) 00000-0000',
    role: 'user',
    status: 'active',
    createdAt: '2024-01-09',
    lastLogin: '2024-01-20 13:10'
  }
];

const Users = () => {
  const [users, setUsers] = useState(mockUsers);
  const [filteredUsers, setFilteredUsers] = useState(mockUsers);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    role: 'user',
    status: 'active'
  });



  useEffect(() => {
    filterUsers();
  }, [searchTerm, selectedFilter, users]);

  const filterUsers = () => {
    let filtered = users;

    // Filtrar por termo de busca
    if (searchTerm) {
      filtered = filtered.filter(user =>
        user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.phone.includes(searchTerm)
      );
    }

    // Filtrar por status
    if (selectedFilter !== 'all') {
      filtered = filtered.filter(user => user.status === selectedFilter);
    }

    setFilteredUsers(filtered);
  };

  const handleAddUser = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      role: 'user',
      status: 'active'
    });
    setShowAddModal(true);
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setFormData({
      name: user.name,
      email: user.email,
      phone: user.phone,
      role: user.role,
      status: user.status
    });
    setShowEditModal(true);
  };

  const handleViewUser = (user) => {
    setSelectedUser(user);
    setFormData({
      name: user.name,
      email: user.email,
      phone: user.phone,
      role: user.role,
      status: user.status
    });
    setShowEditModal(true);
  };

  const handleDeleteUser = (user) => {
    setSelectedUser(user);
    setShowDeleteModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simular delay de API
    await new Promise(resolve => setTimeout(resolve, 800));
    
    if (showAddModal) {
      // Adicionar novo usuário
      const newUser = {
        id: users.length + 1,
        ...formData,
        createdAt: new Date().toISOString().split('T')[0],
        lastLogin: '-'
      };
      setUsers([...users, newUser]);
      setShowAddModal(false);
    } else if (showEditModal) {
      // Editar usuário existente
      const updatedUsers = users.map(user =>
        user.id === selectedUser.id ? { ...user, ...formData } : user
      );
      setUsers(updatedUsers);
      setShowEditModal(false);
    }
    
    setIsSubmitting(false);
  };

  const confirmDelete = async () => {
    setIsSubmitting(true);
    
    // Simular delay de API
    await new Promise(resolve => setTimeout(resolve, 600));
    
    const updatedUsers = users.filter(user => user.id !== selectedUser.id);
    setUsers(updatedUsers);
    setShowDeleteModal(false);
    setIsSubmitting(false);
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <Shield size={16} className="role-icon admin" />;
      case 'manager':
        return <User size={16} className="role-icon manager" />;
      default:
        return <User size={16} className="role-icon user" />;
    }
  };

  const getStatusBadge = (status) => {
    return status === 'active' ? (
      <span className="status-badge active">
        <CheckCircle size={12} />
        Ativo
      </span>
    ) : (
      <span className="status-badge inactive">
        <XCircle size={12} />
        Inativo
      </span>
    );
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'admin':
        return 'Administrador';
      case 'manager':
        return 'Gerente';
      default:
        return 'Usuário';
    }
  };



  return (
    <div className="users-container">
      <div className="users-header">
        <div className="header-content">
          <div className="header-title">
            <UsersIcon size={24} />
            <h1>Gerenciamento de Usuários</h1>
          </div>
        </div>
        <button 
          className="add-user-btn" 
          onClick={handleAddUser}
          title="Adicionar novo usuário ao sistema"
        >
          <Plus size={16} />
          Adicionar Usuário
        </button>
      </div>

      <div className="users-stats">
        <div className="stat-card">
          <div className="stat-icon">
            <UsersIcon size={20} />
          </div>
          <div className="stat-content">
            <span className="stat-number">{users.length}</span>
            <span className="stat-label">Total de Usuários</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon active">
            <CheckCircle size={20} />
          </div>
          <div className="stat-content">
            <span className="stat-number">
              {users.filter(u => u.status === 'active').length}
            </span>
            <span className="stat-label">Usuários Ativos</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon inactive">
            <XCircle size={20} />
          </div>
          <div className="stat-content">
            <span className="stat-number">
              {users.filter(u => u.status === 'inactive').length}
            </span>
            <span className="stat-label">Usuários Inativos</span>
          </div>
        </div>
      </div>

      <div className="users-filters">
        <div className="search-container">
          <Search size={16} />
          <input
            type="text"
            placeholder="Buscar usuários por nome, email ou telefone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-container">
          <Filter size={16} />
          <select
            value={selectedFilter}
            onChange={(e) => setSelectedFilter(e.target.value)}
          >
            <option value="all">Todos os status</option>
            <option value="active">Ativos</option>
            <option value="inactive">Inativos</option>
          </select>
        </div>
      </div>

      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>Usuário</th>
              <th>Contato</th>
              <th>Função</th>
              <th>Status</th>
              <th>Último Login</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map(user => (
              <tr key={user.id}>
                <td>
                  <div className="user-info">
                    <div className="user-avatar">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="user-details">
                      <span className="user-name">{user.name}</span>
                      <span className="user-email">{user.email}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div className="contact-info">
                    <span className="phone">{user.phone}</span>
                  </div>
                </td>
                <td>
                  <div className="role-info">
                    {getRoleIcon(user.role)}
                    <span>{getRoleLabel(user.role)}</span>
                  </div>
                </td>
                <td>
                  {getStatusBadge(user.status)}
                </td>
                <td>
                  <span className="last-login">{user.lastLogin}</span>
                </td>
                <td>
                  <div className="actions">
                    <button
                      className="action-btn view"
                      title="Visualizar detalhes do usuário"
                      onClick={() => handleViewUser(user)}
                    >
                      <Eye size={16} />
                    </button>
                    <button
                      className="action-btn edit"
                      title="Editar usuário"
                      onClick={() => handleEditUser(user)}
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      className="action-btn delete"
                      title="Excluir usuário"
                      onClick={() => handleDeleteUser(user)}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal Adicionar/Editar Usuário */}
      {(showAddModal || showEditModal) && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>{showAddModal ? 'Adicionar Novo Usuário' : 'Editar Usuário'}</h2>
              <button
                className="close-btn"
                onClick={() => {
                  setShowAddModal(false);
                  setShowEditModal(false);
                }}
                title="Fechar modal"
              >
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="modal-form">
              <div className="form-group">
                <label htmlFor="name">Nome Completo *</label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                  placeholder="Digite o nome completo"
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email *</label>
                <input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                  placeholder="Digite o email"
                />
              </div>
              <div className="form-group">
                <label htmlFor="phone">Telefone *</label>
                <input
                  type="tel"
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  required
                  placeholder="(11) 99999-9999"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="role">Função *</label>
                  <select
                    id="role"
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                  >
                    <option value="user">Usuário</option>
                    <option value="manager">Gerente</option>
                    <option value="admin">Administrador</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="status">Status *</label>
                  <select
                    id="status"
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                  >
                    <option value="active">Ativo</option>
                    <option value="inactive">Inativo</option>
                  </select>
                </div>
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => {
                    setShowAddModal(false);
                    setShowEditModal(false);
                  }}
                  disabled={isSubmitting}
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="save-btn"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <div className="spinner-small"></div>
                      {showAddModal ? 'Adicionando...' : 'Salvando...'}
                    </>
                  ) : (
                    showAddModal ? 'Adicionar Usuário' : 'Salvar Alterações'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Confirmar Exclusão */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal delete-modal">
            <div className="modal-header">
              <h2>Confirmar Exclusão</h2>
              <button
                className="close-btn"
                onClick={() => setShowDeleteModal(false)}
                title="Cancelar exclusão"
              >
                <X size={20} />
              </button>
            </div>
            <div className="modal-content">
              <AlertCircle size={48} className="warning-icon" />
              <h3>Excluir usuário</h3>
              <p>Tem certeza que deseja excluir o usuário <strong>{selectedUser?.name}</strong>?</p>
              <div className="warning-details">
                <p>• Esta ação não pode ser desfeita</p>
                <p>• O usuário perderá acesso ao sistema</p>
                <p>• Todos os dados associados serão removidos</p>
              </div>
            </div>
            <div className="modal-actions">
              <button
                className="cancel-btn"
                onClick={() => setShowDeleteModal(false)}
                disabled={isSubmitting}
              >
                Cancelar
              </button>
              <button
                className="delete-btn"
                onClick={confirmDelete}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div className="spinner-small"></div>
                    Excluindo...
                  </>
                ) : (
                  'Excluir Usuário'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users; 