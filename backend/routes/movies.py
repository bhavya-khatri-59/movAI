from flask import Blueprint, request, jsonify
from services.tmdb_service import tmdb_service

movies_bp = Blueprint('movies', __name__)


@movies_bp.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    results = tmdb_service.search_movies(query, page)
    return jsonify(results)


@movies_bp.route('/trending', methods=['GET'])
def trending():
    time_window = request.args.get('window', 'week')
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_trending(time_window, page)
    return jsonify({'results': movies})


@movies_bp.route('/popular', methods=['GET'])
def popular():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_popular(page)
    return jsonify({'results': movies})


@movies_bp.route('/now-playing', methods=['GET'])
def now_playing():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_now_playing(page)
    return jsonify({'results': movies})


@movies_bp.route('/genres', methods=['GET'])
def genres():
    genre_list = tmdb_service.get_genre_list()
    return jsonify({'genres': genre_list})


@movies_bp.route('/genre/<int:genre_id>', methods=['GET'])
def by_genre(genre_id):
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_movies_by_genre(genre_id, page)
    return jsonify({'results': movies})


@movies_bp.route('/<int:movie_id>', methods=['GET'])
def movie_detail(movie_id):
    movie = tmdb_service.get_movie(movie_id)
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    return jsonify(movie)
