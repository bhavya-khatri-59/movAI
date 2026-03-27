import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchMovies, getPopular, getGenres, getByGenre } from '../services/api';
import MovieCard from '../components/MovieCard';
import './Search.css';

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState([]);
  const [genres, setGenres] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getGenres().then(r => setGenres(r.data.genres || [])).catch(() => {});
    const q = searchParams.get('q');
    if (q) {
      handleSearch(q);
    } else {
      loadPopular();
    }
  }, []);

  const loadPopular = async () => {
    setLoading(true);
    try {
      const res = await getPopular();
      setResults(res.data.results || []);
    } finally { setLoading(false); }
  };

  const handleSearch = async (q) => {
    if (!q?.trim()) return loadPopular();
    setLoading(true);
    setSelectedGenre(null);
    try {
      const res = await searchMovies(q.trim());
      setResults(res.data.results || []);
    } finally { setLoading(false); }
  };

  const handleGenreFilter = async (genreId) => {
    if (selectedGenre === genreId) {
      setSelectedGenre(null);
      return loadPopular();
    }
    setSelectedGenre(genreId);
    setQuery('');
    setLoading(true);
    try {
      const res = await getByGenre(genreId);
      setResults(res.data.results || []);
    } finally { setLoading(false); }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    setSearchParams(query ? { q: query } : {});
    handleSearch(query);
  };

  return (
    <div className="page-content">
      <div className="container">
        <div className="search-header animate-fade-in-up">
          <h1>Discover Movies</h1>
          <form className="search-bar-large" onSubmit={onSubmit}>
            <span className="search-icon-lg">🔍</span>
            <input className="input-field search-input-lg" type="text" placeholder="Search movies, actors, directors..."
                   value={query} onChange={(e) => setQuery(e.target.value)} />
          </form>
        </div>

        {/* Genre Filters */}
        <div className="genre-filter-bar">
          {genres.slice(0, 12).map(g => (
            <button key={g.id} className={`mood-chip ${selectedGenre === g.id ? 'active' : ''}`}
                    onClick={() => handleGenreFilter(g.id)}>
              {g.name}
            </button>
          ))}
        </div>

        {/* Results */}
        <div className="search-results">
          <h2 className="section-title">
            {query ? `Results for "${query}"` : selectedGenre ? genres.find(g => g.id === selectedGenre)?.name : 'Popular Movies'}
          </h2>
          {loading ? (
            <div className="movie-grid">
              {Array(12).fill(0).map((_, i) => <div key={i} className="skeleton" style={{ aspectRatio: '2/3' }} />)}
            </div>
          ) : (
            <div className="movie-grid">
              {results.map(m => <MovieCard key={m.id} movie={m} />)}
              {results.length === 0 && <p style={{ color: 'var(--text-muted)', gridColumn: '1/-1' }}>No results found</p>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
