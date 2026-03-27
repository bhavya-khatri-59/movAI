from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.Text, default='')
    avatar_url = db.Column(db.String(500), default='')
    preferences = db.Column(db.JSON, default=dict)
    onboarded = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    ratings = db.relationship('Rating', backref='user', lazy='dynamic')
    interactions = db.relationship('Interaction', backref='user', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    onboarding_prefs = db.relationship('OnboardingPreference', backref='user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'onboarded': self.onboarded,
            'created_at': self.created_at.isoformat(),
            'followers_count': Follow.query.filter_by(following_id=self.id).count(),
            'following_count': Follow.query.filter_by(follower_id=self.id).count(),
            'movies_watched': self.interactions.filter_by(watched=True).count(),
            'reviews_count': self.reviews.count(),
        }


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)  # TMDb movie ID
    rating = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id'),)


class Interaction(db.Model):
    __tablename__ = 'interactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    liked = db.Column(db.Boolean, default=False)
    watchlist = db.Column(db.Boolean, default=False)
    watched = db.Column(db.Boolean, default=False)
    clicked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id'),)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))


class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    follower = db.relationship('User', foreign_keys=[follower_id], backref='following_rel')
    following = db.relationship('User', foreign_keys=[following_id], backref='followers_rel')

    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id'),)


class OnboardingPreference(db.Model):
    __tablename__ = 'onboarding_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(20), nullable=False)  # 'liked', 'disliked', 'not_watched'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'rated', 'reviewed', 'watchlisted', 'liked', 'followed'
    movie_id = db.Column(db.Integer)
    target_user_id = db.Column(db.Integer)
    extra_data = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='activities')
