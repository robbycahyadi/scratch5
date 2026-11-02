# Home Credit Feature Semantics Audit untuk CG-HIL

Tanggal audit: 2 November 2026. Status: diagnostik untuk review mahasiswa; **bukan keputusan perubahan protokol**.

## 1. Executive Summary

Audit memisahkan definisi dokumenter, temuan empiris, interpretasi sekunder, dan inferensi. Seluruh 120 prediktor diperiksa; ID dan TARGET tidak termasuk skor kelengkapan maupun ruang generator. Hasil PASS pilot/full terdahulu adalah validitas teknis terbatas, bukan jaminan koherensi semantik sampel sintetis.

Temuan inti: `365243` tidak layak diinterpolasi sebagai durasi kerja normal; arti resmi kodenya belum terverifikasi. `XNA` perlu dibaca per fitur, bukan dipetakan seragam. Missing struktural dan 47 fitur hunian dapat membuat skor literal lebih mencerminkan ketersediaan blok data daripada kecukupan informasi. Mask kategorikal precheck secara umum tepat, tetapi 12 hitungan mentah memerlukan kebijakan dukungan integral. Rekomendasi adalah **revisi kecil pada spesifikasi implementasi**, bukan perubahan strategi CG-HIL; tidak ada kebijakan baru yang diterapkan audit ini.

## 2. Data Sources and Provenance

- **Data aktual lokal:** [application_train.csv](<application_train.csv>), dibaca tanpa ditulis ulang. Ukuran 166.133.370 byte; SHA-256 `52e96b895b1112e1c853f670e58372719c8441c5ed1c57ac2f7fad559d784f5f`. Diagnostik mencatat hash sebelum dan sesudah; hash independen juga dihitung untuk provenance.
- **Rujukan primer:** [halaman data kompetisi Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk/data). Akses HTTP berhasil tetapi ekstraksi hanya memberikan judul; isi penjelasan dan unduhan resmi tidak dapat diverifikasi langsung pada sesi ini. Karena itu laporan ini tidak mengklaim arti kode khusus sebagai konfirmasi resmi Kaggle.
- **Kamus yang direplikasi:** [arsip mirror workshop GitHub, commit immutable](https://raw.githubusercontent.com/gridl/workshop_2018_dsgo/2b7b0e95828b5a95e0e783b7ea764e5962fb3fb4/00_data/HomeCredit_columns_description.csv.zip). Ini salinan sekunder kamus kompetisi, bukan unduhan terautentikasi Kaggle. SHA-256 CSV hasil ekstraksi byte asli: `eef7665398228a80f7367c9258220c5fbe1038f3f54094244f354d54e2d4fb03`. [Provenance terperinci](<semantic_audit_sources/dictionary_provenance.json>).
- **Pemeriksaan silang sekunder:** [Jupyter Book Home Credit—feature descriptions](https://harnalashok.github.io/credit_risk/application_train_test.html). Memuat definisi yang diatribusikan kepada kamus, tetapi tutorial juga berisi penyederhanaan TARGET dan praktik membuang baris; praktik tersebut **tidak diadopsi**. TARGET berarti kesulitan pembayaran sesuai jendela X/Y yang dianonimkan, bukan semata klaim gagal melunasi semua pinjaman.
- **Dokumentasi algoritma resmi:** [imbalanced-learn, SMOTE variants dan sample generation](https://imbalanced-learn.org/stable/over_sampling.html#smote-variants). SMOTENC menginterpolasi numerik dan memilih kategori dari tetangga; tidak menjamin kendala gabungan antarkolom.

Tingkat bukti: **D** = definisi dalam salinan kamus; **E** = hasil hitung data lokal; **S** = interpretasi/praktik sekunder; **I** = inferensi atau rekomendasi yang belum disahkan. D tidak sama dengan autentikasi byte resmi. Identitas sumber eksternal, formula normalisasi, alasan tiap NaN, dan arti resmi setiap kode tidak tersedia hanya dari nama kolom.

## 3. Special Values Investigation

### 3.1 Frekuensi dan makna empat kode prioritas

Denominator persentase: seluruh **307.511** aplikasi, bukan hanya train.

| Fitur dan kode | Jumlah | Persentase | Kesimpulan dan tingkat bukti |
|---|---:|---:|---|
| `DAYS_EMPLOYED=365243` | 55.374 | 18,0072% | D: jumlah hari sebelum aplikasi saat mulai pekerjaan saat ini. E: semua offset positif adalah kode ini; durasi 365.243 hari (~1.000 tahun) tidak masuk akal sebagai lama kerja biasa. I/S: sentinel/anomali representasi yang kuat; arti kode resmi missing vs not-applicable belum terverifikasi. |
| `ORGANIZATION_TYPE=XNA` | 55.374 | 18,0072% | D: jenis organisasi tempat bekerja. E: berkaitan tepat dengan sentinel pada data lokal. I: kemungkinan ketidakberlakuan pada nonpekerja; **bukan** konfirmasi kepanjangan resmi XNA. Tetap kategori khusus, bukan tipe organisasi substantif. |
| `CODE_GENDER=XNA` | 4 | 0,001301% | D: gender klien. E: kategori literal XNA. Makna gender substantif tidak dapat ditentukan; kandidat unknown untuk kelengkapan, bukan kategori gender yang boleh ditebak atau alasan membuang baris. |
| `NAME_FAMILY_STATUS=Unknown` | 2 | 0,000650% | D: status keluarga. E: label Unknown. Secara literal status tidak diketahui; belum ada aturan resmi konversi ke NaN. Jangan disamakan dengan Single/Other. |

Keempat kolom tidak mempunyai NaN mentah. Nol NaN tidak membuktikan semua informasinya diketahui. Gender XNA dan family Unknown tidak bertumpang tindih (0 baris). Detail konteks tersimpan pada [baris khusus gender/keluarga](<results/semantic_audit/gender_family_special_ids.csv>) dan [tabulasi gender–keluarga](<results/semantic_audit/gender_family_crosstab.csv>).

### 3.2 Tabulasi silang pekerjaan—uji kesamaan baris, bukan hanya frekuensi

| NAME_INCOME_TYPE | Sentinel DAN organisasi XNA | Keduanya bukan kode khusus | Total |
|---|---:|---:|---:|
| Pensioner | 55.352 | 10 | 55.362 |
| Unemployed | 22 | 0 | 22 |
| Working | 0 | 158.774 | 158.774 |
| Commercial associate | 0 | 71.617 | 71.617 |
| State servant | 0 | 21.703 | 21.703 |
| Student | 0 | 18 | 18 |
| Businessman | 0 | 10 | 10 |
| Maternity leave | 0 | 5 | 5 |

**Verifikasi E:** `DAYS_EMPLOYED==365243` dan `ORGANIZATION_TYPE=='XNA'` mempunyai kesamaan mask baris tepat pada data lokal: keduanya benar 55.374, keduanya salah 252.137, masing-masing arah mismatch **0**. Ini dihitung eksplisit, bukan disimpulkan dari jumlah yang sama. [Tabulasi tiga arah](<results/semantic_audit/employment_exact_crosstab.csv>) · [daftar mismatch kosong dengan header](<results/semantic_audit/employment_mismatch_ids.csv>).

Semua kode terkait kategori Pensioner/Unemployed, tetapi **tidak semua Pensioner berkode khusus**: ada 10 pengecualian. Jadi jangan memakai aturan “Pensioner selalu tidak bekerja” atau “Pensioner selalu XNA” sebagai fakta universal. NAME_INCOME_TYPE adalah jenis pendapatan, tidak harus menjadi status pekerjaan eksklusif. Pola mendukung ketidakberlakuan informasi kerja pada mayoritas pensiunan/penganggur, namun tidak menjelaskan secara resmi cara kode itu dibuat atau membuktikan semua NaN pekerjaan struktural.

### 3.3 Missing struktural, hari relatif, dan temuan relevan lain

- `OWN_CAR_AGE`: seluruh 202.924 bukan pemilik mobil (`FLAG_OWN_CAR=N`) mempunyai NaN; 104.582 pemilik mempunyai umur mobil, **5 pemilik masih NaN**. Ini membedakan kemungkinan tidak berlaku dari informasi hilang yang sungguh relevan; jangan mengimputasi atau menilai kedua kondisi identik tanpa kebijakan.
- `OCCUPATION_TYPE`: Pensioner 55.357/55.362 missing (5 terisi), Unemployed 22/22 missing; Working 24.920/158.774 missing dan Commercial associate 12.297/71.617 missing. Jadi NaN pekerjaan tidak semata identik dengan pensiun. [Tabulasi missing struktural](<results/semantic_audit/structural_missing_crosstabs.csv>).
- **Blok bangunan:** 145.755 observasi (47,3983%) mempunyai semua 47 fitur hunian missing; 78.595 semuanya terisi. Terdapat 42 pasangan fitur hunian dengan missing mask identik tepat; ini bukan pernyataan seluruh nilai fiturnya identik. Pola ini tidak mengungkap apakah setiap kasus adalah tidak berlaku, tidak dikumpulkan, atau tidak diketahui. [Pola missing hunian](<results/semantic_audit/housing_missing_patterns.csv>) dan [pasangan mask](<results/semantic_audit/housing_missing_pairs.csv>) memisahkan co-missing dari missing hanya satu sisi.
- `DAYS_BIRTH` seluruhnya negatif (−25.229 sampai −7.489); `DAYS_REGISTRATION` ≤0 dengan 80 nol; `DAYS_ID_PUBLISH` ≤0 dengan 16 nol; `DAYS_LAST_PHONE_CHANGE` ≤0 dengan 37.672 nol dan 1 NaN. `DAYS_EMPLOYED` selain sentinel mempunyai 252.135 negatif dan 2 nol. **Negatif/0 tidak otomatis rusak atau missing.** Ada satu nilai `DAYS_REGISTRATION` nonintegral; karena itu jangan memaksakan semua offset hari mentah integral tanpa pemeriksaan presisi.
- Empat social counts teramati integral/nonnegatif; masing-masing 1.021 NaN. Pada 306.490 pasangan lengkap, pelanggaran `DEF_30>OBS_30` dan `DEF_60>OBS_60` masing-masing **0**. Nilai tinggi OBS_30=348/OBS_60=344 belum terbukti sentinel; perlu validasi, bukan penghapusan otomatis.
- Enam `AMT_REQ_CREDIT_BUREAU_*` teramati integral/nonnegatif, masing-masing 41.519 NaN. QRT maksimum 261 tampak ekstrem, tetapi tidak ada bukti cukup untuk menyebutnya kode missing; tidak dimask. Kategori Other/Other_B, kode angka 0/1, batas 0/1 ukuran ternormalisasi, dan nol inquiry tidak ditafsirkan sebagai missing tanpa bukti.

Rincian nilai aktual semua fitur ada pada [profil prediktor](<results/semantic_audit/predictor_profile.csv>), [frekuensi kategori](<results/semantic_audit/categorical_counts.csv>), dan [pemeriksaan hari/inquiry/sosial](<results/semantic_audit/days_credit_social_numeric_checks.csv>). Tidak ditemukan dasar dokumenter untuk konversi massal kode tidak biasa lain; ini bukan jaminan dataset bebas semua anomali.

## 4. Feature Semantics

Tabel lengkap satu baris per prediktor tersedia pada [kamus audit 120 fitur](<HOME_CREDIT_FEATURE_DICTIONARY_AUDITED.csv>). Definisi sumber dipertahankan verbatim dalam bahasa Inggris agar tidak mengarang perluasan makna; interpretasi operasional dijelaskan di bawah. Dtype aktual adalah hasil pembacaan dengan pandas versi audit, bukan bukti tipe semantik: `float64` dapat menyimpan hitungan dan `str` merupakan kategori, bukan numerik.

| Kelompok | Tipe semantik dan perlakuan yang masuk akal | Masalah yang harus dibedakan |
|---|---|---|
| `DAYS_BIRTH`, `DAYS_EMPLOYED`, `DAYS_REGISTRATION`, `DAYS_ID_PUBLISH`, `DAYS_LAST_PHONE_CHANGE` | Waktu relatif terhadap aplikasi; tanda negatif umumnya sah. Numerik untuk jarak, bukan kategori hanya karena integral. | `365243` bukan durasi kerja biasa. Nol bukan otomatis missing; jangan mengubah semua nilai negatif menjadi NaN. Hari sintetis pecahan memerlukan aturan presisi, berbeda urgensinya dari jumlah anak pecahan. |
| `FLAG_*`, enam indikator perbedaan alamat | Biner; kode 0 dan 1 sama-sama informasi sah; masukkan mask kategorikal SMOTENC. `FLAG_OWN_CAR`/`FLAG_OWN_REALTY` memakai Y/N. | Tidak adanya dokumen/telepon (0) bukan missing. Kamus mereplikasi deskripsi `FLAG_WORK_PHONE` sebagai home phone, tumpang tindih dengan `FLAG_PHONE`; ini ambiguitas dokumentasi, bukan bukti kolom identik. Jangan mengganti nama/makna diam-diam. |
| `NAME_*`, `CODE_GENDER`, `ORGANIZATION_TYPE`, `OCCUPATION_TYPE`, kategori bangunan | Kategorikal; pendidikan secara substantif ordinal, tetapi kategorikal pada SMOTENC defensibel agar tidak menginterpolasi tingkat pendidikan. | Unknown dan XNA tidak boleh diberi arti kategori substantif baru. Label seperti Other, Other_B, Industry:type dan Business Entity Type adalah kategori yang tersedia, bukan otomatis missing. |
| `REGION_RATING_CLIENT*` | Ordinal (1/2/3); mask kategorikal menghindari rating 1,6. | Mengorbankan informasi jarak ordinal di generator dapat dicatat, tidak harus menambah algoritma. |
| Hari dan jam aplikasi | Hari pekan kategorikal/siklik; jam diskret siklik 0–23. Kategorikal pada precheck mencegah jam pecahan. | Kedekatan 23 dan 0 tidak terwakili sebagai jarak siklik; peningkatan opsional, bukan alasan menambah framework. |
| `CNT_CHILDREN`, `CNT_FAM_MEMBERS` | Hitungan diskret nonnegatif. | Penyimpanan float karena NaN tidak membuat ukuran keluarga kontinu; imputasi median dan interpolasi dapat menghasilkan pecahan. |
| `OBS_*_CNT_SOCIAL_CIRCLE`, `DEF_*_CNT_SOCIAL_CIRCLE` | Hitungan diskret, periksa nonnegatif dan DEF ≤ OBS pada pasangan yang teramati. | SMOTENC tidak menjamin kendala gabungan kategori/numerik; jangan menyamakan social count ekstrem dengan sentinel tanpa bukti. |
| `AMT_REQ_CREDIT_BUREAU_*` | **Jumlah inquiry**, bukan uang meskipun awalan AMT; enam jendela waktu. | Nol sah, NaN bukan nol. Kamus menyebut pengecualian jendela sebelumnya pada DAY/WEEK/MON/QRT/YEAR; deskripsi YEAR mengandung salah ketik “one day year”, sehingga jangan mengarang presisi batas waktunya. Dukungan integral sintetis perlu diperiksa. |
| `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `AMT_ANNUITY`, `AMT_GOODS_PRICE` | Besaran moneter numerik; pecahan sah. | Unit mata uang dan periodisasi yang tidak ditulis kamus jangan dikarang. Nilai ekstrem tidak otomatis salah/sentinel; tidak ada winsorisasi baru. |
| `EXT_SOURCE_1/2/3`, `REGION_POPULATION_RELATIVE` | Skor eksternal/populasi relatif yang dinormalisasi. | Identitas provider, formula, kalibrasi probabilitas, dan mekanisme missing tidak dijelaskan. Jangan menyatakan EXT_SOURCE sebagai probabilitas default atau biro tertentu. |
| 42 ukuran bangunan `_AVG/_MODE/_MEDI` + `TOTALAREA_MODE` | Ukuran bangunan yang **sudah dinormalisasi**; numerik kontinu untuk generator, meskipun nama asli mencakup lantai/lift/tahun. | Bukan raw jumlah lift, tahun kalender, atau meter persegi; jangan membulatkan sebagai count mentah dan jangan inverse-normalisasi tanpa formula. `_MODE` tidak selalu berarti kategori. |

Blok bangunan keseluruhan mencakup 47 fitur: 43 ukuran numerik dan empat kategori (`FONDKAPREMONT_MODE`, `HOUSETYPE_MODE`, `WALLSMATERIAL_MODE`, `EMERGENCYSTATE_MODE`). Agregat AVG/MODE/MEDI berulang menggambarkan aspek sama, tetapi **bukan otomatis kolom duplikat**. Missing yang bergerak bersama dapat membuat domain hunian menanggung 47/120 = 39,17% skor kelengkapan. Kemiripan missing mask bukan bukti kesamaan seluruh nilai. Indikator dokumen yang hampir selalu terisi juga menaikkan kelengkapan tanpa menjamin kualitas informasi; ini keterbatasan konstruk, bukan bug `notna()`.

## 5. Implications for CG-HIL

### Jawaban enam pertanyaan utama

1. **Apakah `notna()` masuk akal?** Ya, sebagai ukuran operasional proporsi field terisi yang transparan dan reproduksibel. Tidak cukup untuk disebut kelengkapan semantik/kualitas informasi: sentinel terhitung hadir, missing struktural terhitung absen, dan kolom dari domain yang berulang mendapat bobot lebih besar. Pertahankan sebagai baseline; tuliskan batas konstruknya.
2. **Adakah kode yang memerlukan perlakuan berbeda?** `DAYS_EMPLOYED=365243` harus dibedakan dari durasi kerja normal pada generator. Unknown gender/status keluarga merupakan kandidat informasi tak diketahui pada skor; XNA organisasi tidak boleh otomatis disamakan dengan XNA gender karena hubungannya dengan applicability pekerjaan. Pemetaan final memerlukan persetujuan dan dokumentasi, bukan dugaan bahwa kamus menjelaskan semua kode.
3. **Apakah missing struktural dapat mendorong U?** Dapat, jika missing tersebut memang mencerminkan ketidakberlakuan fitur. Umur mobil tanpa kepemilikan mobil tidak mengurangi kecukupan informasi seperti umur mobil yang tidak tercatat pada pemilik mobil. Pekerjaan pensiunan/nonpekerja juga tidak sama dengan pekerjaan aktif yang tidak dilaporkan. Missing hunian berkelompok dapat mendominasi skor. Pola observasional mendukung kemungkinan ini, tetapi tidak mengidentifikasi mekanisme missing (MCAR/MAR/MNAR) atau alasan setiap NaN.
4. **Apakah mask SMOTENC terdahulu sesuai?** Secara garis besar benar: 51 kategorikal mencakup 16 string dan 35 kode numerik; 69 numerik mencakup uang, waktu, ukuran ternormalisasi dan hitungan. Flag/rating/jam tidak diinterpolasi. Kelemahannya bukan semua numerik harus kategorikal: 12 fitur hitungan mentah tetap numerik sehingga dukungan integral belum dijaga, sedangkan sentinel durasi diperlakukan numerik biasa. Pendidikan ordinal dapat tetap kategorikal. Tidak membulatkan kolom bangunan yang sudah dinormalisasi.
5. **Risiko sintetis tidak masuk akal?** Ada: pecahan anak/anggota keluarga/inquiry/default sosial; angka antara sentinel dan durasi sah; kombinasi Pensioner/organisasi/pekerjaan/durasi yang tidak koheren; umur mobil pada bukan pemilik; hubungan keluarga dan usia/tenur yang tidak diperiksa. Rentang E dan domain kategori per kolom tidak menyingkirkan risiko tersebut. Relasi linear murni yang sudah dipenuhi kedua endpoint dapat terjaga oleh interpolasi bersama, tetapi imputasi dan pemilihan kategori terpisah membuat validasi tetap diperlukan. Ini risiko teridentifikasi, bukan klaim semua sampel full melanggarnya.
6. **Perubahan minimum?** Spesifikasi representasi sentinel, kebijakan integral untuk hitungan mentah, dan assertion semantik lintas fitur sebelum model. Jangan langsung mengganti skor dengan framework baru. Jika baseline `notna()` dipertahankan, nyatakan ini pilihan operasional sadar keterbatasan; jika memakai masking, bekukan kebijakan dan ulangi penentuan kelompok train-only.

### Analisis sensitivitas tanpa model

Split identik audit sebelumnya: train **215.257**, validasi **46.127**, uji **46.127**; train positif **17.377**, 120 fitur, tidak ada fitur konstan train yang dibuang. E ditetapkan `c>τ`, U `c≤τ`; tie tidak diacak. Skenario hanya menghitung mask/score diagnostik di memori; dataset dan pipeline penelitian tidak diubah.

| Skenario | τ positif train | E | U | S | w_U = 1+S/U | Total bobot positif n1+2S | Positif tepat τ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline `notna()` | 0,60000000 | 8.636 | 8.741 | 8.636 | 1,98798764 | 34.649 | 2.794 |
| Mask `365243` saja | 0,60000000 | 8.635 | 8.742 | 8.635 | 1,98776024 | 34.647 | 2.744 |
| Mask keempat kode prioritas | 0,60000000 | 8.635 | 8.742 | 8.635 | 1,98776024 | 34.647 | 2.743 |
| Applicable-aware eksploratif | 0,60000000 | 8.636 | 8.741 | 8.636 | 1,98798764 | 34.649 | 2.743 |

Skenario applicable-aware **hanya** mengeluarkan `DAYS_EMPLOYED` dan `ORGANIZATION_TYPE` dari pembilang dan penyebut pada seluruh Pensioner/Unemployed, sambil memask kode gender/family. Denominator menjadi 118 untuk grup tersebut, 120 lainnya. Umur mobil dan occupation belum disesuaikan. Ini stress test kebijakan hipotetis, **bukan skor applicability yang telah divalidasi**; khususnya ada 10 Pensioner dengan durasi/organisasi teramati yang ikut dikeluarkan pada skenario ini.

Dampak skor secara deterministik: mask satu sentinel menurunkan `c` sebesar 1/120 = 0,00833333 pada baris berkode; mask pasangan sentinel–organisasi menurunkan 2/120 = 0,01666667. Gender/family masing-masing mengurangi 1/120 pada baris terkait. Applicable-aware menggunakan jumlah field hadir yang tersisa /118, bukan sekadar menaikkan semua skor nonpekerja. Nilai skor per baris seluruh train tersedia dalam [sensitivitas keanggotaan train](<results/semantic_audit/train_membership_sensitivity.csv>).

Pada positif train, skenario mask sentinel maupun keempat kode memindahkan **1 E→U**, tidak ada U→E; applicable-aware mempertahankan keanggotaan baseline tepat, bukan hanya jumlahnya. [Transisi E/U](<results/semantic_audit/positive_EU_transitions.csv>) dan [transisi per jenis pendapatan](<results/semantic_audit/positive_income_EU_transitions.csv>) tersedia untuk verifikasi.

Bobot positif asli M1 berubah 1,99395753→1,99384244 pada kedua skenario masking; bobot positif asli M3 berubah 1,49697877→1,49692122. Baseline/applicable-aware identik untuk bobot agregat. [Ringkasan sensitivitas lengkap](<results/semantic_audit/sensitivity_summary.csv>). Perubahan kelompok kecil **tidak membenarkan interpolasi sentinel**, karena validitas jarak/durasi merupakan persoalan berbeda dari sensitivitas median. Demikian pula jumlah E/U yang stabil tidak membuktikan skor bebas bias struktural. Tidak ada performa prediksi digunakan untuk membandingkan skenario.

## 6. Recommended Minimal Changes

### A. Wajib untuk validitas implementasi sebelum eksperimen utama

1. **Bekukan kontrak semantik generator, terutama `DAYS_EMPLOYED=365243`.** Jangan memperlakukan sentinel sebagai durasi kontinu atau menginterpolasinya dengan lama kerja normal. Usulan minimum untuk dibahas: pisahkan penanda status khusus, keluarkan sentinel dari nilai durasi generator, gunakan imputasi train-only yang disetujui, dan periksa konsistensinya dengan status pendapatan/organisasi. Ini usulan, **belum diimplementasikan**, dan tidak otomatis berarti dua kolom harus dikeluarkan dari skor kelengkapan.
2. **Tetapkan kebijakan dukungan hitungan sintetis secara eksplisit.** Kedua CNT, empat social counts, dan enam inquiry counts harus diuji integral/nonnegatif setelah inverse scaling. Pilihan minimum yang dapat direview: proyeksi/bulatkan hanya kolom hitungan mentah dengan aturan deterministik serta pengecekan kendala setelahnya; alternatif mask kategorikal hanya jika dukungan dan jumlah kategori memang layak. Tidak mengubah semua angka menjadi kategori, tidak membulatkan nilai hunian ternormalisasi. Pembulatan tidak sendirinya menjamin hubungan keluarga atau pekerjaan valid.
3. **Perluas assertion semantik.** Pertahankan domain biner/kategori, tambahkan integral count, DEF ≤ OBS, kewajaran umur/tenur, serta tabulasi joint status kerja–organisasi–durasi dan kepemilikan mobil–umur mobil pada sintetis. Bedakan aturan keras yang didukung definisi dari pengecualian yang memang sudah ada pada sumber; dokumentasikan jumlah pelanggaran dan perlakuannya sebelum model. Tidak perlu algoritma baru.
4. **Kunci satu spesifikasi score/mask/daftar fitur/aturan tie sebelum M0–M4.** Jika memilih semantic masking, hitung ulang skor sebelum imputasi pada semua observasi dengan aturan tetap; τ dan E/U hanya dari train positif. Terapkan konsisten lintas metode yang relevan, bukan memilih kebijakan berdasarkan performa. Pertahankan jejak versi dan tabel sensitivitas.

### B. Risiko yang dapat ditangani tanpa mengganti strategi CG-HIL

- Untuk `CODE_GENDER=XNA` dan `NAME_FAMILY_STATUS=Unknown`, kandidat minimum adalah menandainya tidak terinformasi dalam skor, sambil mempertahankan kategori missing/unknown eksplisit untuk generator. Jangan membuang observasi hanya karena langka; dampak E/U harus dilaporkan, bukan diasumsikan.
- `ORGANIZATION_TYPE=XNA` pada status nonkerja dapat memuat informasi ketidakberlakuan. Mempertahankannya sebagai kategori tersendiri defensibel; memask sebagai missing juga skenario audit, **bukan satu-satunya kebijakan benar**. Jangan menyamakan semua XNA di semua kolom.
- Pertahankan `notna()` sebagai baseline operasional dengan label “kelengkapan rekaman teramati”, bukan kualitas atau kecukupan substantif. Nyatakan potensi missing struktural dan dominasi domain bangunan. E berarti relatif lebih banyak field terisi, bukan pasti calon peminjam dengan informasi paling relevan.
- StandardScaler dan imputasi generator yang sudah ada tetap berstatus usulan teknis, tidak otomatis disahkan hanya karena PASS. Audit ini tidak melakukan imputasi/normalisasi baru pada data penelitian.

### C. Peningkatan opsional—bukan syarat minimum dan bukan perubahan yang telah disetujui

Skor applicable-aware, skor berbobot per domain untuk mengurangi penggandaan hunian, perlakuan jarak ordinal/siklik, dan analisis representasi demografis E/U dapat dipertimbangkan kemudian. Denominator per-observasi memerlukan pembuktian applicability, terutama kasus pengecualian; jangan mengadopsinya hanya karena hasil E/U lebih seimbang. Tidak menghapus fitur berkorelasi atau mendesain skor baru pada audit ini.

## 7. Final Assessment

**Rancangan dapat dilanjutkan setelah revisi kecil pada spesifikasi prapemrosesan dan validasi generator; belum layak menyebut validitas semantik sudah selesai.** Tidak ditemukan alasan dari audit ini untuk mengganti RQ, CG-HIL, atau menambah algoritma/dataset. Namun menginterpolasi sentinel lama kerja sebagai durasi normal merupakan masalah material pada representasi fitur tertentu yang perlu diselesaikan sebelum eksperimen utama, bukan disembunyikan oleh PASS teknis.

- **Sudah terverifikasi:** cakupan kolom lokal dan definisi yang tersedia dalam salinan kamus; frekuensi serta hubungan baris-ke-baris kode khusus; tipe aktual vs tipe semantik; hasil sensitivitas train-only; tidak berubahnya hash sumber selama diagnostik. PASS terdahulu hanya memverifikasi pemeriksaan yang ditulis pada precheck.
- **Belum diketahui:** definisi resmi kode sentinel/XNA, penyebab missing setiap baris, applicability pasti pada semua pengecualian pekerjaan, formula normalisasi dan identitas EXT_SOURCE, serta jumlah pelanggaran semantik pada sintetis full terdahulu (baris sintetis tidak disimpan oleh skrip precheck). Tidak ada klaim keunggulan prediksi.
- **Dipertahankan:** dataset asli, split/seed, perhitungan skor sebelum imputasi, pemisahan fit train dari validasi/uji, E sebagai sumber sintesis dan U sebagai penerima bobot sesuai rancangan, serta semua nilai negatif/0 yang sah. Tetap simpan baseline literal agar perbedaan kebijakan dapat dijelaskan.
- **Diperbaiki setelah persetujuan:** representasi sentinel durasi kerja, kebijakan hitungan sintetis dan assertion gabungan, definisi completeness yang eksplisit, serta dokumentasi keterbatasan missing struktural/domain berulang.
- **Mengapa:** keberhasilan eksekusi, rentang numerik, dan kategori valid per kolom tidak menjamin observasi sintetis masuk akal atau skor mencerminkan kecukupan informasi. Perbaikan minimum tersebut menjaga validitas implementasi tanpa mengubah strategi penelitian.

Kamus audit juga mencatat ambiguitas deskripsi inquiry YEAR (“one day year”) dan subtipe telepon. Keduanya tidak menghalangi perlakuan dasar sebagai hitungan/biner, tetapi menghalangi klaim makna yang lebih rinci tanpa sumber tambahan.

**Belum ada rekomendasi yang dianggap telah disetujui mahasiswa.** Review terlebih dahulu khususnya pilihan apakah kategori non-applicable tetap dihitung terisi, dimask, atau dikeluarkan dari denominator; audit tidak memutuskan kebijakan tersebut.

## Reproduksibilitas dan batas pekerjaan

Diagnostik tidak melatih XGBoost, tidak menjalankan M0–M4, tidak mencari hiperparameter, dan tidak memilih kebijakan dengan hasil prediksi. Statistik keseluruhan dipakai untuk audit deskriptif; median, penentuan E/U, dan simulasi bobot dihitung hanya pada split train yang direplikasi. Pemakaian statistik seluruh data ini bukan izin memakainya untuk fit prapemrosesan eksperimen.

Perintah untuk mereproduksi diagnostik (tidak mengubah data asli):

```bash
.venv/bin/python semantic_audit_diagnostics.py --input application_train.csv --out results/semantic_audit
.venv/bin/python build_semantic_dictionary.py
```

[Kode diagnostik](<semantic_audit_diagnostics.py>) · [Pembentuk kamus](<build_semantic_dictionary.py>) · [Kamus audit 120 fitur](<HOME_CREDIT_FEATURE_DICTIONARY_AUDITED.csv>) · [Hasil diagnostik terstruktur](<results/semantic_audit/diagnostics.json>).

**Audit berhenti pada rekomendasi untuk review mahasiswa. Tidak ada perubahan rancangan, data sumber, Bab I/Bab III, RQ, ataupun implementasi prapemrosesan penelitian yang diterapkan.**
