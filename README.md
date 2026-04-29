# Link Streamlit : https://cdc30-penyewaan-sepeda-drsesmyhbzxwvtbncz2qeh.streamlit.app/

## 🚲 Proyek Analisis Data Bike Sharing - Dataset Hourly

## 📌 Ringkasan Proyek

Proyek ini bertujuan untuk menganalisis data penyewaan sepeda per jam (`hour.csv`) guna menjawab **dua pertanyaan bisnis SMART** serta memberikan rekomendasi aksi yang dapat diimplementasikan.  

Analisis mencakup:
- Data Wrangling (pengumpulan, penilaian, pembersihan data)
- Exploratory Data Analysis (EDA) dan Visualisasi
- Analisis lanjutan (pola per jam berdasarkan kondisi cuaca)
- Dashboard interaktif menggunakan Streamlit

---

## 🎯 Pertanyaan Bisnis SMART

### Pertanyaan 1 (Pola Jam Sibuk)
> **"Bagaimana pola jumlah penyewaan sepeda (`cnt`) berdasarkan jam (`hr`) pada hari kerja vs akhir pekan di musim panas tahun 2012?"**

### Pertanyaan 2 (Pengaruh Cuaca Buruk)
> **"Apakah pengaruh cuaca buruk terhadap jumlah pengguna `casual` dan `registered` berbeda pada jam sibuk pagi (6-9) dan sore (17-19) di tahun 2012?"**

---

## ⚙️ Setup Environment

### 1. **Clone atau Download Proyek**
Pastikan semua file dalam struktur di atas sudah tersedia di komputer Anda.

### 2. **Buat Virtual Environment (Opsional tapi disarankan)**

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Jalankan dashboard_hour.py

```bash

# Masuk ke Direktori dashboard
cd dashboard

# Jalankan file yang berisi code Streamlit
streamlit run dashboard_hour.py
```