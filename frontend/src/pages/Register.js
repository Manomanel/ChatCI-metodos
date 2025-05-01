import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import logo from '../Assets/chatci-logo.png';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    primeiro_nome: '',
    ultimo_nome: '',
    email: '',
    senha: '',
    tipo: 'aluno'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('Enviando dados de cadastro:', formData);
      const result = await register(formData);
      if (result.success) {
        navigate('/login');
      } else {
        setError(result.error || 'Falha no cadastro');
      }
    } catch (err) {
      setError('Erro ao conectar ao servidor');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <img src={logo} alt="ChatCI Logo" className="logo" />
        <h1>Cadastro - ChatCI</h1>
      </header>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit} className="form">
        <div>
          <label htmlFor="username">Nome de Usuário</label>
          <input
            id="username"
            name="username"
            type="text"
            value={formData.username}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <div>
          <label htmlFor="primeiro_nome">Primeiro Nome</label>
          <input
            id="primeiro_nome"
            name="primeiro_nome"
            type="text"
            value={formData.primeiro_nome}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <div>
          <label htmlFor="ultimo_nome">Sobrenome</label>
          <input
            id="ultimo_nome"
            name="ultimo_nome"
            type="text"
            value={formData.ultimo_nome}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <div>
          <label htmlFor="senha">Senha</label>
          <input
            id="senha"
            name="senha"
            type="password"
            value={formData.senha}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <div>
          <label htmlFor="tipo">Tipo de Usuário</label>
          <select
            id="tipo"
            name="tipo"
            value={formData.tipo}
            onChange={handleChange}
            className="input-field"
            required
          >
            <option value="aluno">Aluno</option>
            <option value="professor">Professor</option>
            <option value="admin">Administrador</option>
            <option value="superuser">Super Usuário</option>
          </select>
        </div>

        <div className="actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Cadastrando...' : 'Cadastrar'}
          </button>
          <Link to="/login" className="btn btn-secondary">Voltar</Link>
        </div>
      </form>
    </div>
  );
};

export default Register;