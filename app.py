import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- KONFIGURASI ---
SCORE_MAP = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}

def get_category(val):
    if val in ['SS', 'S']: return 'Positif'
    elif val == 'CS': return 'Netral'
    elif val in ['CTS', 'TS', 'STS']: return 'Negatif'
    return 'Unknown'

@st.cache_data
def load_data():
    file_name = 'data_kuesioner.xlsx'
    df = pd.read_excel(file_name, sheet_name='Kuesioner')
    try:
        df_q = pd.read_excel(file_name, sheet_name='Pertanyaan')
    except:
        df_q = pd.DataFrame()
    return df, df_q

# --- MAIN APP ---
st.set_page_config(page_title="Analisis Kuesioner Pro", layout="wide")

try:
    df_raw, df_pertanyaan = load_data()
    q_cols = [col for col in df_raw.columns if col.startswith('Q')]
    # Kolom non-pertanyaan (Demografi)
    demo_cols = [col for col in df_raw.columns if not col.startswith('Q')]
    df_numeric = df_raw[q_cols].replace(SCORE_MAP)
except Exception as e:
    st.error(f"Gagal memuat file: {e}")
    st.stop()

st.title("🚀 Dashboard Analisis Kuesioner v3.0")

# --- SIDEBAR: FILTER & NAV ---
st.sidebar.header("⚙️ Kontrol & Filter")
menu = st.sidebar.radio("Navigasi:", 
    ["Ringkasan Data", "Analisis Sentimen", "Analisis Korelasi", "Analisis Responden & Grup"])

# Filter Dinamis (Contoh: Filter berdasarkan kolom non-pertanyaan pertama)
selected_filter = "Semua"
if len(demo_cols) > 0:
    filter_col = st.sidebar.selectbox("Filter berdasarkan:", ["Tanpa Filter"] + demo_cols)
    if filter_col != "Tanpa Filter":
        val_filter = st.sidebar.unique(df_raw[filter_col])
        selected_filter = st.sidebar.selectbox(f"Pilih {filter_col}:", df_raw[filter_col].unique())
        df_filtered = df_raw[df_raw[filter_col] == selected_filter]
    else:
        df_filtered = df_raw
else:
    df_filtered = df_raw

df_data = df_filtered[q_cols]
df_num_filtered = df_data.replace(SCORE_MAP)

# --- MENU 1: RINGKASAN DATA ---
if menu == "Ringkasan Data":
    all_res = pd.Series(df_data.values.flatten()).dropna()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Responden Terfilter", len(df_filtered))
    col2.metric("Rata-rata Skor", f"{df_num_filtered.mean().mean():.2f}")
    col3.metric("Skor Tertinggi", f"{df_num_filtered.mean().max():.2f}")
    col4.metric("Skor Terendah", f"{df_num_filtered.mean().min():.2f}")

    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📊 Performa per Pertanyaan")
        avg_q = df_num_filtered.mean().sort_values()
        fig_avg = px.bar(x=avg_q.values, y=avg_q.index, orientation='h', 
                         color=avg_q.values, color_continuous_scale='Viridis',
                         labels={'x': 'Skor Rata-rata', 'y': 'Pertanyaan'})
        st.plotly_chart(fig_avg, use_container_width=True)
    
    with c2:
        st.subheader("📋 Top & Bottom 3")
        st.write("**Top 3 Pertanyaan:**")
        st.dataframe(avg_q.nlargest(3))
        st.write("**Bottom 3 Pertanyaan:**")
        st.dataframe(avg_q.nsmallest(3))

# --- MENU 2: ANALISIS SENTIMEN ---
elif menu == "Analisis Sentimen":
    st.subheader("🎭 Analisis Kedalaman Sentimen")
    
    # Transformasi data untuk Heatmap Sebaran
    list_heat = []
    for q in q_cols:
        counts = df_data[q].value_counts(normalize=True).reindex(['SS','S','CS','CTS','TS','STS']).fillna(0) * 100
        list_heat.append(counts)
    df_heat = pd.DataFrame(list_heat, index=q_cols)

    fig_heat = px.imshow(df_heat, text_auto=".1f", aspect="auto",
                         labels=dict(x="Pilihan Jawaban", y="Pertanyaan", color="Persentase (%)"),
                         color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("Warna hijau menunjukkan konsentrasi jawaban positif yang tinggi.")

# --- MENU 3: ANALISIS KORELASI ---
elif menu == "Analisis Korelasi":
    st.subheader("🔗 Hubungan Antar Pertanyaan")
    st.markdown("Fitur ini melihat apakah jawaban di satu pertanyaan cenderung sama dengan pertanyaan lainnya.")
    
    corr = df_num_filtered.corr()
    fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale='RdBu_r', range_color=[-1,1])
    st.plotly_chart(fig_corr, use_container_width=True)
    
    st.info("💡 **Tips:** Nilai mendekati 1.0 menunjukkan dua pertanyaan sangat berkaitan erat.")

# --- MENU 4: ANALISIS RESPONDEN & GRUP ---
elif menu == "Analisis Responden & Grup":
    tab1, tab2 = st.tabs(["Deteksi Kualitas Data", "Perbandingan Grup"])
    
    with tab1:
        st.subheader("🧐 Deteksi Responden Tidak Konsisten")
        # Cari responden yang standar deviasinya 0 (jawabannya sama semua dari awal sampai akhir)
        std_per_user = df_num_filtered.std(axis=1)
        straight_liners = df_filtered[std_per_user == 0]
        
        st.warning(f"Ditemukan {len(straight_liners)} responden yang menjawab dengan nilai yang sama persis di semua pertanyaan.")
        if not straight_liners.empty:
            st.dataframe(straight_liners)

    with tab2:
        if len(demo_cols) > 0:
            st.subheader("Comparing Groups")
            group_col = st.selectbox("Pilih Kolom Pembanding:", demo_cols)
            df_comp = df_raw.copy()
            df_comp['Rata-rata'] = df_numeric.mean(axis=1)
            
            fig_comp = px.box(df_comp, x=group_col, y='Rata-rata', color=group_col,
                             title=f"Distribusi Skor Berdasarkan {group_col}")
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.write("Tidak ada data demografi untuk dibandingkan.")

# --- DOWNLOAD FITUR ---
st.sidebar.markdown("---")
if st.sidebar.button("📥 Generate Ringkasan (CSV)"):
    summary = df_num_filtered.describe().T
    csv = summary.to_csv().encode('utf-8')
    st.sidebar.download_button("Download Sekarang", csv, "summary_kuesioner.csv", "text/csv")
