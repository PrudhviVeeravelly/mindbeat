"""Service for analyzing mood based on audio features."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import statistics
import numpy as np

from app.schemas.mood import MoodAnalysis, TrackMood, AudioFeatures
from app.services.spotify import SpotifyService

logger = logging.getLogger(__name__)

class MoodAnalyzer:
    """Analyzes mood based on audio features."""
    
    def __init__(self, debug: bool = False):
        """Initialize the mood analyzer.
        
        Args:
            debug: If True, use mock data for testing
        """
        self.debug = debug
        
    async def analyze_tracks(self, tracks_data: List[Dict[str, Any]]) -> MoodAnalysis:
        """Analyze a list of tracks and return mood analysis.
        
        Args:
            tracks_data: List of track objects with audio features
            
        Returns:
            MoodAnalysis object with overall mood and track-specific analysis
        """
        try:
            if not tracks_data:
                logger.warning("No tracks provided for analysis")
                return MoodAnalysis(
                    overall_mood=0.5,  # Neutral mood when no data
                    average_energy=0.5,
                    tracks=[],
                    mood_trend=[0.5] * 7  # Neutral trend when no data
                )
            
            # Analyze each track
            track_moods = []
            for track in tracks_data:
                if not track.get("features"):
                    logger.warning(f"No features for track {track.get('id', 'unknown')}")
                    continue
                    
                features = track["features"]
                # Calculate mood score (weighted average of valence and energy)
                mood_score = self._compute_mood_score(features)
                
                track_moods.append(
                    TrackMood(
                        mood_score=mood_score,
                        energy=features.energy,
                        valence=features.valence
                    )
                )
            
            if not track_moods:
                logger.warning("No valid tracks for analysis")
                return MoodAnalysis(
                    overall_mood=0.5,
                    average_energy=0.5,
                    tracks=[],
                    mood_trend=[0.5] * 7
                )
            
            # Calculate overall metrics
            mood_scores = [t.mood_score for t in track_moods]
            energy_scores = [t.energy for t in track_moods]
            
            overall_mood = float(np.mean(mood_scores))
            average_energy = float(np.mean(energy_scores))
            
            # Generate mood trend (last 7 days)
            # For now, we'll just use the most recent tracks
            num_trend_points = min(7, len(mood_scores))
            mood_trend = [float(x) for x in mood_scores[:num_trend_points]]
            # Pad with the average if we don't have enough points
            if len(mood_trend) < 7:
                mood_trend.extend([overall_mood] * (7 - len(mood_trend)))
            
            return MoodAnalysis(
                overall_mood=overall_mood,
                average_energy=average_energy,
                tracks=track_moods,
                mood_trend=mood_trend
            )
            
        except Exception as e:
            logger.error(f"Error analyzing tracks: {str(e)}")
            # Return neutral values in case of error
            return MoodAnalysis(
                overall_mood=0.5,
                average_energy=0.5,
                tracks=[],
                mood_trend=[0.5] * 7
            )
    
    async def analyze_debug_data(self) -> MoodAnalysis:
        """Generate sample mood analysis data for testing.
        
        Returns:
            MoodAnalysis: Sample mood analysis results
        """
        import random
        
        # Generate sample track moods
        tracks = []
        for _ in range(5):
            valence = random.uniform(0.3, 0.9)
            energy = random.uniform(0.4, 0.8)
            tracks.append(
                TrackMood(
                    mood_score=valence,
                    energy=energy,
                    valence=valence
                )
            )
        
        # Calculate overall metrics
        overall_mood = statistics.mean(t.mood_score for t in tracks)
        average_energy = statistics.mean(t.energy for t in tracks)
        
        # Generate sample trend (last 7 days)
        mood_trend = [random.uniform(0.3, 0.8) for _ in range(7)]
        
        return MoodAnalysis(
            overall_mood=overall_mood,
            average_energy=average_energy,
            tracks=tracks,
            mood_trend=mood_trend
        )
    
    def _compute_mood_score(self, features: AudioFeatures) -> float:
        """Compute mood score from audio features.
        
        The mood score is computed using a weighted combination of:
        - Valence (musical positiveness)
        - Energy (intensity and activity)
        - Danceability (how suitable for dancing)
        - Mode (major/minor key)
        
        Args:
            features: Audio features of the track
            
        Returns:
            float: Mood score between 0 and 1
        """
        # Base score from valence (most important)
        base_score = features.valence * 0.5
        
        # Energy contribution
        energy_score = features.energy * 0.25
        
        # Danceability contribution
        dance_score = features.danceability * 0.15
        
        # Mode contribution (major key = slight positive boost)
        mode_score = 0.1 if features.mode == 1 else 0
        
        # Combine all factors
        mood_score = base_score + energy_score + dance_score + mode_score
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, mood_score))
    
    def _calculate_mood_trend(self, tracks: List[TrackMood]) -> List[float]:
        """Calculate daily mood trend from track moods.
        
        Args:
            tracks: List of track moods
            
        Returns:
            List[float]: List of daily mood scores
        """
        # For now, just return the last 7 scores
        # TODO: Group by day and calculate daily averages
        scores = [t.mood_score for t in tracks[:7]]
        while len(scores) < 7:
            scores.append(scores[-1] if scores else 0.5)
        return scores

    def analyze_current_mood(self, tracks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the current mood based on recent tracks.
        
        Args:
            tracks: List of track objects with audio features
            
        Returns:
            Dict containing mood analysis
        """
        if not tracks:
            logger.warning("No tracks provided for analysis")
            return {
                "score": 0.5,  # Neutral mood
                "energy": 0.5,
                "description": "Start listening to music to see your mood analysis!"
            }
        
        try:
            # Calculate average mood score from valence and energy
            total_valence = 0
            total_energy = 0
            count = 0
            
            for track in tracks[:10]:  # Use most recent 10 tracks
                if 'features' in track:
                    total_valence += track['features']['valence']
                    total_energy += track['features']['energy']
                    count += 1
            
            if count == 0:
                return {
                    "score": 0.5,
                    "energy": 0.5,
                    "description": "Start listening to music to see your mood analysis!"
                }
            
            mood_score = total_valence / count
            energy_score = total_energy / count
            
            # Generate mood description
            if mood_score > 0.7:
                description = "Your recent music choices reflect a very positive mood!"
            elif mood_score > 0.5:
                description = "You're in a balanced and content mood."
            else:
                description = "Your music suggests a more reflective mood."
                
            return {
                "score": mood_score,
                "energy": energy_score,
                "description": description
            }
            
        except Exception as e:
            logger.error(f"Error analyzing mood: {str(e)}")
            return {
                "score": 0.5,
                "energy": 0.5,
                "description": "Unable to analyze mood at this time."
            }

    def analyze_mood_trend(self, tracks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the mood trend over time.
        
        Args:
            tracks: List of track objects with timestamps and audio features
            
        Returns:
            Dict containing dates and mood scores
        """
        if not tracks:
            # Return a week of neutral values if no tracks
            dates = []
            scores = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%b %d")
                dates.insert(0, date)
                scores.insert(0, 0.5)
            return {"dates": dates, "scores": scores}
        
        try:
            # Group tracks by day and calculate average mood
            daily_moods = {}
            for track in tracks:
                if 'features' not in track:
                    continue
                    
                date = datetime.strptime(
                    track.get('played_at', datetime.now().isoformat()),
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ).strftime("%b %d")
                
                if date not in daily_moods:
                    daily_moods[date] = {"total": 0, "count": 0}
                
                daily_moods[date]["total"] += track['features']['valence']
                daily_moods[date]["count"] += 1
            
            # Calculate averages and format for chart
            dates = []
            scores = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%b %d")
                mood_data = daily_moods.get(date, {"total": 0.5, "count": 1})
                
                dates.insert(0, date)
                scores.insert(0, mood_data["total"] / mood_data["count"])
            
            return {"dates": dates, "scores": scores}
            
        except Exception as e:
            logger.error(f"Error analyzing mood trend: {str(e)}")
            return {"dates": [], "scores": []}

    def get_recommendations(self, current_mood: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on current mood.
        
        Args:
            current_mood: Dict containing current mood analysis
            
        Returns:
            List of recommendation objects
        """
        recommendations = []
        
        # Add mood-based recommendation
        if current_mood["score"] > 0.7:
            recommendations.append({
                "title": "Keep the Vibe Going!",
                "description": "Your music choices reflect a very positive mood. Here are some similar upbeat tracks to maintain the energy."
            })
        elif current_mood["score"] > 0.4:
            recommendations.append({
                "title": "Balanced Mood",
                "description": "Your playlist shows a good balance. Consider exploring some new genres to discover more music you might enjoy."
            })
        else:
            recommendations.append({
                "title": "Mood Boost",
                "description": "Your recent tracks suggest a more reflective mood. Here are some uplifting songs that might help boost your spirits."
            })
        
        # Add energy-based recommendation
        if current_mood["energy"] > 0.6:
            recommendations.append({
                "title": "Energy Management",
                "description": "Consider adding some calming tracks to balance your high-energy playlist."
            })
        else:
            recommendations.append({
                "title": "Energy Boost",
                "description": "Try adding some upbeat tracks to increase your energy levels."
            })
        
        return recommendations
