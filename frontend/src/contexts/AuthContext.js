import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Verificar se há um usuário já logado na inicialização
  useEffect(() => {
    const checkLoggedIn = async () => {
      try {
        const response = await api.get('/api/perfil');
        if (response.data.success) {
          console.log('Perfil do usuário:', response.data.profile);
          setCurrentUser(response.data.profile);
        }
      } catch (error) {
        if (error.response?.status !== 401) {
          console.error('Erro ao verificar perfil:', error);
        }
      } finally {
        setLoading(false);
      }
    };
    
    checkLoggedIn();
  }, []);

  const login = async (email, password) => {
    try {
      setLoading(true);
      const response = await api.post('/api/login', {
        email,
        senha: password
      });
      
      if (response.data.success) {
        console.log('Login bem-sucedido. Dados do usuário:', response.data.user);
        setCurrentUser(response.data.user);
        return { success: true };
      }
      return { success: false, error: response.data.error };
    } catch (error) {
      console.error('Erro no login:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Erro ao fazer login' 
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      console.log('Enviando dados para cadastro:', userData);
      const response = await api.post('/api/cadastro', userData);
      console.log('Resposta do cadastro:', response.data);
      return response.data;
    } catch (error) {
      console.error('Erro no cadastro:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Erro ao fazer cadastro' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      setLoading(true);
      await api.post('/api/logout');
      setCurrentUser(null);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Erro ao fazer logout' 
      };
    } finally {
      setLoading(false);
    }
  };

  // Determinar permissões com base nas flags enviadas pelo backend
  // CORREÇÃO: is_admin deve ser true para acesso ao painel admin
  const isAdmin = currentUser?.is_admin || currentUser?.is_superuser;
  const isProfessor = currentUser?.is_professor;
  
  console.log('Status de permissões:', {
    currentUser,
    isAdmin,
    isProfessor
  });

  const value = {
    currentUser,
    login,
    register,
    logout,
    isAuthenticated: !!currentUser,
    isAdmin,
    isProfessor,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;