class RewardMapper:
    """
    Maps user interaction events to scalar rewards for the Reinforcement Learning agent.
    Values are based on the system spec: Like -> +2, Watchlist -> +3, Skip -> -1.
    """
    REWARD_MAP = {
        'like': 2.0,
        'dislike': -1.0,
        'watchlist': 1.0,
        'skip': -1.0,
        'click': 0.1,
        'review': 1.5,
        'rate_high': 4.0,  # Rating >= 4
        'rate_low': -1.0,  # Rating <= 2
        'rate_neutral': 0.0 # Rating == 3
    }

    @classmethod
    def get_reward(cls, event_type: str) -> float:
        """Get numerical reward for a specific interaction event."""
        return cls.REWARD_MAP.get(event_type.lower(), 0.0)

reward_mapper = RewardMapper()
