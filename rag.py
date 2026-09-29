import os
import json
import time
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from google import genai

load_dotenv()
llm = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="intfloat/multilingual-e5-small"
)
db = chromadb.PersistentClient(path="chroma_db")
collection = db.get_or_create_collection(name="labor_law", embedding_function=embed_fn)

# Build the index on first run (e.g. on a fresh server)
if collection.count() == 0:
    with open("docs/articles.json", encoding="utf-8") as f:
        articles = json.load(f)
    collection.add(
        documents=["passage: " + f"{a['article']}: {a['text']}".replace("ـ", "") for a in articles],
        ids=[str(i) for i in range(len(articles))],
        metadatas=[{"article": a["article"]} for a in articles],
    )

# Models to try in order; each has its own free daily quota
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]
exhausted = set()


def generate(prompt):
    for model in MODELS:
        if model in exhausted:
            continue
        for attempt in range(3):
            try:
                response = llm.models.generate_content(model=model, contents=prompt)
                return response.text
            except Exception as e:
                msg = str(e)
                if "429" in msg or "404" in msg:
                    print(f"   {model}: unavailable or quota reached, switching model")
                    exhausted.add(model)
                    break
                print(f"   {model}: server busy, retrying in 10s ({attempt + 1}/3)")
                time.sleep(10)
    return None


def rewrite_query(question):
    # Turn colloquial questions into formal legal wording
    prompt = f"""أعد صياغة السؤال التالي بلغة نظامية فصحى تشبه صياغة مواد نظام العمل السعودي.
استخدم المصطلحات النظامية، مثل: "الأجر" بدل "الراتب"، و"صاحب العمل" بدل "الشركة" أو "المدير"، و"إنهاء العقد" بدل "الفصل".
حافظ على الكلمات المحددة في السؤال كما هي، مثل: السفينة، البحار، المتدرب، الحدث.
اكتب السؤال المعاد صياغته فقط دون أي شرح.

السؤال: {question}"""
    rewritten = generate(prompt)
    return rewritten.strip() if rewritten else question


def search(query, k=10):
    res = collection.query(query_texts=["query: " + query], n_results=k)
    titles = [m["article"] for m in res["metadatas"][0]]
    docs = [d.replace("passage: ", "") for d in res["documents"][0]]
    return titles, docs


def fuse(list_a, list_b, k=6, c=60):
    # Reciprocal Rank Fusion: reward articles ranked high in either list
    scores = {}
    for titles in (list_a, list_b):
        for r, t in enumerate(titles, 1):
            scores[t] = scores.get(t, 0) + 1 / (c + r)
    return sorted(scores, key=scores.get, reverse=True)[:k]


def ask(question, k=6):
    rewritten = rewrite_query(question)
    titles_a, docs_a = search(question)
    titles_b, docs_b = search(rewritten)

    text_by_title = dict(zip(titles_a, docs_a))
    text_by_title.update(zip(titles_b, docs_b))
    top_titles = fuse(titles_a, titles_b, k=k)
    docs = [text_by_title[t] for t in top_titles]
    context = "\n\n".join(docs)

    prompt = f"""أنت مساعد قانوني متخصص في نظام العمل السعودي.
أجب عن السؤال بالاعتماد فقط على المواد النظامية أدناه.

القواعد:
- لا تستخدم أي معلومة من خارج المواد المرفقة.
- اذكر اسم المادة التي استندت إليها.
- إذا لم تجد الإجابة في المواد، قل: "لم أجد إجابة لهذا السؤال في نظام العمل."
- اكتب إجابة مختصرة وواضحة.

المواد:
{context}

السؤال: {question}
"""
    answer = generate(prompt)
    if answer is None:
        return "تعذر الاتصال بالخادم أو انتهت الحصة اليومية، حاول لاحقاً.", []

    sources = [{"article": t, "text": d} for t, d in zip(top_titles, docs)]
    return answer, sources
