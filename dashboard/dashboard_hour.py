# dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide", page_icon="🚲")
st.title("🚲 Bike Sharing Dashboard - Analisis Data Per Jam")
st.markdown("Dashboard ini menampilkan visualisasi dari notebook analisis data `hour.csv`.")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('hour.csv')
    df = df.drop(columns=['instant', 'dteday', 'atemp'], errors='ignore')
    df['day_type'] = df['workingday'].map({0: 'Weekend/Holiday', 1: 'Weekday'})
    df['weather_good'] = df['weathersit'].apply(lambda x: 1 if x <= 2 else 0)
    return df

df = load_data()

# ========== 1. PERTANYAAN 1: POLA JAM SIBUK (MUSIM PANAS 2012) ==========
st.header("📌 1. Pola Penyewaan per Jam di Musim Panas 2012")

# Filter data musim panas 2012
df_summer = df[(df['yr'] == 1) & (df['season'] == 3)].copy()
hourly_avg = df_summer.groupby(['hr', 'day_type'])['cnt'].mean().reset_index()

# Cari jam puncak
peak_weekday = hourly_avg[hourly_avg['day_type'] == 'Weekday'].sort_values('cnt', ascending=False).iloc[0]
peak_weekend = hourly_avg[hourly_avg['day_type'] == 'Weekend/Holiday'].sort_values('cnt', ascending=False).iloc[0]

col1, col2 = st.columns(2)
col1.metric("🏙️ Weekday Puncak", f"{peak_weekday['hr']:02d}:00", f"{peak_weekday['cnt']:.0f} sepeda/jam")
col2.metric("🌿 Weekend Puncak", f"{peak_weekend['hr']:02d}:00", f"{peak_weekend['cnt']:.0f} sepeda/jam")

# Line plot
fig1, ax1 = plt.subplots(figsize=(12, 5))
sns.lineplot(data=hourly_avg, x='hr', y='cnt', hue='day_type', marker='o', ax=ax1)
ax1.set_title('Rata-rata Penyewaan per Jam - Musim Panas 2012')
ax1.set_xlabel('Jam')
ax1.set_ylabel('Rata-rata total sepeda')
ax1.set_xticks(range(0, 24))
ax1.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig1)

with st.expander("📊 Insight Pertanyaan 1"):
    st.markdown("""
    - **Weekday (Hari Kerja)**: Dua puncak pada jam 7-8 pagi dan 17-18 sore → pola komuter.
    - **Weekend (Akhir Pekan)**: Satu puncak pada jam 12-14 siang → pola rekreasi.
    - **Perbedaan volume**: Puncak weekday lebih tinggi **120 sepeda/jam** dari puncak weekend.
    """)

st.markdown("---")

# ========== 2. PERTANYAAN 2: DAMPAK CUACA BURUK ==========
st.header("📌 2. Dampak Cuaca Buruk pada *Casual* vs *Registered* (2012)")

# Filter data 2012 dan jam sibuk
df_2012 = df[df['yr'] == 1].copy()
df_2012['peak_hour'] = 'Lainnya'
df_2012.loc[df_2012['hr'].between(6, 9), 'peak_hour'] = 'Pagi (6-9)'
df_2012.loc[df_2012['hr'].between(17, 19), 'peak_hour'] = 'Sore (17-19)'
df_peak = df_2012[df_2012['peak_hour'] != 'Lainnya'].copy()
df_peak['weather_good'] = df_peak['weathersit'].apply(lambda x: 1 if x <= 2 else 0)

# Barplot untuk casual
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_peak, x='peak_hour', y='casual', hue='weather_good', palette='Set2', ax=ax2)
ax2.set_title('Rata-rata Pengguna *Casual* pada Jam Sibuk')
ax2.set_ylabel('Rata-rata casual')
ax2.set_xlabel('Jam Sibuk')
ax2.legend(title='Cuaca', labels=['Baik', 'Buruk'])
st.pyplot(fig2)

# Barplot untuk registered
fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_peak, x='peak_hour', y='registered', hue='weather_good', palette='Set2', ax=ax3)
ax3.set_title('Rata-rata Pengguna *Registered* pada Jam Sibuk')
ax3.set_ylabel('Rata-rata registered')
ax3.set_xlabel('Jam Sibuk')
ax3.legend(title='Cuaca', labels=['Baik', 'Buruk'])
st.pyplot(fig3)

with st.expander("📊 Insight Pertanyaan 2"):
    st.markdown("""
    - ***Casual* (pengguna insidental)** sangat sensitif terhadap cuaca buruk → penurunan hingga **70%**.
    - ***Registered* (pengguna terdaftar)** lebih tahan terhadap cuaca buruk → penurunan hanya **35-40%**.
    - **Kesimpulan**: *Registered* adalah segmen paling loyal dan menjadi tulang punggung bisnis, terutama saat cuaca buruk.
    """)

st.markdown("---")

# ========== 3. ANALISIS LANJUTAN: POLA PER JAM BERDASARKAN CUACA ==========
st.header("📌 Analisis Lanjutan: Pola Penyewaan per Jam Berdasarkan Kondisi Cuaca (2012)")

df_2012_all = df[df['yr'] == 1].copy()
df_2012_all['weather_label'] = df_2012_all['weathersit'].map({1: 'Cerah', 2: 'Berawan', 3: 'Hujan Ringan', 4: 'Hujan Lebat'})
hourly_weather = df_2012_all.groupby(['hr', 'weather_label'])['cnt'].mean().reset_index()

fig4, ax4 = plt.subplots(figsize=(14, 6))
sns.lineplot(data=hourly_weather, x='hr', y='cnt', hue='weather_label', marker='o', ax=ax4)
ax4.set_title('Pola Penyewaan per Jam Berdasarkan Kondisi Cuaca (2012)')
ax4.set_xlabel('Jam')
ax4.set_ylabel('Rata-rata cnt')
ax4.set_xticks(range(0, 24))
ax4.grid(True, linestyle='--', alpha=0.5)
ax4.legend(title='Cuaca')
st.pyplot(fig4)

with st.expander("📊 Insight Analisis Lanjutan"):
    st.markdown("""
    - **Cuaca cerah & berawan** → pola dua puncak (pagi & sore) sangat jelas.
    - **Hujan ringan** → volume turun drastis (puncak hanya 150-200 sepeda/jam).
    - **Hujan lebat** → hampir tidak ada penyewaan (rata-rata < 50 sepeda/jam).
    - Efek cuaca buruk bersifat **global di semua jam**, bukan hanya jam sibuk.
    """)

# ========== FOOTER ==========
st.markdown("---")
st.caption("Dashboard ini dibuat berdasarkan analisis data `hour.csv` untuk menjawab 2 pertanyaan SMART + analisis lanjutan.")