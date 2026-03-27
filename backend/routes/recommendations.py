from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import Interaction, Rating
from utils.auth_utils import jwt_required_custom
from services.recommendation import recommendation_engine

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_recommendations():
    """Get personalized recommendations for the current user."""
    user_id = int(get_jwt_identity())
    mood = request.args.get('mood')
    n = request.args.get('n', 20, type=int)

    # Get disliked movie IDs to exclude
    disliked = Interaction.query.filter_by(user_id=user_id, liked=False).all()
    exclude_ids = {i.movie_id for i in disliked if not i.liked and i.id}

    # Also exclude already watched movies
    watched = Interaction.query.filter_by(user_id=user_id, watched=True).all()
    exclude_ids.update(i.movie_id for i in watched)

    movies = recommendation_engine.recommend(user_id, mood=mood, n=n, exclude_ids=exclude_ids)
    return jsonify({'recommendations': movies, 'mood': mood})


@recommendations_bp.route('/similar/<int:movie_id>', methods=['GET'])
def get_similar(movie_id):
    """Get similar movie recommendations."""
    from services.tmdb_service import tmdb_service
    movie = tmdb_service.get_movie(movie_id)
    if movie:
        return jsonify({'similar': movie.get('similar', [])})
    return jsonify({'similar': []})
