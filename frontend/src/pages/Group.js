import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Group = () => {
  const [group, setGroup] = useState(null);
  const [messages, setMessages] = useState([]);
  const [members, setMembers] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { currentUser, isAdmin } = useAuth();
  const { groupId } = useParams();
  const messagesEndRef = useRef(null);
  const [messageInterval, setMessageInterval] = useState(null);

  useEffect(() => {
    fetchGroupDetails();
    fetchMessages();
    fetchMembers();

    // Setup interval to fetch messages
    const interval = setInterval(() => {
      fetchMessages();
    }, 5000);
    setMessageInterval(interval);

    return () => {
      clearInterval(messageInterval);
    };
  }, [groupId]);

  useEffect(() => {
    // Scroll to bottom when messages change
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchGroupDetails = async () => {
    try {
      const response = await api.get(`/api/grupos/${groupId}`);
      if (response.data.success) {
        setGroup(response.data.group);
      }
    } catch (error) {
      setError('Erro ao carregar detalhes do grupo');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async () => {
    try {
      const response = await api.get(`/api/grupos/${groupId}/mensagens`);
      if (response.data.success) {
        setMessages(response.data.messages);
      }
    } catch (error) {
      console.error('Erro ao carregar mensagens', error);
    }
  };

  const fetchMembers = async () => {
    try {
      const response = await api.get(`/api/grupos/${groupId}/membros`);
      if (response.data.success) {
        setMembers(response.data.members);
      }
    } catch (error) {
      console.error('Erro ao carregar membros', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      const response = await api.post(`/api/grupos/${groupId}/mensagens`, {
        text: newMessage
      });
      
      if (response.data.success) {
        setNewMessage('');
        // Fetch updated messages
        fetchMessages();
      }
    } catch (error) {
      setError('Erro ao enviar mensagem');
      console.error(error);
    }
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return <div className="container">Carregando...</div>;
  }

  if (!group) {
    return (
      <div className="container">
        <div className="error">Grupo não encontrado</div>
        <Link to="/dashboard" className="btn btn-primary">Voltar ao Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="group-page">
      <div className="container">
        <div className="group-header">
          <h1>{group.name}</h1>
          <p>{group.description}</p>
        </div>
        
        {error && <div className="error">{error}</div>}
        
        <div className="group-layout">
          <div className="chat-container">
            <div className="messages">
              {messages.length > 0 ? (
                messages.map(message => (
                  <div 
                    key={message.id} 
                    className={`message ${message.user_id === currentUser.id ? 'own-message' : ''}`}
                  >
                    <div className="message-header">
                      <strong>{message.username}</strong>
                      <span className="message-time">{formatDateTime(message.created_at)}</span>
                    </div>
                    <div className="message-body">{message.text}</div>
                  </div>
                ))
              ) : (
                <div className="no-messages">Nenhuma mensagem ainda. Seja o primeiro a enviar!</div>
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <form onSubmit={sendMessage} className="message-form">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Digite sua mensagem..."
                className="input-field"
              />
              <button type="submit" className="btn btn-primary">Enviar</button>
            </form>
          </div>
          
          <div className="sidebar">
            <div className="members-list">
              <h3>Membros ({members.length})</h3>
              <ul>
                {members.map(member => (
                  <li key={member.id} className="member-item">
                    {member.nome || member.username}
                    {isAdmin && member.id !== currentUser.id && (
                      <button className="btn btn-small btn-danger">Banir</button>
                    )}
                  </li>
                ))}
              </ul>
            </div>
            
            <Link to="/dashboard" className="btn btn-secondary">Voltar ao Dashboard</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Group;