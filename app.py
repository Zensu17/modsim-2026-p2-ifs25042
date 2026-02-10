import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- KONFIGURASI SKOR & KATEGORI ---
SCORE_MAP = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
INV_SCORE_MAP = {v: k for k, v in SCORE_MAP.items()}

def get_category(val):
    if val in ['SS', 'S']: return 'Positif'
    elif val == 'CS': return 'Netral'
    elif val in ['CTS', 'TS', 'STS']: return 'Negatif'
    return 'Unknown'

# --- LOAD DATA ---
@st.cache_data
def load_data():
    file_name = 'data_kuesioner.xlsx'
    try:
        df = pd.read_excel(file_name, sheet_name='Kuesioner')
        try:
            df_q = pd.read_excel(file_name, sheet_name='Pertanyaan')
        except:
            df_q = pd.DataFrame()
        return df, df_q
    except Exception as e:
        return None, None

# --- MAIN APP ---
st.set_page_config(page_title="Analisis Kuesioner Pro", layout="wide")

df_raw, df_pertanyaan = load_data()

if df_raw is None:
    st.error("File 'data_kuesioner.xlsx' tidak ditemukan. Pastikan file berada di folder yang sama.")
    st.stop()

# Persiapan Data
q_cols = [col for col in df_raw.columns if col.startswith('Q')]
df_data = df_raw[q_cols]
df_numeric = df_data.replace(SCORE_MAP)

# --- SIDEBAR ---
st.sidebar.title("🎮 Kontrol Dashboard")
menu = st.sidebar.radio("Pilih Menu:", [
    "Ringkasan Data", 
    "Analisis Distribusi & Kategori", 
    "Analisis Per Pertanyaan",
    "Analisis Hubungan (Korelasi)",
    "Quality Check & Filter"
])

# --- GLOBAL METRICS ---
all_responses = pd.Series(df_data.values.flatten()).dropna()
dist_counts = all_responses.value_counts().reindex(['SS','S','CS','CTS','TS','STS']).fillna(0)
avg_per_q = df_numeric.mean()

# --- MENU 1: RINGKASAN DATA (FITUR LAMA + TOP/BOTTOM) ---
if menu == "Ringkasan Data":
    st.title("🚀 Dashboard Analisis Hasil Kuesioner")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Responden", len(df_raw))
    col2.metric("Total Jawaban", len(all_responses))
    col3.metric("Skala Terbanyak", dist_counts.idxmax())
    col4.metric("Rata-rata Global", f"{df_numeric.mean().mean():.2f}")

    st.markdown("---")
    
    # Fitur Baru: Top & Bottom Performer
    c_top, c_bot = st.columns(2)
    with c_top:
        st.success(f"✅ **Pertanyaan Tertinggi:** {avg_per_q.idxmax()} ({avg_per_q.max():.2f})")
    with c_bot:
        st.error(f"⚠️ **Pertanyaan Terendah:** {avg_per_q.idxmin()} ({avg_per_q.min():.2f})")

    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("📊 Distribusi Jawaban")
        fig1 = px.bar(x=dist_counts.index, y=dist_counts.values, color=dist_counts.index,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)
    with c_right:
        st.subheader("🍕 Proporsi Jawaban")
        fig2 = px.pie(names=dist_counts.index, values=dist_counts.values, hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig2, use_container_width=True)

# --- MENU 2: KATEGORI SENTIMEN (FITUR LAMA) ---
elif menu == "Analisis Distribusi & Kategori":
    st.subheader("🎭 Distribusi Kategori Jawaban")
    cat_data = all_responses.apply(get_category).value_counts().reindex(['Positif', 'Netral', 'Negatif'])
    
    col_cat1, col_cat2 = st.columns([1, 2])
    with col_cat1:
        st.write(cat_data)
    with col_cat2:
        fig3 = px.bar(x=cat_data.index, y=cat_data.values, color=cat_data.index,
                     color_discrete_map={'Positif':'#2ecc71', 'Netral':'#f1c40f', 'Negatif':'#e74c3c'},
                     text=cat_data.values)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Rata-rata Skor per Pertanyaan")
    fig4 = px.bar(x=avg_per_q.sort_values(ascending=False).index, y=avg_per_q.sort_values(ascending=False).values,
                 color=avg_per_q.sort_values(ascending=False).values, color_continuous_scale='RdYlGn')
    st.plotly_chart(fig4, use_container_width=True)

# --- MENU 3: PER PERTANYAAN (FITUR LAMA + RADAR) ---
elif menu == "Analisis Per Pertanyaan":
    st.subheader("📚 Sebaran Jawaban per Pertanyaan")
    stacked_list = []
    for q in q_cols:
        counts = df_data[q].value_counts().reindex(['SS','S','CS','CTS','TS','STS']).fillna(0)
        for skala, val in counts.items():
            stacked_list.append({'Pertanyaan': q, 'Skala': skala, 'Jumlah': val})
    
    df_stacked = pd.DataFrame(stacked_list)
    fig5 = px.bar(df_stacked, x="Pertanyaan", y="Jumlah", color="Skala", barmode="stack")
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("🕸️ Radar Chart: Profil Kualitas")
    fig6 = go.Figure(data=go.Scatterpolar(r=avg_per_q.values, theta=avg_per_q.index, fill='toself', line_color='teal'))
    fig6.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])))
    st.plotly_chart(fig6, use_container_width=True)

# --- MENU 4: KORELASI (FITUR BARU) ---
elif menu == "Analisis Hubungan (Korelasi)":
    st.subheader("🔗 Heatmap Korelasi Antar Pertanyaan")
    st.markdown("Melihat apakah jawaban pada pertanyaan tertentu cenderung searah dengan pertanyaan lain.")
    corr = df_numeric.corr()
    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
    st.plotly_chart(fig_corr, use_container_width=True)

# --- MENU 5: QUALITY CHECK (FITUR BARU) ---
elif menu == "Quality Check & Filter":
    st.subheader("🧐 Deteksi Kualitas Data")
    
    # Deteksi responden yang menjawab lurus (std deviasi = 0)
    df_check = df_numeric.copy()
    df_check['Variansi'] = df_check.std(axis=1)
    outliers = df_check[df_check['Variansi'] == 0]
    
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.info(f"Jumlah responden 'Straight-Lining' (isi sama semua): {len(outliers)}")
        if not outliers.empty:
            st.dataframe(outliers)
    
    with col_q2:
        st.info("Download Summary Data")
        summary_df = avg_per_q.to_frame(name='Rata-rata Skor')
        csv = summary_df.to_csv().encode('utf-8')
        st.download_button("📥 Download Ringkasan CSV", data=csv, file_name="ringkasan_kuesioner.csv", mime="text/csv")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption(f"Sistem Analisis Kuesioner v3.0")
