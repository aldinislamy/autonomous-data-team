import pyodbc
from datetime import datetime


# ─── KONEKSI ───
def get_conn():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=DESKTOP-7GEQ92D;"
        "DATABASE=latihan_langgraph;"
        "Trusted_Connection=yes;"
    )


# ─── SIMPAN PESAN ───
def save_message(agent_name, role, content):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO agent_memory (agent_name, role, content)
        VALUES (?, ?, ?)
    """,
        agent_name,
        role,
        content,
    )
    conn.commit()
    conn.close()


# ─── LOAD MEMORI ───
def load_memory(agent_name, limit=10):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT TOP (?) role, content
        FROM agent_memory
        WHERE agent_name = ?
        ORDER BY created_at DESC
    """,
        limit,
        agent_name,
    )
    rows = cursor.fetchall()
    conn.close()
    # Balik urutan agar kronologis
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


# ─── HAPUS MEMORI ───
def clear_memory(agent_name=None):
    conn = get_conn()
    cursor = conn.cursor()
    if agent_name:
        cursor.execute("DELETE FROM agent_memory WHERE agent_name = ?", agent_name)
    else:
        cursor.execute("DELETE FROM agent_memory")
    conn.commit()
    conn.close()


# ─── TEST ───
if __name__ == "__main__":
    print("🧪 Test memory manager...\n")

    # Simpan beberapa pesan
    save_message("engineer", "user", "Ambil data sales bulan Januari")
    save_message(
        "engineer", "assistant", "Data berhasil diambil: 2 transaksi senilai 52 juta"
    )
    save_message("analyst", "user", "Analisis data sales")
    save_message(
        "analyst", "assistant", "Revenue tertinggi di Januari dengan total 52 juta"
    )

    # Load memori
    print("📚 Memori Engineer:")
    for m in load_memory("engineer"):
        print(f"  [{m['role']}] {m['content']}")

    print("\n📚 Memori Analyst:")
    for m in load_memory("analyst"):
        print(f"  [{m['role']}] {m['content']}")

    print("\n✅ Memory manager berjalan!")
