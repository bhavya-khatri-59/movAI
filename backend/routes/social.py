from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import db, User, Follow, ActivityLog
from utils.auth_utils import jwt_required_custom

social_bp = Blueprint('social', __name__)


@social_bp.route('/follow', methods=['POST'])
@jwt_required_custom
def follow_user():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    target_id = data.get('user_id')

    if not target_id or target_id == user_id:
        return jsonify({'error': 'Invalid user_id'}), 400

    target = User.query.get(target_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    existing = Follow.query.filter_by(follower_id=user_id, following_id=target_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'following': False})

    follow = Follow(follower_id=user_id, following_id=target_id)
    db.session.add(follow)

    activity = ActivityLog(user_id=user_id, action='followed', target_user_id=target_id)
    db.session.add(activity)
    db.session.commit()

    return jsonify({'following': True})


@social_bp.route('/followers/<int:user_id>', methods=['GET'])
def get_followers(user_id):
    follows = Follow.query.filter_by(following_id=user_id).all()
    users = [User.query.get(f.follower_id) for f in follows]
    return jsonify({
        'followers': [{'id': u.id, 'name': u.name, 'username': u.username, 'avatar_url': u.avatar_url} for u in users if u]
    })


@social_bp.route('/following/<int:user_id>', methods=['GET'])
def get_following(user_id):
    follows = Follow.query.filter_by(follower_id=user_id).all()
    users = [User.query.get(f.following_id) for f in follows]
    return jsonify({
        'following': [{'id': u.id, 'name': u.name, 'username': u.username, 'avatar_url': u.avatar_url} for u in users if u]
    })


@social_bp.route('/feed', methods=['GET'])
@jwt_required_custom
def get_feed():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Get users this person follows
    following = Follow.query.filter_by(follower_id=user_id).all()
    following_ids = [f.following_id for f in following]

    if not following_ids:
        return jsonify({'feed': [], 'page': page, 'has_more': False})

    # Get activities from followed users
    activities = ActivityLog.query.filter(
        ActivityLog.user_id.in_(following_ids)
    ).order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    feed = []
    for a in activities.items:
        user = User.query.get(a.user_id)
        item = {
            'id': a.id,
            'user': {'id': user.id, 'name': user.name, 'avatar_url': user.avatar_url} if user else None,
            'action': a.action,
            'movie_id': a.movie_id,
            'target_user_id': a.target_user_id,
            'metadata': a.extra_data,
            'created_at': a.created_at.isoformat(),
        }
        feed.append(item)

    return jsonify({'feed': feed, 'page': page, 'has_more': activities.has_next})


@social_bp.route('/users/search', methods=['GET'])
def search_users():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'users': []})
    users = User.query.filter(
        db.or_(
            User.name.ilike(f'%{query}%'),
            User.username.ilike(f'%{query}%')
        )
    ).limit(20).all()
    return jsonify({'users': [u.to_dict() for u in users]})


@social_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()})
