import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOnboardingMovies, saveOnboardingPrefs } from '../services/api';
import './Onboarding.css';

const GENRES = [
  { id: 'action', title: 'Action', img: 'https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg' }, // Mad Max
  { id: 'scifi', title: 'Sci-Fi', img: 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg' }, // The Matrix
  { id: 'romance', title: 'Romance', img: 'https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg' }, // Titanic
  { id: 'horror', title: 'Horror', img: 'https://image.tmdb.org/t/p/w500/wVYREutTvI2tmxr6ujrHT704wGF.jpg' }, // The Conjuring
  { id: 'drama', title: 'Drama', img: 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg' }, // The Godfather
  { id: 'animation', title: 'Animation', img: 'https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg' }, // Spider-Man
  { id: 'comedy', title: 'Comedy', img: 'https://image.tmdb.org/t/p/w500/A0uS9rHR56FeBtpjVki16M5xxSW.jpg' }, // The Hangover
  { id: 'thriller', title: 'Thriller', img: 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg' }, // Fight Club
];

const ACTORS = [
  { id: 'leonardo_dicaprio', name: 'Leonardo DiCaprio', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDf_4fOIVojzAfyElmyWy4kMxkp5cLb1MRAp_e2mPZQX3-aCiWrmXco2-T-kce2kcpHY43p45z75xBxCc2gakmELnRgtCQop3FYODQHjMUeO8E0mGYY3Urgd8N-BHgPLsGB8G2nm15mqcYGhN_pYU-wHPRTK5k8AeeefwyDJZENvWZvgud_YXwjqwWAkdSFDf6mENqdhU3sUsMykGlYCa3hFCh5FK5tKLrheMQPUyvqnNPSduS8X5RHwwQjiOyHfgBr6_DyDcuTgQ' },
  { id: 'zendaya', name: 'Zendaya', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDSdB8a4qj0EjHHoZ61gfKq-IbS4aKzdAq92xH7Q2zMBqzKgU-grdg_Up1voFZFCzrf_wMnC8p1bv5XsHuJZFKnAnMtbkjKCDfaraw7DsKoIBAhLwLBkdNUXpGnaTvL62WercG2GoQpqNBwyYS5TpzITo1-IZaEINc2gwLsg3s6BgFlfFrWqksqf9j8Qit-VaCubQbeH0tfZ7xuyJWTD_2vAAVOHAcHA7KItC8oHlD6ZIDR1ftmLuOEtvh2P5wgqj3x1Lss4OhY5w' },
  { id: 'denzel_washington', name: 'Denzel Washington', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDAMY7pRt2HeFNVtUIIyHeZUjWZwqwgJtR97G9NpZOx5T1ygO0VAZYN8miXOj4jUZTQNlxMAZ9RUMrjqT-dHHd9q_Vd76dmWSUcZyXVRJoAk9uvEA3EModmRoRqOJ4Bg9akxB6Dct8ba9m_x3DY3L8L80AgB9CwbaK5kOxBQoQMLsT5U_xA9Qmvrtln3CMjN4zORdiuw0wFALkNqZyOKyX1eACsbdSJwuu0H-ImREdOGSN1ManLmz0hfVPZhJFVPbqCiThAApE_fg' },
  { id: 'scarlett_johansson', name: 'Scarlett Johansson', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCABWYS30C-JRt92ByAS7r88xCsusG0OsN4fK1eHTzD-w9I_uuGILnjDAOmk80ZpnJtvk0dDpd5Lcn68IsK_6-0clS5WZd600ffz2aQkjlxKrANDEPhOd5J9afWHkzU7xNATkfej3ro_1WlZWPRaGdoFncERiNYqcv0YQTqt7Iy7mY6s5D13ds2zUN2Ntexj929Pf3RNmPrkapj2rCmLZy1eTnRryUQJUa13CAeXUvdP0DalYT4MHr30MadKw0o7bDyvO5N8VPAoA' },
  { id: 'cillian_murphy', name: 'Cillian Murphy', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDaIetyJvumLD23XpjFu3hhX6o3QYF13Ceh_cVypkLGaaCiDjHFVl4jiQNqPQLzir36fZ0KdteJt0ppkcWbpd_e0v4MlJxMdpRcxKcMp6M9yyN50YpRb7elykImDEQXkM9eDmSEOZszp8KGNK-DnuJrPoymSEGHIg28RGVF0CKGSJF5baZL4rZKct-U-LlzlQ3a75v7Sttd6t-Xy1v5kZ-xzD4yfWbU8JjaORfaiM8paj0SM2NMpKKU-rgcV_jJffz51HMLnaSbLQ' },
  { id: 'viola_davis', name: 'Viola Davis', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDrqXZYaeFGGx9Eu8YtejCadWySk2jr_csEO1QCWr6de7WXWkUzTA071f00yxHKNSDPxEvfO7OoR_jRdDo3s3qHTXipDFKRalmz_ipQOS-5uCUQhjzm3KGnS4GhLpjQd9P0ZubrlNBmK58lqQs2IAsvkiFGRpgcV5WLdFw5iY-YRzpfL5UGGqsZ5a6lObtK4aPP_yT6-9Q1k3NDqfgDWEq6BB6EZedWPMo82iFZzBQdtCxtrl_y3LshVGShpbDXGN3ghxaX7ma2kg' },
];

export default function Onboarding({ user, setUser }) {
  const [step, setStep] = useState(1);
  const [genres, setGenres] = useState([]);
  const [actors, setActors] = useState([]);
  const [hoveredStars, setHoveredStars] = useState({});

  const [movies, setMovies] = useState([]);
  const [prefs, setPrefs] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getOnboardingMovies()
      .then((res) => setMovies(res.data.movies || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const toggleGenre = (id) => {
    setGenres(prev => prev.includes(id) ? prev.filter(g => g !== id) : [...prev, id]);
  };

  const toggleActor = (id) => {
    setActors(prev => prev.includes(id) ? prev.filter(a => a !== id) : [...prev, id]);
  };

  const setMovieRating = (movieId, rating) => {
    setPrefs(prev => ({ ...prev, [movieId]: rating }));
  };

  const handleSubmit = async () => {
    setSaving(true);
    try {
      const preferences = Object.entries(prefs).map(([movie_id, label]) => ({
        movie_id: parseInt(movie_id),
        label: label >= 4 ? 'liked' : 'disliked', // Transform star rating into liked/disliked
      }));
      await saveOnboardingPrefs(preferences, genres, actors);
      setUser({ ...user, onboarded: true });
      navigate('/home');
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  // Rendering Steps
  const renderStepOne = () => (
    <div className="onboarding-main">
      <div className="onboarding-headline">
        <h1>Cinematic DNA</h1>
        <p>Select the frequencies that resonate with your digital soul. Your journey begins with the genres that define your reality.</p>
      </div>
      <div className="genre-grid">
        {GENRES.map((g) => (
          <div
            key={g.id}
            className={`genre-card ${genres.includes(g.id) ? 'selected' : ''}`}
            onClick={() => toggleGenre(g.id)}
          >
            <img src={g.img} alt={g.title} className="genre-image" />
            <div className="genre-gradient"></div>
            <div className="genre-content">
              <span className="genre-label-sm">{genres.includes(g.id) ? 'Selected' : 'Explore'}</span>
              <h3 className="genre-title">{g.title}</h3>
            </div>
            {genres.includes(g.id) && (
              <div className="check-badge">
                <span className="material-symbols-outlined" style={{ fontSize: '14px', fontVariationSettings: "'FILL' 1" }}>check</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderStepTwo = () => (
    <div className="onboarding-main centered">
      <div className="onboarding-headline">
        <h1>Favorite Stars</h1>
        <p>Select the performers who define your cinematic taste. We'll tailor your feed to their filmography.</p>
      </div>
      <div className="star-grid">
        {ACTORS.map((a) => (
          <div
            key={a.id}
            className={`star-item ${actors.includes(a.id) ? 'selected' : ''}`}
            onClick={() => toggleActor(a.id)}
          >
            <div className="star-avatar-container">
              <div className="star-avatar">
                <img src={a.img} alt={a.name} className="star-img" />
              </div>
              {actors.includes(a.id) && (
                <div className="check-badge" style={{ bottom: '-4px', right: '4px' }}>
                  <span className="material-symbols-outlined" style={{ fontSize: '14px', fontVariationSettings: "'FILL' 1" }}>check</span>
                </div>
              )}
            </div>
            <span className="star-name">{a.name}</span>
          </div>
        ))}
      </div>
      <p style={{ marginTop: '4rem', fontSize: '0.625rem', letterSpacing: '0.2em', textTransform: 'uppercase', color: 'rgba(228,227,253,0.6)', fontWeight: 600 }}>
        Can't find your star? You can add more later.
      </p>
    </div>
  );

  const renderStepThree = () => (
    <div className="onboarding-main">
      <div className="onboarding-headline">
        <h1>Rate Recent Watches</h1>
        <p>Help movAI understand your taste. Rate these blockbusters to refine your cinematic projection.</p>
      </div>
      {loading ? (
        <div className="movie-grid">
          {Array(8).fill(0).map((_, i) => (
            <div key={i} className="skeleton" style={{ aspectRatio: '2/3', borderRadius: '1rem' }}></div>
          ))}
        </div>
      ) : (
        <div className="movie-grid">
          {movies.slice(0, 8).map((m) => {
            const rating = prefs[m.id] || 0;
            return (
              <div key={m.id} className={`movie-item ${rating > 0 ? 'selected' : ''}`}>
                <div className="movie-poster-container">
                  <img src={m.poster_path} alt={m.title} className="movie-poster-img" />
                  <div className="movie-poster-gradient"></div>
                  <div className="movie-poster-title">{m.title}</div>
                </div>
                <div className="rating-stars" onMouseLeave={() => setHoveredStars(prev => ({ ...prev, [m.id]: 0 }))}>
                  {[1, 2, 3, 4, 5].map((star) => {
                    const isHovered = (hoveredStars[m.id] || 0) >= star;
                    const isActive = star <= rating;
                    return (
                      <span
                        key={star}
                        className={`material-symbols-outlined rating-star ${isActive || isHovered ? 'active' : ''}`}
                        style={{ fontVariationSettings: isActive || isHovered ? "'FILL' 1" : "'FILL' 0" }}
                        onClick={() => setMovieRating(m.id, star)}
                        onMouseEnter={() => setHoveredStars(prev => ({ ...prev, [m.id]: star }))}
                      >
                        star
                      </span>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  return (
    <div className="onboarding-page">
      <div className="ambient-glow-1"></div>
      <div className="ambient-glow-2"></div>

      {/* Top Nav */}
      <header className="onboarding-top-nav">
        <div className="brand-text">movAI</div>
        <div className="step-indicator">
          <span className="step-text">Step {step} of 3</span>
          <div className="step-bar-container">
            <div className="step-bar-fill" style={{ width: `${(step / 3) * 100}%` }}></div>
          </div>
        </div>
        <div style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-primary)' }}>account_circle</span>
        </div>
      </header>

      {/* Main Content */}
      {step === 1 && renderStepOne()}
      {step === 2 && renderStepTwo()}
      {step === 3 && renderStepThree()}

      {/* Bottom Nav */}
      <footer className="onboarding-bottom-nav">
        <button
          className="nav-btn nav-btn-back"
          onClick={() => step > 1 ? setStep(step - 1) : null}
          disabled={step === 1}
          style={{ visibility: step === 1 ? 'hidden' : 'visible' }}
        >
          <span className="material-symbols-outlined">arrow_back</span>
          <span className="nav-text">Back</span>
        </button>

        {step < 3 ? (
          <button className="nav-btn nav-btn-next" onClick={() => setStep(step + 1)}>
            <span className="nav-text">Continue</span>
            <span className="material-symbols-outlined">arrow_forward</span>
          </button>
        ) : (
          <button className="nav-btn nav-btn-next" onClick={handleSubmit} disabled={saving}>
            <span className="nav-text" style={{ fontSize: '0.875rem', letterSpacing: '0.05em' }}>
              {saving ? 'Initializing...' : 'Finish & Start Exploring'}
            </span>
            {!saving && <span className="material-symbols-outlined">arrow_forward</span>}
          </button>
        )}
      </footer>
    </div>
  );
}
