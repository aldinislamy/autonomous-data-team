# Autonomous Data Team 🤖

Sistem multi-agent AI yang bekerja secara otomatis untuk mengquery data, 
menganalisis, memvalidasi, dan menghasilkan laporan bisnis — cukup input 
satu pertanyaan, laporan lengkap langsung tersedia.

## Tech Stack

- **LangGraph** — multi-agent framework
- **Groq API** — LLM inference (model: openai/gpt-oss-120b)
- **SQL Server** — database + persistent memory (tabel agent_memory)
- **pgvector + Supabase** — vector database untuk semantic search
- **Streamlit** — web interface
- **Python** — bahasa utama

## Arsitektur

Engineer → Analyst → Critic → Reporter
   ↑                    |
   └────────────────────┘
      feedback loop jika Critic belum puas

- **Engineer Agent** — query ke SQL Server, ambil data
- **Analyst Agent** — analisis pola dan insight
- **Critic Agent** — validasi kesimpulan, trigger loop jika perlu
- **Reporter Agent** — hasilkan laporan akhir dalam Markdown

## Setup

1. Clone repo ini
2. Install dependencies:
   pip install langgraph langchain-groq pyodbc supabase streamlit sentence-transformers
3. Buat file `.env`:
   GROQ_API_KEY=your_key
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
4. Jalankan via terminal:
   python autonomous_data_team.py
5. Atau jalankan via web interface:
   streamlit run app.py
