import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    bio: '',
  });
  const { currentUser } = useAuth();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/api/perfil');
      if (response.data.success) {
        setProfile(response.data.profile);
        setFormData({
          bio: response.data.profile.bio || '',
        });
      }
    } catch (error) {
      setError('Erro ao carregar perfil');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const updateProfile = async (e) => {
    e.preventDefault();
    try {
      // Note: The API endpoint for updating profile isn't shown in the provided code
      // This is a placeholder implementation
      const response = await api.put('/api/perfil', formData);
      if (response.data.success) {
        setProfile({...profile, ...formData});
        setEditing(false);
      }
    } catch (error) {
      setError('Erro ao atualizar perfil');
      console.error(error);
    }
  };

  if (loading) {
    return <div className="container">Carregando...</div>;
  }

  return (
    <div className="profile-page">
      <div className="container">
        <h1>Meu Perfil</h1>
        
        {error && <div className="error">{error}</div>}
        
        <div className="profile-card">
          <h2>{currentUser.nome || currentUser.username}</h2>
          <p className="email">{profile?.email}</p>
          
          {editing ? (
            <form onSubmit={updateProfile} className="form">
              <div>
                <label htmlFor="bio">Biografia</label>
                <textarea
                  id="bio"
                  name="bio"
                  value={formData.bio}
                  onChange={handleChange}
                  className="input-field"
                  rows="4"
                />
              </div>
              
              <div className="actions">
                <button type="submit" className="btn btn-primary">Salvar</button>
                <button 
                  type="button"
                  onClick={() => setEditing(false)}
                  className="btn btn-secondary"
                >
                  Cancelar
                </button>
              </div>
            </form>
          ) : (
            <>
              <div className="profile-section">
                <h3>Biografia</h3>
                <p>{profile?.bio || 'Nenhuma biografia definida.'}</p>
              </div>
              
              <button 
                onClick={() => setEditing(true)}
                className="btn btn-primary"
              >
                Editar Perfil
              </button>
            </>
          )}
        </div>
        
        <Link to="/dashboard" className="btn btn-secondary">Voltar ao Dashboard</Link>
      </div>
    </div>
  );
};

export default Profile;