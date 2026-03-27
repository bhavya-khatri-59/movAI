import random
from collections import defaultdict

class RLRecommender:
    """
    Reinforcement Learning Module (Module 8)
    Implements a simple Q-Learning tabular baseline with an Experience Replay Buffer.
    State (S): User ID (simplified from User Embedding for prototype)
    Action (A): Movie ID recommended
    Reward (R): Extracted from Interaction event logs
    """
    def __init__(self, epsilon=0.15, alpha=0.1, gamma=0.9):
        self.epsilon = epsilon  # Exploration rate
        self.alpha = alpha      # Learning rate 
        self.gamma = gamma      # Discount factor
        
        # State-Action value table: q_table[user_id][movie_id] = float score
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Experience Replay Buffer: List of transitions (state, action, reward)
        self.replay_buffer = []

    def get_q_value(self, user_id: int, movie_id: int) -> float:
        """Returns the current Q-value for a user-movie pair."""
        return self.q_table[user_id].get(movie_id, 0.5)

    def update_q_value(self, user_id: int, movie_id: int, reward: float):
        """Updates the Q-table using the standard Q-learning update rule."""
        old_q = self.get_q_value(user_id, movie_id)
        
        # Simplified Q-learning update (assuming next state max Q is 0.5 baseline for prototype)
        # Q(s,a) = Q(s,a) + alpha * [Reward + gamma * max Q(s',a') - Q(s,a)]
        new_q = old_q + self.alpha * (reward + (self.gamma * 0.5) - old_q)
        
        self.q_table[user_id][movie_id] = new_q
        self.store_experience(user_id, movie_id, reward, new_q)
        
    def store_experience(self, user_id: int, movie_id: int, reward: float, new_q: float):
        """Stores interaction tuples into the Experience Replay Buffer for potential offline training."""
        self.replay_buffer.append({
            'state_user_id': user_id,
            'action_movie_id': movie_id,
            'reward': reward,
            'new_q_value': new_q
        })
        
        # Cap replay buffer size to prevent memory leaks
        if len(self.replay_buffer) > 10000:
            self.replay_buffer = self.replay_buffer[-10000:]

    def should_explore(self) -> bool:
        """Epsilon-greedy policy decision rule."""
        return random.random() < self.epsilon

rl_agent = RLRecommender()
