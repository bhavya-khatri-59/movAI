import numpy as np
import pandas as pd
import os
from collections import defaultdict
from models import db, User
from services.tmdb_service import tmdb_service
from services.mood_analyzer import mood_analyzer, GENRE_ID_MAP
from services.feature_engineering import vectorize_movie, compute_cosine_similarity, TMDB_GENRES, DECADE_BINS
from services.rl_recommender import rl_agent
from services.nlp_service import nlp_service
from config import Config

class RecommendationEngine:
    def __init__(self):
        self.user_item_matrix = None
        self.movie_features = {}
        self.user_profiles = {}
        self.user_genome_profiles = {}
        self.genre_vectors = {}
        self.imdb_ratings = {}
        self.genome_scores = {}
        self.tag_vocab = {}
        self.tmdb_cache = {}  # In-memory cache for TMDb API responses
        self.movielens_loaded = False
        self.advanced_loaded = False

    def load_advanced_datasets(self):
        import os, pickle
        cache_path = os.path.join(Config.DATA_DIR, '.dataset_cache.pkl')
        
        # --- FAST PATH: Load from binary cache (< 2 seconds) ---
        if os.path.exists(cache_path):
            try:
                print("Loading datasets from cache...")
                with open(cache_path, 'rb') as f:
                    cached = pickle.load(f)
                self.imdb_ratings = cached.get('imdb_ratings', {})
                self.genome_scores = cached.get('genome_scores', {})
                self.tag_vocab = cached.get('tag_vocab', {})
                self.advanced_loaded = True
                print(f"Cache loaded: {len(self.imdb_ratings)} IMDb ratings, {len(self.genome_scores)} genome vectors, {len(self.tag_vocab)} tags.")
                return
            except Exception as e:
                print(f"Cache corrupted, rebuilding: {e}")

        # --- SLOW PATH: Parse raw CSVs (first boot only) ---
        import pandas as pd
        from collections import defaultdict
        print("First boot: parsing raw datasets (this only happens once)...")
        
        # 1. Load links
        movie_to_tmdb = {}
        try:
            if os.path.exists(Config.LINKS_PATH):
                links = pd.read_csv(Config.LINKS_PATH, dtype={'movieId': str, 'imdbId': str, 'tmdbId': str})
                for _, row in links.iterrows():
                    if pd.notna(row['tmdbId']) and pd.notna(row['imdbId']):
                        imdb_str = f"tt{str(row['imdbId']).zfill(7)}"
                        movie_to_tmdb[str(row['movieId'])] = (imdb_str, int(float(row['tmdbId'])))
        except Exception as e:
            print(f"Error loading links.csv: {e}")

        # 2. Load IMDb Ratings
        try:
            if os.path.exists(Config.IMDB_RATINGS_PATH) and movie_to_tmdb:
                print("Calculating IMDb Bayesian Averages...")
                df_imdb = pd.read_csv(Config.IMDB_RATINGS_PATH, sep='\t', usecols=['tconst', 'averageRating', 'numVotes'])
                df_imdb['numVotes'] = pd.to_numeric(df_imdb['numVotes'], errors='coerce')
                df_imdb['averageRating'] = pd.to_numeric(df_imdb['averageRating'], errors='coerce')
                df_imdb = df_imdb.dropna(subset=['numVotes', 'averageRating'])
                
                # Strict quality filter: only keep well-known movies (>10,000 votes)
                df_imdb = df_imdb[df_imdb['numVotes'] > 10000]
                
                C = df_imdb['averageRating'].mean()
                m = df_imdb['numVotes'].quantile(0.90)
                
                df_imdb['bayesian_avg'] = (df_imdb['numVotes'] / (df_imdb['numVotes'] + m) * df_imdb['averageRating']) + (m / (df_imdb['numVotes'] + m) * C)
                imdb_temp = dict(zip(df_imdb['tconst'], df_imdb['bayesian_avg']))
                
                for m_id, (imdb_id, tmdb_id) in movie_to_tmdb.items():
                    if imdb_id in imdb_temp:
                        self.imdb_ratings[tmdb_id] = imdb_temp[imdb_id]
        except Exception as e:
            print(f"Error loading IMDb ratings: {e}")

        # 3. Load Genome Scores
        try:
            if os.path.exists(Config.GENOME_SCORES_PATH) and movie_to_tmdb:
                print("Loading Tag Genome. This may take a moment...")
                valid_movie_ids = set(movie_to_tmdb.keys())
                genome_dict = defaultdict(list)
                import numpy as np
                for chunk in pd.read_csv(Config.GENOME_SCORES_PATH, chunksize=5000000, dtype={'movieId': str, 'relevance': np.float32}):
                    chunk = chunk[chunk['movieId'].isin(valid_movie_ids)]
                    grouped = chunk.groupby('movieId')['relevance'].apply(list).to_dict()
                    for m_id, rel_list in grouped.items():
                        genome_dict[m_id].extend(rel_list)
                
                for m_id, scores in genome_dict.items():
                    if len(scores) == 1128:
                        tmdb_id = movie_to_tmdb[m_id][1]
                        self.genome_scores[tmdb_id] = np.array(scores, dtype=np.float32)
        except Exception as e:
            print(f"Error loading Genome Scores: {e}")
        
        # 4. Load Genome Tags
        try:
            tags_path = os.path.join(Config.DATA_DIR, 'ml-latest', 'genome-tags.csv')
            if os.path.exists(tags_path):
                df_tags = pd.read_csv(tags_path)
                for _, row in df_tags.iterrows():
                    tag_idx = int(row['tagId']) - 1
                    self.tag_vocab[str(row['tag']).lower()] = tag_idx
        except Exception as e:
            print(f"Error loading Genome Tags: {e}")

        # --- SAVE CACHE for next boot ---
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'imdb_ratings': self.imdb_ratings, 
                    'genome_scores': self.genome_scores,
                    'tag_vocab': self.tag_vocab
                }, f)
            print(f"Dataset cache saved to {cache_path}")
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
            
        self.advanced_loaded = True

    def load_movielens(self, data_path):
        # ... [Unchanged logic] ...
        ratings_path = os.path.join(data_path, 'ratings.csv')
        movies_path = os.path.join(data_path, 'movies.csv')
        if not os.path.exists(ratings_path) or not os.path.exists(movies_path):
            return False
        try:
            self.ml_ratings = pd.read_csv(ratings_path)
            # Sample to prevent memory overflow on large datasets
            if len(self.ml_ratings) > 2000000:
                print(f"Sampling ratings from {len(self.ml_ratings)} to 2,000,000 for collaborative filter...")
                self.ml_ratings = self.ml_ratings.sample(n=2000000, random_state=42)
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
        import numpy as np
        # ... [Unchanged logic] ...
        genre_vec = np.zeros(len(TMDB_GENRES), dtype=np.float32)
        total_weight = 0.0
        
        genome_vec = np.zeros(1128, dtype=np.float32)
        genome_weight = 0.0
        
        if onboarding_prefs:
            for pref in onboarding_prefs:
                movie = tmdb_service.get_movie(pref['movie_id'])
                if movie and 'genre_ids' in movie:
                    weight = 2.0 if pref['label'] == 'liked' else -1.0
                    total_weight += abs(weight)
                    for g in movie['genre_ids']:
                        if g in TMDB_GENRES:
                            genre_vec[TMDB_GENRES.index(g)] += weight
                            
                    if movie['id'] in self.genome_scores:
                        genome_vec += self.genome_scores[movie['id']] * weight
                        genome_weight += abs(weight)
                        
        for rating in ratings:
            movie = tmdb_service.get_movie(rating['movie_id'])
            if movie and 'genre_ids' in movie:
                weight = (rating['rating'] - 3.0) / 2.0
                total_weight += abs(weight)
                for g in movie['genre_ids']:
                    if g in TMDB_GENRES:
                        genre_vec[TMDB_GENRES.index(g)] += weight
                        
                if rating['movie_id'] in self.genome_scores:
                    genome_vec += self.genome_scores[rating['movie_id']] * weight
                    genome_weight += abs(weight)

        if total_weight > 0:
            genre_vec = genre_vec / total_weight
        decade_vec = np.zeros(len(DECADE_BINS), dtype=np.float32)
        profile_vec = np.concatenate([genre_vec, decade_vec, [0.5, 0.5]])
        self.user_profiles[user_id] = profile_vec
        
        if genome_weight > 0:
            genome_vec = genome_vec / genome_weight
        self.user_genome_profiles[user_id] = genome_vec
        
        return profile_vec

    def content_based_score(self, user_id, movie):
        profile_vec = self.user_profiles.get(user_id)
        if profile_vec is None: return 0.5
        movie_vec = vectorize_movie(movie)
        base_score = max(0.0, compute_cosine_similarity(profile_vec, movie_vec))
        
        # --- Tag Genome Boost ---
        movie_id = movie.get('id')
        user_genome = self.user_genome_profiles.get(user_id)
        if user_genome is not None and np.any(user_genome) and movie_id in self.genome_scores:
            movie_genome = self.genome_scores[movie_id]
            genome_sim = max(0.0, compute_cosine_similarity(user_genome, movie_genome))
            return (base_score * 0.3) + (genome_sim * 0.7)
            
        return base_score

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
        
    # --- [NEW] DYNAMIC METADATA TALLY ---
    def update_user_metadata_tally(self, user_id, movie_id, reward):
        """Maintains a rolling scoreboard of the user's favorite actors and directors."""
        user = User.query.get(user_id)
        if not user: return

        # We need the full cast list for this movie
        movie = tmdb_service.get_movie(movie_id)
        if not movie: return

        # Force a copy so SQLAlchemy detects the JSON change
        prefs = dict(user.preferences) if user.preferences else {}
        actor_tally = prefs.get('actor_tally', {})
        director_tally = prefs.get('director_tally', {})

        # Add reward to the Top 5 billed actors in the movie
        for actor in movie.get('cast', [])[:5]:
            name = actor.get('name')
            if name:
                actor_tally[name] = actor_tally.get(name, 0.0) + reward

        # Add reward to the director
        director = movie.get('director', {})
        if director and director.get('name'):
            d_name = director.get('name')
            director_tally[d_name] = director_tally.get(d_name, 0.0) + reward

        # Sort and extract the absolute Top 10 Actors and Top 3 Directors
        top_actors = sorted(actor_tally.items(), key=lambda x: x[1], reverse=True)[:10]
        top_directors = sorted(director_tally.items(), key=lambda x: x[1], reverse=True)[:3]

        # Save back to preferences
        prefs['actor_tally'] = actor_tally
        prefs['director_tally'] = director_tally
        prefs['favorite_actors'] = [a[0] for a in top_actors]
        prefs['favorite_directors'] = [d[0] for d in top_directors]

        user.preferences = prefs
        db.session.commit()

    def update_rl(self, user_id, movie_id, reward):
        """Proxy method to update the RL agent AND our dynamic metadata tallies."""
        rl_agent.update_q_value(user_id, movie_id, reward)
        # Hook into the existing update cycle to calculate top actors!
        self.update_user_metadata_tally(user_id, movie_id, reward)

    def get_movie_cached(self, movie_id):
        """Fetch movie from TMDb with in-memory caching to eliminate repeat API calls."""
        if movie_id in self.tmdb_cache:
            return self.tmdb_cache[movie_id]
        movie = tmdb_service.get_movie(movie_id)
        if movie:
            self.tmdb_cache[movie_id] = movie
        return movie

    def find_genome_candidates(self, user_id, mood_genre_ids=None, n=15, exclude_ids=None):
        """Discover hidden gem movies by finding the closest genome vectors to the user's profile."""
        if exclude_ids is None: exclude_ids = set()
        user_genome = self.user_genome_profiles.get(user_id)
        if user_genome is None or not np.any(user_genome):
            return []
        
        scored = []
        for tmdb_id, movie_genome in self.genome_scores.items():
            if tmdb_id in exclude_ids:
                continue
            
            # Strict filter: only consider genome candidates that are also in our well-known IMDb pool
            if tmdb_id not in self.imdb_ratings:
                continue
                
            sim = compute_cosine_similarity(user_genome, movie_genome)
            
            # If mood is set, boost movies that have matching genres
            if mood_genre_ids and tmdb_id in self.imdb_ratings:
                sim += 0.05  # Small boost for having IMDb data (means it's a real movie)
            
            scored.append((tmdb_id, sim))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N as minimal dicts with just the tmdb_id
        return [{'id': tid, '_genome_score': score} for tid, score in scored[:n]]

    def find_imdb_quality_candidates(self, n=20, exclude_ids=None):
        """Find highly rated movies from the IMDb dataset that the user hasn't seen."""
        if exclude_ids is None: exclude_ids = set()
        import random
        
        # Get all movies with Bayesian avg > 7.5 (excellent quality)
        quality_pool = [(tid, score) for tid, score in self.imdb_ratings.items() 
                        if score > 7.5 and tid not in exclude_ids]
        
        # Shuffle to add variety, then take top N
        random.shuffle(quality_pool)
        return [{'id': tid, '_imdb_score': score} for tid, score in quality_pool[:n]]

    def recommend(self, user_id, mood=None, n=20, exclude_ids=None):
        if exclude_ids is None: exclude_ids = set()

        user = User.query.get(user_id)
        prefs = user.preferences if user and user.preferences else {}
        fav_actors = [a.lower() for a in prefs.get('favorite_actors', [])]
        fav_directors = [d.lower() for d in prefs.get('favorite_directors', [])]

        # === DIVERSIFIED CANDIDATE GENERATION ===
        candidates = []
        
        mood_genre_ids = mood_analyzer.get_genre_ids_for_mood(mood) if mood else None
        
        # Source 1: TMDb Popular/Trending or Mood-filtered (the "what's hot" pool)
        if mood_genre_ids:
            for gid in mood_genre_ids[:2]:
                candidates.extend(tmdb_service.get_movies_by_genre(gid))
        else:
            candidates.extend(tmdb_service.get_popular())
            candidates.extend(tmdb_service.get_trending())
        
        # Source 2: Genome-based discovery (the "hidden gems that match your taste" pool)
        genome_candidates = self.find_genome_candidates(user_id, mood_genre_ids, n=40, exclude_ids=exclude_ids)
        candidates.extend(genome_candidates)
        
        # Source 3: IMDb quality picks (the "universally acclaimed" pool)
        imdb_candidates = self.find_imdb_quality_candidates(n=20, exclude_ids=exclude_ids)
        candidates.extend(imdb_candidates)

        seen = set()
        unique_candidates = []
        for m in candidates:
            if m['id'] not in seen and m['id'] not in exclude_ids:
                seen.add(m['id'])
                unique_candidates.append(m)

        unique_candidates = unique_candidates[:50]  # Fetch a bit more in case we drop some

        scored = []
        for base_movie in unique_candidates:
            full_movie = self.get_movie_cached(base_movie['id'])
            movie_to_score = full_movie if full_movie else base_movie 
            
            # Skip movies with missing critical metadata (nameless/posterless)
            if not movie_to_score.get('title') or not movie_to_score.get('poster_path'):
                continue
                
            # STRICT MOOD REQUIREMENT
            # If the user selected a mood, discard candidates that don't match the required genres
            if mood_genre_ids:
                movie_genres = movie_to_score.get('genre_ids', [])
                if not any(g in mood_genre_ids for g in movie_genres):
                    continue

            content_score = self.content_based_score(user_id, movie_to_score)
            collab_score = self.collaborative_score(user_id, movie_to_score.get('id', 0))
            rl_s = self.rl_score(user_id, movie_to_score) 

            # --- IMDb QUALITY OVERRIDE ---
            tmdb_id = movie_to_score.get('id')
            if tmdb_id in self.imdb_ratings:
                # Bayesian scale usually 5.0 - 9.0. Scale to 0-1
                imdb_quality = min(max((self.imdb_ratings[tmdb_id] - 4.0) / 5.0, 0.0), 1.0)
                # Override the sparse local collab score with the global IMDb consensus!
                collab_score = imdb_quality

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

    def magic_search(self, query, n=15):
        """Map a natural language query to the genome vector and find highly-rated matches."""
        if not self.tag_vocab or not self.genome_scores:
            print("Magic search unavailable (missing tags or genome scores)")
            return []
            
        # 1. Ask NLP service to extract core concepts
        extracted_tags = nlp_service.extract_tags_from_query(query)
        print(f"NL Query: '{query}' -> Extracted concepts: {extracted_tags}")
        
        # 2. Build exactly 1,128-dimension query vector
        query_vector = np.zeros(1128)
        
        for extracted_tag in extracted_tags:
            # Substring/fuzzy matching against our 1128 valid genome tags
            for valid_tag, idx in self.tag_vocab.items():
                if valid_tag in extracted_tag or extracted_tag in valid_tag:
                    query_vector[idx] += 1.0
        
        # Normalize the query vector
        if np.max(query_vector) > 0:
            query_vector = query_vector / np.linalg.norm(query_vector)
            
        print(f"Matched {np.sum(query_vector > 0)} distinct genome dimensions.")

        if np.sum(query_vector) == 0:
            print("No matching tags found for query. Fallback to trending.")
            return tmdb_service.get_trending()[:n]
            
        # 3. Compute cosine similarity across all cached movies
        scored = []
        for tmdb_id, movie_genome in self.genome_scores.items():
            if tmdb_id not in self.imdb_ratings:
                continue # strict quality check
                
            sim = compute_cosine_similarity(query_vector, movie_genome)
            quality_boost = min(max((self.imdb_ratings[tmdb_id] - 5.0) / 5.0, 0.0), 1.0)
            final_score = (sim * 0.70) + (quality_boost * 0.30)
            
            scored.append((tmdb_id, final_score))
            
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 4. Fetch the top metadata from TMDb
        results = []
        for tid, score in scored[:n * 3]: 
            movie = self.get_movie_cached(tid)
            if movie and movie.get('title') and movie.get('poster_path'):
                movie['_magic_score'] = score
                results.append(movie)
            if len(results) >= n:
                break
                
        return results

recommendation_engine = RecommendationEngine()