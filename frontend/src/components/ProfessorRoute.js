import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const AdminRoute = ({ children }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  
  // Log para debug
  console.log('AdminRoute - Verificando permissões:', { isAuthenticated, isAdmin });

  if (loading) {
    return <div className="loading-indicator">Carregando...</div>;
  }

  // Permite acesso apenas para administradores
  return isAuthenticated && isAdmin ? children : <Navigate to="/dashboard" />;
};

export default AdminRoute;