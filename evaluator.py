"""
Top-1 / Top-3 accuracy evaluate කරන main script එක.
T1 සහ T2 dataset JSON files දෙකම load කරලා, එක් එක් "after" record එකකට
healer.py run කරලා, correct answer (target_element_id) එක top-1/top-3
වල තියෙනවද කියලා check කරනවා.
"""

import json
from healer import heal
from text_scorers import TEXT_SCORERS


def load_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate(dataset_path, condition="C1"):
    records = load_dataset(dataset_path)

    before_records = {r["domain"]: r for r in records if r["state"] == "before"}
    after_records = [r for r in records if r["state"] == "after"]

    text_scorer_fn = TEXT_SCORERS[condition]

    top1_correct = 0
    top3_correct = 0
    total = 0
    domain_stats = {}

    for after_record in after_records:
        domain = after_record["domain"]
        before_record = before_records.get(domain)
        if before_record is None:
            continue

        result = heal(before_record, after_record, text_scorer_fn)
        total += 1
        domain_stats.setdefault(domain, {"total": 0, "top1": 0, "top3": 0})
        domain_stats[domain]["total"] += 1

        if result["decision"] == "decline":
            continue

        ranked_ids = [c["element"]["id"] for c in result["ranked"]]
        target_id = result["target_id"]

        if ranked_ids and ranked_ids[0] == target_id:
            top1_correct += 1
            domain_stats[domain]["top1"] += 1

        if target_id in ranked_ids[:3]:
            top3_correct += 1
            domain_stats[domain]["top3"] += 1

    print(f"\n===== Dataset: {dataset_path} | Condition: {condition} =====")
    print(f"Total evaluated pairs: {total}")
    if total > 0:
        print(f"Top-1 Accuracy: {top1_correct}/{total} = {top1_correct/total*100:.1f}%")
        print(f"Top-3 Accuracy: {top3_correct}/{total} = {top3_correct/total*100:.1f}%")

    print("\n--- Domain-wise breakdown ---")
    for domain, stats in domain_stats.items():
        t = stats["total"]
        if t == 0:
            continue
        print(f"{domain:12s}  Top-1: {stats['top1']}/{t} ({stats['top1']/t*100:.1f}%)  "
              f"Top-3: {stats['top3']}/{t} ({stats['top3']/t*100:.1f}%)")

    return {"top1_accuracy": top1_correct / total if total else 0,
            "top3_accuracy": top3_correct / total if total else 0,
            "domain_stats": domain_stats}


if __name__ == "__main__":
    print("############ TIER 2 - SINHALA SYNTHETIC ############")
    for cond in ["C0", "C1", "C2"]:
        evaluate("Tier2 Synthetic/tier2_dataset.json", condition=cond)

    print("\n\n############ TIER 1 - ENGLISH BASELINE ############")
    for cond in ["C0", "C1"]:
        evaluate("Tier1 English/tier1_dataset.json", condition=cond)