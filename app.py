import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- KONFIGURASI SKOR & KATEGORI (DI LUAR FUNGSI AGAR TIDAK ERROR) ---
SCORE_MAP = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}

def get_category(val):
    if val in ['SS', 'S']:
        return 'Positif'
    elif val == 'CS':
        return 'Netral'
    elif val in ['CTS', 'TS', 'STS']:
        return 'Negatif'
    return 'Unknown'

# --- LOAD DATA ---
@st.cache_data
def load_data():
    file_name = 'data_kuesioner.xlsx'
    # Membaca sheet utama
    df = pd.read_excel(file_name, sheet_name='Kuesioner')
    # Membaca sheet pertanyaan untuk label
    try:
        df_q = pd.read_excel(file_name, sheet_name='Pertanyaan')
    except:
        df_q = pd.DataFrame()
        
    return df, df_q

# --- MAIN APP ---
st.set_page_config(page_title="Analisis Kuesioner Interaktif", layout="wide")

try:
    df_raw, df_pertanyaan = load_data()
    q_cols = [col for col in df_raw.columns if col.startswith('Q')]
    df_data = df_raw[q_cols]
except Exception as e:
    st.error(f"Gagal memuat file: {e}")
    st.stop()

st.title("🚀 Dashboard Analisis Hasil Kuesioner")
st.markdown("Analisis mendalam berdasarkan data `data_kuesioner.xlsx` dengan standarisasi skor 1-6.")

# --- SIDEBAR NAVIGATION ---
menu = st.sidebar.radio("Pilih Menu:", ["Ringkasan Data", "Analisis Distribusi & Kategori", "Analisis Per Pertanyaan"])

# Kalkulasi Data Global
all_responses = pd.Series(df_data.values.flatten()).dropna()
dist_counts = all_responses.value_counts().reindex(['SS','S','CS','CTS','TS','STS']).fillna(0)

# --- MENU 1: RINGKASAN DATA ---
if menu == "Ringkasan Data":
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Responden", len(df_raw))
    col2.metric("Total Jawaban", len(all_responses))
    col3.metric("Skala Terbanyak", dist_counts.idxmax())
    
    avg_total = df_data.replace(SCORE_MAP).mean().mean()
    col4.metric("Rata-rata Skor Global", f"{avg_total:.2f}")

    st.markdown("---")
    
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.subheader("📊 Distribusi Jawaban (Bar Chart)")
        fig1 = px.bar(x=dist_counts.index, y=dist_counts.values, 
                     labels={'x':'Skala', 'y':'Jumlah'},
                     color=dist_counts.index,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)

    with c_right:
        st.subheader("🍕 Proporsi Jawaban (Pie Chart)")
        fig2 = px.pie(names=dist_counts.index, values=dist_counts.values, 
                      hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig2, use_container_width=True)

# --- MENU 2: KATEGORI SENTIMEN ---
elif menu == "Analisis Distribusi & Kategori":
    st.subheader("🎭 Distribusi Kategori Jawaban")
    st.info("Kategori: Positif (SS, S), Netral (CS), Negatif (CTS, TS, STS)")
    
    cat_data = all_responses.apply(get_category).value_counts().reindex(['Positif', 'Netral', 'Negatif'])
    
    col_cat1, col_cat2 = st.columns([1, 2])
    
    with col_cat1:
        st.write(cat_data)
        
    with col_cat2:
        fig3 = px.bar(x=cat_data.index, y=cat_data.values,
                     color=cat_data.index,
                     color_discrete_map={'Positif':'#2ecc71', 'Netral':'#f1c40f', 'Negatif':'#e74c3c'},
                     text=cat_data.values)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Rata-rata Skor per Pertanyaan")
    avg_scores = df_data.replace(SCORE_MAP).mean().sort_values(ascending=False)
    
    fig4 = px.bar(x=avg_scores.index, y=avg_scores.values,
                 labels={'x':'Kode Pertanyaan', 'y':'Rata-rata Skor'},
                 color=avg_scores.values,
                 color_continuous_scale='RdYlGn')
    st.plotly_chart(fig4, use_container_width=True)

# --- MENU 3: ANALISIS PER PERTANYAAN ---
elif menu == "Analisis Per Pertanyaan":
    st.subheader("📚 Sebaran Jawaban per Pertanyaan (Stacked Bar)")
    
    # Menyiapkan data untuk Stacked Bar
    stacked_list = []
    for q in q_cols:
        counts = df_data[q].value_counts().reindex(['SS','S','CS','CTS','TS','STS']).fillna(0)
        for skala, val in counts.items():
            stacked_list.append({'Pertanyaan': q, 'Skala': skala, 'Jumlah': val})
    
    df_stacked = pd.DataFrame(stacked_list)
    
    fig5 = px.bar(df_stacked, x="Pertanyaan", y="Jumlah", color="Skala",
                 title="Perbandingan Distribusi Skala antar Pertanyaan",
                 color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")
    
    # BONUS: Radar Chart (Profil Kekuatan)
    st.subheader("🕸️ Radar Chart: Profil Kualitas ")
    avg_scores_raw = df_data.replace(SCORE_MAP).mean()
    
    fig6 = go.Figure()
    fig6.add_trace(go.Scatterpolar(
        r=avg_scores_raw.values,
        theta=avg_scores_raw.index,
        fill='toself',
        name='Skor Rata-rata',
        line_color='teal'
    ))
    fig6.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])))
    st.plotly_chart(fig6, use_container_width=True)

    if not df_pertanyaan.empty:
        with st.expander("Lihat Detail Teks Pertanyaan"):
            st.dataframe(df_pertanyaan)

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("Sistem Analisis Kuesioner v2.0")
