import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///movai.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    TMDB_BASE_URL = 'https://api.themoviedb.org/3'
    TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # Dataset Paths
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    IMDB_RATINGS_PATH = os.path.join(DATA_DIR, 'title.ratings.tsv')
    ML_LATEST_DIR = os.path.join(DATA_DIR, 'ml-latest')
    GENOME_SCORES_PATH = os.path.join(ML_LATEST_DIR, 'genome-scores.csv')
    LINKS_PATH = os.path.join(ML_LATEST_DIR, 'links.csv')
