import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Events = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    date: '',
    time: '',
    local: ''
  });

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await api.get('/api/eventos');
      console.log('API Response:', response.data);
      
      if (response.data.success) {
        const eventsList = response.data.events || response.data.eventos || [];
        
        const formattedEvents = eventsList.map(event => ({
          ...event,
          date: event.event_date ? event.event_date.split('T')[0] : '',
          time: event.event_date && event.event_date.includes('T') ? 
                event.event_date.split('T')[1].slice(0,5) : '',
          title: event.title || event.titulo || '',
          description: event.description || event.descricao || '',
          local: event.local || ''
        }));
        
        console.log('Formatted Events:', formattedEvents);
        setEvents(formattedEvents);
      } else {
        setError('Erro ao carregar eventos');
      }
    } catch (error) {
      console.error('Erro ao buscar eventos:', error);
      setError('Erro ao carregar eventos');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    try {
      // Validação adicional
      if (!formData.date || !formData.time) {
        setError('Data e hora são obrigatórias');
        return;
      }

      // Criação de um novo evento
      if (!selectedEvent) {
        // Para CRIAÇÃO, a API espera:
        // titulo, descricao, data, hora, local
        const createPayload = {
          titulo: formData.title,
          descricao: formData.description,
          data: formData.date,
          hora: formData.time,
          local: formData.local
        };

        console.log('Payload para CRIAÇÃO:', createPayload);
        
        const response = await api.post('/api/eventos/criar', createPayload);
        
        console.log('Resposta da API (criação):', response.data);
        
        if (response.data.success) {
          setSuccess('Evento criado!');
          resetForm();
          fetchEvents();
          setTimeout(() => setSuccess(''), 3000);
        } else {
          setError(response.data.error || 'Erro na operação');
        }
      } 
      // Atualização de um evento existente
      else {
        // CORREÇÃO: Remover o campo link que não existe na tabela
        const updatePayload = {
          title: formData.title,
          description: formData.description,
          event_date: formData.date,  // YYYY-MM-DD apenas
          local: formData.local       // Adicionar local para preservar essa informação
        };

        console.log('Payload para EDIÇÃO (corrigido):', updatePayload);
        console.log('ID do evento para update:', selectedEvent.id);
        
        const response = await api.put(`/api/eventos/${selectedEvent.id}`, updatePayload);
        
        console.log('Resposta da API (edição):', response.data);
        
        if (response.data.success) {
          setSuccess('Evento atualizado!');
          resetForm();
          fetchEvents();
          setTimeout(() => setSuccess(''), 3000);
        } else {
          setError(response.data.error || 'Erro na operação');
        }
      }
    } catch (error) {
      console.error('Erro na operação:', error);
      
      // Log detalhado para debug
      if (error.response) {
        console.error('Status:', error.response.status);
        console.error('Dados:', error.response.data);
        console.error('Headers:', error.response.headers);
      } else if (error.request) {
        console.error('Requisição:', error.request);
      } else {
        console.error('Mensagem:', error.message);
      }
      
      const errorMsg = error.response?.data?.error || 'Erro na comunicação com o servidor';
      setError(errorMsg);
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir este evento?')) {
      return;
    }
    
    setError('');
    setSuccess('');
    
    try {
      const response = await api.delete(`/api/eventos/${id}`);
      
      if (response.data.success) {
        setSuccess('Evento excluído com sucesso!');
        fetchEvents();
      } else {
        setError(response.data.error || 'Erro ao excluir evento');
      }
    } catch (error) {
      console.error('Erro ao excluir evento:', error);
      setError('Erro ao excluir evento. Por favor, tente novamente mais tarde.');
    }
  };

  const handleEdit = (event) => {
    setSelectedEvent(event);
    
    // Extrair data e hora do formato ISO para o formato de input
    let dateValue = '';
    let timeValue = '';
    
    if (event.event_date) {
      try {
        // Se já temos a data formatada, usar direto
        if (event.date) {
          dateValue = event.date;
        } else {
          // Converter a data do formato ISO
          const date = new Date(event.event_date);
          dateValue = date.toISOString().split('T')[0];
        }
        
        // Se já temos a hora formatada, usar direto
        if (event.time) {
          timeValue = event.time;
        } else if (event.event_date.includes('T')) {
          // Extrair a hora do formato ISO
          timeValue = event.event_date.split('T')[1].slice(0,5);
        }
      } catch (e) {
        console.error('Erro ao converter data:', e);
        dateValue = event.date || '';
        timeValue = event.time || '';
      }
    }
    
    setFormData({
      title: event.title || '',
      description: event.description || '',
      date: dateValue,
      time: timeValue,
      local: event.local || ''
    });
    
    setShowForm(true);
    setSuccess('');
    setError('');
  };

  const resetForm = () => {
    setSelectedEvent(null);
    setFormData({
      title: '',
      description: '',
      date: '',
      time: '',
      local: ''
    });
    setShowForm(false);
  };

  if (loading && events.length === 0) {
    return (
      <div className="container">
        <h1>Eventos</h1>
        <div className="loading-indicator">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="events-page">
      <div className="container">
        <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h1>Eventos</h1>
          <button 
            className="btn btn-primary"
            onClick={() => {
              setShowForm(!showForm);
              if (showForm) resetForm();
            }}
          >
            {showForm ? 'Cancelar' : 'Cadastrar Evento'}
          </button>
        </div>
        
        {error && <div className="alert alert-danger">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        
        {showForm && (
          <div className="form-container">
            <div className="form">
              <h2>{selectedEvent ? 'Editar Evento' : 'Novo Evento'}</h2>
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="title" className="form-label">Título</label>
                  <input
                    type="text"
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    className="form-control"
                    required
                  />
                </div>
                
                <div className="mb-3">
                  <label htmlFor="description" className="form-label">Descrição</label>
                  <textarea
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    className="form-control"
                    rows="4"
                    required
                  />
                </div>
                
                <div className="row mb-3">
                  <div className="col-md-6">
                    <label htmlFor="date" className="form-label">Data</label>
                    <input
                      type="date"
                      id="date"
                      name="date"
                      value={formData.date}
                      onChange={handleChange}
                      className="form-control"
                      required
                    />
                  </div>
                  
                  <div className="col-md-6">
                    <label htmlFor="time" className="form-label">Hora</label>
                    <input
                      type="time"
                      id="time"
                      name="time"
                      value={formData.time}
                      onChange={handleChange}
                      className="form-control"
                      required
                    />
                  </div>
                </div>
                
                <div className="mb-3">
                  <label htmlFor="local" className="form-label">Local</label>
                  <input
                    type="text"
                    id="local"
                    name="local"
                    value={formData.local}
                    onChange={handleChange}
                    className="form-control"
                    required
                  />
                </div>
                
                <div className="d-grid gap-2">
                  <button type="submit" className="btn btn-primary">
                    {selectedEvent ? 'Salvar Alterações' : 'Criar Evento'}
                  </button>
                  <button type="button" className="btn btn-secondary" onClick={resetForm}>
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        
        {events.length > 0 ? (
          <div className="row row-cols-1 row-cols-md-2 g-4">
            {events.map(event => (
              <div key={event.id} className="col">
                <div className="card h-100">
                  <div className="card-body">
                    <div className="text-muted small mb-2">
                      {event.date} às {event.time || '00:00'}
                    </div>
                    <h3 className="card-title">{event.title}</h3>
                    <p className="card-text">{event.description}</p>
                    <div className="text-muted mb-3">
                      <i className="bi bi-geo-alt"></i> {event.local}
                    </div>
                    <div className="d-flex gap-2">
                      <button 
                        className="btn btn-outline-primary"
                        onClick={() => handleEdit(event)}
                      >
                        <i className="bi bi-pencil"></i> Editar
                      </button>
                      <button 
                        className="btn btn-outline-danger"
                        onClick={() => handleDelete(event.id)}
                      >
                        <i className="bi bi-trash"></i> Excluir
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-5">
            <p className="lead">Não há eventos cadastrados.</p>
            {!showForm && (
              <button 
                className="btn btn-primary"
                onClick={() => setShowForm(true)}
              >
                <i className="bi bi-plus-lg"></i> Cadastrar Primeiro Evento
              </button>
            )}
          </div>
        )}
        
        <div className="mt-4">
          <Link to="/dashboard" className="btn btn-secondary">
            <i className="bi bi-arrow-left"></i> Voltar ao Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Events;