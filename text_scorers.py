"""
Text Comparison Block - SWAPPABLE (the experimental variable, C0-C4).
දැනට C0 (null) සහ C1 (Levenshtein) විතරයි implement කරලා තියෙන්නේ.
C2 (SinMorphy lemma), C3 (Sinhala embeddings), C4 (multilingual encoder)
පස්සේ මේ file එකටම function විදිහට add කරන්න පුළුවන් - same interface එකෙන්.
"""


def _levenshtein_distance(a: str, b: str) -> int:
    """Pure-python edit distance (external library dependency නැතුව)."""
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)

    prev_row = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr_row = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr_row[j] = min(
                curr_row[j - 1] + 1,      # insertion
                prev_row[j] + 1,          # deletion
                prev_row[j - 1] + cost,   # substitution
            )
        prev_row = curr_row
    return prev_row[-1]


def score_c0(target_text: str, candidate_text: str) -> float:
    """C0: Structural-only baseline - text term එකක්ම නැහැ."""
    return 0.0


def score_c1(target_text: str, candidate_text: str) -> float:
    """C1: Normalized Levenshtein similarity (current industry practice - Similo)."""
    if not target_text and not candidate_text:
        return 1.0
    distance = _levenshtein_distance(target_text, candidate_text)
    max_len = max(len(target_text), len(candidate_text))
    return 1 - (distance / max_len) if max_len > 0 else 1.0


# C2, C3, C4 මෙතනට පස්සේ add කරන්න (SinMorphy, SinBERT/FastText, LaBSE)

TEXT_SCORERS = {
    "C0": score_c0,
    "C1": score_c1,
}