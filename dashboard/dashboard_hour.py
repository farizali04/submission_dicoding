# dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi halaman
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide", page_icon="🚲")
st.title("🚲 Bike Sharing Dashboard - Analisis Data Per Jam")
st.markdown("Dashboard ini menampilkan visualisasi dari notebook analisis data `hour.csv`.")

# Load data
@st.cache_data
def load_data():
    # Dapatkan path absolut file CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'hour.csv')
    df = pd.read_csv(csv_path)
    df.drop(columns=['instant', 'atemp'], errors='ignore', inplace=True)
    # Konversi kolom dteday ke datetime
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['day_type'] = df['workingday'].map({0: 'Weekend/Holiday', 1: 'Weekday'})
    df['weather_good'] = df['weathersit'].apply(lambda x: 1 if x <= 2 else 0)
    return df

df = load_data()

# ========== FITUR INTERAKTIF: FILTER TANGGAL ==========
st.sidebar.header("🎛️ Filter Data")
date_range = st.sidebar.date_input(
    "📅 Pilih Rentang Tanggal",
    value=(df['dteday'].min().date(), df['dteday'].max().date()),
    min_value=df['dteday'].min().date(),
    max_value=df['dteday'].max().date(),
    help="Pilih rentang tanggal untuk menganalisis data"
)

# Validasi date_range
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range[0] if len(date_range) > 0 else df['dteday'].min().date()
    end_date = df['dteday'].max().date()

# Filter data berdasarkan tanggal
df_filtered = df[(df['dteday'].dt.date >= start_date) & (df['dteday'].dt.date <= end_date)].copy()

# Filter Musim
st.sidebar.subheader("🌍 Musim")
season_map = {1: 'Semi (Spring)', 2: 'Panas (Summer)', 3: 'Gugur (Fall)', 4: 'Dingin (Winter)'}
selected_seasons = st.sidebar.multiselect(
    "Pilih Musim",
    options=sorted(df['season'].unique()),
    format_func=lambda x: season_map.get(x, str(x)),
    default=sorted(df['season'].unique())
)

# Terapkan filter musim ke data yang sudah difilter tanggal
df_filtered = df_filtered[df_filtered['season'].isin(selected_seasons)].copy()

# Tampilkan status filter di sidebar
st.sidebar.info(f"📈 Data: **{len(df_filtered):,}** dari **{len(df):,}** baris")

# ========== 1. PERTANYAAN 1: POLA JAM SIBUK ==========
st.header("📌 1. Pola Penyewaan per Jam di Musim Panas 2012")
st.subheader("Bagaimana pola jumlah penyewaan sepeda (cnt) berdasarkan jam (hr) pada hari kerja vs akhir pekan di musim panas tahun 2012, sehingga manajemen dapat mengatur penambahan staf dan sepeda pada jam puncak?")

# Filter data musim panas 2012
df_summer = df_filtered[(df_filtered['yr'] == 1)].copy()
hourly_avg = df_summer.groupby(['hr', 'day_type'])['cnt'].mean().reset_index()

if len(hourly_avg) > 0:
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
else:
    st.warning("⚠️ Tidak ada data musim panas 2012 dalam rentang tanggal yang dipilih.")

st.markdown("---")

# ========== 2. PERTANYAAN 2: DAMPAK CUACA BURUK ==========
st.header("📌 2. Dampak Cuaca Buruk pada *Casual* vs *Registered* (2012)")
st.subheader("Apakah pengaruh cuaca buruk terhadap jumlah pengguna casual dan registered berbeda secara signifikan pada jam sibuk pagi (6-9) dan sore (17-19) di tahun 2012?")

# Filter data 2012 dan jam sibuk
df_2012 = df_filtered[df_filtered['yr'] == 1].copy()
df_2012['peak_hour'] = 'Lainnya'
df_2012.loc[df_2012['hr'].between(6, 9), 'peak_hour'] = 'Pagi (6-9)'
df_2012.loc[df_2012['hr'].between(17, 19), 'peak_hour'] = 'Sore (17-19)'
df_peak = df_2012[df_2012['peak_hour'] != 'Lainnya'].copy()
df_peak['weather_good'] = df_peak['weathersit'].apply(lambda x: 1 if x <= 2 else 0)

if len(df_peak) > 0:
    # Siapkan label cuaca dan palet warna mirip contoh
    df_peak['weather_label'] = df_peak['weather_good'].map({1: 'Baik', 0: 'Buruk'})
    palette = { 'Baik': '#66c2a5', 'Buruk': '#fc8d62' }

    # Urutan kategori jam sibuk
    order = ['Pagi (6-9)', 'Sore (17-19)']

    # Buat dua barplot berdampingan (Casual | Registered) dengan error bars
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    sns.barplot(
        data=df_peak,
        x='peak_hour',
        y='casual',
        hue='weather_label',
        order=order,
        palette=palette,
        ci=None,
        edgecolor='none',
        linewidth=0,
        ax=axes[0]
    )
    axes[0].set_title('Casual: Cuaca Baik vs Buruk')
    axes[0].set_xlabel('peak_hour')
    axes[0].set_ylabel('casual')

    sns.barplot(
        data=df_peak,
        x='peak_hour',
        y='registered',
        hue='weather_label',
        order=order,
        palette=palette,
        ci=None,
        edgecolor='none',
        linewidth=0,
        ax=axes[1]
    )
    axes[1].set_title('Registered: Cuaca Baik vs Buruk')
    axes[1].set_xlabel('peak_hour')
    axes[1].set_ylabel('registered')

    # Perapihan legenda: letakkan legend di pojok kanan atas masing-masing subplot
    axes[0].legend(title='weather_label', loc='upper right')
    axes[1].legend(title='weather_label', loc='upper right')

    fig.tight_layout()
    st.pyplot(fig)

    with st.expander("📊 Insight Pertanyaan 2"):
        st.markdown("""
        - ***Casual* (pengguna insidental)** sangat sensitif terhadap cuaca buruk → penurunan hingga 70%.
        - ***Registered* (pengguna terdaftar)** lebih tahan terhadap cuaca buruk → penurunan hanya 35-40%.
        - **Catatan**: Registered adalah segmen paling loyal dan menjadi tulang punggung bisnis, terutama saat cuaca buruk
        """)
else:
    st.warning("⚠️ Tidak ada data pada jam sibuk tahun 2012 dalam rentang tanggal yang dipilih.")

st.markdown("---")

# ========== 3. ANALISIS LANJUTAN: POLA PER JAM BERDASARKAN CUACA ==========
st.header("📌 Analisis Lanjutan: Pola Penyewaan per Jam Berdasarkan Kondisi Cuaca (2012)")

df_2012_all = df_filtered[df_filtered['yr'] == 1].copy()
df_2012_all['weather_label'] = df_2012_all['weathersit'].map({1: 'Cerah', 2: 'Berawan', 3: 'Hujan Ringan', 4: 'Hujan Lebat'})
hourly_weather = df_2012_all.groupby(['hr', 'weather_label'])['cnt'].mean().reset_index()

if len(hourly_weather) > 0:
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
else:
    st.warning("⚠️ Tidak ada data tahun 2012 dalam rentang tanggal yang dipilih.")

# ========== FOOTER ==========
st.markdown("---")
st.caption("Dashboard ini dibuat berdasarkan analisis data `hour.csv` untuk menjawab 2 pertanyaan SMART + analisis lanjutan.")