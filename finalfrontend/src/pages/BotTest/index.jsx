import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const BotTest = () => {
  const [numero, setNumero] = useState('');
  const [mensagem, setMensagem] = useState('');
  const [historico, setHistorico] = useState([]);
  const [loading, setLoading] = useState(false);
  const [debug, setDebug] = useState('');
  const chatRef = useRef(null);

  // Auto-scroll para a última mensagem
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [historico]);

  const enviarMensagem = async () => {
    if (!numero || !mensagem) {
      setDebug('Erro: Número e mensagem são obrigatórios');
      return;
    }
    
    setLoading(true);
    setDebug(`Enviando para /api/test-bot: ${JSON.stringify({ numero, mensagem })}`);
    
    try {
      const response = await axios.post('/api/test-bot', {
        numero,
        mensagem,
      });
      
      setDebug(`Resposta recebida: ${JSON.stringify(response.data)}`);
      
      setHistorico((h) => [
        ...h,
        { role: 'user', content: mensagem, timestamp: new Date().toLocaleTimeString() },
        { role: 'bot', content: response.data.resposta, timestamp: new Date().toLocaleTimeString() },
      ]);
      setMensagem('');
    } catch (err) {
      setDebug(`Erro na requisição: ${err.message} - ${JSON.stringify(err.response?.data)}`);
      setHistorico((h) => [
        ...h,
        { role: 'user', content: mensagem, timestamp: new Date().toLocaleTimeString() },
        { role: 'bot', content: '❌ Erro ao enviar mensagem. Verifique o console.', timestamp: new Date().toLocaleTimeString() },
      ]);
    }
    setLoading(false);
  };

  const limparHistorico = () => {
    setHistorico([]);
    setDebug('');
  };

  return (
    <div style={{
      maxWidth: 800,
      margin: '20px auto',
      padding: '24px',
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      border: '1px solid #e1e5e9'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        paddingBottom: '16px',
        borderBottom: '2px solid #f0f0f0'
      }}>
        <h2 style={{ 
          margin: 0, 
          color: '#2c3e50',
          fontSize: '24px',
          fontWeight: '600'
        }}>
          🤖 Teste do Bot IAAM
        </h2>
        <button 
          onClick={limparHistorico}
          style={{
            padding: '8px 16px',
            backgroundColor: '#e74c3c',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Limpar Chat
        </button>
      </div>

      {/* Configuração do Número */}
      <div style={{
        marginBottom: '20px',
        padding: '16px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        border: '1px solid #e9ecef'
      }}>
        <label style={{
          display: 'block',
          marginBottom: '8px',
          fontWeight: '600',
          color: '#495057'
        }}>
          📱 Número do Paciente:
        </label>
        <input
          type="text"
          value={numero}
          onChange={e => setNumero(e.target.value)}
          placeholder="Ex: 92991234567"
          style={{
            width: '100%',
            padding: '12px',
            border: '1px solid #ced4da',
            borderRadius: '6px',
            fontSize: '16px',
            boxSizing: 'border-box'
          }}
        />
      </div>

      {/* Área do Chat */}
      <div style={{
        marginBottom: '20px',
        height: '400px',
        backgroundColor: '#f8f9fa',
        padding: '16px',
        borderRadius: '8px',
        border: '1px solid #e9ecef',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px'
      }} ref={chatRef}>
        {historico.length === 0 ? (
          <div style={{
            textAlign: 'center',
            color: '#6c757d',
            fontStyle: 'italic',
            marginTop: '50px'
          }}>
            💬 Digite uma mensagem para começar o teste...
          </div>
        ) : (
          historico.map((msg, idx) => (
            <div key={idx} style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '8px'
            }}>
              <div style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                backgroundColor: msg.role === 'user' ? '#007bff' : '#ffffff',
                color: msg.role === 'user' ? '#ffffff' : '#212529',
                border: msg.role === 'user' ? 'none' : '1px solid #dee2e6',
                boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                wordWrap: 'break-word'
              }}>
                <div style={{ marginBottom: '4px' }}>
                  <strong>{msg.role === 'user' ? '👤 Você' : '🤖 Bot'}</strong>
                  <span style={{
                    fontSize: '12px',
                    color: msg.role === 'user' ? '#b3d9ff' : '#6c757d',
                    marginLeft: '8px'
                  }}>
                    {msg.timestamp}
                  </span>
                </div>
                <div style={{ whiteSpace: 'pre-wrap' }}>
                  {msg.content}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Área de Input */}
      <div style={{
        display: 'flex',
        gap: '12px',
        alignItems: 'flex-end'
      }}>
        <div style={{ flex: 1 }}>
          <input
            type="text"
            value={mensagem}
            onChange={e => setMensagem(e.target.value)}
            placeholder="Digite sua mensagem..."
            style={{
              width: '100%',
              padding: '14px 16px',
              border: '1px solid #ced4da',
              borderRadius: '8px',
              fontSize: '16px',
              boxSizing: 'border-box'
            }}
            onKeyDown={e => { if (e.key === 'Enter' && !loading) enviarMensagem(); }}
            disabled={loading}
          />
        </div>
        <button 
          onClick={enviarMensagem} 
          disabled={loading || !mensagem || !numero}
          style={{
            padding: '14px 24px',
            backgroundColor: loading || !mensagem || !numero ? '#6c757d' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading || !mensagem || !numero ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: '600',
            minWidth: '100px'
          }}
        >
          {loading ? '⏳ Enviando...' : '📤 Enviar'}
        </button>
      </div>

      {/* Debug Info */}
      {debug && (
        <div style={{
          marginTop: '20px',
          padding: '12px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffeaa7',
          borderRadius: '6px',
          fontSize: '12px',
          color: '#856404'
        }}>
          <strong>🔍 Debug:</strong> {debug}
        </div>
      )}
    </div>
  );
};

export default BotTest; 