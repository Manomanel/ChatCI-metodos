import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Dashboard = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { currentUser } = useAuth();

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await api.get('/api/grupos');
      if (response.data.success) {
        // Garantir que groups seja sempre um array
        setGroups(response.data.groups || []);
      } else {
        // Se a resposta indicar erro mas não lançar exceção
        setGroups([]);
        setError('Erro ao carregar grupos: ' + (response.data.error || 'Resposta inválida do servidor'));
      }
    } catch (error) {
      console.error('Erro ao buscar grupos:', error);
      setGroups([]);
      setError('Erro ao carregar grupos. Por favor, tente novamente mais tarde.');
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
    <div className="dashboard-page">
      <div className="container">
        <h1>Dashboard</h1>
        
        {error && <div className="error">{error}</div>}
        
        <div className="welcome-section">
          <h2>Bem-vindo, {currentUser?.nome || currentUser?.username || 'Usuário'}!</h2>
          <p>Esta é a sua área principal de navegação do ChatCI.</p>
        </div>
        
        <div className="groups-section">
          <h3>Seus Grupos</h3>
          
          {groups && groups.length > 0 ? (
            <div className="groups-grid">
              {groups.map(group => (
                <div key={group.id} className="group-card">
                  <h4>{group.nome}</h4>
                  <p>{group.descricao || 'Sem descrição'}</p>
                  <span className="group-type">{group.tipo || 'Tipo não definido'}</span>
                </div>
              ))}
            </div>
          ) : (
            <p>Você ainda não participa de nenhum grupo.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;