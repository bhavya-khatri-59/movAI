from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import db, Rating, Interaction, Review, ActivityLog
from utils.auth_utils import jwt_required_custom
from services.recommendation import recommendation_engine
from utils.reward_mapper import reward_mapper

interactions_bp = Blueprint('interactions', __name__)


@interactions_bp.route('/rate', methods=['POST'])
@jwt_required_custom
def rate_movie():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    movie_id = data.get('movie_id')
    rating_value = data.get('rating')

    if not movie_id or rating_value is None:
        return jsonify({'error': 'movie_id and rating required'}), 400
    if not (1 <= rating_value <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if rating:
        rating.rating = rating_value
    else:
        rating = Rating(user_id=user_id, movie_id=movie_id, rating=rating_value)
        db.session.add(rating)

    # Log activity
    activity = ActivityLog(user_id=user_id, action='rated', movie_id=movie_id,
                           extra_data={'rating': rating_value})
    db.session.add(activity)
    db.session.commit()

    # Update RL
    event_type = 'rate_high' if rating_value >= 4 else ('rate_low' if rating_value <= 2 else 'rate_neutral')
    reward = reward_mapper.get_reward(event_type)
    recommendation_engine.update_rl(user_id, movie_id, reward)

    return jsonify({'message': 'Rating saved', 'rating': rating_value})


@interactions_bp.route('/like', methods=['POST'])
@jwt_required_custom
def like_movie():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    movie_id = data.get('movie_id')

    interaction = Interaction.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if interaction:
        interaction.liked = not interaction.liked
    else:
        interaction = Interaction(user_id=user_id, movie_id=movie_id, liked=True)
        db.session.add(interaction)

    activity = ActivityLog(user_id=user_id, action='liked', movie_id=movie_id)
    db.session.add(activity)
    db.session.commit()

    reward = reward_mapper.get_reward('like' if interaction.liked else 'dislike')
    recommendation_engine.update_rl(user_id, movie_id, reward)

    return jsonify({'liked': interaction.liked})


@interactions_bp.route('/watchlist', methods=['POST'])
@jwt_required_custom
def toggle_watchlist():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    movie_id = data.get('movie_id')

    interaction = Interaction.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if interaction:
        interaction.watchlist = not interaction.watchlist
    else:
        interaction = Interaction(user_id=user_id, movie_id=movie_id, watchlist=True)
        db.session.add(interaction)

    if interaction.watchlist:
        activity = ActivityLog(user_id=user_id, action='watchlisted', movie_id=movie_id)
        db.session.add(activity)

    db.session.commit()

    reward = reward_mapper.get_reward('watchlist' if interaction.watchlist else 'skip')
    recommendation_engine.update_rl(user_id, movie_id, reward)

    return jsonify({'watchlist': interaction.watchlist})


@interactions_bp.route('/watched', methods=['POST'])
@jwt_required_custom
def mark_watched():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    movie_id = data.get('movie_id')

    interaction = Interaction.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if interaction:
        interaction.watched = True
    else:
        interaction = Interaction(user_id=user_id, movie_id=movie_id, watched=True)
        db.session.add(interaction)

    activity = ActivityLog(user_id=user_id, action='watched', movie_id=movie_id)
    db.session.add(activity)
    db.session.commit()

    return jsonify({'watched': True})


@interactions_bp.route('/review', methods=['POST'])
@jwt_required_custom
def create_review():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    movie_id = data.get('movie_id')
    text = data.get('text', '').strip()
    rating_value = data.get('rating')

    if not movie_id or not text:
        return jsonify({'error': 'movie_id and text required'}), 400

    review = Review(user_id=user_id, movie_id=movie_id, text=text, rating=rating_value)
    db.session.add(review)

    activity = ActivityLog(user_id=user_id, action='reviewed', movie_id=movie_id)
    db.session.add(activity)
    db.session.commit()

    return jsonify({'message': 'Review created', 'review_id': review.id}), 201


@interactions_bp.route('/reviews/<int:movie_id>', methods=['GET'])
def get_reviews(movie_id):
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.created_at.desc()).all()
    return jsonify({
        'reviews': [{
            'id': r.id,
            'user_id': r.user_id,
            'user_name': r.user.name,
            'text': r.text,
            'rating': r.rating,
            'likes_count': r.likes_count,
            'created_at': r.created_at.isoformat(),
        } for r in reviews]
    })


@interactions_bp.route('/status/<int:movie_id>', methods=['GET'])
@jwt_required_custom
def get_movie_status(movie_id):
    user_id = int(get_jwt_identity())
    interaction = Interaction.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    return jsonify({
        'liked': interaction.liked if interaction else False,
        'watchlist': interaction.watchlist if interaction else False,
        'watched': interaction.watched if interaction else False,
        'rating': rating.rating if rating else None,
    })


@interactions_bp.route('/watchlist', methods=['GET'])
@jwt_required_custom
def get_watchlist():
    user_id = int(get_jwt_identity())
    items = Interaction.query.filter_by(user_id=user_id, watchlist=True).all()
    return jsonify({'movie_ids': [item.movie_id for item in items]})


@interactions_bp.route('/history', methods=['GET'])
@jwt_required_custom
def get_history():
    user_id = int(get_jwt_identity())
    items = Interaction.query.filter_by(user_id=user_id, watched=True).order_by(
        Interaction.updated_at.desc()).all()
    return jsonify({'movie_ids': [item.movie_id for item in items]})
