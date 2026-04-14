"""
Command line runner for the Music Recommender Simulation.
Run with:  python3 -m src.main
"""

from src.recommender import load_songs, recommend_songs, score_song
from typing import Dict, List, Tuple


def print_recommendations(label: str, recs: list) -> None:
    """Print a labeled block of top-k recommendations."""
    print(f"\n{'='*55}")
    print(f" {label}")
    print(f"{'='*55}")
    for song, score, explanation in recs:
        print(f"  {song['title']} [{song['genre']} / {song['mood']}]")
        print(f"  Score: {score:.2f}  |  {explanation}")
        print()


def run_experiment(songs: list, user_prefs: Dict, label: str) -> None:
    """
    Weight-shift experiment: genre worth 1.0 (halved) and energy worth 2.0 (doubled).
    Lets us see whether energy-first ranking changes the top results.
    """
    print(f"\n{'='*55}")
    print(f" EXPERIMENT — energy x2, genre x1  |  {label}")
    print(f"{'='*55}")

    scored = []
    for song in songs:
        score = 0.0
        reasons = []

        if user_prefs.get("genre") == song.get("genre"):
            score += 1.0          # halved from 2.0
            reasons.append("genre match (+1.0)")

        if user_prefs.get("mood") == song.get("mood"):
            score += 1.0
            reasons.append("mood match (+1.0)")

        energy_sim = 1.0 - abs(float(song["energy"]) - float(user_prefs.get("energy", 0.5)))
        score += energy_sim * 2.0   # doubled
        reasons.append(f"energy similarity (+{energy_sim*2:.2f})")

        scored.append((song, score, ", ".join(reasons)))

    top5 = sorted(scored, key=lambda x: x[1], reverse=True)[:5]
    for song, score, explanation in top5:
        print(f"  {song['title']} [{song['genre']} / {song['mood']}]")
        print(f"  Score: {score:.2f}  |  {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    # ── Profile 1: High-Energy Pop ──────────────────────────────────────────
    profile_pop = {"genre": "pop", "mood": "happy", "energy": 0.9}
    print_recommendations(
        "Profile 1: High-Energy Pop  (genre=pop, mood=happy, energy=0.9)",
        recommend_songs(profile_pop, songs, k=5),
    )

    # ── Profile 2: Chill Lofi ───────────────────────────────────────────────
    profile_lofi = {"genre": "lofi", "mood": "chill", "energy": 0.35}
    print_recommendations(
        "Profile 2: Chill Lofi  (genre=lofi, mood=chill, energy=0.35)",
        recommend_songs(profile_lofi, songs, k=5),
    )

    # ── Profile 3: Deep Intense Rock ────────────────────────────────────────
    profile_rock = {"genre": "rock", "mood": "intense", "energy": 0.95}
    print_recommendations(
        "Profile 3: Deep Intense Rock  (genre=rock, mood=intense, energy=0.95)",
        recommend_songs(profile_rock, songs, k=5),
    )

    # ── Profile 4: Adversarial — Jazz + Euphoric + High Energy ──────────────
    # Jazz is almost always low-energy and relaxed in this dataset.
    # Asking for jazz + euphoric + 0.9 energy creates conflicting signals.
    profile_adversarial = {"genre": "jazz", "mood": "euphoric", "energy": 0.9}
    print_recommendations(
        "Profile 4 (Adversarial): Jazz + Euphoric + High Energy  (energy=0.9)",
        recommend_songs(profile_adversarial, songs, k=5),
    )

    # ── Step 3 Experiment: double energy weight, halve genre weight ──────────
    # Using the adversarial profile so we can see whether the bias flips.
    run_experiment(songs, profile_adversarial, "jazz + euphoric + energy=0.9")


if __name__ == "__main__":
    main()
