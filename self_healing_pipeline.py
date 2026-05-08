from langgraph.graph import StateGraph, END
from typing import TypedDict
import random


class PipelineState(TypedDict):
    status: str
    error_message: str
    retry_count: int


# Worker Node — mengerjakan pipeline
def worker_node(state: PipelineState):
    print(
        f"⚙️  Worker: menjalankan pipeline... (percobaan ke-{state['retry_count'] + 1})"
    )

    if random.random() < 0.9:
        print("❌ Worker: ada error!")
        return {
            "status": "error",
            "error_message": "Data format tidak sesuai",
            "retry_count": state["retry_count"] + 1,
        }

    print("✅ Worker: pipeline berhasil!")
    return {"status": "ok", "error_message": "", "retry_count": state["retry_count"]}


# Validator Node — hanya UPDATE state, tidak return string
def validator_node(state: PipelineState):
    print(f"🔍 Validator: mengecek status... → {state['status']}")
    if state["status"] == "error":
        print(f"⚠️  Validator: belum OK, retry ke-{state['retry_count']}")
    else:
        print("🎉 Validator: semua OK, lanjut!")
    return state  # kembalikan state apa adanya


def notif_wa(state: PipelineState):
    print(f"📱 Mengirim notifikasi WA: pipeline gagal {state['retry_count']} kali!")
    return state


# Routing Function — ini yang memutuskan arah (TERPISAH dari validator_node)
def routing(state: PipelineState):
    if state["retry_count"] >= 3:
        return "notif"
    if state["status"] == "error":
        return "retry"
    return "done"


# Bangun Graph
graph = StateGraph(PipelineState)

graph.add_node("worker", worker_node)
graph.add_node("validator", validator_node)
graph.add_node("notif_wa", notif_wa)

graph.add_edge("worker", "validator")

# Sekarang routing function TERPISAH dari validator_node
graph.add_conditional_edges(
    "validator",
    routing,  # ← fungsi khusus untuk routing
    {"retry": "worker", "notif": "notif_wa", "done": END},
)

graph.set_entry_point("worker")
app = graph.compile()

print("🚀 Memulai Self-Healing Pipeline...\n")
result = app.invoke({"status": "start", "error_message": "", "retry_count": 0})

print(f"\n✅ Pipeline selesai! Status akhir: {result['status']}")
print(f"   Total retry: {result['retry_count']} kali")
