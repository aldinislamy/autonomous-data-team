from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import pyodbc
import operator


# ─── KONEKSI KE SQL SERVER ───
def get_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=DESKTOP-7GEQ92D;"
        "DATABASE=latihan_langgraph;"
        "Trusted_Connection=yes;"
    )
    return conn


# ─── TOOL 1: Query Database ───
@tool
def query_database(query: str) -> str:
    """Gunakan tool ini untuk menjalankan query SQL
    ke database dan mendapatkan data.
    Input: query SQL yang ingin dijalankan."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        hasil = cursor.fetchall()
        kolom = [col[0] for col in cursor.description]

        # Format hasil jadi teks yang mudah dibaca Agent
        output = f"Kolom: {kolom}\n"
        for row in hasil:
            output += f"{dict(zip(kolom, [str(v) for v in row]))}\n"

        conn.close()
        return output
    except Exception as e:
        return f"Error: {str(e)}"


# ─── TOOL 2: Get Schema ───
@tool
def get_schema(table_name: str) -> str:
    """Gunakan tool ini untuk melihat struktur
    kolom dari sebuah tabel di database.
    Input: nama tabel yang ingin dilihat strukturnya."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}'
        """)
        hasil = cursor.fetchall()
        output = f"Struktur tabel '{table_name}':\n"
        for row in hasil:
            output += f"  - {row[0]}: {row[1]}\n"
        conn.close()
        return output
    except Exception as e:
        return f"Error: {str(e)}"


# ─── STATE ───
class AgentState(TypedDict):
    pertanyaan: str
    hasil: Annotated[list, operator.add]
    kesimpulan: str


# ─── TOOLS LIST ───
tools = [query_database, get_schema]

# ─── TEST LANGSUNG ───
if __name__ == "__main__":
    print("🔌 Test koneksi ke SQL Server...\n")

    print("📊 Test query_database:")
    hasil = query_database.invoke("SELECT * FROM sales")
    print(hasil)

    print("\n📋 Test get_schema:")
    schema = get_schema.invoke("sales")
    print(schema)
