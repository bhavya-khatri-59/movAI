import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import Config

class TMDbService:
    """Service for interacting with TMDb API."""

    def __init__(self):
        self.api_key = Config.TMDB_API_KEY
        self.base_url = Config.TMDB_BASE_URL
        self.image_base = Config.TMDB_IMAGE_BASE
        
        # [CRITICAL FIX] Implement connection pooling and retries for burst requests
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,             # Retry up to 5 times
            backoff_factor=0.5,  # Wait 0.5s, 1s, 2s, 4s between retries
            status_forcelist=[429, 500, 502, 503, 504], # Retry on rate limits & server errors
            allowed_methods=["GET"]
        )
        # Pool size of 100 ensures we can handle the loop of 40 candidate movies easily
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get(self, endpoint, params=None):
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        try:
            # Use self.session instead of requests to utilize connection pooling
            resp = self.session.get(f'{self.base_url}{endpoint}', params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f'TMDb API error: {e}')
            return None

    def search_movies(self, query, page=1):
        data = self._get('/search/movie', {'query': query, 'page': page})
        if data:
            return {
                'results': [self._format_movie(m) for m in data.get('results', [])],
                'total_pages': data.get('total_pages', 1),
                'total_results': data.get('total_results', 0),
                'page': data.get('page', 1),
            }
        return {'results': [], 'total_pages': 0, 'total_results': 0, 'page': 1}

    def get_movie(self, movie_id):
        data = self._get(f'/movie/{movie_id}', {'append_to_response': 'credits,similar,videos'})
        if data:
            return self._format_movie_detail(data)
        return None

    def get_trending(self, time_window='week', page=1):
        data = self._get(f'/trending/movie/{time_window}', {'page': page})
        if data:
            return [self._format_movie(m) for m in data.get('results', [])]
        return []

    def get_popular(self, page=1):
        data = self._get('/movie/popular', {'page': page})
        if data:
            return [self._format_movie(m) for m in data.get('results', [])]
        return []

    def get_now_playing(self, page=1):
        data = self._get('/movie/now_playing', {'page': page})
        if data:
            return [self._format_movie(m) for m in data.get('results', [])]
        return []

    def get_movies_by_genre(self, genre_id, page=1):
        data = self._get('/discover/movie', {'with_genres': genre_id, 'page': page, 'sort_by': 'popularity.desc'})
        if data:
            return [self._format_movie(m) for m in data.get('results', [])]
        return []

    def get_genre_list(self):
        data = self._get('/genre/movie/list')
        if data:
            return data.get('genres', [])
        return []

    def get_onboarding_movies(self):
        movies = []
        for page in range(1, 4):
            popular = self._get('/movie/popular', {'page': page})
            if popular:
                movies.extend([self._format_movie(m) for m in popular.get('results', [])[:8]])
        return movies[:25] 

    def _format_movie(self, movie):
        return {
            'id': movie.get('id'),
            'title': movie.get('title', ''),
            'overview': movie.get('overview', ''),
            'poster_path': f"{self.image_base}/w500{movie['poster_path']}" if movie.get('poster_path') else None,
            'backdrop_path': f"{self.image_base}/original{movie['backdrop_path']}" if movie.get('backdrop_path') else None,
            'release_date': movie.get('release_date', ''),
            'vote_average': movie.get('vote_average', 0),
            'vote_count': movie.get('vote_count', 0),
            'genre_ids': movie.get('genre_ids', []),
            'popularity': movie.get('popularity', 0),
        }

    def _format_movie_detail(self, movie):
        credits = movie.get('credits', {})
        cast = credits.get('cast', [])[:10]
        crew = credits.get('crew', [])
        director = next((c for c in crew if c.get('job') == 'Director'), None)
        similar = movie.get('similar', {}).get('results', [])[:6]
        videos = movie.get('videos', {}).get('results', [])
        trailer = next((v for v in videos if v.get('type') == 'Trailer' and v.get('site') == 'YouTube'), None)

        return {
            'id': movie.get('id'),
            'title': movie.get('title', ''),
            'overview': movie.get('overview', ''),
            'poster_path': f"{self.image_base}/w500{movie['poster_path']}" if movie.get('poster_path') else None,
            'backdrop_path': f"{self.image_base}/original{movie['backdrop_path']}" if movie.get('backdrop_path') else None,
            'release_date': movie.get('release_date', ''),
            'runtime': movie.get('runtime', 0),
            'vote_average': movie.get('vote_average', 0),
            'vote_count': movie.get('vote_count', 0),
            'genres': [g.get('name') for g in movie.get('genres', [])],
            
            # [CRITICAL FIX] Added genre_ids back in so the ML vectorizer can read it!
            'genre_ids': [g.get('id') for g in movie.get('genres', [])], 
            
            'tagline': movie.get('tagline', ''),
            'status': movie.get('status', ''),
            'budget': movie.get('budget', 0),
            'revenue': movie.get('revenue', 0),
            'director': {'name': director.get('name'), 'profile_path': f"{self.image_base}/w185{director['profile_path']}" if director and director.get('profile_path') else None} if director else None,
            'cast': [{'id': c.get('id'), 'name': c.get('name'), 'character': c.get('character'), 'profile_path': f"{self.image_base}/w185{c['profile_path']}" if c.get('profile_path') else None} for c in cast],
            'similar': [self._format_movie(m) for m in similar],
            'trailer_key': trailer.get('key') if trailer else None,
        }

tmdb_service = TMDbService()