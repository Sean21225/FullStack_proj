import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Resumes = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingResume, setEditingResume] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: ''
  });

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      console.log('Fetching resumes...');
      const response = await api.get('/resume');
      console.log('Resume response:', response.data);
      
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
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    console.log('Form data being submitted:', formData);
    
    // Validate form data
    if (!formData.title || formData.title.trim().length < 1) {
      alert('Resume title is required');
      return;
    }
    
    if (!formData.content || formData.content.trim().length < 10) {
      alert('Resume content must be at least 10 characters long');
      return;
    }
    
    // Prepare clean data for submission
    const submitData = {
      title: formData.title.trim(),
      content: formData.content.trim()
    };
    
    console.log('Submitting data:', submitData);
    
    try {
      let response;
      if (editingResume) {
        response = await api.put(`/resume/${editingResume.resume_id}`, submitData);
      } else {
        response = await api.post('/resume', submitData);
      }
      
      console.log('Resume saved successfully:', response.data);
      
      setShowModal(false);
      setEditingResume(null);
      resetForm();
      fetchResumes();
    } catch (error) {
      console.error('Failed to save resume:', error);
      console.error('Error response:', error.response);
      
      let errorMessage = 'Failed to save resume. Please try again.';
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map(err => {
            if (typeof err === 'string') return err;
            return err.msg || err.message || JSON.stringify(err);
          }).join(', ');
        }
      } else if (error.response?.status === 422) {
        errorMessage = 'Validation error: Please check your input data.';
      }
      
      alert(errorMessage);
    }
  };

  const handleEdit = (resume) => {
    setEditingResume(resume);
    setFormData({
      title: resume.title,
      content: resume.content
    });
    setShowModal(true);
  };

  const handleDelete = async (resumeId) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      try {
        await api.delete(`/resume/${resumeId}`);
        fetchResumes();
      } catch (error) {
        console.error('Failed to delete resume:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      content: ''
    });
  };

  if (loading) {
    return <div className="loading">Loading resumes...</div>;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Resumes</h1>
        <button 
          onClick={() => {
            resetForm();
            setEditingResume(null);
            setShowModal(true);
          }}
          className="btn btn-primary"
        >
          New Resume
        </button>
      </div>

      <div className="resume-list">
        {resumes.map((resume) => (
          <div key={resume.resume_id} className="resume-item">
            <div className="resume-info">
              <h3>{resume.title}</h3>
              <p>
                Created: {new Date(resume.created_at).toLocaleDateString()}
                {resume.updated_at && (
                  <span> • Updated: {new Date(resume.updated_at).toLocaleDateString()}</span>
                )}
              </p>
              <p style={{ color: '#666', fontSize: '14px' }}>
                {resume.content.substring(0, 150)}...
              </p>
            </div>
            <div className="resume-actions">
              <button 
                onClick={() => handleEdit(resume)}
                className="btn btn-secondary btn-small"
              >
                Edit
              </button>
              <button 
                onClick={() => handleDelete(resume.resume_id)}
                className="btn btn-danger btn-small"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {resumes.length === 0 && (
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <h3>No resumes found</h3>
            <p>Create your first resume to get started with job applications.</p>
            <button 
              onClick={() => setShowModal(true)}
              className="btn btn-primary"
            >
              Create Resume
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
                {editingResume ? 'Edit Resume' : 'New Resume'}
              </h2>
              <button 
                onClick={() => setShowModal(false)}
                className="close-btn"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Resume Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g., Software Engineer Resume"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Resume Content</label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  rows="15"
                  placeholder="Paste your resume content here..."
                  required
                />
              </div>
              
              <div className="actions">
                <button type="submit" className="btn btn-primary">
                  {editingResume ? 'Update' : 'Create'} Resume
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

export default Resumes;