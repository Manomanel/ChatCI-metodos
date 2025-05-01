import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import logo from '../Assets/chatci-logo.png';

const Header = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="main-header">
      <div className="container header-container">
        <div className="header-logo">
          <Link to={currentUser ? '/dashboard' : '/'}>
            <img src={logo} alt="ChatCI Logo" className="small-logo" />
            <span>ChatCI</span>
          </Link>
        </div>

        {currentUser ? (
          <>
            <nav className="header-nav">
              <ul>
                <li><Link to="/dashboard">Dashboard</Link></li>
                <li><Link to="/events">Eventos</Link></li>
                <li><Link to="/professor/turmas">Turmas</Link></li>
                <li><Link to="/admin">Painel Admin</Link></li>
                <li><Link to="/admin/usuarios">Usuários</Link></li>
                <li><Link to="/profile">Perfil</Link></li>
              </ul>
            </nav>
            <div className="header-user">
              <Link to="/profile" className="user-profile">
                {currentUser.nome || currentUser.username}
              </Link>
              <button onClick={handleLogout} className="btn-logout">
                Sair
              </button>
            </div>
          </>
        ) : (
          <nav className="header-nav">
            <ul>
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/register">Cadastro</Link></li>
            </ul>
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;