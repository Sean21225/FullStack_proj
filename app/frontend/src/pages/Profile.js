import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: ''
  });
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const [profileResponse, statsResponse, resumesResponse] = await Promise.all([
        api.get('/user/profile'),
        api.get('/applications/statistics/summary'),
        api.get('/resume')
      ]);
      
      console.log('Profile data:', profileResponse.data);
      console.log('Stats data:', statsResponse.data);
      console.log('Resumes data:', resumesResponse.data);
      
      setProfile(profileResponse.data);
      
      // Combine statistics from applications and resumes
      const combinedStats = {
        ...statsResponse.data,
        total_resumes: Array.isArray(resumesResponse.data) ? resumesResponse.data.length : 0
      };
      
      setStats(combinedStats);
      setFormData({
        username: profileResponse.data.username,
        email: profileResponse.data.email
      });
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.put('/user/profile', formData);
      setProfile(response.data);
      setEditing(false);
      setMessage('Profile updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Failed to update profile:', error);
      setMessage('Failed to update profile. Please try again.');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleCancel = () => {
    setFormData({
      username: profile.username,
      email: profile.email
    });
    setEditing(false);
  };

  if (loading) {
    return <div className="loading">Loading profile...</div>;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Profile</h1>
        {!editing && (
          <button 
            onClick={() => setEditing(true)}
            className="btn btn-primary"
          >
            Edit Profile
          </button>
        )}
      </div>

      {message && (
        <div className={`alert ${message.includes('success') ? 'alert-success' : 'alert-error'}`}>
          {message}
        </div>
      )}

      <div className="card">
        {editing ? (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>

            <div className="actions">
              <button type="submit" className="btn btn-primary">
                Save Changes
              </button>
              <button 
                type="button" 
                onClick={handleCancel}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div>
            <div style={{ marginBottom: '20px' }}>
              <h3>Account Information</h3>
            </div>
            
            <div style={{ display: 'grid', gap: '15px' }}>
              <div>
                <strong>Username:</strong>
                <p style={{ margin: '5px 0 0 0', color: '#666' }}>{profile?.username}</p>
              </div>
              
              <div>
                <strong>Email:</strong>
                <p style={{ margin: '5px 0 0 0', color: '#666' }}>{profile?.email}</p>
              </div>
              
              <div>
                <strong>Member Since:</strong>
                <p style={{ margin: '5px 0 0 0', color: '#666' }}>
                  {profile?.created_at && new Date(profile.created_at).toLocaleDateString()}
                </p>
              </div>
              
              <div>
                <strong>Account Status:</strong>
                <p style={{ margin: '5px 0 0 0', color: profile?.is_active ? '#28a745' : '#dc3545' }}>
                  {profile?.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h3>Account Statistics</h3>
        <div className="grid">
          <div className="stat-card">
            <div className="stat-number">{stats.total_resumes || 0}</div>
            <div className="stat-label">Total Resumes</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.total_applications || 0}</div>
            <div className="stat-label">Total Applications</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">
              {stats.monthly_applications ? 
                Object.values(stats.monthly_applications).reduce((sum, count) => sum + count, 0) : 0}
            </div>
            <div className="stat-label">This Month</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;