import React, { useState } from 'react';
import { linkedinService } from '../services/api';

const JobSearch = () => {
  const [searchParams, setSearchParams] = useState({
    keywords: '',
    location: '',
    experience_level: '',
    limit: 10
  });
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchParams.keywords.trim()) {
      setError('Please enter keywords to search for jobs');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const jobResults = await linkedinService.searchJobs(searchParams);
      setJobs(jobResults);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to search jobs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="job-search-container" style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>LinkedIn Job Search</h2>
      
      <form onSubmit={handleSearch} style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '10px' }}>
          <input
            type="text"
            name="keywords"
            placeholder="Job keywords (e.g., Software Engineer)"
            value={searchParams.keywords}
            onChange={handleInputChange}
            style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
            required
          />
        </div>
        
        <div style={{ marginBottom: '10px' }}>
          <input
            type="text"
            name="location"
            placeholder="Location (optional)"
            value={searchParams.location}
            onChange={handleInputChange}
            style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
          />
        </div>
        
        <div style={{ marginBottom: '10px' }}>
          <select
            name="experience_level"
            value={searchParams.experience_level}
            onChange={handleInputChange}
            style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
          >
            <option value="">Select Experience Level (optional)</option>
            <option value="entry">Entry Level</option>
            <option value="mid">Mid Level</option>
            <option value="senior">Senior Level</option>
            <option value="executive">Executive</option>
          </select>
        </div>
        
        <div style={{ marginBottom: '10px' }}>
          <input
            type="number"
            name="limit"
            placeholder="Number of results"
            value={searchParams.limit}
            onChange={handleInputChange}
            min="1"
            max="50"
            style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading}
          style={{ 
            backgroundColor: '#007bff', 
            color: 'white', 
            padding: '10px 20px', 
            border: 'none', 
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Searching...' : 'Search Jobs'}
        </button>
      </form>

      {error && (
        <div style={{ color: 'red', marginBottom: '20px', padding: '10px', backgroundColor: '#ffe6e6', borderRadius: '4px' }}>
          {error}
        </div>
      )}

      {jobs.length > 0 && (
        <div className="job-results">
          <h3>Job Results ({jobs.length})</h3>
          {jobs.map((job, index) => (
            <div 
              key={index} 
              style={{ 
                border: '1px solid #ddd', 
                padding: '15px', 
                marginBottom: '15px', 
                borderRadius: '4px',
                backgroundColor: '#f9f9f9'
              }}
            >
              <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>{job.title}</h4>
              <p style={{ margin: '5px 0', fontWeight: 'bold' }}>{job.company}</p>
              <p style={{ margin: '5px 0', color: '#666' }}>{job.location}</p>
              {job.posted_date && (
                <p style={{ margin: '5px 0', fontSize: '0.9em', color: '#888' }}>
                  Posted: {job.posted_date}
                </p>
              )}
              <p style={{ margin: '10px 0' }}>{job.description}</p>
              {job.url && (
                <a 
                  href={job.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ color: '#007bff', textDecoration: 'none' }}
                >
                  View Job →
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default JobSearch;