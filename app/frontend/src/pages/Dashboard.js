import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentApplications, setRecentApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, applicationsResponse] = await Promise.all([
        api.get('/applications/statistics/summary'),
        api.get('/applications?limit=5')
      ]);
      
      setStats(statsResponse.data);
      
      // Handle applications response format
      if (Array.isArray(applicationsResponse.data)) {
        setRecentApplications(applicationsResponse.data);
      } else if (applicationsResponse.data.items) {
        setRecentApplications(applicationsResponse.data.items);
      } else {
        setRecentApplications([]);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    const statusMap = {
      'applied': 'status-applied',
      'interview': 'status-interview',
      'offered': 'status-offered',
      'rejected': 'status-rejected'
    };
    return `status-badge ${statusMap[status] || 'status-applied'}`;
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <Link to="/applications" className="btn btn-primary">
          View All Applications
        </Link>
      </div>

      {/* Statistics Grid */}
      <div className="grid">
        <div className="stat-card">
          <div className="stat-number">{stats?.total_applications || 0}</div>
          <div className="stat-label">Total Applications</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">
            {stats?.status_breakdown?.interview || 0}
          </div>
          <div className="stat-label">Interviews</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">
            {stats?.status_breakdown?.offered || 0}
          </div>
          <div className="stat-label">Offers</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">
            {stats?.success_rate?.toFixed(1) || 0}%
          </div>
          <div className="stat-label">Success Rate</div>
        </div>
      </div>

      {/* Recent Applications */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Recent Applications</h2>
          <Link to="/applications" className="btn btn-secondary btn-small">
            View All
          </Link>
        </div>
        
        {recentApplications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            <p>No applications yet. <Link to="/applications">Create your first application</Link></p>
          </div>
        ) : (
          <div className="table">
            <table style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Applied Date</th>
                </tr>
              </thead>
              <tbody>
                {recentApplications.map((app) => (
                  <tr key={app.application_id}>
                    <td>{app.job_title}</td>
                    <td>{app.company}</td>
                    <td>
                      <span className={getStatusBadgeClass(app.status)}>
                        {app.status}
                      </span>
                    </td>
                    <td>{new Date(app.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2>Quick Actions</h2>
        <div className="actions">
          <Link to="/applications" className="btn btn-primary">
            New Application
          </Link>
          <Link to="/resumes" className="btn btn-secondary">
            Manage Resumes
          </Link>
          <Link to="/profile" className="btn btn-secondary">
            Update Profile
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;