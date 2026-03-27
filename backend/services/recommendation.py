import numpy as np
import pandas as pd
import os
from collections import defaultdict
from services.tmdb_service import tmdb_service
from services.mood_analyzer import mood_analyzer
from services.feature_engineering import vectorize_movie, compute_cosine_similarity, TMDB_GENRES
from services.rl_recommender import rl_agent


class RecommendationEngine:
    """Hybrid recommendation engine combining content-based, collaborative, and RL."""

    def __init__(self):
        self.user_item_matrix = None
        self.movie_features = {}
        self.user_profiles = {}
        self.genre_vectors = {}
        self.movielens_loaded = False

    def load_movielens(self, data_path):
        """Load MovieLens dataset for offline training."""
        ratings_path = os.path.join(data_path, 'ratings.csv')
        movies_path = os.path.join(data_path, 'movies.csv')

        if not os.path.exists(ratings_path) or not os.path.exists(movies_path):
            print(f'MovieLens data not found at {data_path}')
            return False

        try:
            self.ml_ratings = pd.read_csv(ratings_path)
            self.ml_movies = pd.read_csv(movies_path)

            # Build genre vectors from MovieLens
            all_genres = set()
            for genres in self.ml_movies['genres'].str.split('|'):
                if isinstance(genres, list):
                    all_genres.update(genres)
            all_genres.discard('(no genres listed)')
            self.all_genres = sorted(all_genres)

            for _, row in self.ml_movies.iterrows():
                genres = row['genres'].split('|') if isinstance(row['genres'], str) else []
                vec = np.zeros(len(self.all_genres))
                for g in genres:
                    if g in self.all_genres:
                        vec[self.all_genres.index(g)] = 1.0
                self.genre_vectors[row['movieId']] = vec

            # Precompute user-item matrix for collaborative filtering
            self.user_item_matrix = self.ml_ratings.pivot_table(
                index='userId', columns='movieId', values='rating'
            ).fillna(0)

            self.movielens_loaded = True
            print(f'Loaded MovieLens: {len(self.ml_ratings)} ratings, {len(self.ml_movies)} movies')
            return True
        except Exception as e:
            print(f'Error loading MovieLens: {e}')
            return False

    def build_user_profile(self, user_id, ratings, onboarding_prefs=None):
        """Build user feature vector from ratings and onboarding data."""
        # Simple weighted logic mimicking aggregate_user_profile to prevent massive TMDb lookups
        # Converts genres dynamically
        genre_vec = np.zeros(len(TMDB_GENRES), dtype=np.float32)
        total_weight = 0.0

        if onboarding_prefs:
            for pref in onboarding_prefs:
                movie = tmdb_service.get_movie(pref['movie_id'])
                if movie and 'genre_ids' in movie:
                    weight = 2.0 if pref['label'] == 'liked' else -1.0
                    total_weight += abs(weight)
                    for g in movie['genre_ids']:
                        if g in TMDB_GENRES:
                            genre_vec[TMDB_GENRES.index(g)] += weight

        for rating in ratings:
            movie = tmdb_service.get_movie(rating['movie_id'])
            if movie and 'genre_ids' in movie:
                weight = (rating['rating'] - 3.0) / 2.0  # Normalize to [-1, 1]
                total_weight += abs(weight)
                for g in movie['genre_ids']:
                    if g in TMDB_GENRES:
                        genre_vec[TMDB_GENRES.index(g)] += weight

        if total_weight > 0:
            genre_vec = genre_vec / total_weight
            
        # Feature profile is genre vector + default neutral pop/vote
        profile_vec = np.append(genre_vec, [0.5, 0.5])
        self.user_profiles[user_id] = profile_vec
        return profile_vec

    def content_based_score(self, user_id, movie):
        """Score a movie based on actual cosine similarity to user feature vector."""
        profile_vec = self.user_profiles.get(user_id)
        if profile_vec is None:
            return 0.5
            
        movie_vec = vectorize_movie(movie)
        return max(0.0, compute_cosine_similarity(profile_vec, movie_vec))

    def collaborative_score(self, user_id, movie_id):
        """Score based on collaborative filtering using MovieLens data."""
        if not self.movielens_loaded:
            return 0.5
        # Simplified: return average rating for the movie from MovieLens
        if movie_id in self.user_item_matrix.columns:
            ratings = self.user_item_matrix[movie_id]
            rated = ratings[ratings > 0]
            if len(rated) > 0:
                return rated.mean() / 5.0
        return 0.5

    def rl_score(self, user_id, movie_id):
        """Delegate RL Q-value fetch."""
        return rl_agent.get_q_value(user_id, movie_id)

    def update_rl(self, user_id, movie_id, reward):
        """Proxy method to update the overarching Reinforcement Learning agent."""
        rl_agent.update_q_value(user_id, movie_id, reward)

    def recommend(self, user_id, mood=None, n=20, exclude_ids=None):
        """Generate hybrid recommendations for a user."""
        if exclude_ids is None:
            exclude_ids = set()

        # Get candidate movies from TMDb
        candidates = []

        if mood:
            genre_ids = mood_analyzer.get_genre_ids_for_mood(mood)
            for gid in genre_ids[:2]:
                candidates.extend(tmdb_service.get_movies_by_genre(gid))
        else:
            candidates.extend(tmdb_service.get_popular())
            candidates.extend(tmdb_service.get_trending())

        # Deduplicate and filter
        seen = set()
        unique_candidates = []
        for m in candidates:
            if m['id'] not in seen and m['id'] not in exclude_ids:
                seen.add(m['id'])
                unique_candidates.append(m)

        # Score each candidate
        scored = []
        for movie in unique_candidates:
            content_score = self.content_based_score(user_id, movie)
            collab_score = self.collaborative_score(user_id, movie.get('id', 0))
            rl_s = self.rl_score(user_id, movie.get('id', 0))

            # Hybrid weighted score (Ranking Layer 7.4)
            hybrid_score = (0.40 * content_score + 0.20 * collab_score + 0.40 * rl_s)

            # Epsilon-greedy exploration via RL Agent
            if rl_agent.should_explore():
                hybrid_score = np.random.uniform(0.1, 1.0)

            movie['score'] = round(hybrid_score, 3)
            movie['match_pct'] = round(hybrid_score * 100)
            scored.append(movie)

        # Sort by score and return top-N
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:n]


recommendation_engine = RecommendationEngine()
