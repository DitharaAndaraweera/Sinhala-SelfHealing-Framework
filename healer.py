"""
Fusion + Ranking + Decline mechanism.
Structural score එකයි text score එකයි fixed weights එකෙන් combine කරලා,
candidates rank කරලා, confidence threshold එකට check කරලා heal/decline තීරණය කරනවා.
"""

from structural_scorer import structural_score


def heal(before_record, after_record, text_scorer_fn,
         structural_weight=0.5, text_weight=0.5, decline_threshold=0.3):

    before_elements = before_record["interactable_elements"]
    target_id = after_record["target_element_id"]

    # "Before" state එකේ target element එක සොයාගැනීම (ground truth source)
    target_element = next((el for el in before_elements if el["id"] == target_id), None)
    if target_element is None:
        return {"decision": "error", "reason": "target not found in before state"}

    target_position = before_elements.index(target_element)
    target_text = after_record["before_text"]   # mutation එකට කලින් තිබ්බ text එක

    candidates = after_record["interactable_elements"]
    max_position = max(len(candidates) - 1, 1)

    scored = []
    for idx, cand in enumerate(candidates):
        s_score = structural_score(target_element, target_position, cand, idx, max_position)
        t_score = text_scorer_fn(target_text, cand["visible_text"])
        fused = structural_weight * s_score + text_weight * t_score
        scored.append({
            "element": cand,
            "fused_score": fused,
            "structural_score": s_score,
            "text_score": t_score,
        })

    scored.sort(key=lambda x: x["fused_score"], reverse=True)

    if not scored or scored[0]["fused_score"] < decline_threshold:
        return {"decision": "decline", "ranked": scored, "target_id": target_id}

    return {"decision": "heal", "ranked": scored, "target_id": target_id}