import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
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
      setError('');
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
    setError('');
    setSuccess('');
    setSaving(true);
    
    try {
      const response = await api.put('/api/perfil', formData);
      
      if (response.data.success) {
        setProfile(response.data.profile);
        setEditing(false);
        setSuccess('Perfil atualizado com sucesso!');
        
        // Limpa a mensagem de sucesso após 3 segundos
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(response.data.error || 'Erro ao atualizar perfil');
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Erro ao atualizar perfil');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    // Restaurar os dados originais do perfil
    setFormData({
      bio: profile?.bio || '',
    });
    setEditing(false);
    setError('');
  };

  if (loading) {
    return (
      <div className="profile-page">
        <div className="container">
          <div className="loading-spinner">Carregando...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="container">
        <h1>Meu Perfil</h1>
        
        {error && <div className="alert alert-danger">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        
        <div className="profile-card">
          <h2>{profile?.nome || currentUser?.nome || currentUser?.username}</h2>
          <p className="email">{profile?.email}</p>
          
          {editing ? (
            <form onSubmit={updateProfile} className="form">
              <div className="form-group">
                <label htmlFor="bio">Biografia</label>
                <textarea
                  id="bio"
                  name="bio"
                  value={formData.bio}
                  onChange={handleChange}
                  className="form-control"
                  rows="4"
                  placeholder="Conte um pouco sobre você..."
                />
              </div>
              
              <div className="actions">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? 'Salvando...' : 'Salvar'}
                </button>
                <button 
                  type="button"
                  onClick={handleCancel}
                  className="btn btn-secondary"
                  disabled={saving}
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
        
        <Link to="/dashboard" className="btn btn-secondary mt-3">Voltar ao Dashboard</Link>
      </div>
    </div>
  );
};

export default Profile;