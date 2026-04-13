from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_recommend_k_limits_results():
    rec = make_small_recommender()
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    assert len(rec.recommend(user, k=1)) == 1


def test_acoustic_user_prefers_high_acousticness():
    songs = [
        Song(id=1, title="Electric Track", artist="A", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.1),
        Song(id=2, title="Acoustic Track", artist="B", genre="lofi", mood="chill",
             energy=0.4, tempo_bpm=80, valence=0.6, danceability=0.5, acousticness=0.9),
    ]
    rec = Recommender(songs)
    user = UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.4,
        likes_acoustic=True,
    )
    results = rec.recommend(user, k=2)
    assert results[0].title == "Acoustic Track"


def test_no_match_returns_discovery_explanation():
    songs = [
        Song(id=1, title="Odd Track", artist="X", genre="metal", mood="rage",
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
    ]
    rec = Recommender(songs)
    user = UserProfile(
        favorite_genre="classical",
        favorite_mood="peaceful",
        target_energy=0.5,
        likes_acoustic=False,
    )
    explanation = rec.explain_recommendation(user, songs[0])
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
