import { useState, useEffect } from 'react';
import { getRecommendations, getTrending, getMoodOptions } from '../services/api';
import MovieCard from '../components/MovieCard';
import './Home.css';

export default function Home({ user }) {
  const [mood, setMood] = useState(null);
  const [moods, setMoods] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(true);

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
    try {
      const res = await getRecommendations(newMood, 12);
      setRecommendations(res.data.recommendations || []);
    } catch (e) {
      console.error(e);
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

        {/* Mood Selector */}
        <div className="mood-chips animate-fade-in">
          {moods.map((m) => (
            <button key={m.id} className={`mood-chip ${mood === m.id ? 'active' : ''}`}
                    onClick={() => handleMoodChange(m.id)}>
              {m.label}
            </button>
          ))}
        </div>

        {/* Recommendations */}
        <section className="home-section">
          <h2 className="section-title">
            {mood ? `${mood.charAt(0).toUpperCase() + mood.slice(1)} Picks` : 'Recommended for You'}
          </h2>
          {loading ? (
            <div className="movie-carousel">
              {Array(6).fill(0).map((_, i) => <div key={i} className="skeleton" style={{ minWidth: 155, aspectRatio: '2/3' }} />)}
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
