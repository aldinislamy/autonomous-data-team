from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import operator
import os

# Import tools yang sudah kita buat tadi
from tools_database import query_database, get_schema

# Load API Key dari .env
load_dotenv()

# ─── OTAK AGENT: Groq LLM ───
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

# Kasih tau LLM tentang tools yang tersedia
llm_dengan_tools = llm.bind_tools([query_database, get_schema])


# ─── STATE ───
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]


# ─── NODE 1: Agent (Otak) ───
def agent_node(state: AgentState):
    print("🧠 Agent: berpikir...")

    system = SystemMessage(
        content="""Kamu adalah data analyst expert. 
    Kamu punya akses ke database sales.
    Jawab pertanyaan user berdasarkan data nyata dari database.
    Gunakan tools yang tersedia untuk query data.
    Jawab dalam bahasa Indonesia."""
    )

    response = llm_dengan_tools.invoke([system] + state["messages"])
    return {"messages": [response]}


# ─── NODE 2: Tools (Eksekutor) ───
tool_node = ToolNode([query_database, get_schema])


# ─── ROUTING: Agent mau pakai tool atau sudah selesai? ───
def routing(state: AgentState):
    last_message = state["messages"][-1]

    # Kalau Agent minta pakai tool
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"🔧 Agent memilih tool: {last_message.tool_calls[0]['name']}")
        return "pakai_tool"

    # Kalau Agent sudah punya jawaban
    print("✅ Agent sudah punya jawaban!")
    return "selesai"


# ─── BANGUN GRAPH ───
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_conditional_edges("agent", routing, {"pakai_tool": "tools", "selesai": END})

# Setelah tool selesai → balik ke agent untuk simpulkan
graph.add_edge("tools", "agent")

graph.set_entry_point("agent")
app = graph.compile()

# ─── JALANKAN! ───
print("🚀 Agent SQL Server siap!\n")
print("=" * 50)

pertanyaan = "Bulan mana yang paling tinggi revenue nya dan berapa totalnya?"

print(f"❓ Pertanyaan: {pertanyaan}\n")

result = app.invoke({"messages": [HumanMessage(content=pertanyaan)]})

# Ambil jawaban terakhir
jawaban = result["messages"][-1].content
print(f"\n💬 Jawaban Agent:\n{jawaban}")
