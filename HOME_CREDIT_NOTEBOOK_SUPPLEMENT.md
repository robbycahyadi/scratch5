# Catatan tambahan dari ZIP notebook Home Credit

Tujuan: bahan pendamping untuk dikirim bersama [laporan semantik utama](<HOME_CREDIT_SEMANTIC_AUDIT.md>) dan [kamus audit 120 fitur](<HOME_CREDIT_FEATURE_DICTIONARY_AUDITED.csv>), bukan perubahan rancangan CG-HIL.

## Provenance dan batas pemeriksaan

Sumber: [ZIP unggahan pengguna](<Home-Credit-Default-Risk-main.zip>). Terdapat empat notebook: EDA, Feature Engineering and Modelling, Final, dan Deployment Model Trainnig - 300 Features; juga pipeline deployment dan model pickle. [README hasil ekstraksi](<results/notebook_review/README.txt>) menyebut proyek sebagai end-to-end case study. Identitas penulis, URL repositori asal, dan versi/commit tidak dipastikan dari README tersebut.

Notebook dibaca sebagai JSON; sel kode/markdown dan output teks yang tersimpan diekstrak ke teks. **Tidak ada sel notebook yang dieksekusi, model pickle yang dimuat, atau training yang dijalankan.** Output tersimpan adalah hasil milik penulis, bukan eksperimen yang direplikasi pada lingkungan ini. Pemeriksaan terarah berfokus pada relevansi semantik; bukan audit menyeluruh keamanan, performa, atau seluruh alur validasi proyek.

## Temuan yang berguna—dan batasnya

| Temuan pada notebook | Bukti yang dibaca | Nilai untuk CG-HIL |
|---|---|---|
| Penulis mengganti DAYS_EMPLOYED=365243 menjadi NaN | [Feature Engineering, teks:2535–2537](<results/notebook_review/Feature Engineering and Modelling.txt#L2535-L2537>) | Menguatkan bahwa penggantian sentinel merupakan praktik sekunder yang nyata. **Tidak menjelaskan arti resmi kode**, dan tidak membuktikan bahwa masking adalah satu-satunya kebijakan benar untuk skor kelengkapan. |
| Penulis menyebut XNA organisasi “could probably denote unclassified” | [EDA, teks:1620–1625](<results/notebook_review/EDA - Home Credit Default.txt#L1620-L1625>) | Ini secara eksplisit dugaan penulis. Jangan dijadikan definisi resmi atau menggantikan tabulasi lokal: kode terkait Pensioner/Unemployed, dengan 10 pengecualian Pensioner. |
| Empat baris gender XNA dibuang | [Feature Engineering, teks:2543–2544](<results/notebook_review/Feature Engineering and Modelling.txt#L2543-L2544>) | Pilihan cleaning penulis, bukan kewajiban penelitian. **Tidak direkomendasikan disalin otomatis**; kelangkaan dan label nondefault tidak membenarkan pemilihan penghapusan berdasarkan TARGET. |
| NaN kategorikal diisi dengan label XNA | [Feature Engineering, teks:2545–2548](<results/notebook_review/Feature Engineering and Modelling.txt#L2545-L2548>) | Menyatukan missing buatan dengan XNA asli berisiko menghapus perbedaan makna. CG-HIL sebaiknya mempertahankan mask sebelum imputasi dan membedakan marker imputasi dari kode asli. |
| Dua region rating dikonversi menjadi object | [Feature Engineering, teks:2549–2553](<results/notebook_review/Feature Engineering and Modelling.txt#L2549-L2553>) | Selaras dengan perlakuan kategorikal untuk menghindari interpolasi rating, tetapi alasannya pada notebook juga terkait pola TARGET, bukan bukti skala semantik baru. |
| Dibuat MISSING_VALS_TOTAL_APP setelah cleaning dan pengisian NaN kategori | [Feature Engineering, teks:2554–2556](<results/notebook_review/Feature Engineering and Modelling.txt#L2554-L2556>) | Berguna sebagai pembanding konsep missing-count, **bukan ekuivalen skor CG-HIL**: urutan transformasi, daftar kolom, penghapusan fitur/baris, dan normalisasi berbeda. Field kategori yang semula missing sudah tidak ikut hitungan. |

## Peringatan teknis penting saat membaca notebook

### 1. Ada kode yang tidak melakukan perubahan yang diklaim komentar

Pada [teks:2538–2542](<results/notebook_review/Feature Engineering and Modelling.txt#L2538-L2542>), komentar mengatakan nilai social count >30 akan dibuang/diganti, tetapi ekspresinya memakai **`== np.nan`**, bukan assignment `= np.nan`. Ini membandingkan nilai, bukan memutasi data. Artinya tindakan cleaning yang diklaim komentar tersebut **tidak terlaksana pada baris kode itu**.

Ambang >30 juga merupakan keputusan penulis, bukan bukti bahwa semua social count >30 adalah sentinel. Audit utama tetap tidak otomatis membuang nilai ekstrem tanpa dasar. Penggunaan chained assignment di tempat lain juga perlu ditulis ulang jika kode hendak dipakai pada pandas modern; tidak diuji eksekusinya di sini.

### 2. Beberapa fitur turunan mencampur satuan

Pada [teks:2532–2537](<results/notebook_review/Feature Engineering and Modelling.txt#L2532-L2537>), DAYS_BIRTH dikonversi menjadi tahun, sementara DAYS_EMPLOYED masih hari. Kemudian pada [teks:2634–2640](<results/notebook_review/Feature Engineering and Modelling.txt#L2634-L2640>) keduanya dikurangkan/dibagi, dan OWN_CAR_AGE juga dikombinasikan dengan DAYS_EMPLOYED. Berdasarkan urutan kode ini, fitur seperti AGE_EMPLOYED_DIFF dan CAR_EMPLOYED_DIFF **bukan selisih durasi dalam satuan sama**. Jangan menyalin dan melabelinya sebagai fitur domain yang sudah benar tanpa menyamakan unit. Ini tidak mengubah 120 fitur asli pada audit CG-HIL, karena fitur turunan tersebut tidak diadopsi.

### 3. Fitur berbasis TARGET memerlukan validasi out-of-fold

[Metode neighbors, teks:2717–2751](<results/notebook_review/Feature Engineering and Modelling.txt#L2717-L2751>) mem-fit tetangga pada application_train dengan TARGET, kemudian menghitung rerata TARGET tetangga untuk baris train yang sama. Kode itu sendiri tidak menunjukkan pembentukan out-of-fold, dan query train dapat memasukkan baris sendiri. **Jika** fitur dihitung pada seluruh train sebelum pemisahan validasi, terdapat risiko kebocoran label validasi serta kontribusi label sendiri. Catatan ini adalah risiko lokal pada metode yang dibaca, bukan kesimpulan audit penuh atas setiap skor notebook.

Tidak relevan untuk ditambahkan pada CG-HIL saat ini; jangan memakai fitur berbasis TARGET ini untuk menentukan completeness, E/U, atau imputasi.

### 4. Model imputasi EXT_SOURCE tidak mengungkap semantik sumber

[Metode EXT_SOURCE, teks:2561–2604](<results/notebook_review/Feature Engineering and Modelling.txt#L2561-L2604>) melatih XGBRegressor untuk mengisi skor eksternal yang missing. Ini strategi imputasi berbasis model milik penulis, **bukan dokumentasi identitas sumber eksternal, formula skor, ataupun mekanisme missing**. Tidak dijalankan dan tidak direkomendasikan sebagai tambahan otomatis karena akan memperluas desain yang diminta.

## Apa yang ditambahkan terhadap audit utama?

- **Tambahan terverifikasi dari artefak:** contoh konkret praktik sentinel→NaN; penggabungan missing kategori dengan XNA; waktu perhitungan missing count; bug perbandingan vs assignment; potensi masalah unit pada fitur turunan; kebutuhan kehati-hatian pada fitur TARGET-neighbor.
- **Tidak terjawab oleh ZIP:** arti resmi 365243/XNA, penyebab missing struktural tiap observasi, formula EXT_SOURCE, atau validitas semantik SMOTENC full CG-HIL.
- **Tidak berubah:** kesimpulan audit utama—revisi kecil spesifikasi sentinel dan validasi hitungan/gabungan diperlukan sebelum eksperimen utama; tidak perlu menyalin pipeline orang lain atau mengganti strategi tesis.

## Teks pengantar siap dikirim ke ChatGPT

> Saya lampirkan laporan semantik Home Credit, kamus audit 120 fitur, serta catatan review notebook pihak ketiga. Perlakukan notebook sebagai sumber sekunder/praktik implementasi, bukan dokumentasi resmi. Bedakan fakta data lokal, komentar penulis, kode yang benar-benar melakukan transformasi, dan inferensi. Jangan langsung menyalin penghapusan gender XNA, pengisian semua kategori dengan XNA, model imputasi EXT_SOURCE, atau fitur TARGET-neighbor. Tolong review apakah rekomendasi minimum audit sudah memadai tanpa mengubah strategi CG-HIL, RQ, atau menambah eksperimen. Tidak ada training baru atau perubahan data/protokol yang sudah disetujui.

**Status akhir:** catatan tambahan untuk review; tidak ada perubahan pada laporan utama, dataset asli, atau implementasi penelitian.
