import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/dashboard" className="navbar-brand">
          Job Application Manager
        </Link>
        <ul className="navbar-nav">
          <li><Link to="/dashboard">Dashboard</Link></li>
          <li><Link to="/applications">Applications</Link></li>
          <li><Link to="/resumes">Resumes</Link></li>
          <li><Link to="/job-search">Job Search</Link></li>
          <li><Link to="/profile">Profile</Link></li>
          <li>
            <span style={{ color: 'white', marginRight: '10px' }}>
              Welcome, {user?.username}
            </span>
            <button 
              onClick={handleLogout}
              className="btn btn-secondary btn-small"
            >
              Logout
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;