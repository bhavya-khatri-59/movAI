import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function Navbar({ user, onLogout }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/home" className="navbar-logo">
          mov<span>AI</span>
        </Link>

        <form className="navbar-search" onSubmit={handleSearch}>
          <span className="search-icon">⌕</span>
          <input
            type="text"
            placeholder="Search movies, actors..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>

        <div className="navbar-links">
          <Link to="/home" className={isActive('/home')}>Home</Link>
          <Link to="/search" className={isActive('/search')}>Discover</Link>
          <Link to="/feed" className={isActive('/feed')}>Social</Link>
        </div>

        <div className="navbar-user">
          <Link to={`/profile/${user.id}`} className="navbar-avatar">
            {user.name?.charAt(0).toUpperCase()}
          </Link>
          <button className="btn btn-ghost" onClick={onLogout}
                  style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '4px 12px', borderRadius: '20px', border: '1px solid var(--outline)' }}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
