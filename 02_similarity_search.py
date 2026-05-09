from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ── Query: kalimat yang TIDAK persis sama dengan data di DB
query = "database tidak bisa diakses"

print(f"🔍 Mencari error yang mirip dengan: '{query}'\n")

# ── Ubah query jadi vector
query_vector = model.encode(query).tolist()

# ── Similarity search via Supabase RPC
result = supabase.rpc(
    "match_error_logs",  # function PostgreSQL yang akan kita buat
    {
        "query_embedding": query_vector,
        "match_threshold": 0.0,  # minimum similarity score
        "match_count": 3,  # ambil top 3
    },
).execute()

print("📊 Hasil Similarity Search:")
print("─" * 50)
for item in result.data:
    print(f"Score    : {round(item['similarity'], 4)}")
    print(f"Error    : {item['error_message']}")
    print(f"Solution : {item['solution'] or '-'}")
    print(f"Source   : {item['source']} | {item['severity']}")
    print(f"Time     : {item['created_at']}")
    print("─" * 50)
