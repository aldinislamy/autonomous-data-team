# Autonomous Data Team

Agent AI yang bekerja sama untuk menganalisis data secara otomatis.

## Tech Stack
- LangGraph
- Groq API
- SQL Server
- Python

## Agents
- Engineer Agent — query database
- Analyst Agent — analisis data
- Critic Agent — validasi kesimpulan
- Reporter Agent — laporan akhir

## Setup
1. Clone repo ini
2. Install dependencies: `pip install langgraph langchain-groq pyodbc`
3. Buat file `.env` dan isi `GROQ_API_KEY=your_key`
4. Jalankan: `python autonomous_data_team.py`