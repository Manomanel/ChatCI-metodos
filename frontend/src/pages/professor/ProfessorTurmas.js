import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const ProfessorTurmas = () => {
  const [turmas, setTurmas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { currentUser } = useAuth();

  useEffect(() => {
    fetchTurmas();
  }, []);

  const fetchTurmas = async () => {
    try {
      const response = await api.get('/api/professor/turmas');
      if (response.data.success) {
        setTurmas(response.data.turmas || []);
      } else {
        setTurmas([]);
        setError('Erro ao carregar turmas: ' + (response.data.error || 'Resposta inválida do servidor'));
      }
    } catch (error) {
      console.error('Erro ao buscar turmas:', error);
      setTurmas([]);
      setError('Erro ao carregar turmas. Por favor, tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading-indicator">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="professor-turmas-page">
      <div className="container">
        <h1>Minhas Turmas</h1>
        
        {error && <div className="error">{error}</div>}
        
        <div className="page-actions">
          <button className="btn btn-primary">Nova Turma</button>
        </div>
        
        {turmas && turmas.length > 0 ? (
          <div className="turmas-grid">
            {turmas.map(turma => (
              <div key={turma.id} className="turma-card">
                <h3>{turma.nome}</h3>
                <p>{turma.descricao || 'Sem descrição'}</p>
                <div className="turma-info">
                  <span>Alunos: {turma.total_alunos || 0}</span>
                  <span>Código: {turma.codigo}</span>
                </div>
                <div className="turma-actions">
                  <Link to={`/professor/turma/${turma.id}`} className="btn btn-secondary">
                    Ver Detalhes
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>Você ainda não possui turmas cadastradas.</p>
            <p>Clique em "Nova Turma" para começar.</p>
          </div>
        )}
        
        <Link to="/dashboard" className="btn btn-secondary mt-20">Voltar ao Dashboard</Link>
      </div>
    </div>
  );
};

export default ProfessorTurmas;