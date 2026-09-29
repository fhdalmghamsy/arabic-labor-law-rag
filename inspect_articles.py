import json
from collections import Counter

with open("docs/articles.json", encoding="utf-8") as f:
    articles = json.load(f)

titles = [a["article"] for a in articles]
print(f"Total: {len(articles)}\n")

dups = [t for t, c in Counter(titles).items() if c > 1]
print("Duplicate titles:", dups, "\n")

print("Suspicious entries (odd title or very short text):")
for i, a in enumerate(articles):
    if len(a["article"]) > 45 or len(a["text"]) < 40:
        print(f"{i} | {a['article']} | {a['text'][:100]}")