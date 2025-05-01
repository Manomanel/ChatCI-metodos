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
    titulo: '',
    descricao: '',
    data: '',
    hora: '',
    local: ''
  });

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/eventos');
      if (response.data.success) {
        setEvents(response.data.eventos || []);
      } else {
        setEvents([]);
        setError('Erro ao carregar eventos: ' + (response.data.error || 'Resposta inválida do servidor'));
      }
    } catch (error) {
      console.error('Erro ao buscar eventos:', error);
      setEvents([]);
      setError('Erro ao carregar eventos. Por favor, tente novamente mais tarde.');
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
      let response;
      if (selectedEvent) {
        // Atualizar evento existente
        response = await api.put(`/api/eventos/${selectedEvent.id}`, formData);
      } else {
        // Criar novo evento
        response = await api.post('/api/eventos', formData);
      }
      
      if (response.data.success) {
        setSuccess(selectedEvent ? 'Evento atualizado com sucesso!' : 'Evento criado com sucesso!');
        resetForm();
        fetchEvents();
      } else {
        setError(response.data.error || 'Erro ao salvar evento');
      }
    } catch (error) {
      console.error('Erro ao salvar evento:', error);
      setError('Erro ao salvar evento. Por favor, tente novamente mais tarde.');
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
    setFormData({
      titulo: event.titulo || '',
      descricao: event.descricao || '',
      data: event.data || '',
      hora: event.hora || '',
      local: event.local || ''
    });
    setShowForm(true);
    setSuccess('');
    setError('');
  };

  const resetForm = () => {
    setSelectedEvent(null);
    setFormData({
      titulo: '',
      descricao: '',
      data: '',
      hora: '',
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
        
        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}
        
        {showForm && (
          <div className="form-container">
            <div className="form">
              <h2>{selectedEvent ? 'Editar Evento' : 'Novo Evento'}</h2>
              <form onSubmit={handleSubmit}>
                <div>
                  <label htmlFor="titulo">Título</label>
                  <input
                    type="text"
                    id="titulo"
                    name="titulo"
                    value={formData.titulo}
                    onChange={handleChange}
                    className="input-field"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="descricao">Descrição</label>
                  <textarea
                    id="descricao"
                    name="descricao"
                    value={formData.descricao}
                    onChange={handleChange}
                    className="input-field"
                    rows="4"
                    required
                  />
                </div>
                
                <div style={{ display: 'flex', gap: '10px' }}>
                  <div style={{ flex: 1 }}>
                    <label htmlFor="data">Data</label>
                    <input
                      type="date"
                      id="data"
                      name="data"
                      value={formData.data}
                      onChange={handleChange}
                      className="input-field"
                      required
                    />
                  </div>
                  
                  <div style={{ flex: 1 }}>
                    <label htmlFor="hora">Hora</label>
                    <input
                      type="time"
                      id="hora"
                      name="hora"
                      value={formData.hora}
                      onChange={handleChange}
                      className="input-field"
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="local">Local</label>
                  <input
                    type="text"
                    id="local"
                    name="local"
                    value={formData.local}
                    onChange={handleChange}
                    className="input-field"
                    required
                  />
                </div>
                
                <div className="actions">
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                  >
                    Salvar
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={resetForm}
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        
        {events.length > 0 ? (
          <div className="events-list">
            {events.map(event => (
              <div key={event.id} className="event-card">
                <div className="event-date">{event.data} às {event.hora}</div>
                <h3>{event.titulo}</h3>
                <p>{event.descricao}</p>
                <div className="event-location">Local: {event.local}</div>
                
                <div className="event-footer">
                  <button 
                    className="btn btn-secondary"
                    onClick={() => handleEdit(event)}
                    style={{ marginRight: '10px' }}
                  >
                    Editar
                  </button>
                  <button 
                    className="btn"
                    onClick={() => handleDelete(event.id)}
                    style={{ backgroundColor: 'var(--danger-color)', color: 'white' }}
                  >
                    Excluir
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '30px 0' }}>
            <p>Não há eventos cadastrados.</p>
            {!showForm && (
              <button 
                className="btn btn-primary"
                onClick={() => setShowForm(true)}
                style={{ marginTop: '10px' }}
              >
                Cadastrar Primeiro Evento
              </button>
            )}
          </div>
        )}
        
        <div style={{ marginTop: '20px' }}>
          <Link to="/dashboard" className="btn btn-secondary">
            Voltar ao Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Events;