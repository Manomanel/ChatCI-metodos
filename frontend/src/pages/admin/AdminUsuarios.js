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
        
        {error && <div className="error">{error}</div>}
        
        <div className="page-actions">
          <Link to="/register" className="btn btn-primary">Adicionar Usuário</Link>
        </div>
        
        {usuarios && usuarios.length > 0 ? (
          <div className="table-responsive">
            <table className="usuarios-table">
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
                    <td className="actions">
                      <button className="btn-action edit">Editar</button>
                      <button className="btn-action delete">Excluir</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <p>Nenhum usuário encontrado.</p>
          </div>
        )}
        
        <Link to="/admin" className="btn btn-secondary mt-20">Voltar ao Painel Admin</Link>
      </div>
    </div>
  );
};

export default AdminUsuarios;