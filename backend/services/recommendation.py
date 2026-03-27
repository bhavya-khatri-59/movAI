import numpy as np
import pandas as pd
import os
from collections import defaultdict
from models import User
from services.tmdb_service import tmdb_service
from services.mood_analyzer import mood_analyzer, GENRE_ID_MAP
from services.feature_engineering import vectorize_movie, compute_cosine_similarity, TMDB_GENRES
from services.rl_recommender import rl_agent

class RecommendationEngine:
    def __init__(self):
        self.user_item_matrix = None
        self.movie_features = {}
        self.user_profiles = {}
        self.genre_vectors = {}
        self.movielens_loaded = False

    def load_movielens(self, data_path):
        # ... [Unchanged logic] ...
        ratings_path = os.path.join(data_path, 'ratings.csv')
        movies_path = os.path.join(data_path, 'movies.csv')
        if not os.path.exists(ratings_path) or not os.path.exists(movies_path):
            return False
        try:
            self.ml_ratings = pd.read_csv(ratings_path)
            self.ml_movies = pd.read_csv(movies_path)
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
            self.user_item_matrix = self.ml_ratings.pivot_table(
                index='userId', columns='movieId', values='rating'
            ).fillna(0)
            self.movielens_loaded = True
            return True
        except Exception as e:
            return False

    def build_user_profile(self, user_id, ratings, onboarding_prefs=None):
        # ... [Unchanged logic] ...
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
                weight = (rating['rating'] - 3.0) / 2.0
                total_weight += abs(weight)
                for g in movie['genre_ids']:
                    if g in TMDB_GENRES:
                        genre_vec[TMDB_GENRES.index(g)] += weight
        if total_weight > 0:
            genre_vec = genre_vec / total_weight
        profile_vec = np.append(genre_vec, [0.5, 0.5])
        self.user_profiles[user_id] = profile_vec
        return profile_vec

    def content_based_score(self, user_id, movie):
        profile_vec = self.user_profiles.get(user_id)
        if profile_vec is None: return 0.5
        movie_vec = vectorize_movie(movie)
        return max(0.0, compute_cosine_similarity(profile_vec, movie_vec))

    def collaborative_score(self, user_id, movie_id):
        if not self.movielens_loaded: return 0.5
        if movie_id in self.user_item_matrix.columns:
            ratings = self.user_item_matrix[movie_id]
            rated = ratings[ratings > 0]
            if len(rated) > 0: return rated.mean() / 5.0
        return 0.5

    def rl_score(self, user_id, movie):
        genre_ids = movie.get('genre_ids', [])
        if not genre_ids:
            return 0.5
        q_values = []
        for gid in genre_ids:
            genre_name = GENRE_ID_MAP.get(gid)
            if genre_name:
                q_values.append(rl_agent.get_q_value(user_id, genre_name))
        if not q_values:
            return 0.5
        return sum(q_values) / len(q_values) 

    def recommend(self, user_id, mood=None, n=20, exclude_ids=None):
        if exclude_ids is None: exclude_ids = set()

        user = User.query.get(user_id)
        prefs = user.preferences if user and user.preferences else {}
        fav_actors = [a.lower() for a in prefs.get('favorite_actors', [])]
        fav_directors = [d.lower() for d in prefs.get('favorite_directors', [])]

        candidates = []
        if mood:
            genre_ids = mood_analyzer.get_genre_ids_for_mood(mood)
            for gid in genre_ids[:2]:
                candidates.extend(tmdb_service.get_movies_by_genre(gid))
        else:
            candidates.extend(tmdb_service.get_popular())
            candidates.extend(tmdb_service.get_trending())

        seen = set()
        unique_candidates = []
        for m in candidates:
            if m['id'] not in seen and m['id'] not in exclude_ids:
                seen.add(m['id'])
                unique_candidates.append(m)

        # [NEW] Slice down to Top 5 so we don't overwhelm the TMDB API
        unique_candidates = unique_candidates[:5]

        scored = []
        for base_movie in unique_candidates:
            # [NEW] Fetch the FULL profile to get Cast/Crew
            full_movie = tmdb_service.get_movie(base_movie['id'])
            
            # Fallback if API fails
            movie_to_score = full_movie if full_movie else base_movie 

            content_score = self.content_based_score(user_id, movie_to_score)
            collab_score = self.collaborative_score(user_id, movie_to_score.get('id', 0))
            rl_s = self.rl_score(user_id, movie_to_score) 

            hybrid_score = (0.40 * content_score + 0.20 * collab_score + 0.40 * rl_s)

            # --- METADATA BOOSTING ---
            metadata_boost = 0.0
            director = movie_to_score.get('director', {})
            cast = movie_to_score.get('cast', [])
            
            if director and director.get('name', '').lower() in fav_directors:
                metadata_boost += 5.0
                
            for actor in cast:
                if actor.get('name', '').lower() in fav_actors:
                    metadata_boost += 0.5
                    
            hybrid_score += metadata_boost

            if rl_agent.should_explore():
                hybrid_score = np.random.uniform(0.1, 1.0) + metadata_boost

            movie_to_score['score'] = round(hybrid_score, 3)
            movie_to_score['match_pct'] = min(100, round(hybrid_score * 100)) 
            scored.append(movie_to_score)

        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:n]

recommendation_engine = RecommendationEngine()