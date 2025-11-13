import { createContext, useContext, useReducer, useEffect, useRef, useCallback } from 'react';
import { io } from 'socket.io-client';
import { whatsappAPI, sessionsAPI } from '../utils/api';

const ChatContext = createContext();

const initialState = {
  conversations: [],
  selectedConversation: null,
  messages: [],
  loading: false,
  error: null,
  unreadCounts: {},
  stats: null,
  socketConnected: false,
};

const chatReducer = (state, action) => {
  switch (action.type) {
    case 'SET_CONVERSATIONS':
      return { ...state, conversations: action.payload };
    case 'SET_SELECTED_CONVERSATION':
      return { ...state, selectedConversation: action.payload };
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload };
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'UPDATE_UNREAD_COUNT':
      return {
        ...state,
        unreadCounts: {
          ...state.unreadCounts,
          [action.payload.conversationId]: action.payload.count,
        },
      };
    case 'MARK_AS_READ':
      return {
        ...state,
        unreadCounts: {
          ...state.unreadCounts,
          [action.payload]: 0,
        },
      };
    case 'SET_STATS':
      return { ...state, stats: action.payload };
    case 'UPDATE_CONVERSATION':
      return {
        ...state,
        conversations: state.conversations.map(conv =>
          conv.phone === action.payload.phone ? action.payload : conv
        ),
      };
    case 'SET_SOCKET_CONNECTED':
      return { ...state, socketConnected: action.payload };
    case 'REMOVE_MESSAGE':
      return {
        ...state,
        messages: state.messages.filter(msg => msg.id !== action.payload),
      };
    default:
      return state;
  }
};

// Função para formatar o nome do contato
const formatContactName = (phone, name, originalName, formattedPhone) => {
  // Se temos um nome real (não "Paciente"), usamos ele + telefone formatado
  if (originalName && originalName !== 'Paciente' && !originalName.startsWith('Paciente')) {
    // Evita duplicidade: se formattedPhone já está no nome, não repete
    if (formattedPhone && originalName.includes(formattedPhone)) {
      return originalName;
    }
    return `${originalName} • ${formattedPhone || phone}`;
  }
  
  // Se não temos nome real, mostra só o telefone formatado
  return formattedPhone || phone;
};

// Função para gerar avatar baseado no nome ou telefone
const generateAvatar = (phone, name, backendAvatar) => {
  // Se o backend já forneceu um avatar, usa ele
  if (backendAvatar) {
    return backendAvatar;
  }
  
  // Se temos um nome real, usa a primeira letra
  if (name && name !== 'Paciente' && !name.startsWith('Paciente')) {
    const initial = name.charAt(0).toUpperCase();
    return `https://api.dicebear.com/7.x/initials/svg?seed=${initial}&backgroundColor=25D366&textColor=FFFFFF`;
  }
  
  // Se não temos nome, usa as últimas 2 letras do telefone
  const phoneDigits = phone.replace(/\D/g, '');
  const lastTwo = phoneDigits.slice(-2);
  return `https://api.dicebear.com/7.x/initials/svg?seed=${lastTwo}&backgroundColor=25D366&textColor=FFFFFF`;
};

// Função para comparar arrays de mensagens (deep compare)
function areMessagesEqual(a, b) {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (
      a[i].text !== b[i].text ||
      a[i].sender !== b[i].sender
    ) {
      return false;
    }
  }
  return true;
}

// Função para comparar arrays de conversas (deep compare)
function areConversationsEqual(a, b) {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (
      a[i].id !== b[i].id ||
      a[i].name !== b[i].name ||
      a[i].phone !== b[i].phone ||
      a[i].lastMessage !== b[i].lastMessage ||
      !areMessagesEqual(a[i].messages || [], b[i].messages || [])
    ) {
      return false;
    }
  }
  return true;
}

// Função utilitária para mapear mensagens do backend para o frontend
function mapMessages(messages, phone) {
  console.log('🔎 Mensagens recebidas para mapear:', messages);
  return (messages || []).map((msg, index) => {
    // Se já tem sender, não remapeia
    if (msg.sender) return msg;
    
    // PADRÃO WHATSAPP CORRETO:
    // direction='received' (mensagens recebidas do paciente) -> sender='received' (esquerda, branco)
    // direction='sent' (mensagens enviadas pelo bot/agente) -> sender='sent' (direita, verde)
    const sender = msg.direction === 'received' ? 'received' : 'sent';
    
    return {
      id: `${phone}-${index}-${msg.text}`,
      text: msg.text,
      sender,
      timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
    };
  });
}

export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  const pollingIntervalRef = useRef(null);
  const socketRef = useRef(null);
  const lastUpdateRef = useRef(0);

  // Inicializar WebSocket
  const initializeSocket = () => {
    try {
      socketRef.current = io('http://localhost:5001', {
        transports: ['polling', 'websocket'], // Polling primeiro para compatibilidade
        timeout: 20000,
        forceNew: true,
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });

      socketRef.current.on('connect', () => {
        console.log('🔌 WebSocket conectado');
        dispatch({ type: 'SET_SOCKET_CONNECTED', payload: true });
      });

      socketRef.current.on('disconnect', () => {
        console.log('🔌 WebSocket desconectado');
        dispatch({ type: 'SET_SOCKET_CONNECTED', payload: false });
      });

      socketRef.current.on('message_update', (data) => {
        console.log('📨 Atualização de mensagens recebida via WebSocket');
        
        // Extrair conversas do objeto correto que vem do backend
        const conversations = data.conversations || data;
        
        // Verificar se as conversas realmente mudaram antes de atualizar
        const currentConversations = state.conversations;
        const hasChanges = !areConversationsEqual(currentConversations, conversations);
        
        if (!hasChanges) {
          console.log('⏸️ Nenhuma mudança detectada, ignorando atualização WebSocket');
          return;
        }
        
        // Processar conversas imediatamente sem delays
        const formattedConversations = conversations.map(conv => {
          const formattedName = formatContactName(
            conv.phone, 
            conv.name, 
            conv.originalName, 
            conv.formattedPhone
          );
          const avatar = generateAvatar(conv.phone, conv.name, conv.avatar);
          
          // Mapear mensagens imediatamente
          const formattedMessages = conv.messages.map((msg, index) => ({
            id: `${conv.phone}-${index}-${msg.text}`, // ID estável baseado no conteúdo
            text: msg.text,
            sender: msg.direction === 'received' ? 'received' : 'sent', // PADRÃO WHATSAPP: received = esquerda (branco), sent = direita (verde)
            timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
          }));
          
          return {
            id: conv.phone,
            name: formattedName,
            originalName: conv.originalName || conv.name,
            phone: conv.phone,
            formattedPhone: conv.formattedPhone || conv.phone,
            lastMessage: conv.messages.length > 0 ? conv.messages[conv.messages.length - 1].text : 'Nenhuma mensagem',
            timestamp: new Date(),
            unread: 0,
            avatar: avatar,
            messages: formattedMessages,
            // Adicionar campos de transferência
            transferido_humano: conv.transferido_humano || false,
            atribuido_para: conv.atribuido_para || null,
            dados_transferencia: conv.dados_transferencia || null,
          };
        });

        // Atualizar estado imediatamente
        dispatch({ type: 'SET_CONVERSATIONS', payload: formattedConversations });
        
        // Atualizar mensagens da conversa selecionada imediatamente
        if (state.selectedConversation) {
          const selectedConv = formattedConversations.find(c => c.id === state.selectedConversation.id);
          if (selectedConv) {
            console.log(`🔄 Atualizando mensagens da conversa selecionada: ${selectedConv.messages.length} mensagens`);
            dispatch({ type: 'SET_MESSAGES', payload: selectedConv.messages });
          }
        }
      });

      socketRef.current.on('stats_update', (stats) => {
        console.log('📊 Atualização de estatísticas recebida via WebSocket');
        dispatch({ type: 'SET_STATS', payload: stats });
      });

      socketRef.current.on('connect_error', (error) => {
        console.error('❌ Erro na conexão WebSocket:', error);
        dispatch({ type: 'SET_SOCKET_CONNECTED', payload: false });
      });

    } catch (error) {
      console.error('❌ Erro ao inicializar WebSocket:', error);
      dispatch({ type: 'SET_SOCKET_CONNECTED', payload: false });
    }
  };

  // Load conversations from backend
  const loadConversations = useCallback(async () => {
    // Debounce para evitar múltiplas chamadas em sequência
    const now = Date.now();
    if (now - lastUpdateRef.current < 2000) { // 2 segundos de debounce
      console.log('⏸️ Debounce: ignorando chamada muito rápida');
      return;
    }
    lastUpdateRef.current = now;
    
    try {
      console.log('🔄 Iniciando carregamento de conversas...');
      dispatch({ type: 'SET_LOADING', payload: true });
      
      console.log('📡 Fazendo requisição para /api/messages...');
      const response = await whatsappAPI.getConversations();
      console.log('✅ Resposta recebida:', response.data);
      
      // Transform backend data to frontend format
      const conversations = response.data.map(conv => {
        console.log('🔄 Processando conversa:', conv);
        const formattedName = formatContactName(
          conv.phone, 
          conv.name, 
          conv.originalName, 
          conv.formattedPhone
        );
        const avatar = generateAvatar(conv.phone, conv.name, conv.avatar);
        
        const formattedMessages = mapMessages(conv.messages, conv.phone);
        
        console.log(`📱 loadConversations - Conversa ${conv.phone}: ${formattedMessages.length} mensagens formatadas`);
        console.log(`📋 Campos de transferência para ${conv.phone}:`, {
          transferido_humano: conv.transferido_humano,
          atribuido_para: conv.atribuido_para,
          dados_transferencia: conv.dados_transferencia
        });
        formattedMessages.forEach((msg, i) => {
          console.log(`  ${i}: sender="${msg.sender}" | "${msg.text}"`);
        });
        
        return {
          id: conv.phone,
          name: formattedName,
          originalName: conv.originalName || conv.name,
          phone: conv.phone,
          formattedPhone: conv.formattedPhone || conv.phone,
          lastMessage: conv.messages.length > 0 ? conv.messages[conv.messages.length - 1].text : 'Nenhuma mensagem',
          timestamp: new Date(), // Backend doesn't provide timestamp, using current time
          unread: 0, // Backend doesn't provide unread count yet
          avatar: avatar,
          messages: formattedMessages,
          // Adicionar campos de transferência
          transferido_humano: conv.transferido_humano || false,
          atribuido_para: conv.atribuido_para || null,
          dados_transferencia: conv.dados_transferencia || null,
        };
      });

      // Sempre atualizar as conversas quando chamado explicitamente
      dispatch({ type: 'SET_CONVERSATIONS', payload: conversations });
      // Set unread counts (for now, all 0)
      conversations.forEach(conv => {
        dispatch({
          type: 'UPDATE_UNREAD_COUNT',
          payload: { conversationId: conv.id, count: conv.unread },
        });
      });
      console.log('✅ Conversas atualizadas');
      
    } catch (error) {
      console.error('❌ Erro ao carregar conversas:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Erro ao carregar conversas' });
      
      // Fallback to mock data if API fails
      console.log('🔄 Usando dados mock como fallback...');
      const mockConversations = [
        {
          id: '1',
          name: 'João Silva • +55 11 99999-9999',
          originalName: 'João Silva',
          phone: '+55 11 99999-9999',
          formattedPhone: '+55 11 99999-9999',
          lastMessage: 'Olá, gostaria de agendar uma consulta',
          timestamp: new Date(Date.now() - 1000 * 60 * 5),
          unread: 2,
          avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=JS&backgroundColor=25D366&textColor=FFFFFF',
        },
        {
          id: '2',
          name: 'Maria Santos • +55 11 88888-8888',
          originalName: 'Maria Santos',
          phone: '+55 11 88888-8888',
          formattedPhone: '+55 11 88888-8888',
          lastMessage: 'Obrigada pelo atendimento!',
          timestamp: new Date(Date.now() - 1000 * 60 * 30),
          unread: 0,
          avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=MS&backgroundColor=25D366&textColor=FFFFFF',
        },
      ];
      dispatch({ type: 'SET_CONVERSATIONS', payload: mockConversations });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  // Load statistics
  const loadStats = useCallback(async () => {
    try {
      const response = await whatsappAPI.getStats();
      dispatch({ type: 'SET_STATS', payload: response.data });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  }, []);

  // Start polling for real-time updates with shorter interval (fallback)
  const startPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }
    
    // Poll every 60 seconds as fallback (reduced frequency since we have WebSocket)
    pollingIntervalRef.current = setInterval(() => {
      // Only poll if WebSocket is not connected
      if (!state.socketConnected) {
        console.log('🔄 Polling fallback - WebSocket não conectado');
        loadConversations();
        loadStats();
      } else {
        console.log('⏸️ Polling pausado - WebSocket conectado');
      }
    }, 60000); // 60 segundos para reduzir conflitos
  };

  // Stop polling
  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  // Disconnect WebSocket
  const disconnectSocket = () => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
  };

  // Initial load and start services
  useEffect(() => {
    console.log('🚀 ChatContext useEffect executado - iniciando serviços...');
    
    // Carregar dados iniciais apenas uma vez
    const initializeData = async () => {
      await loadConversations();
      await loadStats();
    };
    
    initializeData();
    initializeSocket();
    startPolling();

    // Cleanup on unmount
    return () => {
      console.log('🧹 ChatContext cleanup - parando serviços...');
      stopPolling();
      disconnectSocket();
    };
  }, []);

  // Atualizar mensagens quando a conversa selecionada mudar
  useEffect(() => {
    if (state.selectedConversation && state.conversations.length > 0) {
      const selectedConv = state.conversations.find(c => c.id === state.selectedConversation.id);
      if (selectedConv) {
        console.log(`🔄 Conversa selecionada mudou, atualizando mensagens: ${selectedConv.messages.length} mensagens`);
        dispatch({ type: 'SET_MESSAGES', payload: mapMessages(selectedConv.messages, selectedConv.phone) });
      }
    }
  }, [state.selectedConversation?.id]); // Apenas quando o ID da conversa selecionada mudar

  // Atualizar conversas apenas se mudarem (WebSocket) - Otimizado
  const handleConversationsUpdate = (conversations) => {
    console.log('🔄 handleConversationsUpdate iniciado');
    
    // Atualizar conversas imediatamente
    dispatch({ type: 'SET_CONVERSATIONS', payload: conversations });
    
    // Atualizar mensagens da conversa selecionada se houver uma selecionada
    if (state.selectedConversation) {
      const selectedConv = conversations.find(c => c.id === state.selectedConversation.id);
      if (selectedConv) {
        console.log(`🔄 Atualizando mensagens da conversa selecionada: ${selectedConv.messages.length} mensagens`);
        dispatch({ type: 'SET_MESSAGES', payload: selectedConv.messages });
      }
    }
  };

  const sendMessage = async (text) => {
    if (!state.selectedConversation) return;

    const newMessage = {
      id: `${state.selectedConversation.phone}-${Date.now()}-${text}`, // ID estável
      text,
      sender: 'sent', // Mensagens enviadas pelo painel são 'sent' (lado direito, verde)
      timestamp: new Date(),
    };

    // Add message to local state immediately for instant feedback
    dispatch({ type: 'ADD_MESSAGE', payload: newMessage });

    try {
      // Send message to backend
      const response = await whatsappAPI.sendMessage(state.selectedConversation.phone, text);
      console.log('✅ Mensagem enviada para o backend:', response.data);
      
      // Não precisamos atualizar manualmente aqui porque o WebSocket vai atualizar
      // A mensagem já foi adicionada localmente para feedback imediato
    } catch (error) {
      console.error('❌ Erro ao enviar mensagem:', error);
      // Remove message from local state if failed
      dispatch({ type: 'REMOVE_MESSAGE', payload: newMessage.id });
    }
  };

  const refreshConversations = useCallback(async () => {
    console.log('🔄 refreshConversations iniciado...');
    try {
      // Forçar recarregamento das conversas
      await loadConversations();
      await loadStats();
      
      // Aguardar um pouco para garantir que os dados foram processados
      await new Promise(resolve => setTimeout(resolve, 100));
      
      console.log('✅ refreshConversations concluído');
      
      // Forçar uma nova renderização
      console.log('🔄 Forçando atualização da interface...');
      
    } catch (error) {
      console.error('❌ Erro no refreshConversations:', error);
    }
  }, []);

  // Atualizar mensagens apenas se mudarem
  const selectConversation = (conversation) => {
    dispatch({ type: 'SET_SELECTED_CONVERSATION', payload: conversation });
    if (!areMessagesEqual(state.messages, conversation.messages || [])) {
      dispatch({ type: 'SET_MESSAGES', payload: mapMessages(conversation.messages, conversation.phone) });
    }
    dispatch({ type: 'MARK_AS_READ', payload: conversation.id });
    // Join conversation room via WebSocket
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit('join_conversation', { conversation_id: conversation.id });
    }
  };

  // Load messages for a specific session
  const loadSessionMessages = useCallback(async (phone, sessionId) => {
    try {
      const response = await sessionsAPI.getSessionMessages(phone, sessionId);
      const sessionMessages = response.data.messages || [];
      
      // Map session messages to the same format as regular messages
      const formattedMessages = mapMessages(
        sessionMessages.map(msg => ({
          text: msg.text,
          direction: msg.direction,
          from: msg.from,
          timestamp: msg.timestamp
        })),
        phone
      );
      
      // Update messages for the selected conversation
      if (state.selectedConversation && state.selectedConversation.phone === phone) {
        dispatch({ type: 'SET_MESSAGES', payload: formattedMessages });
      }
      
      return formattedMessages;
    } catch (error) {
      console.error('❌ Erro ao carregar mensagens da sessão:', error);
      return [];
    }
  }, [state.selectedConversation]);

  const value = {
    ...state,
    selectConversation,
    sendMessage,
    refreshConversations,
    loadConversations,
    loadStats,
    loadSessionMessages,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}; 