import json
import chromadb
from chromadb.utils import embedding_functions

# Load articles
with open("docs/articles.json", encoding="utf-8") as f:
    articles = json.load(f)

# Multilingual embedding model that supports Arabic
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="intfloat/multilingual-e5-small"
)

# Create a persistent database on disk
client = chromadb.PersistentClient(path="chroma_db")

# Start fresh each time we rebuild
try:
    client.delete_collection("labor_law")
except Exception:
    pass

collection = client.create_collection(name="labor_law", embedding_function=embed_fn)

# Prepare documents (title + text, tatweel removed)
docs, ids, metas = [], [], []
for i, a in enumerate(articles):
    content = f"{a['article']}: {a['text']}".replace("ـ", "")
    docs.append("passage: " + content)
    ids.append(str(i))
    metas.append({"article": a["article"]})

collection.add(documents=docs, ids=ids, metadatas=metas)
print(f"Indexed {collection.count()} articles\n")

# Quick retrieval test
question = "كم مدة الإجازة المرضية؟"
results = collection.query(query_texts=["query: " + question], n_results=3)

print(f"Question: {question}\n")
for meta, doc in zip(results["metadatas"][0], results["documents"][0]):
    print("→", meta["article"])
    print("  ", doc.replace("passage: ", "")[:200], "\n")