# E-Commerce Dashboard

Selamat datang di **E-Commerce Dashboard**! Dashboard ini dibuat menggunakan Streamlit untuk menganalisis data e-commerce, termasuk kategori produk terlaris, distribusi skor ulasan, analisis RFM, dan visualisasi geospasial. Dashboard ini memberikan wawasan mendalam tentang perilaku pelanggan dan performa penjualan

## Fitur Dashboard

Dashboard ini memiliki beberapa visualisasi yang dapat diakses melalui menu navigasi di sidebar:

1. **Kategori Produk Terlaris**: Menampilkan kategori produk dengan penjualan terbanyak.
2. **Produk dengan Review Terbanyak**: Menampilkan 10 produk yang paling sering diulas.
3. **Distribusi Skor Review**: Menunjukkan distribusi skor ulasan untuk 3 produk teratas.
4. **Kota dengan Pesanan Terbanyak**: Menampilkan 10 kota dengan jumlah pesanan tertinggi.
5. **Analisis RFM**: Menganalisis pelanggan berdasarkan Recency, Frequency, dan Monetary, dengan visualisasi pelanggan terbaik.
6. **Analisis Geospasial**: Menampilkan peta distribusi pesanan dengan heatmap dan penanda untuk kota tertentu

## Prasyarat

Sebelum menjalankan dashboard, pastikan Anda telah menginstal dependensi berikut:

- Python 3.8 atau lebih baru
- Library Python:
  - `streamlit`
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `geopandas`
  - `folium`
  - `streamlit-folium`
  - `geodatasets`

Anda dapat menginstal semua dependensi dengan perintah berikut:
pip install streamlit pandas matplotlib seaborn geopandas folium streamlit-folium geodatasets

## Cara Menjalankan Dashboard

Ikuti langkah-langkah berikut untuk menjalankan E-Commerce Dashboard dari repositori ini di komputer lokal Anda:

### Clone Repositori

Unduh kode dari repositori GitHub dengan perintah berikut di terminal Anda:

1. git clone https://github.com/Sidqiamn/analisis-data-streamlit-deploy.git
2. cd analisis-data-streamlit-deploy
3. pip install streamlit pandas matplotlib seaborn geopandas folium streamlit-folium geodatasets
4. streamlit run dashboard3.py

# Penggunaan 
1. Navigasi Sidebar: Pilih visualisasi yang ingin dilihat dari menu dropdown di sidebar.
2. Filter Data:
  - Gunakan filter "Tanggal Mulai" dan "Tanggal Selesai" untuk mempersempit data berdasarkan periode waktu.
  - Gunakan filter "Pilih Kategori Produk" untuk menyaring berdasarkan kategori produk. Pada awal tampilan memungkinkan hanya tampil satu produk karena perlu di filter.
  - Gunakan filter "Pilih State" untuk menyaring berdasarkan provinsi pelanggan.
3. Interaktivitas: Semua grafik Plotly memungkinkan zoom, hover untuk detail, dan interaksi lainnya. Peta       geospasial menggunakan Folium untuk menampilkan heatmap dan penanda interaktif.
4. Jika data tidak muncul atau ambigu dapat disesuaikan lagi tanggalnya.
