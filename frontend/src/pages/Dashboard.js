import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Modal from 'react-modal';

Modal.setAppElement('#root');

const Dashboard = () => {
  const [allGroups, setAllGroups] = useState([]);
  const [userGroups, setUserGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [disciplina, setDisciplina] = useState('');
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await api.get('/api/grupos');
      // Check if the response contains the expected data structure
      if (response.data && response.data.all_groups) {
        setAllGroups(response.data.all_groups);
        setUserGroups(response.data.user_groups || []);
      } else {
        setError('Erro ao carregar grupos: formato de resposta inválido');
      }
    } catch (error) {
      console.error('Erro ao buscar grupos:', error);
      setError('Erro ao carregar grupos');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGroup = async () => {
    if (!selectedGroup) {
      setError('Nenhum grupo selecionado');
      return;
    }

    try {
      const response = await api.post(`/api/grupos/${selectedGroup.id}/entrar`);

      if (response.data.success) {
        await fetchGroups();
        closeModal();
      } else {
        setError(response.data.error || 'Erro ao entrar no grupo');
      }
    } catch (error) {
      console.error('Erro ao entrar no grupo:', error);
      setError('Erro ao entrar no grupo');
    }
  };

  const openModal = (group) => {
    setSelectedGroup(group);
    // Extract discipline from group name if possible
    const match = group.name.match(/- (\d+) - (.+?) \(/);
    if (match && match[2]) {
      setDisciplina(match[2]);
    } else {
      setDisciplina('');
    }
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setSelectedGroup(null);
    setDisciplina('');
    setError('');
  };

  const navigateToGroup = (groupId) => {
    navigate(`/grupos/${groupId}`);
  };

  // Format the description for better display
  const formatDescription = (description) => {
    return description.split('\n').map((line, index) => (
      <div key={index}>{line.trim()}</div>
    ));
  };

  // Check if a user is already in a group
  const isUserInGroup = (groupId) => {
    return userGroups.some(group => group.id === groupId);
  };

  return (
    <div className="dashboard-page">
      <div className="container">
        <h1>Dashboard</h1>
        
        {error && <div className="alert alert-danger">{error}</div>}
        
        <div className="welcome-section mb-5">
          <h2>Bem-vindo, {currentUser?.nome || currentUser?.username || 'Usuário'}!</h2>
          <p>Gerencie suas turmas e disciplinas:</p>
        </div>

        {loading ? (
          <div className="text-center">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Carregando...</span>
            </div>
          </div>
        ) : (
          <div>
            {/* Todas as Turmas - Em uma linha separada com barra de rolagem */}
            <div className="row mb-4">
              <div className="col-12">
                <div className="card">
                  <div className="card-header">
                    <h3 className="mb-0">Todas as Turmas</h3>
                  </div>
                  <div className="card-body" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    {allGroups.length === 0 ? (
                      <p>Nenhuma turma disponível no momento</p>
                    ) : (
                      <div className="list-group">
                        {allGroups.map(group => (
                          !isUserInGroup(group.id) && (
                            <button
                              key={group.id}
                              className="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                              onClick={() => openModal(group)}
                            >
                              <div className="ms-2 me-auto">
                                <div className="fw-bold">{group.name}</div>
                                <small className="text-muted">
                                  {group.description && formatDescription(group.description)[0]}
                                </small>
                              </div>
                              <span className="badge bg-primary rounded-pill">Participar</span>
                            </button>
                          )
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Minhas Turmas - Em uma linha separada com barra de rolagem */}
            <div className="row">
              <div className="col-12">
                <div className="card">
                  <div className="card-header">
                    <h3 className="mb-0">Minhas Turmas</h3>
                  </div>
                  <div className="card-body" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    {userGroups.length === 0 ? (
                      <p>Você não está em nenhuma turma</p>
                    ) : (
                      <div className="list-group">
                        {userGroups.map(group => (
                          <button
                            key={group.id}
                            className="list-group-item list-group-item-action"
                            onClick={() => navigateToGroup(group.id)}
                          >
                            <div className="d-flex justify-content-between align-items-center">
                              <div>
                                <h5 className="mb-1">{group.name}</h5>
                                <small className="text-muted">
                                  {group.description && formatDescription(group.description)[0]}
                                </small>
                              </div>
                              <span className="badge bg-success">Acessar</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <Modal
          isOpen={modalIsOpen}
          onRequestClose={closeModal}
          style={{
            overlay: {
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            },
            content: {
              position: 'relative',
              top: 'auto',
              left: 'auto',
              right: 'auto',
              bottom: 'auto',
              width: '500px',
              margin: '0 auto',
              padding: 0,
              border: '1px solid #ccc',
              borderRadius: '4px',
              background: '#fff',
              overflow: 'auto',
              WebkitOverflowScrolling: 'touch',
              outline: 'none'
            }
          }}
        >
          <div className="p-3">
            <h5 className="mb-3 border-bottom pb-2">Entrar na Turma</h5>
            
            {selectedGroup && (
              <div>
                <p><strong>Turma: {selectedGroup.name}</strong></p>
                
                <div className="border p-3 mb-3" style={{ maxHeight: '250px', overflowY: 'auto' }}>
                  {selectedGroup.description && formatDescription(selectedGroup.description)}
                </div>
                
                <p>Confirma que deseja entrar nesta turma?</p>
                
                <div className="d-flex justify-content-center mt-4">
                  <button 
                    className="btn btn-primary mx-2"
                    onClick={handleJoinGroup}
                  >
                    Confirmar
                  </button>
                  <button 
                    className="btn btn-secondary mx-2"
                    onClick={closeModal}
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            )}
          </div>
        </Modal>
      </div>
    </div>
  );
};

export default Dashboard;