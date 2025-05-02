import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import Modal from 'react-modal';

Modal.setAppElement('#root');

const ProfessorTurmas = () => {
  const [turmas, setTurmas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [currentTurma, setCurrentTurma] = useState(null);
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    codigo: ''
  });
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
        setError('Erro ao carregar turmas');
      }
    } catch (error) {
      console.error('Erro ao buscar turmas:', error);
      setError('Erro ao carregar turmas');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.nome || !formData.codigo) {
      setError('Nome e código são obrigatórios');
      return;
    }

    try {
      if (currentTurma) {
        // Editar turma existente
        await api.put(`/api/professor/turmas/${currentTurma.id}`, formData);
      } else {
        // Criar nova turma
        await api.post('/api/professor/turmas', formData);
      }
      await fetchTurmas();
      closeModal();
    } catch (error) {
      setError(error.response?.data?.error || 'Erro ao salvar turma');
    }
  };

  const handleDelete = async (turmaId) => {
    if (window.confirm('Tem certeza que deseja excluir esta turma?')) {
      try {
        await api.delete(`/api/professor/turmas/${turmaId}`);
        setTurmas(turmas.filter(t => t.id !== turmaId));
      } catch (error) {
        setError('Erro ao excluir turma');
      }
    }
  };

  const openCreateModal = () => {
    setCurrentTurma(null);
    setFormData({ nome: '', descricao: '', codigo: '' });
    setModalIsOpen(true);
  };

  const openEditModal = (turma) => {
    setCurrentTurma(turma);
    setFormData({
      nome: turma.nome,
      descricao: turma.descricao,
      codigo: turma.codigo
    });
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setCurrentTurma(null);
    setFormData({ nome: '', descricao: '', codigo: '' });
    setError('');
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
        
        {error && <div className="alert alert-danger">{error}</div>}
        
        <div className="page-actions mb-4">
          <button className="btn btn-primary" onClick={openCreateModal}>
            Nova Turma
          </button>
          <Link to="/dashboard" className="btn btn-secondary ms-2">
            Voltar ao Dashboard
          </Link>
        </div>
        
        {turmas.length > 0 ? (
          <div className="row">
            {turmas.map(turma => (
              <div key={turma.id} className="col-md-4 mb-4">
                <div className="card h-100">
                  <div className="card-body">
                    <h3 className="card-title">{turma.nome}</h3>
                    <p className="card-text">{turma.descricao || 'Sem descrição'}</p>
                    <div className="turma-info mb-3">
                      <div><strong>Alunos:</strong> {turma.total_alunos || 0}</div>
                      <div><strong>Código:</strong> {turma.codigo}</div>
                    </div>
                    <div className="d-grid gap-2">
                      <Link 
                        to={`/professor/turma/${turma.id}`} 
                        className="btn btn-primary"
                      >
                        Ver Detalhes
                      </Link>
                      <button 
                        className="btn btn-outline-secondary"
                        onClick={() => openEditModal(turma)}
                      >
                        Editar
                      </button>
                      <button 
                        className="btn btn-outline-danger"
                        onClick={() => handleDelete(turma.id)}
                      >
                        Excluir
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state text-center py-5">
            <p className="lead">Você ainda não possui turmas cadastradas.</p>
            <p>Clique em "Nova Turma" para começar.</p>
          </div>
        )}

        <Modal
          isOpen={modalIsOpen}
          onRequestClose={closeModal}
          className="modal-dialog"
          overlayClassName="modal-overlay"
        >
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">
                {currentTurma ? 'Editar Turma' : 'Nova Turma'}
              </h5>
              <button type="button" className="btn-close" onClick={closeModal}></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="mb-3">
                  <label className="form-label">Nome da Turma</label>
                  <input
                    type="text"
                    className="form-control"
                    name="nome"
                    value={formData.nome}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Código</label>
                  <input
                    type="text"
                    className="form-control"
                    name="codigo"
                    value={formData.codigo}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Descrição</label>
                  <textarea
                    className="form-control"
                    name="descricao"
                    value={formData.descricao}
                    onChange={handleInputChange}
                    rows="3"
                  ></textarea>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary">
                  {currentTurma ? 'Salvar Alterações' : 'Criar Turma'}
                </button>
              </div>
            </form>
          </div>
        </Modal>
      </div>
    </div>
  );
};

export default ProfessorTurmas;