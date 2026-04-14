# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder suggests up to five songs from a small catalog based on three user-supplied preferences: favorite genre, favorite mood, and a target energy level (0.0–1.0). The goal is to demonstrate how content-based filtering works — matching a user's stated preferences against measurable features of each song and ranking the results by similarity score.

### Intended Use
This system is designed for classroom exploration only. It is meant to help students understand how a recommender system scores, ranks, and explains results. It works best as a learning tool when you want to see how changing a single weight or preference shifts the output.

### Non-Intended Use
This system should **not** be used to make real music recommendations for real users. It has no access to listening history, it cannot personalize over time, it treats every user the same way, and its 18-song catalog is too small to produce meaningful variety. It should not be used in any context where recommendations affect a person's experience of a product or platform. It also should not be used to draw conclusions about what genres or moods "belong together" — the associations it makes are based only on manually assigned labels, not any analysis of the actual audio.

---

## 3. How the Model Works

Think of the system as a judge at a talent show. Each song in the catalog walks across the stage, and the judge awards points in three rounds:

- **Genre round** — if the song's genre matches what the user said they like, it gets 2 points. This is the most important round.
- **Mood round** — if the song's mood matches, it gets 1 point.
- **Energy round** — the closer the song's energy level is to the user's target, the closer to 1 full point it receives. A perfect match earns 1.0; a song on the complete opposite end of the scale earns 0.0.

After every song is judged, they are ranked from highest score to lowest, and the top five are recommended.

---

## 4. Data

The catalog contains **18 songs** stored in `data/songs.csv`. The original 10-song starter set was expanded to add 8 new songs covering genres not previously represented:

| New genre | Song title |
|---|---|
| hip-hop | Block Party Anthem |
| country | Porch Swing Evenings |
| classical | Adagio for Quiet Rooms |
| metal | Ironclad |
| R&B | Slow Burn |
| folk | Mountain Trail Song |
| EDM | Festival Drop |
| blues | Rainy Monday Blues |

Each song has seven features: genre, mood, energy (0–1), tempo BPM, valence (positivity, 0–1), danceability (0–1), and acousticness (0–1). Only genre, mood, and energy are used in scoring. The dataset reflects a broad but still limited slice of musical taste — primarily English-language Western genres.

---

## 5. Strengths

- **Well-represented genres score cleanly.** Profiles for lofi, pop, and rock all produced results that matched intuition. The Chill Lofi profile returned all three lofi tracks at the top, with the closest-energy song scoring a perfect 4.0.
- **Transparent reasoning.** Every recommendation includes a plain-English explanation of exactly which criteria contributed points, making the decision auditable.
- **Fast and dependency-free.** The system needs only Python's standard library; no external packages or models are required.

---

## 6. Limitations and Bias

**The genre weight creates a "genre gravity" problem.** Because a genre match is worth 2.0 points and a perfect energy match is worth at most 1.0, a song that matches the genre but is completely wrong in every other way will almost always beat a song that matches mood and energy perfectly but comes from a different genre.

The adversarial test exposed this clearly. A user who asked for *jazz + euphoric + high energy* received **Coffee Shop Stories** — a slow, relaxed café jazz piece — as their top recommendation, simply because its genre tag matched. The song scored 2.47 (genre +2.0, energy +0.47) while the actually energetic and euphoric **Festival Drop** scored only 1.95. The system chose a song the user would likely skip immediately.

Additional limitations:
- The system only uses three of the seven available features. Valence, danceability, acousticness, and tempo are ignored in scoring, even though they can strongly affect whether a song "fits the vibe."
- All users are forced into a single mood label. A user who wants "mostly happy but a little melancholic" cannot express that nuance.
- The dataset is small (18 songs). Many genres have only one representative, so if a user's genre isn't in the catalog, their entire 2-point bonus disappears and the recommendations fall back to energy-only sorting.
- The system has no memory or personalization. It cannot learn that a user kept skipping the songs it recommended.

---

## 7. Evaluation

Four user profiles were tested:

### Profile 1 — High-Energy Pop (`genre=pop, mood=happy, energy=0.9`)
```
Sunrise City [pop / happy]       Score: 3.92
Gym Hero [pop / intense]         Score: 2.97
Rooftop Lights [indie pop/happy] Score: 1.86
Storm Runner [rock / intense]    Score: 0.99
Block Party Anthem [hip-hop]     Score: 0.97
```
**Observation:** Results felt right. Sunrise City (pop/happy, energy 0.82) is a near-perfect match. Gym Hero appeared second despite its mood being "intense" rather than "happy" — this is the genre weight dominating mood. A human listener who only wants *happy* pop would likely skip Gym Hero.

### Profile 2 — Chill Lofi (`genre=lofi, mood=chill, energy=0.35`)
```
Library Rain [lofi / chill]      Score: 4.00  ← perfect score
Midnight Coding [lofi / chill]   Score: 3.93
Focus Flow [lofi / focused]      Score: 2.95
Spacewalk Thoughts [ambient]     Score: 1.93
Coffee Shop Stories [jazz]       Score: 0.98
```
**Observation:** The cleanest result of all four profiles. When the dataset has good coverage of the requested genre, the system works exactly as intended. Library Rain earned a perfect 4.0 — genre, mood, and energy all matched.

### Profile 3 — Deep Intense Rock (`genre=rock, mood=intense, energy=0.95`)
```
Storm Runner [rock / intense]    Score: 3.96
Ironclad [metal / intense]       Score: 1.99
Gym Hero [pop / intense]         Score: 1.98
Festival Drop [edm / euphoric]   Score: 1.00
Block Party Anthem [hip-hop]     Score: 0.92
```
**Observation:** Storm Runner is the only rock song in the catalog, so it wins by a large margin. Ironclad (metal) and Gym Hero (pop) almost tied for second, both scoring ~1.99 via mood + energy — the system correctly identified that metal is a closer neighbor to rock than pop is, but by a margin of only 0.01. Surprising: an "intense pop" song ended up ahead of every non-intense song regardless of genre.

### Profile 4 (Adversarial) — Jazz + Euphoric + High Energy (`genre=jazz, mood=euphoric, energy=0.9`)
```
Coffee Shop Stories [jazz/relaxed] Score: 2.47  ← BIAS
Festival Drop [edm / euphoric]     Score: 1.95
Storm Runner [rock / intense]      Score: 0.99
Gym Hero [pop / intense]           Score: 0.97
Block Party Anthem [hip-hop]       Score: 0.97
```
**Observation:** This is the most revealing result. Coffee Shop Stories is a 90 BPM slow jazz café track — essentially the opposite of what a "high-energy euphoric" listener wants. Yet it ranked first because the 2.0-point genre bonus outweighed its terrible energy match (0.47 points). Festival Drop, which is genuinely euphoric and high-energy, lost to it by 0.52 points. The genre weight is too powerful when genre and energy conflict.

### Experiment — Weight shift (genre ×0.5, energy ×2)
```
Festival Drop [edm / euphoric]     Score: 2.90  ← now correct
Storm Runner [rock / intense]      Score: 1.98
Gym Hero [pop / intense]           Score: 1.94
Coffee Shop Stories [jazz/relaxed] Score: 1.94  ← demoted to 4th
Block Party Anthem [hip-hop]       Score: 1.94
```
**Finding:** Halving the genre weight and doubling the energy weight fixed the adversarial profile — Festival Drop moved from 2nd to 1st and Coffee Shop Stories fell to 4th. The trade-off is that the "correct" profiles (lofi, pop, rock) would lose some precision because genre now matters less than energy throughout the entire system.

---

## 8. Future Work

- **Use all seven features.** Valence could replace or supplement mood (it is already a 0–1 number, so it fits naturally into the energy-similarity formula). Acousticness would help differentiate electric vs. acoustic guitar rock.
- **Per-feature weight tuning.** Rather than one fixed set of weights, allow the user to declare which features matter most to them (e.g., "I care about energy more than genre").
- **Diversity penalty.** Currently the top-5 can include four lofi songs if a lofi user has three lofi songs in the catalog. Add a small penalty for returning more than two songs by the same genre to encourage variety.
- **Negative preferences.** Let users say "no metal" or "never sad mood" to hard-filter the list before scoring.
- **Larger catalog.** With 18 songs, some genres have only one representative. A 200-song catalog would allow the energy and mood dimensions to do more meaningful work.

---

## 9. Personal Reflection

### Biggest learning moment
The most surprising moment was seeing **Coffee Shop Stories** rank first for a user who asked for high-energy euphoric jazz. The algorithm did exactly what it was told — genre is worth 2 points, so the only jazz song won. But the result felt completely wrong. That gap between "the math is correct" and "the result is useful" is something I hadn't expected to feel so clearly from such a small program. It made the abstract idea of algorithmic bias concrete: bias doesn't require bad intentions, just a weight that favors one feature too strongly over others.

### How AI tools helped — and where I had to verify
Using AI assistance to generate the initial scoring logic and boilerplate was genuinely faster than writing it from scratch. The suggestions for the energy-similarity formula (`1.0 - abs(song_energy - user_energy)`) and the `sorted()` pattern were accurate and idiomatic. Where I had to slow down and double-check was the **weight values themselves** — the AI suggested plausible-sounding numbers, but I had to actually run the adversarial profile to discover that a genre weight of 2.0 would dominate the entire scoring system in a bad way. The code was correct; the design decision buried in it was not. That is a pattern worth remembering: AI tools are good at structure and syntax, but only running the system on real inputs reveals whether the logic actually does what you intended.

### What surprised me about simple algorithms "feeling" like recommendations
I expected a three-rule scoring function to feel obviously mechanical and easy to see through. What surprised me is how much it *doesn't* feel that way when the top result matches your intuition. When the Chill Lofi profile returned Library Rain with a perfect 4.0, it felt satisfying — like the system understood the user. That feeling was an illusion produced by three integer comparisons and one subtraction. It made me understand why users trust recommendation systems even when those systems are doing something quite simple under the hood. The system doesn't need to be complex to feel smart; it just needs to be right often enough that you stop questioning it.

### What I would try next
If I kept developing this, the first thing I would change is replacing the binary genre-match (either 2 points or 0) with a **genre similarity table** — so that "metal" and "rock" are treated as closer neighbors than "metal" and "lofi." The second thing would be adding **valence** to the scoring formula, because positivity/negativity is independent of energy and catches cases like "calm but sad" versus "calm but happy." Both changes would make the system more nuanced without adding significant complexity.
