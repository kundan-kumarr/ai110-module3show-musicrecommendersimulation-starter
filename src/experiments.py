"""
Experiments: run different user profiles and weight configurations
to see how the recommender behaves.

Run with:
    python -m src.experiments
"""
from src.recommender import (
    load_songs, recommend_songs,
    _GENRE_WEIGHT, _MOOD_WEIGHT, _ENERGY_WEIGHT,
    _ACOUSTIC_WEIGHT, _VALENCE_WEIGHT, _DANCE_WEIGHT,
)
import src.recommender as rec_module


def print_recommendations(label: str, user_prefs: dict, songs: list, k: int = 3):
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: {label}")
    print(f"User: {user_prefs}")
    print(f"{'='*60}")
    results = recommend_songs(user_prefs, songs, k=k)
    for i, (song, score, explanation) in enumerate(results, 1):
        print(f"  {i}. {song['title']} ({song['genre']}, {song['mood']}) - Score: {score:.2f}")
        print(f"     {explanation}")


def run_experiments():
    songs = load_songs("data/songs.csv")

    # ------------------------------------------------------------------ #
    # Experiment 1 – Baseline: pop / happy / high energy user
    # ------------------------------------------------------------------ #
    baseline_user = {"genre": "pop", "mood": "happy", "energy": 0.8}
    print_recommendations("1. Baseline (pop / happy / energy 0.8)", baseline_user, songs)

    # ------------------------------------------------------------------ #
    # Experiment 2 – Lower genre weight from 3.0 → 0.5
    # Shows how genre dominance changes the ranking
    # ------------------------------------------------------------------ #
    print(f"\n{'='*60}")
    print("EXPERIMENT: 2. Same user but genre weight changed 3.0 -> 0.5")
    print(f"User: {baseline_user}")
    print(f"{'='*60}")

    original_genre_weight = rec_module._GENRE_WEIGHT
    rec_module._GENRE_WEIGHT = 0.5          # lower the genre importance
    results = recommend_songs(baseline_user, songs, k=3)
    for i, (song, score, explanation) in enumerate(results, 1):
        print(f"  {i}. {song['title']} ({song['genre']}, {song['mood']}) — Score: {score:.2f}")
        print(f"     {explanation}")
    rec_module._GENRE_WEIGHT = original_genre_weight   # restore

    # ------------------------------------------------------------------ #
    # Experiment 3 – Same pop/happy user but likes_acoustic = True
    # ------------------------------------------------------------------ #
    acoustic_pop_user = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": True}
    print_recommendations("3. Pop/happy user who likes acoustic", acoustic_pop_user, songs)

    # ------------------------------------------------------------------ #
    # Experiment 4 – Chill lofi / acoustic user (low energy)
    # ------------------------------------------------------------------ #
    chill_user = {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
    print_recommendations("4. Chill lofi / acoustic / low energy user", chill_user, songs)

    # ------------------------------------------------------------------ #
    # Experiment 5 – Genre NOT in catalog (hip-hop)
    # Shows how the system falls back to secondary features
    # ------------------------------------------------------------------ #
    missing_genre_user = {"genre": "hip-hop", "mood": "relaxed", "energy": 0.5}
    print_recommendations("5. Genre not in catalog (hip-hop) — fallback behavior", missing_genre_user, songs)


if __name__ == "__main__":
    run_experiments()
