import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('movai_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export const signup = (data) => api.post('/auth/signup', data);
export const login = (data) => api.post('/auth/login', data);
export const getMe = () => api.get('/auth/me');
export const updateProfile = (data) => api.put('/auth/me', data);

// Movies
export const searchMovies = (q, page = 1) => api.get('/movies/search', { params: { q, page } });
export const getTrending = (window = 'week') => api.get('/movies/trending', { params: { window } });
export const getPopular = (page = 1) => api.get('/movies/popular', { params: { page } });
export const getNowPlaying = () => api.get('/movies/now-playing');
export const getMovieDetail = (id) => api.get(`/movies/${id}`);
export const getGenres = () => api.get('/movies/genres');
export const getByGenre = (genreId, page = 1) => api.get(`/movies/genre/${genreId}`, { params: { page } });

// Interactions
export const rateMovie = (movie_id, rating) => api.post('/interactions/rate', { movie_id, rating });
export const likeMovie = (movie_id) => api.post('/interactions/like', { movie_id });
export const toggleWatchlist = (movie_id) => api.post('/interactions/watchlist', { movie_id });
export const markWatched = (movie_id) => api.post('/interactions/watched', { movie_id });
export const createReview = (movie_id, text, rating) => api.post('/interactions/review', { movie_id, text, rating });
export const getReviews = (movie_id) => api.get(`/interactions/reviews/${movie_id}`);
export const getMovieStatus = (movie_id) => api.get(`/interactions/status/${movie_id}`);
export const getWatchlist = () => api.get('/interactions/watchlist');
export const getHistory = () => api.get('/interactions/history');

// Social
export const followUser = (user_id) => api.post('/social/follow', { user_id });
export const getFollowers = (user_id) => api.get(`/social/followers/${user_id}`);
export const getFollowing = (user_id) => api.get(`/social/following/${user_id}`);
export const getFeed = (page = 1) => api.get('/social/feed', { params: { page } });
export const searchUsers = (q) => api.get('/social/users/search', { params: { q } });
export const getUserProfile = (user_id) => api.get(`/social/user/${user_id}`);

// Onboarding
export const getOnboardingMovies = () => api.get('/onboarding/movies');
export const saveOnboardingPrefs = (preferences, genres = [], actors = []) => api.post('/onboarding/preferences', { preferences, genres, actors });

// Mood
export const getMoodOptions = () => api.get('/mood/options');
export const getMoodMovies = (mood) => api.get('/mood/movies', { params: { mood } });

// Recommendations
export const getRecommendations = (mood, n = 20) => api.get('/recommendations/', { params: { mood, n } });
export const getSimilar = (movie_id) => api.get(`/recommendations/similar/${movie_id}`);

export default api;
