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
        
        {error && <div className="alert alert-danger">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        
        <div className="admin-card card mb-4 p-4">
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
            <div className="integration-result mt-4">
              <h3>Resultado da Integração:</h3>
              <ul className="list-group">
                <li className="list-group-item">Turmas encontradas: {integrationResult.turmas_found}</li>
                <li className="list-group-item">Grupos criados: {integrationResult.groups_created}</li>
                <li className="list-group-item">Grupos existentes: {integrationResult.groups_existing}</li>
              </ul>
              
              {integrationResult.errors && integrationResult.errors.length > 0 && (
                <>
                  <h4 className="mt-3">Erros:</h4>
                  <ul className="list-group error-list">
                    {integrationResult.errors.map((error, index) => (
                      <li className="list-group-item list-group-item-danger" key={index}>{error}</li>
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