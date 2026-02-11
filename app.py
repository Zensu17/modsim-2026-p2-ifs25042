import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import time  # Ditambahkan untuk jeda update jam

# --- 1. KONFIGURASI & PEMBACAAN DATA ---
st.set_page_config(page_title="NEO-ACADEMIC v1.1", layout="wide", page_icon="🎓")

# Mapping skor
SCORE_MAP = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}

@st.cache_data
def load_data():
    file_path = 'data_kuesioner.xlsx'
    try:
        df_resp = pd.read_excel(file_path, sheet_name='Kuesioner')
        df_pert = pd.read_excel(file_path, sheet_name='Pertanyaan')
        q_cols = [col for col in df_resp.columns if col.startswith('Q')]
        df_num = df_resp[q_cols].replace(SCORE_MAP)
        q_dict = dict(zip(df_pert['Kode'], df_pert['Pertanyaan']))
        return df_resp, df_num, q_dict, df_pert, q_cols
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return None, None, None, None, None

df_raw, df_num, q_map, df_pert_full, q_cols = load_data()

if df_raw is None: 
    st.stop()

# --- 2. GLOBAL CALCULATIONS ---
avg_per_q = df_num.mean()
avg_total = avg_per_q.mean() 

# --- 3. CUSTOM UI & LOGO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    * { font-family: 'Outfit', sans-serif; }
    
    .logo-container {
        display: flex; align-items: center; gap: 20px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px; border-radius: 20px; margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .logo-box {
        width: 70px; height: 70px; background: white;
        border-radius: 15px; display: flex; align-items: center;
        justify-content: center; font-size: 30px; font-weight: 900; color: #1e3c72;
    }
    .header-title { color: white; margin: 0; font-size: 32px; font-weight: 800; line-height: 1.2; }
    .stMetric { border-radius: 20px; background: rgba(30, 60, 114, 0.03); border: 1px solid rgba(30, 60, 114, 0.1); padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR & LIVE CLOCK ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><h1 style='color: #1E90FF;'>NEO-ACADEMIC</h1></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Bagian Jam Real-time
    st.write("🕒 **Waktu Sistem:**")
    clock_placeholder = st.empty() # Placeholder untuk jam agar bisa di-update tanpa refresh page
    
    st.markdown("---")
    menu = st.radio("Pilih Analisis:", [
        "📊 Ringkasan Eksekutif", 
        "🔍 Detail Pertanyaan", 
        "🌡️ Heatmap Konsistensi",
        "⚖️ Matriks Prioritas",
        "📋 Database Instrumen"
    ])
    st.markdown("---")
    st.caption("v1.1 Stable | Laguboti, Indonesia")

# --- 5. HEADER LOGO ---
st.markdown(f"""
    <div class="logo-container">
        <div class="logo-box">NA</div>
        <div>
            <p class="header-title">PUSAT INTELIJEN AKADEMIK</p>
            <p style="color: rgba(255,255,255,0.8); margin: 0;">Analisis Data Kuesioner Evaluasi Pembelajaran</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. LOGIKA MENU ---
# (Konten menu tetap sama seperti kode Anda sebelumnya)

if menu == "📊 Ringkasan Eksekutif":
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rata-rata Global", f"{avg_total:.2f}")
    m2.metric("Total Partisipan", f"{len(df_raw)}")
    m3.metric("Skor Tertinggi", f"{avg_per_q.max():.2f} ({avg_per_q.idxmax()})")
    m4.metric("Kualitas Respons", "Sangat Baik")
    st.markdown("---")
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("📊 Skor Rata-rata per Kode (Q1-Q17)")
        df_chart = avg_per_q.reset_index()
        df_chart.columns = ['Kode', 'Skor']
        fig_bar = px.bar(df_chart, x='Kode', y='Skor', color='Skor', color_continuous_scale='Blues', text_auto='.2f')
        fig_bar.update_layout(yaxis_range=[1, 6], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_r:
        st.subheader("🎯 Sebaran Jawaban")
        all_votes = pd.Series(df_raw[q_cols].values.flatten()).value_counts()
        fig_pie = px.pie(names=all_votes.index, values=all_votes.values, hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_pie, use_container_width=True)

elif menu == "🔍 Detail Pertanyaan":
    st.title("🔍 Bedah Detail Pertanyaan")
    sel_q = st.selectbox("Pilih Pertanyaan:", q_cols, format_func=lambda x: f"{x}: {q_map.get(x, '')[:60]}...")
    st.info(f"**Teks Pertanyaan:** {q_map.get(sel_q)}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Radar Chart")
        fig_radar = go.Figure(data=go.Scatterpolar(r=avg_per_q, theta=q_cols, fill='toself', line_color='#1e3c72'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_radar, use_container_width=True)
    with c2:
        st.subheader("Distribusi Skor")
        dist = df_raw[sel_q].value_counts().reindex(['SS','S','CS','CTS','TS','STS']).fillna(0)
        fig_dist = px.bar(x=dist.index, y=dist.values, color=dist.values, color_continuous_scale='GnBu')
        st.plotly_chart(fig_dist, use_container_width=True)

elif menu == "🌡️ Heatmap Konsistensi":
    st.title("🌡️ Matriks Korelasi Antar Poin")
    corr = df_num.corr()
    fig_heat = px.imshow(corr, text_auto=".1f", color_continuous_scale='RdBu_r')
    st.plotly_chart(fig_heat, use_container_width=True)

elif menu == "⚖️ Matriks Prioritas":
    st.title("⚖️ Matriks Keputusan")
    priority_df = pd.DataFrame({'Kode': q_cols, 'Skor': avg_per_q.values, 'Variansi': df_num.std().values})
    fig_scatter = px.scatter(priority_df, x='Skor', y='Variansi', text='Kode', size='Skor', color='Skor', color_continuous_scale='Viridis')
    fig_scatter.add_vline(x=avg_total, line_dash="dash", line_color="red", annotation_text="Rerata Global")
    st.plotly_chart(fig_scatter, use_container_width=True)

elif menu == "📋 Database Instrumen":
    st.title("📋 Repositori Data Kuesioner")
    t1, t2 = st.tabs(["Daftar Pertanyaan Lengkap", "Data Mentah"])
    with t1: st.table(df_pert_full)
    with t2: st.dataframe(df_raw, use_container_width=True)

# --- 7. FOOTER & LIVE CLOCK ENGINE ---
st.markdown("---")
st.markdown(f"<center><small>EduInsight v1.1 Stable | Laguboti, Indonesia | {datetime.now().year}</small></center>", unsafe_allow_html=True)

# Logika untuk mengupdate jam secara real-time tanpa mengganggu interaksi user
# Menggunakan looping di akhir skrip agar tidak memblokir render komponen di atas
while True:
    t_now = datetime.now()
    clock_placeholder.markdown(f"""
        📅 {t_now.strftime('%d %B %Y')}  
        ⏰ **{t_now.strftime('%H:%M:%S')}**
    """)
    time.sleep(1)
