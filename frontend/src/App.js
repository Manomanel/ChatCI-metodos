import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
// Importar outros componentes necessários
import Header from './components/Header';
import Footer from './components/Footer';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import AdminPanel from './pages/AdminPanel';
import AdminUsuarios from './pages/admin/AdminUsuarios';
import ProfessorTurmas from './pages/professor/ProfessorTurmas';
import NotFound from './pages/NotFound';
import Dashboard from './pages/Dashboard';
import Events from './pages/Events';
import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="app">
          <Header />
          <main className="main-content">
            <Routes>
              {/* Rotas públicas */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Todas as rotas protegidas agora usam apenas PrivateRoute */}
              <Route path="/dashboard" element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } />
              <Route path="/events" element={
                <PrivateRoute>
                  <Events />
                </PrivateRoute>
              } />
              <Route path="/profile" element={
                <PrivateRoute>
                  <Profile />
                </PrivateRoute>
              } />
              <Route path="/admin" element={
                <PrivateRoute>
                  <AdminPanel />
                </PrivateRoute>
              } />
              <Route path="/admin/usuarios" element={
                <PrivateRoute>
                  <AdminUsuarios />
                </PrivateRoute>
              } />
              <Route path="/professor/turmas" element={
                <PrivateRoute>
                  <ProfessorTurmas />
                </PrivateRoute>
              } />
              
              <Route path="/" element={<Login />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;