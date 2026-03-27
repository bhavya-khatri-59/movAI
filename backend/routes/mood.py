from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from utils.auth_utils import jwt_required_custom
from services.mood_analyzer import mood_analyzer
from services.tmdb_service import tmdb_service

mood_bp = Blueprint('mood', __name__)


@mood_bp.route('/options', methods=['GET'])
def get_moods():
    """Get available mood options."""
    return jsonify({'moods': mood_analyzer.get_mood_options()})


@mood_bp.route('/movies', methods=['GET'])
def get_mood_movies():
    """Get movies filtered by mood."""
    mood = request.args.get('mood', '')
    page = request.args.get('page', 1, type=int)

    if not mood:
        return jsonify({'error': 'Mood parameter required'}), 400

    genre_ids = mood_analyzer.get_genre_ids_for_mood(mood)
    if not genre_ids:
        return jsonify({'results': []})

    all_movies = []
    for gid in genre_ids[:2]:
        movies = tmdb_service.get_movies_by_genre(gid, page)
        all_movies.extend(movies)

    # Deduplicate
    seen = set()
    unique = []
    for m in all_movies:
        if m['id'] not in seen:
            seen.add(m['id'])
            unique.append(m)

    return jsonify({'results': unique[:20], 'mood': mood})
