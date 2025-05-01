import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const AdminRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="loading-indicator">Carregando...</div>;
  }

  // Temporariamente permite acesso para qualquer usuário autenticado
  return isAuthenticated ? children : <Navigate to="/login" />;
};

export default AdminRoute;