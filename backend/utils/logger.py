import logging
import sys

def setup_logger(name='movAI', level=logging.INFO):
    """
    Module 13: Centralized custom logger for movAI prototype.
    Configures formatters for Request, Error, and Interaction logs.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Standard stdout handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Standard formatter
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

app_logger = setup_logger()

def log_interaction(user_id, action, movie_id, extra=''):
    """Explicit interaction footprint logger."""
    app_logger.info(f"INTERACTION | User:{user_id} | Action:{action.upper()} | Movie:{movie_id} | {extra}")

def log_rl_decision(user_id, recommended_ids, is_exploration, avg_q):
    """Logs the Reinforcement Learning agent's branching logic."""
    branch = "EXPLORATION (Random)" if is_exploration else "EXPLOITATION (Greedy)"
    app_logger.info(f"RL_AGENT | User:{user_id} | Policy:{branch} | AvgQ:{avg_q:.3f} | Recs:{recommended_ids[:3]}...")
