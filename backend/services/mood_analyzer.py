# Genre-to-mood mapping for mood-aware recommendations
GENRE_MOOD_MAP = {
    'happy': [35, 16, 10751],        # Comedy, Animation, Family
    'emotional': [18, 10749, 36],     # Drama, Romance, History
    'thriller': [53, 9648, 80],       # Thriller, Mystery, Crime
    'romantic': [10749, 35, 18],      # Romance, Comedy, Drama
    'action': [28, 12, 878, 10752],   # Action, Adventure, Sci-Fi, War
    'feel-good': [35, 16, 10751, 10402],  # Comedy, Animation, Family, Music
}

# TMDb genre ID to name mapping
GENRE_ID_MAP = {
    28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy',
    80: 'Crime', 99: 'Documentary', 18: 'Drama', 10751: 'Family',
    14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music',
    9648: 'Mystery', 10749: 'Romance', 878: 'Science Fiction',
    10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western',
}

MOODS = ['happy', 'emotional', 'thriller', 'romantic', 'action', 'feel-good']


class MoodAnalyzer:
    """Analyze and map moods to genres for movie recommendations."""

    def get_genre_ids_for_mood(self, mood):
        mood_lower = mood.lower().strip()
        return GENRE_MOOD_MAP.get(mood_lower, [])

    def infer_mood_from_genres(self, genre_ids):
        """Infer mood tags from a list of genre IDs."""
        moods = []
        for mood, genre_list in GENRE_MOOD_MAP.items():
            if any(g in genre_list for g in genre_ids):
                moods.append(mood)
        return moods

    def get_mood_options(self):
        """Return available moods."""
        return [
            {'id': 'happy', 'label': 'Happy'},
            {'id': 'emotional', 'label': 'Emotional'},
            {'id': 'thriller', 'label': 'Thriller'},
            {'id': 'romantic', 'label': 'Romantic'},
            {'id': 'action', 'label': 'Action'},
            {'id': 'feel-good', 'label': 'Feel-Good'},
        ]


mood_analyzer = MoodAnalyzer()
