# Music Recommender Simulation

## Project Summary

This project implements a small music recommender system called **VibeFinder 1.0**. It scores a 10-song catalog against a user's taste profile.

- favorite genre, preferred mood, target energy level, and acoustic preference 
- returns the top-k best matches along with plain-language explanations for each recommendation.

---

## How The System Works

### Song features

Each `Song` stores ten attributes loaded from `data/songs.csv`:

| Feature | Type | What it captures |
|---|---|---|
| `genre` | string | Musical category (pop, rock, lofi, jazz, …) |
| `mood` | string | Emotional tone (happy, chill, intense, moody, …) |
| `energy` | 0–1 float | Perceived loudness / intensity |
| `tempo_bpm` | float | Beats per minute |
| `valence` | 0–1 float | Musical positivity / happiness |
| `danceability` | 0–1 float | How suited the track is for dancing |
| `acousticness` | 0–1 float | Presence of acoustic (non-electronic) sound |

### User profile

A `UserProfile` stores four preferences:

- `favorite_genre` - preferred genre string
- `favorite_mood` - preferred mood string
- `target_energy` - preferred energy level (0–1)
- `likes_acoustic` - boolean flag for acoustic vs. electronic preference

### Scoring rule

The `Recommender` calls `_score_song_obj` for every song:

1. **Genre match** (+3.0) - exact match (case-insensitive)
2. **Mood match** (+2.0) - exact match (case-insensitive)
3. **Energy proximity** (+0–2.0) - `(1 − |song.energy − target|) × 2.0`
4. **Acoustic preference** (+0–1.5) - acousticness × 1.5 if user likes acoustic; else (1 - acousticness) × 0.75
5. **Valence bonus** (+0–0.5) - valence × 0.5
6. **Danceability bonus** (+0–0.5) - danceability × 0.5

Max possible score ≈ 9.5. Songs are ranked descending; top-k are returned.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main
   ```

### Running Tests

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Run all experiments yourself with:

```bash
python -m src.experiments
```

---

### Experiment 1 - Baseline: pop / happy / energy 0.8

**User:** `genre=pop, mood=happy, energy=0.8`

| Rank | Song | Genre | Mood | Score |
|---|---|---|---|---|
| 1 | Sunrise City | pop | happy | 8.39 |
| 2 | Gym Hero | pop | intense | 6.28 |
| 3 | Rooftop Lights | indie pop | happy | 5.22 |

"Sunrise City" wins by hitting genre + mood + energy + low acousticness + high valence all at once (8.39 out of ~9.5 max).

---

### Experiment 2 - Genre weight changed from 3.0 to 0.5

**User:** same as above - `genre=pop, mood=happy, energy=0.8`

| Rank | Song | Genre | Mood | Score |
|---|---|---|---|---|
| 1 | Sunrise City | pop | happy | 5.89 |
| 2 | Rooftop Lights | indie pop | happy | 5.22 |
| 3 | Gym Hero | pop | intense | 3.78 |

**What changed:** "Rooftop Lights" (indie pop, not pop) jumped from #3 to #2, displacing "Gym Hero". Without strong genre weighting, mood and valence matter more - and "Rooftop Lights" scores well on both. This shows that the genre weight is the main reason pop tracks dominate for a pop user.

---

### Experiment 3 - Same pop/happy user, but `likes_acoustic=True`

**User:** `genre=pop, mood=happy, energy=0.8, likes_acoustic=True`

| Rank | Song | Genre | Mood | Score |
|---|---|---|---|---|
| 1 | Sunrise City | pop | happy | 8.04 |
| 2 | Gym Hero | pop | intense | 5.64 |
| 3 | Rooftop Lights | indie pop | happy | 5.26 |

**What changed:** Scores dropped slightly for pop tracks because they have low acousticness (0.18 and 0.05), which now earns them less acoustic-preference credit. Top-3 order held because genre + mood bonuses still dominate, but a lofi/jazz track would climb if the energy target were lower.

---

### Experiment 4 - Chill lofi / acoustic / low energy user

**User:** `genre=lofi, mood=chill, energy=0.35, likes_acoustic=True`

| Rank | Song | Genre | Mood | Score |
|---|---|---|---|---|
| 1 | Library Rain | lofi | chill | 8.88 |
| 2 | Midnight Coding | lofi | chill | 8.52 |
| 3 | Focus Flow | lofi | focused | 6.67 |

**What happened:** Both lofi/chill tracks scored nearly as high as the best pop result (8.39), because they hit genre + mood + energy + high acousticness all at once. This is the system working as intended - the profile is well-served by the catalog.

---

### Experiment 5 - Genre not in catalog (hip-hop) - fallback behavior

**User:** `genre=hip-hop, mood=relaxed, energy=0.5`

| Rank | Song | Genre | Mood | Score |
|---|---|---|---|---|
| 1 | Coffee Shop Stories | jazz | relaxed | 4.45 |
| 2 | Sunrise City | pop | happy | 2.79 |
| 3 | Rooftop Lights | indie pop | happy | 2.78 |

**What happened:** No genre match fires at all - scores are much lower (4.45 vs 8+ for matched users). "Coffee Shop Stories" wins purely on mood match (relaxed) and energy proximity. This shows a real limitation: users whose genre is missing from the catalog get poor results regardless of weights.

---

## Limitations and Risks

- Only a 10-song catalog - results are heavily constrained by what's available.
- Genres are exact strings, so "indie pop" ≠ "pop" - a user who likes pop misses indie-pop tracks entirely.
- No personalization history; every run starts from scratch with stated preferences.
- Danceability and valence always add small bonus points, which subtly biases the system toward upbeat, danceable tracks for every user.
- No diversity mechanism - the top-5 can be dominated by songs that share a single high-weight attribute.

---

## Reflection

This system brought home the nature of the decisions made in building a recommender in an actual product. It seems obvious to weight one attribute higher than another when making a judgment about the importance of each, such as giving more importance to the genre attribute than to the danceability attribute, but the moment you test it out, you understand that there is a lot of subjectivity behind these numerical values, which are inherently biased toward certain types of users.

The most important realization from all of this was how quickly small biases can multiply. Since valence and danceability bonuses are applied to every single user, everyone's list starts drifting towards happy, danceable songs. If this were used in an actual product, it would be shaping music discovery without even realizing it.

---

## Model Card

See [model_card.md](model_card.md) for a full breakdown of the model's design, data, strengths, limitations, and evaluation.
