import json
import os
import time
from rag import collection, rewrite_query

with open("eval_set.json", encoding="utf-8") as f:
    eval_set = json.load(f)

# Cache rewrites so we never spend quota twice on the same question
cache_path = "rewrites.json"
if os.path.exists(cache_path):
    with open(cache_path, encoding="utf-8") as f:
        rewrites = json.load(f)
else:
    rewrites = {}

for i, item in enumerate(eval_set, 1):
    q = item["question"]
    if q in rewrites:
        continue
    rewritten = rewrite_query(q)
    if rewritten == q:
        print("\nAll models are out of quota. Progress saved — run again later.")
        break
    rewrites[q] = rewritten
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(rewrites, f, ensure_ascii=False, indent=2)
    print(f"Rewritten {i}/{len(eval_set)}")
    time.sleep(4)

if len(rewrites) < len(eval_set):
    print(f"Have {len(rewrites)}/{len(eval_set)} rewrites. Run again later to finish.")
    raise SystemExit


def search_titles(query, k=10):
    res = collection.query(query_texts=["query: " + query], n_results=k)
    return [m["article"] for m in res["metadatas"][0]]


def rank_in(titles, target):
    return titles.index(target) + 1 if target in titles else None


def fuse(list_a, list_b, k=6, c=60):
    # Reciprocal Rank Fusion: reward articles ranked high in either list
    scores = {}
    for titles in (list_a, list_b):
        for r, t in enumerate(titles, 1):
            scores[t] = scores.get(t, 0) + 1 / (c + r)
    return sorted(scores, key=scores.get, reverse=True)[:k]


def summarize(ranks):
    n = len(ranks)
    hit1 = sum(1 for r in ranks if r == 1) / n
    hit3 = sum(1 for r in ranks if r and r <= 3) / n
    hit6 = sum(1 for r in ranks if r) / n
    mrr = sum(1 / r for r in ranks if r) / n
    return hit1, hit3, hit6, mrr


base_ranks, rw_ranks, fused_ranks, misses = [], [], [], []
for item in eval_set:
    q, target = item["question"], item["article"]
    a = search_titles(q)
    b = search_titles(rewrites[q])

    base_ranks.append(rank_in(a[:6], target))
    rw_ranks.append(rank_in(b[:6], target))
    f = rank_in(fuse(a, b), target)
    fused_ranks.append(f)
    if f is None:
        misses.append((q, rewrites[q], target))

print("\n" + "=" * 62)
print(f"{'':<22}{'Hit@1':>9}{'Hit@3':>9}{'Hit@6':>9}{'MRR':>9}")
for name, ranks in [
    ("Original question", base_ranks),
    ("Rewritten question", rw_ranks),
    ("Fusion (both)", fused_ranks),
]:
    h1, h3, h6, mrr = summarize(ranks)
    print(f"{name:<22}{h1:>9.0%}{h3:>9.0%}{h6:>9.0%}{mrr:>9.2f}")
print("=" * 62)

print(f"\nMissed with fusion ({len(misses)}):")
for q, rw, target in misses:
    print(f"- Q: {q}\n  Rewritten: {rw}\n  Expected: {target}\n")