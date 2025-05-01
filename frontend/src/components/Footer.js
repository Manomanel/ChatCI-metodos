import React from 'react';

const Footer = () => {
  return (
    <footer className="main-footer">
      <div className="footer-container">
        <p>&copy; {new Date().getFullYear()} ChatCI - Sistema de Comunicação para Cursos</p>
      </div>
    </footer>
  );
};

export default Footer;