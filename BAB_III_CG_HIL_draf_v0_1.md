# BAB III — METODOLOGI PENELITIAN
## Draf operasional CG-HIL v0.1

**Tanggal:** 29 Oktober 2026  
**Status:** Usulan rancangan teknis untuk pembahasan pembimbing dan uji kelayakan implementasi. **Bukan** hasil eksperimen atau keputusan final mahasiswa/pembimbing.  
**Judul kerja penelitian:** Pengembangan Metode Hibrida Berbasis Kelengkapan Informasi untuk Penanganan Ketidakseimbangan Kelas pada Prediksi Risiko Gagal Bayar Kredit Konsumen.

> **Acuan utama:** `THESIS_STATE.md` (28 Oktober 2026), `BAB_I_CG_HIL_credit_scoring.md` (28 Oktober 2026), dan `proposal_skeleton.md`. Berkas `rancangan_hybrid_credit_scoring_2026.md` disebut dalam state, tetapi tidak tersedia di materi yang dapat diakses saat penyusunan draf ini. Angka dan rumus teknis yang baru ditentukan di sini adalah **usulan v0.1**.

## Ringkasan rancangan

Penelitian mengembangkan **Completeness-Guided Hybrid Imbalance Learning (CG-HIL)** sebagai mekanisme penentuan perlakuan ketimpangan kelas pada tingkat observasi. Pada data latih, observasi minoritas yang lebih lengkap digunakan sebagai sumber SMOTENC secara terbatas; observasi minoritas yang kurang lengkap tidak digunakan untuk membentuk sampel sintetis, tetapi tetap diikutkan dan diberi bobot lebih besar. Semua observasi asli yang sah dipertahankan. Model prediksi tunggal yang digunakan adalah XGBoost.

Klaim yang hendak diperiksa: **apakah aturan alokasi perlakuan berdasarkan kelengkapan memberi manfaat dibanding penyeimbangan hibrida tanpa aturan tersebut**, bukan apakah SMOTENC, bobot sampel, atau XGBoost merupakan algoritma baru.

---

## III.1 Identifikasi Masalah dan Motivasi

Dataset *Home Credit Default Risk* pada `application_train.csv` memuat 307.511 observasi berlabel, dengan 24.825 observasi `TARGET = 1` (sekitar 8,07%) menurut dokumen Bab I. Target menggambarkan kondisi kesulitan pembayaran sesuai definisi operasional dataset; bukan seluruh bentuk gagal bayar secara umum.

Dua persoalan yang diperiksa adalah:

1. **Ketidakseimbangan kelas:** observasi `TARGET = 1` jauh lebih sedikit daripada kelas lain.
2. **Ketidaklengkapan informasi:** sebagian fitur pemohon berisi nilai kosong, dengan kelengkapan yang dapat berbeda antarobservasi.

Metode oversampling menambah contoh minoritas, tetapi sintesis dari observasi dengan banyak nilai kosong memerlukan keputusan imputasi dan bisa mengubah representasi informasi. Sebaliknya, pembobotan dapat memperbesar kontribusi observasi tanpa membuat contoh sintetis. Penelitian menguji **mekanisme memilih perlakuan tersebut** berdasarkan tingkat kelengkapan observasi, tidak menyimpulkan terlebih dahulu bahwa observasi lebih lengkap pasti lebih representatif.

**Catatan batas masalah:** sebagian nilai kosong mungkin bersifat struktural atau berarti *tidak berlaku*, bukan mutu informasi buruk. Skor kelengkapan pada draf ini adalah ukuran operasional jumlah fitur yang tersedia, **bukan ukuran kualitas atau kebenaran data**. Implikasi ini dibahas sebagai keterbatasan interpretasi.

Keluaran tahap III.1: rumusan masalah, dasar literatur, deskripsi data, dan hipotesis rancangan.

## III.2 Penentuan Tujuan Solusi

Artefak yang dikembangkan harus memenuhi kriteria berikut:

1. Memisahkan observasi minoritas menurut kelengkapan fitur yang dihitung sebelum imputasi.
2. Membatasi sumber pembangkitan sintetis pada kelompok minoritas yang relatif lengkap.
3. Mempertahankan seluruh observasi asli yang sah, termasuk yang memiliki nilai kosong.
4. Memberi kontribusi pembelajaran kepada kelompok minoritas kurang lengkap melalui `sample_weight`.
5. Menghasilkan satu model XGBoost yang dapat dievaluasi secara *offline*.
6. Mengisolasi manfaat aturan kelengkapan melalui pembanding hibrida global dengan **jumlah sintetis dan total bobot efektif kelas positif yang sama**.

**RQ1:** bagaimana metode dirancang dan dijalankan? Bukti: spesifikasi, kode, catatan pembagian kelompok, jumlah sintesis dan bobot yang digunakan, serta demonstrasi.

**RQ2:** apakah aturan kelengkapan bermanfaat? Bukti: perbandingan PR-AUC pada data uji yang sama terhadap baseline dan terutama terhadap hibrida global; metrik pelengkap untuk melihat kompromi deteksi.

## III.3 Perancangan dan Pengembangan Artefak

### III.3.1 Data dan unit analisis

- Sumber utama: `application_train.csv` dari kompetisi Home Credit.
- Unit analisis: **satu aplikasi kredit**.
- Variabel keluaran: `TARGET ∈ {0,1}`.
- Fitur prediktor: kolom selain `TARGET` dan pengenal `SK_ID_CURR`.
- Tabel riwayat tambahan tidak dipakai dalam rancangan awal.
- Tidak ada penghapusan baris hanya karena banyak nilai kosong. Kolom yang seluruhnya kosong atau tidak memiliki variasi boleh dikeluarkan berdasarkan **data latih saja**, dengan pencatatan kolom yang dikeluarkan; aturan itu berlaku sama pada semua metode.

### III.3.2 Pembagian data dan pencegahan kebocoran

**Usulan pembagian awal:** 70% pelatihan, 15% validasi, 15% pengujian, secara acak terstratifikasi menurut `TARGET`, dengan `random_state=42` dan pemeriksaan bahwa pengenal aplikasi tidak tumpang tindih.

Urutan proses wajib:

1. Pisahkan data menjadi latih, validasi, dan uji.
2. Tentukan fitur dan parameter prapemrosesan hanya dari data latih.
3. Hitung ambang kelengkapan hanya dari observasi minoritas **data latih**.
4. Bentuk sampel sintetis hanya dari data latih.
5. Gunakan validasi untuk menentukan ambang klasifikasi dan konfigurasi yang memang telah diizinkan protokol.
6. Gunakan data uji **satu kali untuk pelaporan final**, tanpa menyesuaikan metode berdasarkan hasilnya.

Karena dataset tidak menyediakan penanda waktu kalender yang siap digunakan untuk pengujian kronologis, pembagian acak ini **tidak boleh diklaim** menguji kemampuan generalisasi antarkurun waktu.

### III.3.3 Skor kelengkapan

Untuk observasi \(i\) dan himpunan fitur prediktor terpilih \(F\), definisikan:

\[
c_i = \frac{1}{|F|}\sum_{j \in F} \mathbf{1}(x_{ij}\ \text{tersedia})
\]

di mana `1` menandakan nilai tidak kosong dan `0` nilai kosong, sebelum imputasi. `SK_ID_CURR` dan `TARGET` tidak digunakan untuk menghitung skor.

**Usulan aturan awal:** ambang \(\tau\) adalah median \(c_i\) di antara observasi `TARGET=1` pada data latih. Definisikan:

- \(E=\{i:y_i=1,\ c_i>\tau\}\): minoritas relatif lengkap, calon sumber sintesis.
- \(U=\{i:y_i=1,\ c_i\leq\tau\}\): minoritas relatif tidak lengkap, calon penerima bobot.

Aturan sengaja menggunakan `>` dan `≤` untuk menangani skor yang sama persis dengan median secara deterministik. Proporsi anggota tiap kelompok **tidak dijamin 50:50** karena skor dapat memiliki banyak nilai yang sama.

**Pemeriksaan kelayakan sebelum eksperimen penuh:** pastikan \(n_E\geq 6\) untuk `SMOTENC(k_neighbors=5)`, \(n_U>0\), dan terdapat variasi kelengkapan yang masuk akal. Jika gagal, **jangan mengganti aturan secara diam-diam**; catat kegagalan dan evaluasi revisi desain.

### III.3.4 Ukuran sintesis dan bobot (usulan v0.1)

Tuliskan \(n_1=n_E+n_U\), yaitu seluruh observasi minoritas data latih.

Untuk menjadikan sintesis terbatas dan mencegah bobot individu ekstrem, tetapkan anggaran dasar:

\[
S=\min(n_E,n_U)
\]

- CG-HIL membentuk **\(S\) sampel sintetis** dari kelompok \(E\).
- Seluruh observasi mayoritas serta semua observasi minoritas asli tetap mendapat bobot dasar **1**.
- Seluruh observasi minoritas asli pada kelompok \(U\) mendapat bobot:

\[
w_U=1+\frac{S}{n_U}
\]

- Sampel sintetis mendapat bobot **1**.
- Dengan demikian \(1<w_U\leq 2\) dan bobot efektif total positif menjadi:

\[
W_1=n_1+2S
\]

Rumus tersebut **pilihan desain awal** untuk mengendalikan intensitas penanganan ketimpangan, bukan angka optimal yang telah terbukti. Tidak ada klaim bahwa setelah koreksi kelas menjadi seimbang 1:1.

**Contoh hitungan ilustratif (bukan statistik Home Credit):** jika ada 100 contoh positif dengan \(n_E=45\), \(n_U=55\), maka \(S=45\) dan \(w_U=1+45/55 \approx 1{,}818\). Bobot efektif positif adalah \(100+45+45=190\). Semua 100 baris positif asli tetap dipakai.

### III.3.5 Prapemrosesan dan pembentukan contoh sintetis

Dua representasi digunakan demi menjaga makna nilai kosong pada observasi asli:

1. **Representasi untuk SMOTENC (generator):** nilai numerik kosong diisi median yang dihitung dari data latih; nilai kategorikal kosong diberi kategori khusus `__MISSING__`. Prosedur ini diterapkan pada sumber generator sebelum SMOTENC, dengan tipe fitur kategorikal ditetapkan eksplisit.
2. **Representasi untuk XGBoost (model):** nilai numerik kosong pada seluruh observasi **asli** tetap berupa `NaN`, karena pohon keputusan XGBoost mendukung pengolahan nilai kosong. Nilai kategorikal menggunakan encoding yang sama untuk semua metode, termasuk kategori `__MISSING__`; encoder dipelajari hanya dari data latih.

Sampel sintetis yang dihasilkan generator berada dalam ruang fitur yang telah disiapkan untuk SMOTENC, lalu dikonversi menggunakan encoder model yang sama. Baris asli **tidak digantikan** dengan baris yang sudah diimputasi pada representasi model; karena itu pola `NaN` numerik aslinya tetap tersedia bagi XGBoost. Konsistensi tipe kolom, nama kolom, urutan fitur, dan kategori hasil sintesis wajib diuji.

**Detail implementasi penting:** `SMOTENC` tidak dijalankan dengan input yang *hanya* berisi kelas \(E\), sebab API resampling memerlukan sampel berlabel untuk mengenali kelas. Buat input generator yang berisi **observasi mayoritas dari data latih + minoritas \(E\)**, jalankan `SMOTENC(sampling_strategy={1: n_E + S}, k_neighbors=5, random_state=42)`, kemudian **ambil hanya \(S\) baris sintetis baru**. Pelatihan XGBoost memakai kembali **seluruh observasi asli**, bukan hanya subset generator. Pemeriksaan jumlah dan label hasil sintetis merupakan syarat verifikasi kode.

Untuk pembanding oversampling global, prosedur yang sama digunakan dengan **seluruh minoritas** sebagai sumber generator, bukan hanya \(E\). Jumlah sampel mayoritas pada input generator harus cukup sehingga `sampling_strategy` yang diminta valid. Pengaturan awal menggunakan seluruh mayoritas latih untuk menghindari prosedur tambahan.

### III.3.6 Lima konfigurasi yang dibandingkan

Lima konfigurasi di bawah selalu memakai pembagian data, fitur, prapemrosesan model, dan parameter XGBoost yang sama. Untuk empat metode penanganan ketimpangan, **total bobot efektif kelas positif dibuat sama, yaitu \(n_1+2S\)**.

| Konfigurasi | Sumber sintesis | Sampel sintetis | Bobot observasi positif asli |
|---|---|---:|---|
| M0 — XGBoost standar | Tidak ada | 0 | Semua 1 |
| M1 — Pembobotan saja | Tidak ada | 0 | Semua \(1+2S/n_1\) |
| M2 — SMOTENC saja | Seluruh minoritas | \(2S\) | Semua 1 |
| M3 — Hibrida global | Seluruh minoritas | \(S\) | Semua \(1+S/n_1\) |
| M4 — **CG-HIL** | Hanya \(E\) | \(S\) | \(E=1\); \(U=1+S/n_U\) |

**Bobot semua sampel sintetis: 1. Bobot semua observasi mayoritas: 1.**

**M3 adalah pembanding utama untuk menguji kontribusi mekanisme seleksi:** M3 dan M4 menghasilkan jumlah sampel sintetis yang sama, memiliki total bobot efektif positif sama, dan memakai komponen algoritma sama. Perbedaannya adalah **sumber sintesis serta penerima pembobotan**.

Kesetaraan jumlah/bobot tidak berarti distribusi fitur atau efek regularisasi otomatis identik; justru efek dari perbedaan alokasi tersebut yang diuji. Besarnya \(S\), jumlah baris yang dipakai melatih model, dan total bobot per kelas wajib dilaporkan.

### III.3.7 Model dan keluaran artefak

- Model prediksi: `XGBClassifier`, `objective="binary:logistic"`, `tree_method="hist"`, dan `scale_pos_weight=1` agar tidak terjadi pembobotan otomatis di luar desain.
- Parameter kapasitas model (misalnya `max_depth`, `n_estimators`, dan `learning_rate`) **dibekukan sama untuk kelima konfigurasi**. Nilai praktis ditentukan sebelum evaluasi data uji. Tidak diperlukan pencarian hiperparameter besar.
- Hasil tiap model berupa skor prediksi `TARGET=1` pada data validasi/uji.
- Artefak minimum: kode prapemrosesan, implementasi pemilihan \(E/U\), generator SMOTENC, penetapan bobot, pelatihan lima model, skrip evaluasi, serta satu berkas konfigurasi yang dapat direproduksi.
- **Tidak perlu membuat dashboard atau sistem web** untuk membuktikan metode.

### III.3.8 Pseudocode inti CG-HIL

```text
Input: X_train, y_train, selected_features, seed=42
c = fraction_nonmissing(X_train[selected_features])
tau = median(c where y_train == 1)

E = rows where y_train == 1 and c > tau
U = rows where y_train == 1 and c <= tau
assert len(E) >= 6 and len(U) > 0

S = min(len(E), len(U))
w = ones(len(y_train))
w[U] = 1 + S / len(U)

X_gen = fit_training_only_imputers(X_train)
X_pool = concatenate(X_gen[y_train == 0], X_gen[E])
y_pool = concatenate(zeros(n_majority), ones(len(E)))

X_res, y_res = SMOTENC(
    categorical_features=known_categorical_columns,
    sampling_strategy={1: len(E) + S},
    k_neighbors=5,
    random_state=42
).fit_resample(X_pool, y_pool)

X_synthetic = extract_exactly_S_new_rows(X_pool, X_res)
X_model_orig = encode_for_xgboost_with_original_numeric_NaNs(X_train)
X_model_syn = encode_for_xgboost(X_synthetic)
X_final = concatenate(X_model_orig, X_model_syn)
y_final = concatenate(y_train, ones(S))
w_final = concatenate(w, ones(S))

model = XGBClassifier(... fixed_common_parameters ...)
model.fit(X_final, y_final, sample_weight=w_final)
return model, {tau, nE, nU, S, sum_positive_weights}
```

Pseudocode ini menunjukkan logika, **bukan kode yang telah dijalankan**. Terdapat pekerjaan implementasi untuk memastikan jenis matriks dan hasil `fit_resample()` sesuai versi pustaka yang dipakai.

## III.4 Demonstrasi

Demonstrasi dilakukan pada hasil pemisahan data latihan dan contoh dari data uji yang telah dipersiapkan.

Keluaran demonstrasi yang dicatat:

- jumlah observasi asli menurut kelas;
- distribusi skor kelengkapan dan ambang \(\tau\);
- jumlah observasi \(E\) dan \(U\);
- jumlah sampel sintetis \(S\), tanpa sampel sintetis pada validasi/uji;
- bobot untuk masing-masing kelompok dan total bobot efektif;
- keluaran skor prediksi satu atau beberapa observasi pada data uji.

Demonstrasi menyatakan bahwa mekanisme dapat dioperasikan. **Hasil demonstrasi tidak dipakai sebagai pengganti evaluasi efektivitas.**

## III.5 Evaluasi

### III.5.1 Prinsip perbandingan

1. Lima konfigurasi M0–M4 dilatih pada data pelatihan yang sama.
2. Kecuali perlakuan ketimpangan yang sedang dibandingkan, prosedur dan parameter model tetap sama.
3. Keempat metode penanganan ketimpangan M1–M4 memakai \(W_1=n_1+2S\); M3 dan M4 juga memakai jumlah sintetis sama \(S\).
4. Ambang klasifikasi ditentukan **pada data validasi**, bukan pada data uji; semua konfigurasi menggunakan aturan penentuan ambang yang sama.
5. Data uji mempertahankan prevalensi kelas alami dan digunakan untuk evaluasi final.

### III.5.2 Metrik dan keputusan

**Metrik primer:** *Area Under the Precision–Recall Curve* (PR-AUC / *average precision*, dengan definisi implementasi dicatat eksplisit). Metrik ini dipilih untuk memperhatikan kemampuan pemeringkatan pada kelas positif yang relatif jarang.

**Metrik pelengkap:** ROC-AUC, recall, precision, F1, dan *confusion matrix*. Untuk metrik berbasis klasifikasi biner, ambang tiap model dipilih dengan memaksimalkan F1 pada **validasi** menggunakan prosedur yang sama. Ambang ini kemudian dibekukan dan diterapkan pada data uji.

**Perbandingan paling menentukan:**

\[
\Delta \mathrm{PR\mbox{-}AUC} =
\mathrm{PR\mbox{-}AUC}_{M4} -
\mathrm{PR\mbox{-}AUC}_{M3}
\]

- Jika selisih positif: laporkan besarnya manfaat, kompromi precision/recall, dan batas interpretasi.
- Jika mendekati nol: jangan klaim aturan kelengkapan meningkatkan kinerja; simpulkan manfaatnya belum teramati dalam pengujian.
- Jika negatif: laporkan bahwa pendekatan hibrida global lebih baik pada kondisi tersebut, dan bahas kemungkinan penyebab.

Perbedaan harus dinilai dari **besar efek dan ketidakpastian**, bukan hanya tanda positif/negatif. Pemeriksaan ketidakpastian selisih PR-AUC pada **data uji yang sama** (misalnya bootstrap berpasangan) dapat dilakukan bila diperlukan untuk memperkuat klaim; ini tidak mengharuskan menambah model atau dataset.

### III.5.3 Risiko validitas yang relevan

- **Skor kelengkapan belum tentu berarti kualitas informasi:** beberapa fitur mungkin kosong karena tidak berlaku bagi pemohon.
- **Distribusi sintesis:** SMOTENC dari data yang diimputasi dapat menghasilkan contoh dengan karakteristik yang berbeda dari observasi asli.
- **Bobot bukan pengganti sintetis yang sempurna:** walaupun total bobot positif sama, efek pembobotan dan sintesis terhadap XGBoost tidak harus identik.
- **Satu dataset:** temuan tidak otomatis berlaku pada seluruh lembaga pembiayaan atau populasi pemohon.
- **Tidak ada evaluasi dampak kredit nyata:** hasil mengukur prediksi label, bukan keuntungan bank, kerugian ekonomi, atau konsekuensi keputusan operasional.

## III.6 Komunikasi

Hasil disampaikan melalui naskah tesis dan artefak minimal yang dapat direproduksi: kode, konfigurasi tetap, ringkasan karakteristik data, tabel hasil lima konfigurasi, penjelasan mekanisme seleksi, dan keterbatasan. Berkas mentah Home Credit tidak perlu disalin ke repositori publik; penyebarluasan mengikuti ketentuan sumber data.

---

## Gerbang implementasi: pemeriksaan paling menentukan

Sebelum eksperimen penuh, jalankan **satu uji kelayakan singkat** atas data latih:

1. Pastikan fitur `TARGET=1` memang menunjukkan variasi skor kelengkapan sehingga \(E\) dan \(U\) terbentuk secara bermakna.
2. Pastikan input SMOTENC memenuhi tipe numerik/kategorikal yang valid dan mampu menghasilkan tepat \(S\) sampel dari sumber \(E\).
3. Pastikan semua observasi asli tetap ada dan tidak ada `SK_ID_CURR`/label yang masuk ke prediktor.
4. Verifikasi secara programatik bahwa bobot positif pada M1–M4 sama (\(n_1+2S\)) dan jumlah sintetis M3=M4.

**Keputusan setelah gerbang:** jika lulus, lanjut ke eksperimen lima konfigurasi. Jika gagal, lakukan revisi kecil yang terdokumentasi; jangan mengubah seluruh arah penelitian secara sepihak.

## Status keputusan

**Sudah dipilih mahasiswa menurut state:** domain kredit konsumen; Home Credit; pengembangan metode CG-HIL; XGBoost; tidak menggunakan Federated Learning.

**Usulan teknis baru dalam draf ini (belum diputuskan mahasiswa/pembimbing):** split 70/15/15, ambang median dengan aturan `>`/`≤`, \(S=\min(n_E,n_U)\), \(w_U=1+S/n_U\), budget pembanding M1–M4 yang disetarakan, penanganan nilai kosong berbeda antara generator dan model, serta pemilihan threshold dengan F1 validasi.

**Belum dibuktikan:** keunggulan CG-HIL, kesesuaian distribusi kelengkapan terhadap desain, keberhasilan eksekusi SMOTENC, dan persetujuan formal perubahan konteks/judul/RQ oleh pembimbing.

## Referensi implementasi dan landasan

1. Home Credit Group (2018), *Home Credit Default Risk*, https://www.kaggle.com/competitions/home-credit-default-risk/data
2. imbalanced-learn (versi dokumentasi stabil saat pemeriksaan), *SMOTENC*, https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTENC.html
3. XGBoost, *Python API: XGBClassifier.fit(sample_weight)*, https://xgboost.readthedocs.io/en/stable/python/python_api.html
4. XGBoost, *Frequently Asked Questions: Missing Values*, https://xgboost.readthedocs.io/en/stable/faq.html
5. Peffers, Tuunanen, Rothenberger, dan Chatterjee (2007), *A Design Science Research Methodology for Information Systems Research*, https://doi.org/10.2753/MIS0742-1222240302

**Catatan:** Referensi karya terdekat serta daftar pustaka konteks kredit tetap mengikuti Bab I yang telah diberikan; draf ini tidak mengganti Bab I.
