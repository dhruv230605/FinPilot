
import os
import json
import faiss
import numpy as np
from tqdm import tqdm
from langchain_community.embeddings import HuggingFaceEmbeddings

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

#2. Paths
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "large_financial_data.json")
INDEX_DIR = "faiss_multi_output"
META_DIR = os.path.join(INDEX_DIR, "metadata")
os.makedirs(META_DIR, exist_ok=True)

#3. Load dataset
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

#4. Formatting functions
def format_transaction(t):
    return f"{t['merchant_name']} | {t['category']} | {t['amount']} {t['currency']} | {t['payment_method']} | {t['location']['city']}, {t['location']['country']} | tags: {', '.join(t.get('tags', []))}"

def format_offer(o):
    return f"{o['name']} | {o['description']} | Categories: {', '.join(o.get('applicable_categories', []))} | Spend ≥ {o.get('minimum_transaction_amount', 0)} | Partners: {', '.join(o.get('partner_merchants', []))}"

def format_asset(a):
    return f"{a['name']} | Type: {a['type']} | Issuer: {a['issuer']} | Risk: {a['risk_rating']} | Return: {a['expected_return']}% | Tenure: {a['tenure']}"

def format_strategy(s):
    return f"{s['name']} | Risk: {s['risk_profile']} | Return Target: {s['target_annual_return']}% | Allocation: {s['allocation_blueprint']}"

#5. Embedding function
def get_embedding(text):
    return embeddings.embed_query(text)

#6. Build + Save FAISS index
def process_and_index(items, formatter, identifier_key, output_prefix):
    print(f"\n[*] Processing {output_prefix}...")

    texts = [formatter(item) for item in items]
    metadata = [item[identifier_key] for item in items]

    embeddings_list = [get_embedding(text) for text in tqdm(texts)]
    matrix = np.array(embeddings_list).astype("float32")

    index = faiss.IndexFlatL2(matrix.shape[1])
    index.add(matrix)

    # Save index + metadata
    index_path = os.path.join(INDEX_DIR, f"{output_prefix}.index")
    meta_path = os.path.join(META_DIR, f"{output_prefix}.json")
    faiss.write_index(index, index_path)
    with open(meta_path, "w") as f:
        json.dump(metadata, f)

    print(f"[OK] Saved index: {index_path}")
    print(f"[OK] Saved metadata: {meta_path}")
    return index, metadata

#7. Main sections to process
sections = [
    ("transactions", data.get("transactions", []), format_transaction, "transaction_id"),
    ("offers", data.get("offers", []), format_offer, "offer_id"),
    ("financial_assets", data.get("financial_assets", []), format_asset, "asset_id"),
    ("investment_strategies", data.get("investment_strategies", []), format_strategy, "strategy_id")
]

indexes = {}

for name, items, formatter, id_key in sections:
    if items:
        idx, meta = process_and_index(items, formatter, id_key, name)
        indexes[name] = (idx, meta)
    else:
        print(f"[!] No data found for {name}")

#8. Search function
def search(category, query, k=3):
    print(f"\n[] Search in '{category}' for: \"{query}\"")
    if category not in indexes:
        print(" No index found for that category.")
        return
    idx, meta = indexes[category]
    query_vec = np.array([get_embedding(query)], dtype="float32")
    D, I = idx.search(query_vec, k)
    for i, index_id in enumerate(I[0]):
        print(f"{i+1}. ID: {meta[index_id]} | Score: {D[0][i]:.4f}")

# #9. Test searches
# search("transactions", "electronics in Delhi")
# search("offers", "cashback on dining")
# search("financial_assets", "low-risk bonds with high return")
# search("investment_strategies", "retirement plan for risk averse")
