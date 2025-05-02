import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProfessorRoute = ({ children }) => {
  const { isAuthenticated, isProfessor, isAdmin, loading } = useAuth();
  
  // Log para debug
  console.log('ProfessorRoute - Verificando permissões:', { isAuthenticated, isProfessor, isAdmin });

  if (loading) {
    return <div className="loading-indicator">Carregando...</div>;
  }

  // Permite acesso para professores e admins
  return isAuthenticated && (isProfessor || isAdmin) ? children : <Navigate to="/dashboard" />;
};

export default ProfessorRoute;