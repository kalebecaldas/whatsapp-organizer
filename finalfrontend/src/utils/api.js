import axios from 'axios';

// Base URL for the backend API
const API_BASE_URL = 'http://localhost:5001/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API functions for WhatsApp conversations
export const whatsappAPI = {
  // Get all conversations with messages
  getConversations: () => api.get('/messages'),
  
  // Send a message to a specific phone number
  sendMessage: (phone, message) => api.post('/send-message', { phone, message }),
  
  // Simulate receiving a message (for testing)
  simulateMessage: (from, body) => api.post('/webhook', { from, body }),
  
  // Get conversation statistics
  getStats: () => api.get('/stats'),
};

// API functions for conversations (legacy - for future use)
export const conversationsAPI = {
  // Get all conversations
  getAll: () => api.get('/conversations'),
  
  // Get a specific conversation
  getById: (id) => api.get(`/conversations/${id}`),
  
  // Create a new conversation
  create: (data) => api.post('/conversations', data),
  
  // Update a conversation
  update: (id, data) => api.put(`/conversations/${id}`, data),
  
  // Delete a conversation
  delete: (id) => api.delete(`/conversations/${id}`),
};

// API functions for messages (legacy - for future use)
export const messagesAPI = {
  // Get messages for a conversation
  getByConversation: (conversationId) => 
    api.get(`/conversations/${conversationId}/messages`),
  
  // Send a message
  send: (conversationId, message) => 
    api.post(`/conversations/${conversationId}/messages`, message),
  
  // Mark messages as read
  markAsRead: (conversationId) => 
    api.put(`/conversations/${conversationId}/messages/read`),
};

// API functions for authentication
export const authAPI = {
  // Login
  login: (credentials) => api.post('/auth/login', credentials),
  
  // Logout
  logout: () => api.post('/auth/logout'),
  
  // Get current user
  getCurrentUser: () => api.get('/auth/me'),
};

// API functions for real-time updates (WebSocket)
export const realtimeAPI = {
  // Connect to WebSocket for real-time messages
  connect: (token) => {
    // This will be implemented when we add WebSocket support
    console.log('WebSocket connection will be implemented');
  },
  
  // Disconnect from WebSocket
  disconnect: () => {
    // This will be implemented when we add WebSocket support
    console.log('WebSocket disconnection will be implemented');
  },
};

// Função para gerar avatar baseado no número
function generateAvatar(phone) {
  const digits = phone.replace(/\D/g, '');
  const lastTwo = digits.slice(-2);
  // Usar DiceBear API que é mais confiável
  return `https://api.dicebear.com/7.x/initials/svg?seed=${lastTwo}&backgroundColor=25D366&textColor=FFFFFF`;
}

export default api; 