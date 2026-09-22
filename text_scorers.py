"""
Text Comparison Block - SWAPPABLE (the experimental variable, C0-C4).
C0 (null), C1 (Levenshtein), C2 (Simplified Sinhala lemma + Levenshtein)
දැන් implement කරලා තියෙනවා.
C3 (Sinhala embeddings), C4 (multilingual encoder) පස්සේ මේ file එකටම
function විදිහට add කරන්න පුළුවන් - same interface එකෙන්.
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


# ============================================================
# C2: Simplified Rule-Based Sinhala Lemmatizer + Levenshtein
# NOTE: මේක සම්පූර්ණ SinMorphy FST analyzer එකක් නෙවෙයි - SinMorphy
# publicly easy-install library එකක් නොවීම නිසා, common Sinhala
# verb suffixes strip කරන rule-based approximation එකක්. මේක
# proposal එකේ Section 3.4.3 (fallback conditions) එකට align වෙන
# academically-documented simplification එකක්.
# ============================================================

SINHALA_VERB_SUFFIXES = [
    "න්නට", "න්න",       # imperative / -to do
    "මට",                 # infinitive (-මට)
    "වා", "වූ",           # past tense markers
    "ීම", "ීමට",          # gerund / infinitive noun form
    "නු",                  # imperative alt form
    "ණා", "ුණා",          # past tense (intransitive)
    "ෙන්න",               # imperative alt
    "ය",                   # noun-forming suffix
]


def lemmatize_sinhala(word: str) -> str:
    """
    Common Sinhala verb suffixes ඉවත් කරලා, root එකට close කරන
    simplified lemmatizer. Longest matching suffix එක මුලින් try කරනවා
    (e.g. 'ීමට' 'මට' ට කලින් check කරනවා, partial match වළක්වන්න).
    """
    word = word.strip()
    sorted_suffixes = sorted(SINHALA_VERB_SUFFIXES, key=len, reverse=True)
    for suffix in sorted_suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            return word[: -len(suffix)]
    return word


def score_c2(target_text: str, candidate_text: str) -> float:
    """C2: SinMorphy-style lemma normalization (simplified) + Levenshtein."""
    if not target_text and not candidate_text:
        return 1.0

    # Multi-word phrases නම්, අන්තිම වචනය (verb එක සාමාන්‍යයෙන් අන්තිමට) lemmatize කරනවා
    target_words = target_text.split()
    candidate_words = candidate_text.split()

    if target_words:
        target_words[-1] = lemmatize_sinhala(target_words[-1])
    if candidate_words:
        candidate_words[-1] = lemmatize_sinhala(candidate_words[-1])

    lemma_target = " ".join(target_words)
    lemma_candidate = " ".join(candidate_words)

    distance = _levenshtein_distance(lemma_target, lemma_candidate)
    max_len = max(len(lemma_target), len(lemma_candidate))
    return 1 - (distance / max_len) if max_len > 0 else 1.0


# C3, C4 මෙතනට පස්සේ add කරන්න (Sinhala embeddings, multilingual encoder)

TEXT_SCORERS = {
    "C0": score_c0,
    "C1": score_c1,
    "C2": score_c2,
}