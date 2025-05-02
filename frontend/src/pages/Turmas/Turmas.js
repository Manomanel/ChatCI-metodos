import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import Modal from 'react-modal';
import './Turmas.css';

Modal.setAppElement('#root');

const Turmas = ({ isProfessorView = false }) => {
  // Estados para os grupos/turmas
  const [grupos, setGrupos] = useState([]);
  const [grupoAtual, setGrupoAtual] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Estados para o chat
  const [mensagens, setMensagens] = useState([]);
  const [novaMensagem, setNovaMensagem] = useState('');
  const [loadingMensagens, setLoadingMensagens] = useState(false);
  
  // Estados para o modal (criar/editar turma)
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [currentTurma, setCurrentTurma] = useState(null);
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    codigo: ''
  });
  
  const { currentUser } = useAuth();
  const { grupoId } = useParams();
  const navigate = useNavigate();
  const chatContainerRef = useRef(null);
  
  // Verificar se o usuário é professor
  const isProfessor = isProfessorView || (currentUser && currentUser.role === 'professor');

  // Buscar grupos/turmas
  useEffect(() => {
    fetchGrupos();
  }, [isProfessorView]);

  const fetchGrupos = async () => {
    try {
      // Se for visualização de professor ou o usuário é professor, buscar as turmas que ele criou
      // Senão, buscar os grupos/turmas que o usuário participa
      const endpoint = isProfessorView ? '/api/professor/turmas' : '/api/usuarios/grupos';
      const response = await api.get(endpoint);
      
      console.log('Resposta da API:', response.data);
      
      if (response.data.success) {
        // Normalizar os dados independentemente da origem
        const items = isProfessorView 
          ? (response.data.turmas || [])
          : (response.data.groups || []);
        
        console.log('Itens processados:', items);
        setGrupos(items);
        
        // Selecionar grupo atual baseado no ID da URL ou o primeiro disponível
        if (grupoId && items.length > 0) {
          const grupo = items.find(g => g.id === parseInt(grupoId));
          if (grupo) {
            setGrupoAtual(grupo);
          } else if (items.length > 0) {
            setGrupoAtual(items[0]);
            navigate(isProfessorView 
              ? `/professor/turma/${items[0].id}` 
              : `/turmas/${items[0].id}`);
          }
        } else if (items.length > 0) {
          setGrupoAtual(items[0]);
          navigate(isProfessorView 
            ? `/professor/turma/${items[0].id}` 
            : `/turmas/${items[0].id}`);
        }
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

  // Buscar mensagens quando o grupo atual mudar
  useEffect(() => {
    if (grupoAtual) {
      fetchMensagens();
    }
  }, [grupoAtual]);

  // Rolar para a última mensagem quando novas mensagens são carregadas
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [mensagens]);

  const fetchMensagens = async () => {
    if (!grupoAtual) return;
    
    setLoadingMensagens(true);
    try {
      const response = await api.get(`/api/grupos/${grupoAtual.id}/mensagens`);
      if (response.data.success) {
        setMensagens(response.data.messages || []);
      } else {
        console.error('Erro ao carregar mensagens:', response.data.error);
      }
    } catch (error) {
      console.error('Erro ao buscar mensagens:', error);
    } finally {
      setLoadingMensagens(false);
    }
  };

  const handleSelectGrupo = (grupo) => {
    setGrupoAtual(grupo);
    navigate(isProfessorView 
      ? `/professor/turma/${grupo.id}` 
      : `/turmas/${grupo.id}`);
  };

  const handleEnviarMensagem = async (e) => {
    e.preventDefault();
    if (!novaMensagem.trim() || !grupoAtual) return;

    try {
      // Adaptado para corresponder à API existente que espera 'text' em vez de 'texto'
      const response = await api.post(`/api/grupos/${grupoAtual.id}/mensagens`, {
        text: novaMensagem
      });
      
      if (response.data.success) {
        setNovaMensagem('');
        fetchMensagens();
      } else {
        setError('Erro ao enviar mensagem');
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setError('Erro ao enviar mensagem');
    }
  };

  // Funções para o modal (apenas para professores)
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
      await fetchGrupos();
      closeModal();
    } catch (error) {
      setError(error.response?.data?.error || 'Erro ao salvar turma');
    }
  };

  const handleDelete = async (turmaId) => {
    if (window.confirm('Tem certeza que deseja excluir esta turma?')) {
      try {
        await api.delete(`/api/professor/turmas/${turmaId}`);
        setGrupos(grupos.filter(t => t.id !== turmaId));
        
        // Se a turma excluída for a atual, selecionar outra
        if (grupoAtual && grupoAtual.id === turmaId) {
          if (grupos.length > 1) {
            const novoGrupo = grupos.find(g => g.id !== turmaId);
            setGrupoAtual(novoGrupo);
            navigate(`/professor/turma/${novoGrupo.id}`);
          } else {
            setGrupoAtual(null);
            navigate('/professor/turmas');
          }
        }
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
      nome: turma.nome || turma.name || '',
      descricao: turma.descricao || turma.description || '',
      codigo: turma.codigo || ''
    });
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setCurrentTurma(null);
    setFormData({ nome: '', descricao: '', codigo: '' });
    setError('');
  };

  // Render loading state
  if (loading) {
    return (
      <div className="container">
        <div className="loading-indicator">Carregando...</div>
      </div>
    );
  }

  // Determinar o título baseado no papel do usuário
  const pageTitle = isProfessorView ? 'Gerenciar Turmas' : 'Minhas Turmas';
  
  // Normalizar os nomes de propriedades para exibição
  const getNome = (grupo) => grupo.nome || grupo.name || 'Sem nome';
  const getDescricao = (grupo) => grupo.descricao || grupo.description || 'Sem descrição';
  const getCodigo = (grupo) => grupo.codigo || '';

  return (
    <div className="turmas-page">
      <div className="container">
        <h1>{pageTitle}</h1>
        
        {error && <div className="alert alert-danger">{error}</div>}
        
        <div className="page-actions mb-4">
          {isProfessorView && (
            <button className="btn btn-primary" onClick={openCreateModal}>
              Nova Turma
            </button>
          )}
          <Link to="/dashboard" className="btn btn-secondary ms-2">
            Voltar ao Dashboard
          </Link>
        </div>
        
        {grupos.length > 0 ? (
          <div className="turmas-chat-container">
            {/* Lista de grupos/turmas */}
            <div className="grupos-lista">
              <h2>Turmas</h2>
              <div className="list-group">
                {grupos.map(grupo => (
                  <button
                    key={grupo.id}
                    className={`list-group-item list-group-item-action ${grupoAtual && grupo.id === grupoAtual.id ? 'active' : ''}`}
                    onClick={() => handleSelectGrupo(grupo)}
                  >
                    <div className="grupo-item">
                      <h5 className="mb-1">{getNome(grupo)}</h5>
                      <small className="text-muted">
                        {new Date(grupo.created_at).toLocaleDateString('pt-BR')}
                      </small>
                    </div>
                    <p className="mb-1 grupo-descricao">
                      {getDescricao(grupo).length > 100 
                        ? getDescricao(grupo).substring(0, 100) + '...' 
                        : getDescricao(grupo)}
                    </p>
                    {isProfessorView && (
                      <div className="grupo-actions mt-2">
                        <button 
                          className="btn btn-sm btn-outline-primary me-2"
                          onClick={(e) => {
                            e.stopPropagation();
                            openEditModal(grupo);
                          }}
                        >
                          Editar
                        </button>
                        <button 
                          className="btn btn-sm btn-outline-danger"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(grupo.id);
                          }}
                        >
                          Excluir
                        </button>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Área de chat */}
            <div className="chat-container">
              {grupoAtual ? (
                <>
                  <div className="chat-header">
                    <h3>{getNome(grupoAtual)}</h3>
                    {getCodigo(grupoAtual) && (
                      <div className="codigo-turma">
                        <span>Código: {getCodigo(grupoAtual)}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="chat-messages" ref={chatContainerRef}>
                    {loadingMensagens ? (
                      <div className="text-center p-3">Carregando mensagens...</div>
                    ) : mensagens.length > 0 ? (
                      mensagens.map(mensagem => (
                        <div 
                          key={mensagem.id} 
                          className={`message ${mensagem.user_id === (currentUser?.id || 0) ? 'message-own' : 'message-other'}`}
                        >
                          <div className="message-header">
                            <span className="message-author">{mensagem.username}</span>
                            <span className="message-time">
                              {new Date(mensagem.created_at).toLocaleTimeString('pt-BR', { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              })}
                            </span>
                          </div>
                          <div className="message-content">{mensagem.text}</div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center p-3">Sem mensagens. Seja o primeiro a enviar!</div>
                    )}
                  </div>
                  
                  <div className="chat-input">
                    <form onSubmit={handleEnviarMensagem}>
                      <div className="input-group">
                        <input
                          type="text"
                          className="form-control"
                          placeholder="Digite sua mensagem..."
                          value={novaMensagem}
                          onChange={(e) => setNovaMensagem(e.target.value)}
                        />
                        <button 
                          type="submit" 
                          className="btn btn-primary"
                          disabled={!novaMensagem.trim()}
                        >
                          Enviar
                        </button>
                      </div>
                    </form>
                  </div>
                </>
              ) : (
                <div className="no-chat-selected">
                  <p>Selecione uma turma para ver o chat</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="empty-state text-center py-5">
            <p className="lead">
              {isProfessorView
                ? 'Você ainda não possui turmas cadastradas.'
                : 'Você ainda não está em nenhuma turma.'}
            </p>
            <p>
              {isProfessorView
                ? 'Clique em "Nova Turma" para começar.'
                : 'Entre em contato com seu professor para receber um convite.'}
            </p>
          </div>
        )}

        {/* Modal para criar/editar turma (apenas para professores) */}
        <Modal
          isOpen={modalIsOpen && isProfessorView}
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

export default Turmas;