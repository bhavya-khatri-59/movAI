import numpy as np

import math

# Standard TMDb Genre IDs
TMDB_GENRES = [
    28, 12, 16, 35, 80, 99, 18, 10751, 14, 36, 27, 10402, 9648, 10749, 878, 10770, 53, 10752, 37
]

DECADE_BINS = [1960, 1970, 1980, 1990, 2000, 2010, 2020]

def vectorize_movie(movie: dict) -> np.ndarray:
    """
    Converts a TMDb movie dictionary into a numerical feature vector.
    Features:
    - One-hot encoded genres length 19
    - One-hot encoded decades length 7
    - Scaled popularity [0-1] (Logarithmic)
    - Scaled vote average [0-1]
    """
    movie_genres = movie.get('genre_ids', [])
    # One-hot genre vector
    genre_vector = [1.0 if g in movie_genres else 0.0 for g in TMDB_GENRES]
    
    # One-hot decade vector
    decade_vector = [0.0] * len(DECADE_BINS)
    release_date = movie.get('release_date', '')
    if release_date and len(release_date) >= 4:
        try:
            year = int(release_date[:4])
            bin_idx = 0
            for i, d in enumerate(DECADE_BINS):
                if year >= d:
                    bin_idx = i
            decade_vector[bin_idx] = 1.0
        except ValueError:
            pass
    
    # Scale continuous features (Log1p for Blockbuster bias reduction)
    pop = movie.get('popularity', 0)
    scaled_pop = min(math.log1p(pop) / math.log1p(2000), 1.0)
    
    vote = movie.get('vote_average', 0) / 10.0           
    
    return np.array(genre_vector + decade_vector + [scaled_pop, vote], dtype=np.float32)

def aggregate_user_profile(user_interactions: list, movies_data: dict) -> np.ndarray:
    """
    Builds a user feature vector by calculating the weighted average of
    the feature vectors of movies the user has interacted with.
    
    user_interactions: list of dicts e.g., [{'movie_id': 123, 'weight': 2.0}]
    movies_data: dict mapping movie_id to movie metadata dict
    """
    vectors = []
    weights = []
    
    for interaction in user_interactions:
        m_id = interaction['movie_id']
        if m_id in movies_data:
            vec = vectorize_movie(movies_data[m_id])
            vectors.append(vec)
            weights.append(interaction.get('weight', 1.0))
            
    if not vectors:
        # 19 genres + 7 decades + 2 continuous = 28 dim vector
        return np.zeros(len(TMDB_GENRES) + len(DECADE_BINS) + 2, dtype=np.float32)
        
    vectors = np.array(vectors, dtype=np.float32)
    weights = np.array(weights, dtype=np.float32).reshape(-1, 1)
    
    # Compute weighted average
    total_weight = np.sum(np.abs(weights))
    if total_weight == 0:
        return np.mean(vectors, axis=0)
        
    user_vector = np.sum(vectors * weights, axis=0) / total_weight
    return user_vector

def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Computes cosine similarity between two feature vectors."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
