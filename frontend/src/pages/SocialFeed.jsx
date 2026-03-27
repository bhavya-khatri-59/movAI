import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { searchUsers, followUser } from '../services/api';
import { getFeed } from '../services/api';
import './SocialFeed.css';

export default function SocialFeed() {
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadFeed();
  }, []);

  const loadFeed = async () => {
    setLoading(true);
    try {
      const res = await getFeed(1);
      setFeed(res.data.feed || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    try {
      const res = await searchUsers(searchQuery.trim());
      setSearchResults(res.data.users || []);
    } catch (e) { console.error(e); }
    finally { setSearching(false); }
  };

  const handleFollow = async (userId) => {
    await followUser(userId);
    // Refresh search results
    if (searchQuery.trim()) {
      const res = await searchUsers(searchQuery.trim());
      setSearchResults(res.data.users || []);
    }
    loadFeed();
  };

  const getActionText = (item) => {
    switch (item.action) {
      case 'rated': return `rated a movie ${item.metadata?.rating ? `★${item.metadata.rating}` : ''}`;
      case 'reviewed': return 'wrote a review';
      case 'watchlisted': return 'added to watchlist';
      case 'liked': return 'liked a movie';
      case 'watched': return 'watched a movie';
      case 'followed': return 'followed someone';
      default: return item.action;
    }
  };

  const timeAgo = (date) => {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  return (
    <div className="page-content">
      <div className="container">
        <div className="feed-layout">
          <div className="feed-main">
            <h1 className="animate-fade-in-up" style={{ marginBottom: 'var(--space-xl)' }}>Social Feed</h1>

            {loading ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                {Array(5).fill(0).map((_, i) => <div key={i} className="skeleton" style={{ height: 100 }} />)}
              </div>
            ) : feed.length === 0 ? (
              <div className="empty-feed glass-card" style={{ padding: 'var(--space-2xl)', textAlign: 'center' }}>
                <h3>Your feed is empty</h3>
                <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-sm)' }}>
                  Search for users by name or username and follow them to see their activity here.
                </p>
              </div>
            ) : (
              <div className="feed-list">
                {feed.map((item) => (
                  <div key={item.id} className="feed-item glass-card">
                    <div className="feed-avatar">
                      {item.user?.name?.charAt(0) || '?'}
                    </div>
                    <div className="feed-content">
                      <div className="feed-action">
                        <strong>{item.user?.name}</strong> {getActionText(item)}
                      </div>
                      <div className="feed-time">{timeAgo(item.created_at)}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="feed-sidebar">
            {/* Find Friends */}
            <div className="sidebar-card glass-card">
              <h3>Find Friends</h3>
              <form onSubmit={handleSearch} style={{ marginTop: 'var(--space-md)' }}>
                <input
                  className="input-field"
                  type="text"
                  placeholder="Search by name or username..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ fontSize: 'var(--font-small)' }}
                />
                <button className="btn btn-primary" type="submit" style={{ width: '100%', marginTop: 'var(--space-sm)' }}
                        disabled={searching}>
                  {searching ? 'Searching...' : 'Search'}
                </button>
              </form>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="search-results-list">
                  {searchResults.map((u) => (
                    <div key={u.id} className="search-user-item">
                      <div className="search-user-avatar">{u.name?.charAt(0)}</div>
                      <div className="search-user-info">
                        <div className="search-user-name">{u.name}</div>
                        <div className="search-user-username">@{u.username}</div>
                      </div>
                      <div style={{ display: 'flex', gap: '4px' }}>
                        <button className="btn btn-outline" style={{ padding: '3px 10px', fontSize: '0.7rem' }}
                                onClick={() => navigate(`/profile/${u.id}`)}>
                          View
                        </button>
                        <button className="btn btn-primary" style={{ padding: '3px 10px', fontSize: '0.7rem' }}
                                onClick={() => handleFollow(u.id)}>
                          Follow
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="sidebar-card glass-card" style={{ marginTop: 'var(--space-md)' }}>
              <h3>Quick Links</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)', marginTop: 'var(--space-md)' }}>
                <Link to="/search" style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-small)' }}>Discover Movies</Link>
                <Link to="/home" style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-small)' }}>Home</Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
