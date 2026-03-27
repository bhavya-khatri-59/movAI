import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getMovieDetail, getMovieStatus, rateMovie, likeMovie, toggleWatchlist, markWatched, getReviews, createReview } from '../services/api';
import { ThumbsUp, BookmarkPlus, BookmarkCheck, Eye, EyeOff } from 'lucide-react';
import StarRating from '../components/StarRating';
import MovieCard from '../components/MovieCard';
import './MovieDetails.css';

export default function MovieDetails() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [status, setStatus] = useState({});
  const [reviews, setReviews] = useState([]);
  const [reviewText, setReviewText] = useState('');
  const [reviewRating, setReviewRating] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getMovieDetail(id).then(r => setMovie(r.data)),
      getMovieStatus(id).then(r => setStatus(r.data)).catch(() => {}),
      getReviews(id).then(r => setReviews(r.data.reviews || [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, [id]);

  const handleRate = async (rating) => {
    await rateMovie(parseInt(id), rating);
    setStatus(s => ({ ...s, rating }));
  };

  const handleLike = async () => {
    const res = await likeMovie(parseInt(id));
    setStatus(s => ({ ...s, liked: res.data.liked }));
  };

  const handleWatchlist = async () => {
    const res = await toggleWatchlist(parseInt(id));
    setStatus(s => ({ ...s, watchlist: res.data.watchlist }));
  };

  const handleWatched = async () => {
    await markWatched(parseInt(id));
    setStatus(s => ({ ...s, watched: true }));
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!reviewText.trim()) return;
    await createReview(parseInt(id), reviewText, reviewRating || null);
    setReviewText('');
    setReviewRating(0);
    const res = await getReviews(id);
    setReviews(res.data.reviews || []);
  };

  if (loading) {
    return (
      <div className="page-content">
        <div className="container">
          <div className="skeleton" style={{ height: 400, borderRadius: 'var(--radius-lg)', marginBottom: '2rem' }} />
        </div>
      </div>
    );
  }
  if (!movie) return <div className="page-content container"><p>Movie not found</p></div>;

  return (
    <div className="page-content movie-details-page">
      {/* Backdrop */}
      <div className="movie-backdrop">
        {movie.backdrop_path && <img src={movie.backdrop_path} alt="" />}
        <div className="backdrop-overlay" />
      </div>

      <div className="container movie-details-content">
        <div className="movie-main animate-fade-in-up">
          {/* Poster */}
          <div className="movie-poster-large">
            {movie.poster_path ? (
              <img src={movie.poster_path} alt={movie.title} />
            ) : (
              <div style={{ width: '100%', height: 360, background: 'var(--bg-card)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No Poster</div>
            )}
          </div>

          {/* Info */}
          <div className="movie-info">
            <h1 className="movie-title-large">{movie.title}</h1>
            {movie.tagline && <p className="movie-tagline">"{movie.tagline}"</p>}

            <div className="movie-meta">
              <span>{movie.release_date?.slice(0, 4)}</span>
              {movie.runtime > 0 && <span>{Math.floor(movie.runtime / 60)}h {movie.runtime % 60}min</span>}
              <span>★ {movie.vote_average?.toFixed(1)}</span>
            </div>

            <div className="movie-genres">
              {movie.genres?.map((g, i) => <span key={i} className="badge badge-accent">{g}</span>)}
            </div>

            {/* User Actions */}
            <div className="movie-actions">
              <div className="rating-section">
                <span className="action-label">Your Rating</span>
                <StarRating rating={status.rating || 0} onRate={handleRate} size="1.5rem" />
              </div>
              <div className="action-buttons">
                <button className={`btn ${status.liked ? 'btn-primary' : 'btn-outline'}`} onClick={handleLike} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <ThumbsUp size={16} fill={status.liked ? 'currentColor' : 'none'} /> {status.liked ? 'Liked' : 'Like'}
                </button>
                <button className={`btn ${status.watchlist ? 'btn-primary' : 'btn-outline'}`} onClick={handleWatchlist} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {status.watchlist ? <><BookmarkCheck size={16} fill="currentColor" /> In Watchlist</> : <><BookmarkPlus size={16} /> Watchlist</>}
                </button>
                <button className={`btn ${status.watched ? 'btn-primary' : 'btn-outline'}`} onClick={handleWatched} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {status.watched ? <><Eye size={16} /> Watched</> : <><EyeOff size={16} /> Mark Watched</>}
                </button>
              </div>
            </div>

            {/* Overview */}
            <div className="movie-overview">
              <h3>Overview</h3>
              <p>{movie.overview}</p>
            </div>

            {/* Director */}
            {movie.director && (
              <div className="movie-director">
                <span className="action-label">Director</span>
                <span>{movie.director.name}</span>
              </div>
            )}
          </div>
        </div>

        {/* Cast */}
        {movie.cast?.length > 0 && (
          <section className="movie-section">
            <h2 className="section-title">Cast</h2>
            <div className="cast-grid">
              {movie.cast.map((c, i) => (
                <div key={i} className="cast-card">
                  <div className="cast-avatar">
                    {c.profile_path ? <img src={c.profile_path} alt={c.name} /> : <span>{c.name?.charAt(0)}</span>}
                  </div>
                  <div className="cast-name">{c.name}</div>
                  <div className="cast-char">{c.character}</div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Write Review */}
        <section className="movie-section">
          <h2 className="section-title">Write a Review</h2>
          <form className="review-form glass-card" onSubmit={handleSubmitReview}>
            <StarRating rating={reviewRating} onRate={setReviewRating} size="1.3rem" />
            <textarea className="input-field" placeholder="Share your thoughts about this movie..." value={reviewText}
                      onChange={(e) => setReviewText(e.target.value)} rows={4} />
            <button type="submit" className="btn btn-primary">Post Review</button>
          </form>
        </section>

        {/* Reviews */}
        {reviews.length > 0 && (
          <section className="movie-section">
            <h2 className="section-title">Reviews ({reviews.length})</h2>
            <div className="reviews-list">
              {reviews.map((r) => (
                <div key={r.id} className="review-card glass-card">
                  <div className="review-header">
                    <div className="review-avatar">{r.user_name?.charAt(0)}</div>
                    <div>
                      <div className="review-author">{r.user_name}</div>
                      {r.rating && <StarRating rating={r.rating} interactive={false} size="0.9rem" />}
                    </div>
                    <span className="review-date">{new Date(r.created_at).toLocaleDateString()}</span>
                  </div>
                  <p className="review-text">{r.text}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Similar Movies */}
        {movie.similar?.length > 0 && (
          <section className="movie-section">
            <h2 className="section-title">Similar Movies</h2>
            <div className="movie-carousel">
              {movie.similar.map((m) => <MovieCard key={m.id} movie={m} />)}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
