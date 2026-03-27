from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

from config import Config
from models import db
from services.recommendation import recommendation_engine


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)

    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    JWTManager(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.movies import movies_bp
    from routes.interactions import interactions_bp
    from routes.social import social_bp
    from routes.onboarding import onboarding_bp
    from routes.mood import mood_bp
    from routes.recommendations import recommendations_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(movies_bp, url_prefix='/api/movies')
    app.register_blueprint(interactions_bp, url_prefix='/api/interactions')
    app.register_blueprint(social_bp, url_prefix='/api/social')
    app.register_blueprint(onboarding_bp, url_prefix='/api/onboarding')
    app.register_blueprint(mood_bp, url_prefix='/api/mood')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')

    # Create database tables
    with app.app_context():
        db.create_all()

        # Try loading MovieLens data
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ml-latest-small')
        if os.path.exists(data_path):
            recommendation_engine.load_movielens(data_path)
        else:
            print(f'MovieLens data not found at {data_path}. Running without offline data.')

    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'movielens_loaded': recommendation_engine.movielens_loaded}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
