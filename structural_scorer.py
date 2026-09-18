"""
Structural Similarity Scorer - FIXED across all conditions (C0-C4).
Element ID එක structural score එකට INCLUDE කරන්නේ නැහැ -
මොකද target locator එකේ ID එකම persist වුණොත්, ID match එකෙන්ම
100% accuracy ලැබෙනවා (text/semantic layer එකේ value එක test කරන්නම බෑ).
ඒ නිසා tag, class, සහ position (order in DOM) විතරයි use කරන්නේ.
"""

def structural_score(target_element, target_position, candidate_element, candidate_position, max_position):
    weights = {"tag": 0.4, "class": 0.3, "position": 0.3}

    # 1. Tag match
    tag_score = 1.0 if target_element["tag"] == candidate_element["tag"] else 0.0

    # 2. Class list overlap (Jaccard similarity)
    # NOTE: structural noise එකතු කරලා තියෙන නිසා (generator.py),
    # target එකේ class list එක සහ candidate class list එක දෙකම
    # empty වෙන්නත් පුළුවන් - ඒක fair විදිහට handle කරනවා.
    t_classes = set(target_element.get("class_list", []))
    c_classes = set(candidate_element.get("class_list", []))
    if not t_classes and not c_classes:
        class_score = 1.0  # දෙකම empty නම් "match" එකක් විදිහට ගණන් ගන්නවා
    elif not t_classes or not c_classes:
        class_score = 0.0  # එකක් empty, එකක් නෑ නම් - mismatch
    else:
        union = t_classes | c_classes
        class_score = len(t_classes & c_classes) / len(union) if union else 1.0

    # 3. Position similarity (DOM ordinal position based distance)
    denom = max(max_position, 1)
    position_score = max(0.0, 1 - abs(target_position - candidate_position) / denom)

    total = (
        weights["tag"] * tag_score
        + weights["class"] * class_score
        + weights["position"] * position_score
    )
    return total