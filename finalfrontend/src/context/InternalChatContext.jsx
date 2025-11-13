import { createContext, useContext, useReducer, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import api from '../utils/api';

const InternalChatContext = createContext();

const initialState = {
  conversations: [],
  selectedConversation: null,
  messages: {},
  loading: false,
  error: null,
  socketConnected: false,
};

const internalChatReducer = (state, action) => {
  switch (action.type) {
    case 'SET_CONVERSATIONS':
      return { ...state, conversations: action.payload };
    case 'SET_SELECTED_CONVERSATION':
      return { ...state, selectedConversation: action.payload };
    case 'SET_MESSAGES':
      return {
        ...state,
        messages: {
          ...state.messages,
          [action.payload.conversationId]: action.payload.messages
        }
      };
    case 'ADD_MESSAGE':
      const convId = action.payload.conversation_id;
      return {
        ...state,
        messages: {
          ...state.messages,
          [convId]: [...(state.messages[convId] || []), action.payload.message]
        }
      };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_SOCKET_CONNECTED':
      return { ...state, socketConnected: action.payload };
    default:
      return state;
  }
};

export const InternalChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(internalChatReducer, initialState);
  const socketRef = useRef(null);

  // Initialize WebSocket
  const initializeSocket = () => {
    try {
      socketRef.current = io('http://localhost:5001', {
        transports: ['polling', 'websocket'],
        timeout: 20000,
        forceNew: true,
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });

      socketRef.current.on('connect', () => {
        console.log('🔌 Internal Chat WebSocket conectado');
        dispatch({ type: 'SET_SOCKET_CONNECTED', payload: true });
      });

      socketRef.current.on('disconnect', () => {
        console.log('🔌 Internal Chat WebSocket desconectado');
        dispatch({ type: 'SET_SOCKET_CONNECTED', payload: false });
      });

      socketRef.current.on('internal_message_new', (data) => {
        console.log('📨 Nova mensagem interna recebida:', data);
        dispatch({
          type: 'ADD_MESSAGE',
          payload: {
            conversation_id: data.conversation_id,
            message: data.message
          }
        });
      });

      socketRef.current.on('internal_conversation_update', (data) => {
        console.log('🔄 Atualização de conversa interna:', data);
        loadConversations();
      });

    } catch (error) {
      console.error('❌ Erro ao inicializar WebSocket:', error);
      dispatch({ type: 'SET_SOCKET_CONNECTED', payload: false });
    }
  };

  // Load conversations
  const loadConversations = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await api.get('/internal-conversations?user_id=current-user');
      dispatch({ type: 'SET_CONVERSATIONS', payload: response.data.conversations || [] });
    } catch (error) {
      console.error('❌ Erro ao carregar conversas internas:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Erro ao carregar conversas' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Load messages for a conversation
  const loadMessages = async (conversationId) => {
    try {
      const response = await api.get(`/internal-conversations/${conversationId}/messages`);
      dispatch({
        type: 'SET_MESSAGES',
        payload: {
          conversationId,
          messages: response.data.messages || []
        }
      });
    } catch (error) {
      console.error('❌ Erro ao carregar mensagens:', error);
    }
  };

  // Send message
  const sendMessage = async (conversationId, content) => {
    try {
      const response = await api.post(`/internal-conversations/${conversationId}/messages`, {
        sender_id: 'current-user', // TODO: Get from auth
        content,
        message_type: 'text'
      });

      if (response.data.success) {
        // Message will be added via WebSocket
        return { success: true };
      }
    } catch (error) {
      console.error('❌ Erro ao enviar mensagem:', error);
      return { success: false, error: error.message };
    }
  };

  // Create conversation
  const createConversation = async (name, type, memberIds, description) => {
    try {
      const response = await api.post('/internal-conversations', {
        name,
        type,
        member_ids: memberIds,
        creator_id: 'current-user', // TODO: Get from auth
        description
      });

      if (response.data.success) {
        await loadConversations();
        return { success: true, conversation_id: response.data.conversation_id };
      }
    } catch (error) {
      console.error('❌ Erro ao criar conversa:', error);
      return { success: false, error: error.message };
    }
  };

  // Select conversation
  const selectConversation = (conversation) => {
    dispatch({ type: 'SET_SELECTED_CONVERSATION', payload: conversation });
    if (conversation && !state.messages[conversation.id]) {
      loadMessages(conversation.id);
    }
  };

  // Initial load
  useEffect(() => {
    initializeSocket();
    loadConversations();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, []);

  // Load messages when conversation is selected
  useEffect(() => {
    if (state.selectedConversation) {
      loadMessages(state.selectedConversation.id);
    }
  }, [state.selectedConversation?.id]);

  const value = {
    ...state,
    loadConversations,
    loadMessages,
    sendMessage,
    createConversation,
    selectConversation,
  };

  return (
    <InternalChatContext.Provider value={value}>
      {children}
    </InternalChatContext.Provider>
  );
};

export const useInternalChat = () => {
  const context = useContext(InternalChatContext);
  if (!context) {
    throw new Error('useInternalChat must be used within an InternalChatProvider');
  }
  return context;
};
