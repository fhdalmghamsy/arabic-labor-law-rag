import json
import os
import random
import time
from rag import generate

with open("docs/articles.json", encoding="utf-8") as f:
    articles = json.load(f)

candidates = [a for a in articles if len(a["text"]) > 150]
random.seed(42)
sample = random.sample(candidates, 40)

# Resume from previous progress if the file exists
path = "eval_set.json"
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        eval_set = json.load(f)
else:
    eval_set = []
done = {item["article"] for item in eval_set}
print(f"Already have {len(eval_set)} questions\n")

for i, a in enumerate(sample, 1):
    if a["article"] in done:
        continue

    prompt = f"""اقرأ المادة التالية من نظام العمل السعودي، واكتب سؤالاً واحداً قد يطرحه موظف عادي بلهجة سعودية بسيطة، بحيث تكون إجابته موجودة في هذه المادة.
اكتب السؤال فقط دون أي شرح.

{a['article']}: {a['text']}"""

    question = generate(prompt)
    if question is None:
        print("\nAll models are out of quota. Progress is saved — run again later.")
        break

    eval_set.append({"question": question.strip(), "article": a["article"]})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(eval_set, f, ensure_ascii=False, indent=2)
    print(f"{i}/40 → {question.strip()}")
    time.sleep(4)

print(f"\nTotal saved: {len(eval_set)} questions")