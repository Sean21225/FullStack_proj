import React, { useState } from 'react';
import { linkedInService } from '../services/api';

const JobSearch = () => {
  const [searchParams, setSearchParams] = useState({
    keywords: '',
    location: '',
    experience_level: '',
    limit: 10
  });
  const [companySearch, setCompanySearch] = useState('');
  const [jobs, setJobs] = useState([]);
  const [companyInfo, setCompanyInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('jobs');

  const handleJobSearch = async (e) => {
    e.preventDefault();
    if (!searchParams.keywords.trim()) {
      setError('Please enter job keywords');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const results = await linkedInService.searchJobs(searchParams);
      setJobs(results);
      
      // Show helpful message for location-based searches
      if (searchParams.location && results.length === 0) {
        // Check if it's an unsupported location
        const unsupportedLocations = ['tel aviv', 'israel', 'india', 'japan', 'korea'];
        const isUnsupported = unsupportedLocations.some(loc => 
          searchParams.location.toLowerCase().includes(loc)
        );
        
        if (isUnsupported) {
          setError(`Jobs in ${searchParams.location} aren't available in our current databases. Try searching without location for remote opportunities, or search in US, UK, Germany, France, Netherlands, Canada, or Australia.`);
        } else {
          setError(`No jobs found in ${searchParams.location}. Try a different location or search without location for remote jobs.`);
        }
      } else if (searchParams.location && results.length > 0) {
        // Check if we got results but they might not be from the exact location
        const hasLocationMatch = results.some(job => 
          job.location.toLowerCase().includes(searchParams.location.toLowerCase())
        );
        
        if (!hasLocationMatch && results.length < 5) {
          setError(`Limited results for ${searchParams.location}. Consider searching in major cities or without location for more opportunities.`);
        }
      }
    } catch (err) {
      setError('Failed to search jobs. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompanySearch = async (e) => {
    e.preventDefault();
    if (!companySearch.trim()) {
      setError('Please enter a company name');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const info = await linkedInService.getCompanyInfo(companySearch);
      setCompanyInfo(info);
    } catch (err) {
      setError('Failed to get company information. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Job Search</h1>
        <p>Search for jobs and company information from LinkedIn</p>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab ${activeTab === 'jobs' ? 'active' : ''}`}
          onClick={() => setActiveTab('jobs')}
        >
          Job Search
        </button>
        <button 
          className={`tab ${activeTab === 'company' ? 'active' : ''}`}
          onClick={() => setActiveTab('company')}
        >
          Company Lookup
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Job Search Tab */}
      {activeTab === 'jobs' && (
        <div className="tab-content">
          <form onSubmit={handleJobSearch} className="search-form">
            <div className="form-group">
              <label>Job Keywords *</label>
              <input
                type="text"
                value={searchParams.keywords}
                onChange={(e) => setSearchParams({...searchParams, keywords: e.target.value})}
                placeholder="e.g., Software Engineer, Data Scientist"
                required
              />
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  value={searchParams.location}
                  onChange={(e) => setSearchParams({...searchParams, location: e.target.value})}
                  placeholder="e.g., New York, NY"
                />
              </div>
              
              <div className="form-group">
                <label>Experience Level</label>
                <select
                  value={searchParams.experience_level}
                  onChange={(e) => setSearchParams({...searchParams, experience_level: e.target.value})}
                >
                  <option value="">Any Level</option>
                  <option value="internship">Internship</option>
                  <option value="entry_level">Entry Level</option>
                  <option value="associate">Associate</option>
                  <option value="mid_senior">Mid-Senior</option>
                  <option value="director">Director</option>
                  <option value="executive">Executive</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Results Limit</label>
                <select
                  value={searchParams.limit}
                  onChange={(e) => setSearchParams({...searchParams, limit: parseInt(e.target.value)})}
                >
                  <option value={5}>5 results</option>
                  <option value={10}>10 results</option>
                  <option value={25}>25 results</option>
                  <option value={50}>50 results</option>
                </select>
              </div>
            </div>
            
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Searching...' : 'Search Jobs'}
            </button>
          </form>

          {/* Job Results */}
          {jobs.length > 0 && (
            <div className="results-section">
              <h3>Job Results ({jobs.length})</h3>
              <div className="job-list">
                {jobs.map((job, index) => (
                  <div key={index} className="job-card">
                    <div className="job-header">
                      <h4>{job.title}</h4>
                      <span className="company">{job.company}</span>
                    </div>
                    <div className="job-details">
                      <p className="location">{job.location}</p>
                      {job.posted_date && <p className="date">Posted: {job.posted_date}</p>}
                    </div>
                    <div className="job-description">
                      <p>{job.description?.substring(0, 200)}...</p>
                    </div>
                    {job.url && (
                      <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                        View Job
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Company Search Tab */}
      {activeTab === 'company' && (
        <div className="tab-content">
          <form onSubmit={handleCompanySearch} className="search-form">
            <div className="form-group">
              <label>Company Name *</label>
              <input
                type="text"
                value={companySearch}
                onChange={(e) => setCompanySearch(e.target.value)}
                placeholder="e.g., Google, Microsoft, Apple"
                required
              />
            </div>
            
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Searching...' : 'Get Company Info'}
            </button>
          </form>

          {/* Company Results */}
          {companyInfo && (
            <div className="results-section">
              <h3>Company Information</h3>
              <div className="company-card">
                <div className="company-header">
                  <h4>{companyInfo.name}</h4>
                  <span className="industry">{companyInfo.industry}</span>
                </div>
                
                <div className="company-details">
                  {companyInfo.size && <p><strong>Size:</strong> {companyInfo.size}</p>}
                  {companyInfo.headquarters && <p><strong>Headquarters:</strong> {companyInfo.headquarters}</p>}
                  {companyInfo.website && (
                    <p><strong>Website:</strong> 
                      <a href={companyInfo.website} target="_blank" rel="noopener noreferrer">
                        {companyInfo.website}
                      </a>
                    </p>
                  )}
                </div>
                
                <div className="company-description">
                  <h5>About</h5>
                  <p>{companyInfo.description}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default JobSearch;