import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const AdminUsuarios = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsuarios();
  }, []);

  const fetchUsuarios = async () => {
    try {
      const response = await api.get('/api/admin/usuarios');
      if (response.data.success) {
        setUsuarios(response.data.usuarios || []);
      } else {
        setUsuarios([]);
        setError('Erro ao carregar usuários: ' + (response.data.error || 'Resposta inválida do servidor'));
      }
    } catch (error) {
      console.error('Erro ao buscar usuários:', error);
      setUsuarios([]);
      setError('Erro ao carregar usuários. Por favor, tente novamente mais tarde.');
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
    <div className="admin-usuarios-page">
      <div className="container">
        <h1>Gerenciar Usuários</h1>
        
        {error && <div className="alert alert-danger">{error}</div>}
        
        <div className="page-actions mb-4">
          <Link to="/register" className="btn btn-primary">Adicionar Usuário</Link>
        </div>
        
        {usuarios && usuarios.length > 0 ? (
          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nome</th>
                  <th>Email</th>
                  <th>Tipo</th>
                  <th>Admin</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map(usuario => (
                  <tr key={usuario.id}>
                    <td>{usuario.id}</td>
                    <td>{usuario.nome || usuario.username}</td>
                    <td>{usuario.email}</td>
                    <td>{usuario.tipo}</td>
                    <td>{usuario.is_admin ? 'Sim' : 'Não'}</td>
                    <td>
                      <button className="btn btn-sm btn-outline-primary me-2">Editar</button>
                      <button className="btn btn-sm btn-outline-danger">Excluir</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="alert alert-info">
            <p className="mb-0">Nenhum usuário encontrado.</p>
          </div>
        )}
        
        <div className="mt-4">
          <Link to="/admin" className="btn btn-secondary">Voltar ao Painel Admin</Link>
        </div>
      </div>
    </div>
  );
};

export default AdminUsuarios;