import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Applications = () => {
  const [applications, setApplications] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingApplication, setEditingApplication] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    company: ''
  });
  const [formData, setFormData] = useState({
    job_title: '',
    company: '',
    status: 'applied',
    job_description: '',
    application_url: '',
    notes: '',
    resume_id: ''
  });

  useEffect(() => {
    fetchApplications();
    fetchResumes();
  }, [filters]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchApplications = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status_filter', filters.status);
      if (filters.company) params.append('company_filter', filters.company);
      
      console.log('Fetching applications...');
      const response = await api.get(`/applications?${params.toString()}`);
      console.log('Applications response:', response.data);
      
      // Handle different response formats
      if (Array.isArray(response.data)) {
        setApplications(response.data);
      } else if (response.data.items) {
        setApplications(response.data.items);
      } else {
        setApplications([]);
      }
    } catch (error) {
      console.error('Failed to fetch applications:', error);
      setApplications([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchResumes = async () => {
    try {
      console.log('Fetching resumes for applications...');
      const response = await api.get('/resume');
      console.log('Resumes response for applications:', response.data);
      
      // Handle different response formats
      if (Array.isArray(response.data)) {
        setResumes(response.data);
      } else if (response.data.items) {
        setResumes(response.data.items);
      } else {
        setResumes([]);
      }
    } catch (error) {
      console.error('Failed to fetch resumes:', error);
      setResumes([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    console.log('Submitting application:', formData);
    
    try {
      const submitData = { ...formData };
      if (!submitData.resume_id) delete submitData.resume_id;

      let response;
      if (editingApplication) {
        response = await api.put(`/applications/${editingApplication.application_id}`, submitData);
      } else {
        response = await api.post('/applications', submitData);
      }
      
      console.log('Application saved successfully:', response.data);
      
      setShowModal(false);
      setEditingApplication(null);
      resetForm();
      fetchApplications();
    } catch (error) {
      console.error('Failed to save application:', error);
      console.error('Error response:', error.response);
      
      let errorMessage = 'Failed to save application. Please try again.';
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map(err => err.msg || err).join(', ');
        }
      }
      alert(errorMessage);
    }
  };

  const handleEdit = (application) => {
    setEditingApplication(application);
    setFormData({
      job_title: application.job_title,
      company: application.company,
      status: application.status,
      job_description: application.job_description || '',
      application_url: application.application_url || '',
      notes: application.notes || '',
      resume_id: application.resume_id || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (applicationId) => {
    if (window.confirm('Are you sure you want to delete this application?')) {
      try {
        await api.delete(`/applications/${applicationId}`);
        fetchApplications();
      } catch (error) {
        console.error('Failed to delete application:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      job_title: '',
      company: '',
      status: 'applied',
      job_description: '',
      application_url: '',
      notes: '',
      resume_id: ''
    });
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
    return <div className="loading">Loading applications...</div>;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Job Applications</h1>
        <button 
          onClick={() => {
            resetForm();
            setEditingApplication(null);
            setShowModal(true);
          }}
          className="btn btn-primary"
        >
          New Application
        </button>
      </div>

      {/* Filters */}
      <div className="filter-group">
        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
        >
          <option value="">All Status</option>
          <option value="applied">Applied</option>
          <option value="interview">Interview</option>
          <option value="offered">Offered</option>
          <option value="rejected">Rejected</option>
        </select>
        
        <input
          type="text"
          placeholder="Filter by company..."
          value={filters.company}
          onChange={(e) => setFilters({ ...filters, company: e.target.value })}
        />
      </div>

      {/* Applications Grid */}
      <div className="application-grid">
        {applications.map((app) => (
          <div key={app.application_id} className="application-card">
            <div className="application-header">
              <div>
                <h3 className="application-title">{app.job_title}</h3>
                <p className="application-company">{app.company}</p>
                <span className={getStatusBadgeClass(app.status)}>
                  {app.status}
                </span>
              </div>
              <div className="application-date">
                {new Date(app.created_at).toLocaleDateString()}
              </div>
            </div>
            
            {app.notes && (
              <p style={{ margin: '10px 0', color: '#666', fontSize: '14px' }}>
                {app.notes.substring(0, 100)}...
              </p>
            )}
            
            <div className="application-actions">
              <button 
                onClick={() => handleEdit(app)}
                className="btn btn-secondary btn-small"
              >
                Edit
              </button>
              <button 
                onClick={() => handleDelete(app.application_id)}
                className="btn btn-danger btn-small"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {applications.length === 0 && (
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <h3>No applications found</h3>
            <p>Start tracking your job applications by creating your first one.</p>
            <button 
              onClick={() => setShowModal(true)}
              className="btn btn-primary"
            >
              Create Application
            </button>
          </div>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">
                {editingApplication ? 'Edit Application' : 'New Application'}
              </h2>
              <button 
                onClick={() => setShowModal(false)}
                className="close-btn"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label>Job Title</label>
                  <input
                    type="text"
                    value={formData.job_title}
                    onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>Company</label>
                  <input
                    type="text"
                    value={formData.company}
                    onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                    required
                  />
                </div>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  >
                    <option value="applied">Applied</option>
                    <option value="interview">Interview</option>
                    <option value="offered">Offered</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Resume</label>
                  <select
                    value={formData.resume_id}
                    onChange={(e) => setFormData({ ...formData, resume_id: e.target.value })}
                  >
                    <option value="">Select Resume (Optional)</option>
                    {resumes.map((resume) => (
                      <option key={resume.resume_id} value={resume.resume_id}>
                        {resume.title}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="form-group">
                <label>Application URL</label>
                <input
                  type="url"
                  value={formData.application_url}
                  onChange={(e) => setFormData({ ...formData, application_url: e.target.value })}
                  placeholder="https://..."
                />
              </div>
              
              <div className="form-group">
                <label>Job Description</label>
                <textarea
                  value={formData.job_description}
                  onChange={(e) => setFormData({ ...formData, job_description: e.target.value })}
                  rows="4"
                />
              </div>
              
              <div className="form-group">
                <label>Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows="3"
                />
              </div>
              
              <div className="actions">
                <button type="submit" className="btn btn-primary">
                  {editingApplication ? 'Update' : 'Create'} Application
                </button>
                <button 
                  type="button" 
                  onClick={() => setShowModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Applications;