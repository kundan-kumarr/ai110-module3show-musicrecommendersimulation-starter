# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 suggests up to 5 songs from a small 10-song catalog based on a user's stated genre preference, mood preference, target energy level, and acoustic taste. It is built for classroom exploration of how recommender systems work - not for real-world deployment. It assumes the user can articulate their taste in advance, and it treats every listening session as independent (no history or feedback loop).

---

## 3. How the Model Works

When a user describes their taste, VibeFinder gives each song in the catalog a numeric score based on how closely it matches four qualities:

1. **Genre** - Does the song's genre match the user's favorite? If yes, it gets the biggest reward in the scoring formula.
2. **Mood** - Does the song's emotional tone (happy, chill, intense, etc.) match what the user wants right now? A match earns a medium-sized reward.
3. **Energy** - Songs closer to the user's target energy level score higher. A track that is very far off in energy (e.g. a loud, intense track for someone who wants calm music) is penalized.
4. **Acoustic preference** - If the user likes acoustic sound, songs with high acousticness earn extra points. If the user prefers electronic sound, low-acousticness songs get a small bonus instead.

Two smaller bonuses - one for overall musical positivity (valence) and one for danceability - always add a little to every song's score, regardless of the user's stated preferences.

After scoring all songs, VibeFinder sorts them from highest to lowest and returns the top results, plus a plain-language sentence explaining what made each song a good match.

### Changes from the starter logic

The starter provided empty function stubs (`load_songs`, `score_song`, `recommend_songs`) and placeholder classes. The following were added:

- **Weighted scoring formula** with six components (genre, mood, energy, acoustic, valence, danceability) instead of a single placeholder score.
- **Acoustic preference branching** - the starter had no acoustic logic; this version rewards acoustic songs for acoustic users and slightly rewards non-acoustic songs for other users.
- **Explain recommendation** - a new method that returns a plain-English sentence listing exactly which features drove the score for each song.
- **OOP interface** (`Recommender` class with `recommend` and `explain_recommendation`) alongside the functional interface, so both the app and the test suite can use the same logic.

---

## 4. Data

The catalog is `data/songs.csv`, which contains **10 songs** across 6 genres:

| Genre | Songs |
|---|---|
| pop | 2 (Sunrise City, Gym Hero) |
| lofi | 2 (Midnight Coding, Focus Flow) |
| rock | 1 (Storm Runner) |
| ambient | 1 (Spacewalk Thoughts) |
| jazz | 1 (Coffee Shop Stories) |
| synthwave | 1 (Night Drive Loop) |
| indie pop | 1 (Rooftop Lights) |
| lofi | 1 (Library Rain) |

Moods covered: happy, chill, intense, focused, relaxed, moody.

The catalog was not modified from the starter; it was created for this exercise and does not represent any real streaming platform's data. Genres like hip-hop, R&B, classical, country, and metal are completely absent, so users with those preferences will receive poor recommendations regardless of weights.

---

## 5. Strengths

- **Pop / happy / high-energy users**: The catalog has two pop tracks and both score very well for users in this profile - the top recommendation ("Sunrise City") hits genre, mood, energy, and valence simultaneously, which felt correct intuitively.
- **Chill / acoustic users**: Lofi and ambient tracks dominate for low-energy, acoustic-loving users, and the explanations accurately identify why each track was chosen.
- **Transparency**: Every recommendation comes with a plain-English explanation of which features drove the score. Unlike a black-box neural network, it is easy to trace exactly why a song ranked where it did.
- **Simplicity**: The scoring function is easy to audit and adjust. Changing one weight immediately changes the ranking, which makes the system predictable.

---

## 6. Limitations and Bias

- **Tiny catalog**: 10 songs means the top-5 results often include songs that are not good matches - the system has no fallback for under-served tastes.
- **Exact-string genre matching**: "indie pop" does not match "pop," so a pop fan misses "Rooftop Lights" on genre points even though it would likely appeal to them.
- **Always-on valence and danceability bonuses**: These bonuses fire for every user regardless of preference, which subtly biases all recommendation lists toward happier and more danceable tracks. A user who wants melancholic, low-energy music is quietly disadvantaged.
- **No history or feedback**: The system cannot learn that a user skipped a recommendation or replayed one - every session starts cold.
- **Missing musical taste dimensions**: Lyrics, language, tempo ranges, key, mode (major vs. minor), and cultural context are all ignored. Two songs can score identically even if one is instrumental jazz and the other is screamo metal.
- **Uniform user model**: All users are assumed to weight genre, mood, and energy equally except for the acoustic flag. In reality, some listeners care far more about tempo or lyrical content than genre.

---

## 7. Evaluation

Three user profiles were tested manually:

| Profile | Expected top result | Actual top result | Match? |
|---|---|---|---|
| pop / happy / energy 0.8 / non-acoustic | Sunrise City | Sunrise City | Yes |
| lofi / chill / energy 0.4 / acoustic | Library Rain or Midnight Coding | Library Rain | Yes |
| rock / intense / energy 0.9 / non-acoustic | Storm Runner | Storm Runner | Yes |

A fourth test used a genre not in the catalog (hip-hop / relaxed / energy 0.5):

- Top result was "Coffee Shop Stories" (jazz, relaxed) because relaxed mood + moderate energy proximity produced the highest combined score in the absence of a genre match. This is a graceful fallback but not a meaningful recommendation.

Automated tests in `tests/test_recommender.py` verify:
- `Recommender.recommend` returns results sorted by score and puts the genre-and-mood-matched song first.
- `Recommender.explain_recommendation` returns a non-empty string for any scored song.

---

## 8. Future Work

- **Expand the catalog**: 10 songs is too small to serve users well. Even 100 songs would significantly improve recall for underrepresented genres.
- **Soft genre matching**: Build a genre similarity map (e.g. pop ↔ indie pop ↔ dance pop) so related genres earn partial credit instead of zero.
- **User-tunable weights**: Let users say "I care most about mood, not genre" and adjust the scoring formula accordingly.
- **Diversity injection**: Ensure the top-k list contains songs from at least two different genres or moods to avoid a monotone playlist.
- **Feedback loop**: Track which recommendations the user skips or replays and update their profile automatically over multiple sessions.
- **Richer features**: Add support for lyrical themes, language, tempo range preferences, and mode (major/minor) to capture more dimensions of taste.

---

## 9. Personal Reflection

The most surprising moment was realizing how much the weights act as hidden opinions about what "good music" means. Setting genre weight to 3.0 and danceability to 0.5 is not a neutral technical decision - it encodes the judgment that genre is six times more important than danceability. A user who primarily cares about danceability gets systematically worse service than one who cares about genre, and the system never tells them that.

Building this also made it easier to understand why real recommender systems generate "filter bubbles." Once a user is profiled as a pop listener, every interaction reinforces pop suggestions, and exposure to other genres shrinks. Even in this tiny simulation, the exact-match genre rule means a lofi fan will never naturally discover jazz unless the catalog happens to have a low-energy, chill jazz track that scores well on secondary features. Human curation deliberately surfacing music outside the model's confidence zone which still matters precisely because algorithms optimize for the preferences they can measure, not the ones they cannot.
