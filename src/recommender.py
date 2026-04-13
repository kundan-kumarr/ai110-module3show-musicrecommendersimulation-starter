import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

_GENRE_WEIGHT = 3.0
_MOOD_WEIGHT = 2.0
_ENERGY_WEIGHT = 2.0
_ACOUSTIC_WEIGHT = 1.5
_VALENCE_WEIGHT = 0.5
_DANCE_WEIGHT = 0.5


def _score_song_obj(user: UserProfile, song: Song) -> Tuple[float, List[str]]:
    """Score a Song dataclass against a UserProfile. Returns (score, reasons)."""
    score = 0.0
    reasons: List[str] = []

    # Genre match
    if song.genre.lower() == user.favorite_genre.lower():
        score += _GENRE_WEIGHT
        reasons.append(f"genre matches your favourite ({song.genre})")

    # Mood match
    if song.mood.lower() == user.favorite_mood.lower():
        score += _MOOD_WEIGHT
        reasons.append(f"mood matches your preference ({song.mood})")

    # Energy proximity  (closer → higher reward)
    energy_sim = 1.0 - abs(song.energy - user.target_energy)
    score += energy_sim * _ENERGY_WEIGHT
    if energy_sim >= 0.85:
        reasons.append(f"energy level is very close to your target ({song.energy:.2f})")
    elif energy_sim >= 0.65:
        reasons.append(f"energy level is reasonably close to your target ({song.energy:.2f})")

    # Acoustic preference
    if user.likes_acoustic:
        score += song.acousticness * _ACOUSTIC_WEIGHT
        if song.acousticness >= 0.6:
            reasons.append(f"high acousticness suits your taste ({song.acousticness:.2f})")
    else:
        score += (1.0 - song.acousticness) * _ACOUSTIC_WEIGHT * 0.5
        if song.acousticness <= 0.3:
            reasons.append(f"low acousticness fits your preference ({song.acousticness:.2f})")

    # Valence (positivity) bonus
    score += song.valence * _VALENCE_WEIGHT
    if song.valence >= 0.75:
        reasons.append(f"very positive / uplifting vibe (valence {song.valence:.2f})")

    # Danceability bonus
    score += song.danceability * _DANCE_WEIGHT

    return round(score, 4), reasons


# ---------------------------------------------------------------------------
# OOP interface (required by tests)
# ---------------------------------------------------------------------------

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by score for the given user."""
        scored = [(_score_song_obj(user, s)[0], s) for s in self.songs]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why a song was recommended."""
        _, reasons = _score_song_obj(user, song)
        if not reasons:
            return "This song is included as a general discovery pick outside your usual preferences."
        return "Recommended because: " + "; ".join(reasons) + "."


# ---------------------------------------------------------------------------
# Functional interface (required by main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts."""
    print(f"Loading songs from {csv_path}...")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"  Loaded {len(songs)} songs.")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song dict against a user_prefs dict.

    user_prefs keys: genre (str), mood (str), energy (float),
                     likes_acoustic (bool, optional – default False)
    Returns: (score, list_of_reason_strings)
    """
    score = 0.0
    reasons: List[str] = []

    likes_acoustic: bool = user_prefs.get("likes_acoustic", False)

    # Genre match
    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        score += _GENRE_WEIGHT
        reasons.append(f"genre matches your favourite ({song['genre']})")

    # Mood match
    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        score += _MOOD_WEIGHT
        reasons.append(f"mood matches your preference ({song['mood']})")

    # Energy proximity
    target_energy: float = float(user_prefs.get("energy", 0.5))
    energy_sim = 1.0 - abs(song["energy"] - target_energy)
    score += energy_sim * _ENERGY_WEIGHT
    if energy_sim >= 0.85:
        reasons.append(f"energy level is very close to your target ({song['energy']:.2f})")
    elif energy_sim >= 0.65:
        reasons.append(f"energy level is reasonably close to your target ({song['energy']:.2f})")

    # Acoustic preference
    if likes_acoustic:
        score += song["acousticness"] * _ACOUSTIC_WEIGHT
        if song["acousticness"] >= 0.6:
            reasons.append(f"high acousticness suits your taste ({song['acousticness']:.2f})")
    else:
        score += (1.0 - song["acousticness"]) * _ACOUSTIC_WEIGHT * 0.5
        if song["acousticness"] <= 0.3:
            reasons.append(f"low acousticness fits your preference ({song['acousticness']:.2f})")

    # Valence bonus
    score += song["valence"] * _VALENCE_WEIGHT
    if song["valence"] >= 0.75:
        reasons.append(f"very positive / uplifting vibe (valence {song['valence']:.2f})")

    # Danceability bonus
    score += song["danceability"] * _DANCE_WEIGHT

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Return the top-k recommended songs as (song_dict, score, explanation) tuples.
    """
    scored = []
    for song in songs:
        s, reasons = score_song(user_prefs, song)
        explanation = (
            "Recommended because: " + "; ".join(reasons) + "."
            if reasons
            else "General discovery pick outside your usual preferences."
        )
        scored.append((song, s, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]