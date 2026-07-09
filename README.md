# ☕ Kopiseru – Area Manager Dashboard

Selamat datang di **Kopiseru Area Manager Dashboard**! 

Aplikasi ini adalah dashboard interaktif yang dibangun menggunakan [Streamlit](https://streamlit.io/) khusus untuk **Area Manager**. Dashboard ini dirancang agar Area Manager dapat dengan mudah memantau, menganalisis performa bisnis, dan mengambil keputusan strategis berdasarkan data dari berbagai cabang Kopiseru di wilayah yang dikelola.

---

## 🌟 Fitur & Fungsionalitas Utama

Dashboard ini dilengkapi dengan berbagai fitur interaktif yang memungkinkan Area Manager untuk melakukan *deep-dive* ke dalam data operasional:

### 1. 🎛️ Kontrol & Filter Interaktif (Navbar)
- **📍 Filter Provinsi:** Pilih provinsi spesifik untuk melihat performa cabang-cabang di area tersebut.
- **📅 Rentang Tanggal:** Sesuaikan periode analisis dengan memilih rentang tanggal awal dan akhir (*Start Date & End Date*).
- **🏪 Tipe Cabang:** Filter data berdasarkan tipe cabang tertentu (misalnya, cabang reguler, kiosk, dll) untuk melihat performa spesifik format toko.
- **🏢 Filter Cabang Spesifik:** Terdapat opsi *checkbox* untuk memilih atau mengecualikan cabang tertentu dalam provinsi terpilih agar analisis lebih terfokus.
- **🎨 Tema Visual:** Dukungan peralihan instan antara **Light Mode** (terang) dan **Dark Mode** (gelap) menyesuaikan kenyamanan mata.

### 2. 📊 Key Performance Indicators (KPI)
Di bagian paling atas, terdapat ringkasan metrik (KPI) yang memberikan gambaran performa secara instan:
- **💰 Total Pendapatan:** Total omzet/pendapatan kotor.
- **💵 Total Laba (Profit):** Total keuntungan bersih setelah dikurangi biaya operasional.
- **📈 Rata-rata Margin Laba:** Rata-rata persentase margin keuntungan dari cabang-cabang yang dipilih.
- **🏆 Cabang Terlaris:** Menampilkan nama cabang dengan total profit tertinggi di wilayah dan periode tersebut.

### 3. 📈 Grafik & Visualisasi Analitik
Dashboard menyediakan 6 grafik utama yang interaktif (dapat di-*hover*, di-*zoom*, dan akan otomatis menyesuaikan menjadi *Pie Chart* jika hanya 1 cabang yang difilter):

1. **Tren Pendapatan, Biaya & Profit (Line Chart):** 
   Melihat pergerakan pendapatan, pengeluaran, dan profit dari waktu ke waktu secara komprehensif dalam satu grafik.
2. **Pendapatan dan Biaya per Cabang (Bar Chart):** 
   Membandingkan rasio pendapatan kotor terhadap pengeluaran operasional di masing-masing cabang.
3. **Profit Margin Cabang (Bar Chart vs Rata-rata):** 
   Menampilkan persentase margin laba per cabang dan membandingkannya dengan *Rata-rata Margin Nasional*. Grafik akan berwarna **Hijau** jika di atas rata-rata dan **Merah** jika di bawah rata-rata.
4. **Rata-rata Nilai Transaksi / *Ticket Size* (Bar Chart vs Rata-rata):** 
   Membandingkan nilai rata-rata per transaksi pelanggan di setiap cabang dengan rata-rata transaksi nasional.
5. **Komposisi Channel Penjualan (Stacked Bar Chart):** 
   Menampilkan persentase kontribusi penjualan dari metode **Dine-in** (Makan di tempat), **Delivery** (Pesan antar), dan **Takeaway** (Bawa pulang).
6. **Transaksi Hari Kerja vs Akhir Pekan (Grouped Bar Chart):** 
   Membandingkan volume jumlah transaksi yang terjadi pada *Weekdays* (Hari Kerja) versus *Weekends* (Akhir Pekan) untuk mengetahui pola keramaian.

---

## 🛠️ Persyaratan Sistem (Requirements)

Pastikan Anda telah menginstal pustaka Python berikut sebelum menjalankan aplikasi (tercantum dalam `requirements.txt`):
- `streamlit`
- `pandas`
- `plotly`

