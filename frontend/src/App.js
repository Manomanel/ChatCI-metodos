import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
// Importar componentes de rota diretamente dos componentes, não da pasta routes
import AdminRoute from './components/AdminRoute';
import ProfessorRoute from './components/ProfessorRoute';

// Componentes de layout
import Header from './components/Header';
import Footer from './components/Footer';

// Páginas públicas
import Login from './pages/Login';
import Register from './pages/Register';
import NotFound from './pages/NotFound';

// Páginas protegidas
import Dashboard from './pages/Dashboard';
import Events from './pages/Events';
import Profile from './pages/Profile';
// Importar AdminPanel diretamente da raiz de pages
import AdminPanel from './pages/AdminPanel';
import AdminUsuarios from './pages/admin/AdminUsuarios';

// Importar com a capitalização correta da pasta
import Turmas from './pages/Turmas/Turmas';

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
              
              {/* Rotas protegidas gerais */}
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
              
              {/* Rotas de admin */}
              <Route path="/admin" element={
                <AdminRoute>
                  <AdminPanel />
                </AdminRoute>
              } />
              <Route path="/admin/usuarios" element={
                <AdminRoute>
                  <AdminUsuarios />
                </AdminRoute>
              } />
              
              {/* Rotas de turmas para todos os usuários */}
              <Route path="/turmas" element={
                <PrivateRoute>
                  <Turmas />
                </PrivateRoute>
              } />
              <Route path="/turmas/:grupoId" element={
                <PrivateRoute>
                  <Turmas />
                </PrivateRoute>
              } />
              
              {/* Rotas de turmas específicas para professores - usando o mesmo componente */}
              <Route path="/professor/turmas" element={
                <ProfessorRoute>
                  <Turmas isProfessorView={true} />
                </ProfessorRoute>
              } />
              <Route path="/professor/turma/:grupoId" element={
                <ProfessorRoute>
                  <Turmas isProfessorView={true} />
                </ProfessorRoute>
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