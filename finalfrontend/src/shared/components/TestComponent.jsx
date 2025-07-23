import { useState, useEffect } from 'react';
import { whatsappAPI } from '../utils/api';

const TestComponent = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const testAPI = async () => {
      try {
        console.log('🧪 Testando API...');
        const response = await whatsappAPI.getConversations();
        console.log('✅ API funcionando:', response.data);
        setData(response.data);
      } catch (err) {
        console.error('❌ Erro na API:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    testAPI();
  }, []);

  if (loading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error}</div>;

  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', margin: '10px' }}>
      <h3>Teste da API</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

export default TestComponent; 