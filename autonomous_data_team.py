from memory_manager import save_message, load_memory
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import operator
import os

from tools_database import query_database, get_schema

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"))


# ─── STATE BERSAMA ───
class TeamState(TypedDict):
    pertanyaan: str
    messages: Annotated[list, operator.add]
    data_mentah: str
    analisis: str
    kritik: str
    laporan: str
    status: str


# ─── HELPER: KONVERSI MEMORI DB → LANGCHAIN MESSAGES ───
def build_history(agent_name: str, limit: int = 6) -> list:
    rows = load_memory(agent_name, limit=limit)
    msgs = []
    for r in rows:
        if r["role"] == "user":
            msgs.append(HumanMessage(content=r["content"]))
        else:
            msgs.append(AIMessage(content=r["content"]))
    return msgs


# ─── ENGINEER AGENT ───
llm_engineer = llm.bind_tools([query_database, get_schema])


def engineer_node(state: TeamState):
    print("\n⚙️  Engineer: mengambil data dari database...")

    history = build_history("engineer", limit=3)

    system = SystemMessage(
        content="""Kamu adalah Engineer Agent.
    Tugasmu HANYA mengambil data dari database menggunakan tools.
    Jangan analisis — cukup ambil data yang relevan dengan pertanyaan.
    Setelah dapat data, kembalikan data mentahnya saja.

    PENTING — Database menggunakan Microsoft SQL Server (T-SQL), bukan MySQL.
    Gunakan syntax T-SQL yang benar:
    - Tanggal hari ini: CAST(GETDATE() AS DATE) bukan CURDATE()
    - Bulan ini: MONTH(GETDATE()) bukan MONTH(NOW())
    - Limit hasil: SELECT TOP 10 bukan LIMIT 10
    - Jangan gunakan backtick (`), gunakan tanda kurung siku [] jika perlu escape nama kolom."""
    )

    messages = [system] + history + [HumanMessage(content=state["pertanyaan"])]
    response = llm_engineer.invoke(messages)

    print(f"🔧 tool_calls: {response.tool_calls}")

    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_node = ToolNode([query_database, get_schema])
        tool_result = tool_node.invoke({"messages": [response]})
        data = tool_result["messages"][-1].content
        print(f"📦 data dari tool:\n{data[:300]}")
    else:
        data = response.content
        print(f"⚠️  Tool tidak dipanggil! LLM menjawab sendiri:\n{data[:300]}")

    save_message("engineer", "user", state["pertanyaan"])
    save_message("engineer", "assistant", data)

    print(f"📊 Engineer selesai — data didapat!")
    return {"data_mentah": data, "status": "engineer_done"}


# ─── ANALYST AGENT ───
def analyst_node(state: TeamState):
    print("\n🔍 Analyst: menganalisis data...")

    history = build_history("analyst", limit=6)

    system = SystemMessage(
        content="""Kamu adalah Analyst Agent.
    Tugasmu menganalisis data mentah yang diberikan Engineer.
    Temukan pola, trend, dan insight menarik dari data.
    Berikan analisis yang mendalam dalam bahasa Indonesia."""
    )

    prompt = f"""
    Pertanyaan: {state["pertanyaan"]}

    Data mentah dari Engineer:
    {state["data_mentah"]}

    Analisis data ini secara mendalam!
    """

    messages = [system] + history + [HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    save_message("analyst", "user", state["pertanyaan"])
    save_message("analyst", "assistant", response.content)

    print("💡 Analyst selesai — analisis dibuat!")
    return {"analisis": response.content, "status": "analyst_done"}


# ─── CRITIC AGENT ───
def critic_node(state: TeamState):
    print("\n🧐 Critic: memvalidasi analisis...")

    history = build_history("critic", limit=6)

    system = SystemMessage(
        content="""Kamu adalah Critic Agent.
    Tugasmu memvalidasi analisis dari Analyst.
    Cek apakah analisis sudah akurat, logis, dan menjawab pertanyaan.
    Jika ada yang kurang atau salah, sebutkan.
    Berikan verdict: VALID atau PERLU REVISI beserta alasannya."""
    )

    prompt = f"""
    Pertanyaan awal: {state["pertanyaan"]}
    Data mentah: {state["data_mentah"]}
    Analisis Analyst: {state["analisis"]}

    Validasi analisis ini!
    """

    messages = [system] + history + [HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    save_message("critic", "user", state["pertanyaan"])
    save_message("critic", "assistant", response.content)

    print("✅ Critic selesai — validasi selesai!")
    return {"kritik": response.content, "status": "critic_done"}


# ─── REPORTER AGENT ───
def reporter_node(state: TeamState):
    print("\n📝 Reporter: menulis laporan akhir...")

    history = build_history("reporter", limit=6)

    system = SystemMessage(
        content="""Kamu adalah Reporter Agent.
    Tugasmu menulis laporan akhir yang rapi dan profesional.
    Gabungkan data, analisis, dan validasi menjadi laporan yang mudah dibaca.
    Format laporan dengan jelas menggunakan poin-poin."""
    )

    prompt = f"""
    Pertanyaan: {state["pertanyaan"]}
    Data: {state["data_mentah"]}
    Analisis: {state["analisis"]}
    Validasi: {state["kritik"]}

    Tulis laporan akhir yang profesional!
    """

    messages = [system] + history + [HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    save_message("reporter", "user", state["pertanyaan"])
    save_message("reporter", "assistant", response.content)

    print("📄 Reporter selesai — laporan siap!")
    return {"laporan": response.content, "status": "done"}


# ─── ROUTING ───
def routing(state: TeamState):
    status = state.get("status", "")
    if status == "engineer_done":
        return "ke_analyst"
    elif status == "analyst_done":
        return "ke_critic"
    elif status == "critic_done":
        return "ke_reporter"
    else:
        return "selesai"


# ─── BANGUN GRAPH ───
graph = StateGraph(TeamState)

graph.add_node("engineer", engineer_node)
graph.add_node("analyst", analyst_node)
graph.add_node("critic", critic_node)
graph.add_node("reporter", reporter_node)

graph.add_conditional_edges("engineer", routing, {"ke_analyst": "analyst"})
graph.add_conditional_edges("analyst", routing, {"ke_critic": "critic"})
graph.add_conditional_edges("critic", routing, {"ke_reporter": "reporter"})
graph.add_conditional_edges("reporter", routing, {"selesai": END})

graph.set_entry_point("engineer")
app = graph.compile()


def run_pipeline(pertanyaan: str) -> dict:
    return app.invoke(
        {
            "pertanyaan": pertanyaan,
            "messages": [],
            "data_mentah": "",
            "analisis": "",
            "kritik": "",
            "laporan": "",
            "status": "",
        }
    )


if __name__ == "__main__":
    print("🚀 Autonomous Data Team siap!\n")
    print("=" * 50)

    pertanyaan = "Dari analisis sebelumnya, produk mana yang paling laku dan bagaimana tren penjualannya per bulan?"

    print(f"❓ Pertanyaan: {pertanyaan}\n")

    result = run_pipeline(pertanyaan)

    print("\n" + "=" * 50)
    print("📄 LAPORAN AKHIR:")
    print("=" * 50)
    print(result["laporan"])
