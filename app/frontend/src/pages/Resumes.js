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
      const response = await api.get('/resume');
      setResumes(response.data.items || []);
    } catch (error) {
      console.error('Failed to fetch resumes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingResume) {
        await api.put(`/resume/${editingResume.resume_id}`, formData);
      } else {
        await api.post('/resume', formData);
      }
      
      setShowModal(false);
      setEditingResume(null);
      resetForm();
      fetchResumes();
    } catch (error) {
      console.error('Failed to save resume:', error);
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