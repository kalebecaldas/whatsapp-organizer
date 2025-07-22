import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Simular chamada de API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validação básica
      if (!formData.email || !formData.password) {
        throw new Error('Por favor, preencha todos os campos');
      }

      if (!formData.email.includes('@')) {
        throw new Error('Email inválido');
      }

      // Simular login bem-sucedido
      const userData = {
        id: 1,
        name: 'Administrador',
        email: formData.email,
        role: 'admin'
      };

      login(userData);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo">
            <Shield size={40} className="logo-icon" />
            <h1>WhatsApp Organizer</h1>
          </div>
          <p className="login-subtitle">Faça login para acessar o sistema</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message">
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">
              <Mail size={16} />
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Digite seu email"
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              <Lock size={16} />
              Senha
            </label>
            <div className="password-input">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Digite sua senha"
                required
                disabled={isLoading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={togglePasswordVisibility}
                disabled={isLoading}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <div className="form-options">
            <label className="remember-me">
              <input type="checkbox" />
              <span>Lembrar de mim</span>
            </label>
            <a href="#" className="forgot-password">
              Esqueceu a senha?
            </a>
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
                Entrando...
              </div>
            ) : (
              <>
                <User size={16} />
                Entrar
              </>
            )}
          </button>
        </form>

        <div className="login-footer">
          <p>Não tem uma conta? <a href="#">Solicitar acesso</a></p>
        </div>
      </div>
    </div>
  );
};

export default Login; 