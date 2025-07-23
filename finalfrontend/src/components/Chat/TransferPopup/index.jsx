import React, { useState, useEffect } from 'react';
import { Users, X, ArrowRight, Upload, Search } from 'lucide-react';
import './TransferPopup.css';

const TransferPopup = ({ 
  isVisible, 
  onClose, 
  onTransfer, 
  onTransferToGlobalQueue,
  conversation 
}) => {
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [availableUsers, setAvailableUsers] = useState([]);

  // Simular lista de usuários disponíveis
  useEffect(() => {
    if (isVisible) {
      // Em produção, isso viria da API
      setAvailableUsers([
        { id: 'user1', name: 'João Silva', status: 'online', avatar: 'JS' },
        { id: 'user2', name: 'Maria Santos', status: 'online', avatar: 'MS' },
        { id: 'user3', name: 'Pedro Costa', status: 'offline', avatar: 'PC' },
        { id: 'user4', name: 'Ana Oliveira', status: 'online', avatar: 'AO' },
        { id: 'user5', name: 'Carlos Lima', status: 'online', avatar: 'CL' }
      ]);
    }
  }, [isVisible]);

  const filteredUsers = availableUsers.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    user.status === 'online'
  );

  const handleTransfer = async () => {
    if (!selectedUser) return;
    
    setLoading(true);
    try {
      await onTransfer(conversation.id, selectedUser.id);
      onClose();
    } catch (error) {
      console.error('Erro ao transferir conversa:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTransferToGlobalQueue = async () => {
    setLoading(true);
    try {
      await onTransferToGlobalQueue(conversation.id);
      onClose();
    } catch (error) {
      console.error('Erro ao enviar para fila global:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="transfer-popup-overlay">
      <div className="transfer-popup">
        <div className="transfer-popup-header">
          <h3>Transferir Conversa</h3>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="transfer-popup-content">
          <div className="conversation-info">
            <div className="conversation-avatar">
              {conversation?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="conversation-details">
              <h4>{conversation?.name || 'Conversa'}</h4>
              <p>{conversation?.phone || 'Número não disponível'}</p>
            </div>
          </div>

          <div className="search-section">
            <div className="search-box">
              <Search size={16} />
              <input
                type="text"
                placeholder="Pesquisar usuários..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div className="users-section">
            <h4>Usuários Disponíveis</h4>
            <div className="users-list">
              {filteredUsers.length === 0 ? (
                <div className="no-users">
                  <Users size={32} />
                  <p>Nenhum usuário online encontrado</p>
                </div>
              ) : (
                filteredUsers.map((user) => (
                  <div
                    key={user.id}
                    className={`user-item ${selectedUser?.id === user.id ? 'selected' : ''}`}
                    onClick={() => setSelectedUser(user)}
                  >
                    <div className="user-avatar">
                      <span>{user.avatar}</span>
                      <div className={`status-dot ${user.status}`} />
                    </div>
                    <div className="user-info">
                      <span className="user-name">{user.name}</span>
                      <span className="user-status">{user.status}</span>
                    </div>
                    {selectedUser?.id === user.id && (
                      <div className="selected-indicator">
                        <ArrowRight size={16} />
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="global-queue-section">
            <h4>Ou enviar para fila global</h4>
            <button
              className="global-queue-btn"
              onClick={handleTransferToGlobalQueue}
              disabled={loading}
            >
              <Upload size={16} />
              Enviar para Fila Global
            </button>
          </div>
        </div>

        <div className="transfer-popup-actions">
          <button className="cancel-btn" onClick={onClose}>
            Cancelar
          </button>
          <button
            className="transfer-btn"
            onClick={handleTransfer}
            disabled={!selectedUser || loading}
          >
            {loading ? 'Transferindo...' : 'Transferir'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TransferPopup; 