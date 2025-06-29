import React, { useState } from 'react';
import { linkedinService } from '../services/api';

const CompanySearch = () => {
  const [companyName, setCompanyName] = useState('');
  const [companyInfo, setCompanyInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!companyName.trim()) {
      setError('Please enter a company name');
      return;
    }

    setLoading(true);
    setError('');
    setCompanyInfo(null);
    
    try {
      const result = await linkedinService.getCompanyInfo(companyName);
      setCompanyInfo(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to find company information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="company-search-container" style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>LinkedIn Company Search</h2>
      
      <form onSubmit={handleSearch} style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '10px' }}>
          <input
            type="text"
            placeholder="Enter company name (e.g., Google, Microsoft)"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
            required
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
          {loading ? 'Searching...' : 'Search Company'}
        </button>
      </form>

      {error && (
        <div style={{ color: 'red', marginBottom: '20px', padding: '10px', backgroundColor: '#ffe6e6', borderRadius: '4px' }}>
          {error}
        </div>
      )}

      {companyInfo && (
        <div className="company-info" style={{ 
          border: '1px solid #ddd', 
          padding: '20px', 
          borderRadius: '4px',
          backgroundColor: '#f9f9f9'
        }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#333' }}>{companyInfo.name}</h3>
          
          {companyInfo.industry && (
            <div style={{ marginBottom: '10px' }}>
              <strong>Industry:</strong> {companyInfo.industry}
            </div>
          )}
          
          {companyInfo.size && (
            <div style={{ marginBottom: '10px' }}>
              <strong>Company Size:</strong> {companyInfo.size}
            </div>
          )}
          
          {companyInfo.headquarters && (
            <div style={{ marginBottom: '10px' }}>
              <strong>Headquarters:</strong> {companyInfo.headquarters}
            </div>
          )}
          
          {companyInfo.website && (
            <div style={{ marginBottom: '10px' }}>
              <strong>Website:</strong> 
              <a 
                href={companyInfo.website} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#007bff', textDecoration: 'none', marginLeft: '5px' }}
              >
                {companyInfo.website}
              </a>
            </div>
          )}
          
          {companyInfo.description && (
            <div style={{ marginTop: '15px' }}>
              <strong>Description:</strong>
              <p style={{ marginTop: '5px', lineHeight: '1.5' }}>{companyInfo.description}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CompanySearch;