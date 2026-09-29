import re
import json
import unicodedata
import pymupdf

doc = pymupdf.open("docs/labor-law.pdf")

# Step 1: extract and clean all lines
lines = []
for page in doc:
    text = unicodedata.normalize("NFKC", page.get_text())
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if re.fullmatch(r"[\d/()\sـهم\-]+", line):
            continue
        if "ىكللما" in line or "موسرلماب" in line or line.startswith("نظام العمل:") or line.startswith("( وتاريخ"):
            continue
        lines.append(line)

clean_text = re.sub(r"\s+", " ", " ".join(lines).replace("ـ", ""))

# Step 2: split into articles (a heading cannot contain a period)
parts = re.split(r"(المادة\s+[^:.]{1,60}:)", clean_text)

articles = []
for i in range(1, len(parts), 2):
    title = parts[i].rstrip(":").strip()
    title = re.sub(r'[\s"\d]+$', "", title)          # drop trailing footnote marks
    body = parts[i + 1].strip() if i + 1 < len(parts) else ""
    body = re.sub(r"^\d+\s*", "", body)              # drop leading footnote numbers

    # A cross-reference inside an article is not a new article: merge it back
    if articles and re.search(r"\s(من|في|هذا|هذه)\s", f" {title} "):
        articles[-1]["text"] += f" {title}: {body}"
        continue

    articles.append({"article": title, "text": body})

# Step 3: drop repealed articles
found = len(articles)
articles = [a for a in articles if not re.fullmatch(r"[()\s]*ملغاة[()\s]*", a["text"])]
print(f"Headings found: {found}")
print(f"Repealed removed: {found - len(articles)}")
print(f"Active articles: {len(articles)}\n")

with open("docs/articles.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

for a in articles[:3]:
    print(a["article"], "→", a["text"][:120], "\n")
print("Last:", articles[-1]["article"], "→", articles[-1]["text"][:120])