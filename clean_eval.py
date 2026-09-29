import json

# Question numbers to remove (unrealistic: they mention article numbers directly)
remove = [20, 37]

with open("eval_set.json", encoding="utf-8") as f:
    data = json.load(f)

kept = [q for i, q in enumerate(data, 1) if i not in remove]

with open("eval_set.json", "w", encoding="utf-8") as f:
    json.dump(kept, f, ensure_ascii=False, indent=2)

print(f"Removed {len(data) - len(kept)} questions. Remaining: {len(kept)}")