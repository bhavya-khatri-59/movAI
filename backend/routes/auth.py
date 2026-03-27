import re
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity
from models import db, User
from utils.auth_utils import jwt_required_custom

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Generate or validate username
    username = data.get('username', '').strip().lower()
    if not username:
        # Auto-generate from name
        base = re.sub(r'[^a-z0-9]', '', data['name'].lower())
        username = base
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f'{base}{counter}'
            counter += 1
    else:
        if not re.match(r'^[a-z0-9_]{3,30}$', username):
            return jsonify({'error': 'Username must be 3-30 chars, lowercase letters, numbers, underscores only'}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 409

    user = User(
        name=data['name'],
        username=username,
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'message': 'Account created successfully'
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })


@auth_bp.route('/me', methods=['GET'])
@jwt_required_custom
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()})


@auth_bp.route('/me', methods=['PUT'])
@jwt_required_custom
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if data.get('name'):
        user.name = data['name']
    if data.get('bio') is not None:
        user.bio = data['bio']
    if data.get('avatar_url') is not None:
        user.avatar_url = data['avatar_url']

    db.session.commit()
    return jsonify({'user': user.to_dict()})
