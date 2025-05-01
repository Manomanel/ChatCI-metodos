import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="loading-indicator">Carregando...</div>;
  }

  // Apenas verifica se o usuário está autenticado
  return isAuthenticated ? children : <Navigate to="/login" />;
};

export default PrivateRoute;