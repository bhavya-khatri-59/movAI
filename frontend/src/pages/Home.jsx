import { useState, useEffect } from 'react';
import { getRecommendations, getTrending, getMoodOptions, getMagicRecommendations } from '../services/api';
import MovieCard from '../components/MovieCard';
import './Home.css';

export default function Home({ user }) {
  const [mood, setMood] = useState(null);
  const [moods, setMoods] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(true);

  const [recLoading, setRecLoading] = useState(false);
  
  // Magic Search states
  const [magicQuery, setMagicQuery] = useState('');
  const [magicSearchTerm, setMagicSearchTerm] = useState('');
  const [magicResults, setMagicResults] = useState(null);
  const [magicLoading, setMagicLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      getMoodOptions().then(r => setMoods(r.data.moods || [])),
      getRecommendations(null, 12).then(r => setRecommendations(r.data.recommendations || [])).catch(() => {}),
      getTrending().then(r => setTrending(r.data.results || [])),
    ]).finally(() => setLoading(false));
  }, []);

  const handleMoodChange = async (m) => {
    const newMood = mood === m ? null : m;
    setMood(newMood);
    setRecLoading(true);
    try {
      const res = await getRecommendations(newMood, 12);
      setRecommendations(res.data.recommendations || []);
    } catch (e) {
      console.error(e);
    } finally {
      setRecLoading(false);
    }
  };

  const handleMagicSearch = async (e) => {
    e.preventDefault();
    if (!magicQuery.trim()) return;
    
    setMagicLoading(true);
    setMagicResults(null); 
    setMood(null); // Clear mood if they use magic search
    try {
      const res = await getMagicRecommendations(magicQuery);
      setMagicResults(res.data.recommendations || []);
      setMagicSearchTerm(magicQuery);
    } catch (error) {
      console.error("Magic search error:", error);
      setMagicResults([]);
    } finally {
      setMagicLoading(false);
    }
  };

  return (
    <div className="page-content">
      <div className="container">
        {/* Welcome */}
        <div className="home-welcome animate-fade-in-up">
          <h1>Welcome back, <span className="gradient-text">{user.name?.split(' ')[0]}</span></h1>
          <p>What are you in the mood for today?</p>
        </div>

        {/* AI Semantic Search */}
        <div className="ai-search-section animate-fade-in-up">
          <form className="ai-search-form" onSubmit={handleMagicSearch}>
            <svg className="ai-search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input 
              type="text" 
              placeholder="Describe what you want to watch (e.g. A psychological thriller about time travel)"
              value={magicQuery}
              onChange={(e) => setMagicQuery(e.target.value)}
              className="ai-search-input"
            />
            <button type="submit" className="ai-search-btn" disabled={magicLoading}>
              {magicLoading ? (
                <>
                  <svg className="spinner-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
                  Processing
                </>
              ) : 'Discover'}
            </button>
          </form>
        </div>

        {/* Mood Selector */}
        <div className="mood-chips animate-fade-in">
          {moods.map((m) => (
            <button key={m.id} className={`mood-chip ${mood === m.id ? 'active' : ''}`}
                    onClick={() => handleMoodChange(m.id)}>
              {m.label}
            </button>
          ))}
        </div>

        {magicResults && (
          <section className="home-section animate-fade-in-up">
            <h2 className="section-title">
              <span className="gradient-text">Semantic Discovery</span> for "{magicSearchTerm}"
            </h2>
            <div className="movie-carousel">
              {magicResults.map((m) => <MovieCard key={m.id} movie={m} showMatch />)}
              {magicResults.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No exact semantic matches found. Try broadening your query!</p>}
            </div>
          </section>
        )}

        {/* Recommendations */}
        <section className="home-section">
          <h2 className="section-title">
            {mood ? `${mood.charAt(0).toUpperCase() + mood.slice(1)} Picks` : 'Recommended for You'}
          </h2>
          {(loading || recLoading) ? (
            <div className="movie-carousel">
              {Array(6).fill(0).map((_, i) => <div key={i} className="skeleton" style={{ minWidth: 155, aspectRatio: '2/3', borderRadius: '12px' }} />)}
            </div>
          ) : (
            <div className="movie-carousel">
              {recommendations.map((m) => <MovieCard key={m.id} movie={m} showMatch />)}
              {recommendations.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No recommendations yet. Rate some movies first!</p>}
            </div>
          )}
        </section>

        {/* Trending */}
        <section className="home-section">
          <h2 className="section-title">Trending This Week</h2>
          {loading ? (
            <div className="movie-carousel">
              {Array(6).fill(0).map((_, i) => <div key={i} className="skeleton" style={{ minWidth: 155, aspectRatio: '2/3' }} />)}
            </div>
          ) : (
            <div className="movie-carousel">
              {trending.slice(0, 12).map((m) => <MovieCard key={m.id} movie={m} />)}
            </div>
          )}
        </section>

      </div>
    </div>
  );
}
