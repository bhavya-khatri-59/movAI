from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import db, User, OnboardingPreference
from utils.auth_utils import jwt_required_custom
from services.tmdb_service import tmdb_service
from services.recommendation import recommendation_engine

onboarding_bp = Blueprint('onboarding', __name__)


@onboarding_bp.route('/movies', methods=['GET'])
def get_onboarding_movies():
    """Get curated movies for onboarding."""
    movies = tmdb_service.get_onboarding_movies()
    return jsonify({'movies': movies})


@onboarding_bp.route('/preferences', methods=['POST'])
@jwt_required_custom
def save_preferences():
    """Save user's onboarding preferences including genres and actors."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    preferences = data.get('preferences', [])
    genres = data.get('genres', [])
    actors = data.get('actors', [])

    if not preferences and not genres and not actors:
        return jsonify({'error': 'At least some preferences are required'}), 400

    # Clear old preferences
    OnboardingPreference.query.filter_by(user_id=user_id).delete()

    for pref in preferences:
        op = OnboardingPreference(
            user_id=user_id,
            movie_id=pref['movie_id'],
            label=pref['label']  # 'liked', 'disliked', 'not_watched'
        )
        db.session.add(op)

    # Mark user as onboarded
    user = User.query.get(user_id)
    user.onboarded = True

    # Build initial preference profile
    genre_affinity = {}
    for pref in preferences:
        if pref['label'] != 'not_watched':
            movie = tmdb_service.get_movie(pref['movie_id'])
            if movie:
                for genre in movie.get('genres', []):
                    weight = 2.0 if pref['label'] == 'liked' else -1.0
                    genre_affinity[genre] = genre_affinity.get(genre, 0) + weight

    user.preferences = {
        'genre_affinity': genre_affinity,
        'favorite_genres': genres,
        'favorite_actors': actors
    }
    db.session.commit()

    # Build RL profile
    recommendation_engine.build_user_profile(user_id, [], preferences)

    return jsonify({'message': 'Preferences saved', 'onboarded': True})
