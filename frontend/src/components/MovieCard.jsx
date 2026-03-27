import { useNavigate } from 'react-router-dom';

export default function MovieCard({ movie, showMatch }) {
  const navigate = useNavigate();

  return (
    <div className="movie-card" onClick={() => navigate(`/movie/${movie.id}`)}>
      {movie.poster_path ? (
        <img src={movie.poster_path} alt={movie.title} loading="lazy" />
      ) : (
        <div style={{ width: '100%', height: '100%', background: 'var(--bg-card)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem', padding: '1rem', textAlign: 'center' }}>
          {movie.title}
        </div>
      )}
      {movie.vote_average > 0 && (
        <div className="movie-card-rating">★ {movie.vote_average?.toFixed(1)}</div>
      )}
      {showMatch && movie.match_pct && (
        <div className="movie-card-match">{movie.match_pct}%</div>
      )}
      <div className="movie-card-overlay">
        <div className="movie-card-title">{movie.title}</div>
        <div className="movie-card-year">{movie.release_date?.slice(0, 4)}</div>
      </div>
    </div>
  );
}
