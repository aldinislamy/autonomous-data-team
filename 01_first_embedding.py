from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

# ── 1. Init model embedding (download otomatis ~90MB, sekali saja)
model = SentenceTransformer("all-MiniLM-L6-v2")  # output: 384 dimensi ✅

# ── 2. Contoh error log yang akan di-embed
sample_logs = [
    {
        "error_message": "Connection timeout saat query ke SQL Server setelah 30 detik",
        "source": "pipeline_etl",
        "severity": "ERROR",
    },
    {
        "error_message": "Null value ditemukan di kolom user_id yang seharusnya NOT NULL",
        "source": "data_validation",
        "severity": "WARNING",
    },
    {
        "error_message": "Memory usage mencapai 95%, proses ETL dihentikan otomatis",
        "source": "pipeline_etl",
        "severity": "CRITICAL",
    },
]

# ── 3. Buat embedding untuk setiap log
print("🔄 Membuat embedding...")
for log in sample_logs:
    # Generate vector dari teks error_message
    vector = model.encode(log["error_message"]).tolist()

    print(f"✅ '{log['error_message'][:40]}...'")
    print(f"   Vector size: {len(vector)} dimensi")
    print(f"   Preview: {[round(v, 4) for v in vector[:5]]}...\n")

print("🎉 Embedding berhasil dibuat!")

# ── 4. Koneksi Supabase
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ── 5. Insert ke tabel error_logs
print("💾 Menyimpan ke Supabase...")
for log in sample_logs:
    vector = model.encode(log["error_message"]).tolist()

    result = (
        supabase.table("error_logs")
        .insert(
            {
                "error_message": log["error_message"],
                "source": log["source"],
                "severity": log["severity"],
                "embedding": vector,  # ← inilah kolom VECTOR(384)-nya
            }
        )
        .execute()
    )

    print(f"✅ Tersimpan! ID: {result.data[0]['id']}")

print("\n🎉 Semua log berhasil disimpan ke pgvector!")
