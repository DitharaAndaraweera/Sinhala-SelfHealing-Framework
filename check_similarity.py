"""
Mutation Catalogue එකේ තියෙන phrases වල Levenshtein similarity score
calculate කරන tool එක. දැන් catalogue එක generator.py එකෙන්ම
DIRECTLY import කරනවා - manual copy-paste නිසා catalogues out-of-sync
වීම (මීට කලින් වුණා වගේ) වළක්වන්න.
"""

from text_scorers import score_c1
from generator import mutation_catalogue   # ← Direct import, duplicate copy නෑ


def check_catalogue():
    results = []
    for original, variants in mutation_catalogue.items():
        for variant in variants:
            score = score_c1(original, variant)
            results.append((original, variant, score))

    results.sort(key=lambda x: x[2], reverse=True)

    print(f"{'Original':35s} {'Variant':35s} {'Score':>8s}  Flag")
    print("-" * 90)

    easy_count = 0
    hard_count = 0

    for original, variant, score in results:
        if score >= 0.5:
            flag = "⚠️  TOO EASY - REPLACE කරන්න"
            easy_count += 1
        elif score >= 0.3:
            flag = "🟡 Medium"
        else:
            flag = "✅ Good (genuine inflection)"
            hard_count += 1

        print(f"{original:35s} {variant:35s} {score:8.2f}  {flag}")

    print("\n" + "=" * 90)
    print(f"Total pairs: {len(results)}")
    print(f"⚠️  'Too Easy' (score >= 0.5): {easy_count}")
    print(f"✅ 'Good' (score < 0.3): {hard_count}")
    print(f"🟡 Medium (0.3 - 0.5): {len(results) - easy_count - hard_count}")


if __name__ == "__main__":
    check_catalogue()