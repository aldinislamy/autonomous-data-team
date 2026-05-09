import streamlit as st
from autonomous_data_team import run_pipeline

st.set_page_config(page_title="Autonomous Data Team", layout="wide")
st.title("🤖 Autonomous Data Team")
st.caption("Multi-agent AI untuk analisis data otomatis")

pertanyaan = st.text_area(
    "Masukkan pertanyaan analisis data:",
    placeholder="Contoh: Produk mana yang paling laku bulan ini?",
    height=100,
)

if st.button("Analisis", type="primary", disabled=not pertanyaan.strip()):
    with st.spinner("Tim AI sedang bekerja..."):
        result = run_pipeline(pertanyaan)

    st.subheader("📊 Laporan Akhir")
    st.markdown(result["laporan"])

    with st.expander("🔍 Detail Proses"):
        st.subheader("Data Mentah")
        st.text(result["data_mentah"])
        st.subheader("Analisis")
        st.markdown(result["analisis"])
        st.subheader("Kritik & Validasi")
        st.markdown(result["kritik"])
