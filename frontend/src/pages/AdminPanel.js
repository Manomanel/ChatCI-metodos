import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const AdminPanel = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [integrationResult, setIntegrationResult] = useState(null);

  const runSaciIntegration = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    setIntegrationResult(null);
    
    try {
      const response = await api.post('/api/admin/scrape-saci');
      if (response.data.success) {
        setSuccess('Integração SACI executada com sucesso!');
        setIntegrationResult(response.data);
      } else {
        setError('Erro na integração SACI');
      }
    } catch (error) {
      setError('Erro ao executar integração SACI');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-page">
      <div className="container">
        <h1>Painel Administrativo</h1>
        
        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}
        
        <div className="admin-card">
          <h2>Integração SACI</h2>
          <p>Execute a integração para sincronizar grupos com o SACI.</p>
          <button 
            onClick={runSaciIntegration}
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Executando...' : 'Executar Integração'}
          </button>
          
          {integrationResult && (
            <div className="integration-result">
              <h3>Resultado da Integração:</h3>
              <ul>
                <li>Turmas encontradas: {integrationResult.turmas_found}</li>
                <li>Grupos criados: {integrationResult.groups_created}</li>
                <li>Grupos existentes: {integrationResult.groups_existing}</li>
              </ul>
              
              {integrationResult.errors.length > 0 && (
                <>
                  <h4>Erros:</h4>
                  <ul className="error-list">
                    {integrationResult.errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          )}
        </div>
        
        <Link to="/dashboard" className="btn btn-secondary">Voltar ao Dashboard</Link>
      </div>
    </div>
  );
};

export default AdminPanel;