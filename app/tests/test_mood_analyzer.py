import pytest
from datetime import datetime, timezone
from app.services.mood_analyzer import MoodAnalyzer
from app.schemas.mood import AudioFeatures

@pytest.fixture
def mood_analyzer():
    return MoodAnalyzer(debug=True)

@pytest.fixture
def sample_tracks_data():
    return [
        {
            'id': '1',
            'name': 'Happy Song',
            'artist': 'Test Artist',
            'played_at': '2025-03-27T10:00:00+00:00',
            'audio_features': {
                'valence': 0.8,
                'energy': 0.7,
                'tempo': 120,
                'danceability': 0.6,
                'instrumentalness': 0.1,
                'loudness': -8.0,
                'mode': 1
            }
        },
        {
            'id': '2',
            'name': 'Sad Song',
            'artist': 'Test Artist 2',
            'played_at': '2025-03-27T09:00:00+00:00',
            'audio_features': {
                'valence': 0.2,
                'energy': 0.3,
                'tempo': 80,
                'danceability': 0.4,
                'instrumentalness': 0.8,
                'loudness': -12.0,
                'mode': 0
            }
        }
    ]

def test_compute_mood_score(mood_analyzer):
    features = AudioFeatures(
        valence=0.8,
        energy=0.7,
        tempo=120,
        danceability=0.6,
        instrumentalness=0.1,
        loudness=-8.0,
        mode=1
    )
    
    score = mood_analyzer._compute_mood_score(features)
    assert -1.0 <= score <= 1.0
    assert score > 0  # Should be positive for happy song

def test_analyze_recent_tracks(mood_analyzer, sample_tracks_data):
    analysis = mood_analyzer.analyze_recent_tracks(sample_tracks_data)
    
    assert analysis.user_id == "test_user"
    assert len(analysis.tracks_analyzed) == 2
    assert analysis.average_mood != 0  # Should have computed a non-zero mood
    assert analysis.mood_trend in ["improving", "declining", "stable"]
    assert len(analysis.recommendations) > 0

def test_mood_trend_detection(mood_analyzer):
    # Test declining mood trend
    declining_tracks = [
        {
            'id': str(i),
            'name': f'Test Song {i}',
            'artist': 'Test Artist',
            'played_at': f'2025-03-27T{10-i:02d}:00:00+00:00',
            'audio_features': {
                'valence': max(0.1, 0.9 - (i * 0.2)),  # Decreasing valence
                'energy': 0.5,
                'tempo': 120,
                'danceability': 0.6,
                'instrumentalness': 0.1,
                'loudness': -8.0,
                'mode': 1
            }
        } for i in range(5)
    ]
    
    analysis = mood_analyzer.analyze_recent_tracks(declining_tracks)
    assert analysis.mood_trend == "declining"
    assert "uplift" in ' '.join(analysis.recommendations).lower()

def test_error_handling(mood_analyzer):
    with pytest.raises(Exception):
        # Test with invalid data
        mood_analyzer.analyze_recent_tracks([{'invalid': 'data'}])

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
