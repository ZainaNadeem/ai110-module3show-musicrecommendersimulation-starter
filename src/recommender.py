import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its audio feature attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's musical taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """OOP wrapper around the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted by score for the given user profile."""
        def _score(song: Song) -> float:
            score = 0.0
            if user.favorite_genre == song.genre:
                score += 2.0
            if user.favorite_mood == song.mood:
                score += 1.0
            score += 1.0 - abs(song.energy - user.target_energy)
            if user.likes_acoustic and song.acousticness > 0.6:
                score += 0.5
            return score

        return sorted(self.songs, key=_score, reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        reasons = []
        if user.favorite_genre == song.genre:
            reasons.append("genre match (+2.0)")
        if user.favorite_mood == song.mood:
            reasons.append("mood match (+1.0)")
        energy_sim = 1.0 - abs(song.energy - user.target_energy)
        reasons.append(f"energy similarity (+{energy_sim:.2f})")
        if user.likes_acoustic and song.acousticness > 0.6:
            reasons.append("acoustic preference match (+0.5)")
        return ", ".join(reasons) if reasons else "general match"


def load_songs(csv_path: str) -> List[Dict]:
    """Read songs from a CSV file and return a list of dicts with typed numeric fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences; returns (score, reasons)."""
    score = 0.0
    reasons = []

    # Genre match: +2.0
    if user_prefs.get("genre") == song.get("genre"):
        score += 2.0
        reasons.append("genre match (+2.0)")

    # Mood match: +1.0
    if user_prefs.get("mood") == song.get("mood"):
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Energy similarity: up to +1.0 (closer = higher)
    user_energy = float(user_prefs.get("energy", 0.5))
    song_energy = float(song.get("energy", 0.5))
    energy_sim = 1.0 - abs(song_energy - user_energy)
    score += energy_sim
    reasons.append(f"energy similarity (+{energy_sim:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, then return the top-k results sorted highest to lowest."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))

    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
