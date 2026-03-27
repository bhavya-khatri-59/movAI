import random
from models import db, User
from services.tmdb_service import tmdb_service

class RLRecommender:
    """
    Reinforcement Learning Module (Module 8)
    [UPGRADED] - Memory persists to Database.
    [UPGRADED] - Learns via Genres to generalize across new movies.
    """
    def __init__(self, epsilon=0.15, alpha=0.1, gamma=0.9):
        self.epsilon = epsilon  
        self.alpha = alpha      
        self.gamma = gamma      
        self.replay_buffer = []

    def get_q_value(self, user_id: int, genre_name: str) -> float:
        """Returns the Q-value for a specific genre from the user's DB profile."""
        user = User.query.get(user_id)
        if not user or not user.rl_q_table:
            return 0.5
        return user.rl_q_table.get(genre_name, 0.5)

    def update_q_value(self, user_id: int, movie_id: int, reward: float):
        """Updates the DB Q-table for ALL genres associated with the interacted movie."""
        user = User.query.get(user_id)
        if not user:
            return

        # Fetch the movie to see what genres triggered this reward
        movie = tmdb_service.get_movie(movie_id)
        if not movie:
            return
            
        genres = movie.get('genres', []) # e.g., ['Action', 'Sci-Fi']
        if not genres:
            return

        # Pull memory from DB, copy it to trigger SQLAlchemy JSON updates
        q_table = dict(user.rl_q_table) if user.rl_q_table else {}

        # Apply the reward to EVERY genre in the movie
        for genre in genres:
            old_q = q_table.get(genre, 0.5)
            # Standard Q-Learning Formula
            new_q = old_q + self.alpha * (reward + (self.gamma * 0.5) - old_q)
            q_table[genre] = new_q
            self.store_experience(user_id, genre, reward, new_q)
            
        # Save updated memory back to DB
        user.rl_q_table = q_table
        db.session.commit()
        
    def store_experience(self, user_id: int, genre: str, reward: float, new_q: float):
        """Stores interaction tuples into the Experience Replay Buffer for offline training."""
        self.replay_buffer.append({
            'state_user_id': user_id,
            'action_genre': genre,
            'reward': reward,
            'new_q_value': new_q
        })
        if len(self.replay_buffer) > 10000:
            self.replay_buffer = self.replay_buffer[-10000:]

    def should_explore(self) -> bool:
        """Epsilon-greedy policy decision rule."""
        return random.random() < self.epsilon

rl_agent = RLRecommender()