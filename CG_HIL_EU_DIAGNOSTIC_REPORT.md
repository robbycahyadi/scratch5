# Diagnosis pascates CG-HIL — Phase 1: E/U

**Tanggal:** 2 November 2026. **Status:** diagnosis deskriptif selesai; rekomendasi menunggu review mahasiswa. Tidak ada perubahan definisi metode/protokol atau hasil M0–M4.

## 1. Ringkasan eksekutif

**Asumsi kelengkapan sebagai dasar memilih sumber sintesis melemah, meskipun perhitungan E/U benar dan dapat direproduksi.** Skor mentah sah sebagai ukuran jumlah field terisi, tetapi bukti train tidak cukup untuk menyebut E lebih berkualitas, lebih representatif, atau lebih layak diinterpolasi daripada U.

Pemisahan ternyata sangat didominasi satu domain: **47 fitur hunian**. Seluruh fitur hunian kosong pada **8.633 dari 8.741 U (98,76%)**, dibanding **777 dari 8.636 E (9,00%)**. Secara aritmetis, perbedaan jumlah fitur hunian kosong menjelaskan **97,72% selisih rata-rata skor E–U**. Di luar hunian, rata-rata kelengkapan kedua kelompok sangat tinggi dan berdekatan: **96,67% E versus 95,56% U**. Tidak ada bukti bahwa semua kekosongan hunian berarti tidak berlaku ataupun buruknya kualitas pemohon/data.

Raw `notna()` juga menghukum ketidakberlakuan yang kuat secara semantik: semua **142.086 bukan pemilik mobil** di train mempunyai umur mobil kosong. Dalam pemeriksaan sensitivitas satu faktor dengan ambang tetap 0,6, mengeluarkan umur mobil yang tidak berlaku dari penyebut memindahkan **1.483 U ke sisi E**; ini bukan definisi E/U baru. Sebaliknya, masking sentinel pekerjaan hanya memindahkan **1 E ke U**. Jadi keberadaan masalah konstruk tidak selalu berarti dampak keanggotaan sama besar.

**Implikasi:** hasil negatif CG-HIL konsisten dengan kekhawatiran bahwa seleksi lebih banyak memisahkan ketersediaan blok data dan profil pemohon daripada kelayakan sintesis. Namun diagnosis ini **tidak membuktikan** bahwa itulah penyebab AP M4 lebih rendah. Seleksi sumber dan distribusi bobot sama-sama berubah pada M3–M4. **Ablation A1/A2 masih berguna sebagai usulan tindak lanjut**, setelah definisi dan protokolnya disetujui; tidak dijalankan di fase ini, dan bukan sarana memperbaiki metode berdasarkan test.

## 2. Lingkup, sumber, dan reproduksi

Pertanyaan: apakah kelengkapan raw pada 120 prediktor memberikan dasar yang defensibel untuk membagi positif train menjadi E/U bagi sintesis selektif?

- Konteks dibaca dari [state](<THESIS_STATE.md>), [laporan eksperimen](<CG_HIL_EXPERIMENT_REPORT.md>), [ringkasan metrik](<CG_HIL_MODEL_SUMMARY.csv>), [persetujuan freeze](<PROTOCOL_FREEZE_APPROVAL.md>), [audit semantik](<HOME_CREDIT_SEMANTIC_AUDIT.md>), naskah relevan, dan implementasi. **Catatan pascates yang diminta dengan nama `CG_HIL_POSTTEST_DIAGNOSTIC_NOTES.md` tidak tersedia** di repositori. Tidak diasumsikan isi maupun definisi A1/A2 di dalamnya. Ini keterbatasan konteks, bukan blocker perhitungan E/U karena sumber data, rumus, kode, dan checksum split tersedia.
- Sumber raw [data aplikasi lokal](<application_train.csv>) dibaca read-only. SHA-256 sebelum/sesudah sama: `52e96b895b1112e1c853f670e58372719c8441c5ed1c57ac2f7fad559d784f5f`.
- Mengikuti tahap pertama split asli: stratified 70/30 seed 42. Train sudah tetap sebelum holdout dibagi validasi/test, sehingga tidak perlu merekonstruksi atau menganalisis kedua subset holdout. Checksum urutan indeks train cocok [manifest beku](<CG_HIL_EXPERIMENT_MANIFEST.json#L642-L645>): `693ceb768bba5f9fcd6b11b7aca117f67bb566d316609dece0a972b2d88bea3b`.
- Label sumber dibaca hanya untuk mereproduksi penetapan split yang sudah ada. Pembacaan CSV berikutnya dilakukan per chunk dan **hanya baris train dipertahankan**; statistik predictor dihitung setelah seleksi train. CSV secara fisik tetap harus diparse per chunk, tetapi tidak ada statistik/peninjauan fitur holdout. Tidak membaca prediksi test, model, atau prepared matrices eksperimen.
- ID/TARGET dikeluarkan, fitur konstan disaring hanya dari train: tidak ada yang dibuang; urutan 120 fitur cocok manifest. Semua hash sumber beku pada manifest juga cocok. Rumus direplikasi dari [runner](<run_cghil_experiment.py#L178-L190>) dan [precheck](<precheck_smotenc_cghil.py#L95-L109>), tanpa mengimpor runner atau menjalankan generator/model.
- Python 3.13.5, numpy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1. Tidak memasang dependency baru.

Reproduksi minimal (direktori output harus belum ada):

```bash
.venv/bin/python diagnose_cghil_eu.py --out results/eu_phase1_20261102
```

[Kode diagnosis](<diagnose_cghil_eu.py>) menghasilkan [agregat JSON lokal](<results/eu_phase1_20261102/diagnostics.json>) serta [profil missingness seluruh 120 fitur](<results/eu_phase1_20261102/feature_missingness.csv>). Keduanya berada di ignored results; laporan ini menyimpan bukti ringkas tanpa baris individu. Assertions split/hash/fitur/invarian PASS, exit 0. Pemeriksaan tambahan jumlah missing per fitur versus per kelompok dan identitas E+U=positif untuk setiap fitur juga PASS. Tidak menjalankan ulang suite generator, training, atau evaluasi karena tidak diperlukan.

## 3. Reproduksi E/U beku — fakta terverifikasi

`c_i = jumlah prediktor raw yang notna / 120`, sebelum imputasi atau masking sentinel. `tau = median c` pada positif train; `E: TARGET=1 dan c>tau`, `U: TARGET=1 dan c<=tau`.

| Invarian | Diharapkan | Aktual |
|---|---:|---:|
| Baris train | 215.257 | 215.257 |
| Positif train | 17.377 | 17.377 |
| Prediktor | 120 | 120 |
| Tau | 0,6 | 0,6 |
| E | 8.636 | 8.636 |
| U | 8.741 | 8.741 |

Sebanyak **2.794 positif tepat pada tau** (72/120 field terisi) dan semuanya masuk U. E mulai dari 73/120. Banyaknya tie membuat pembagian tidak persis separuh. Tidak ada prevalensi positif E/U yang dihitung: keduanya memang berisi positif saja.

## 4. Missingness pada seluruh train

Dari 120 fitur, **67 mempunyai NaN dan 53 tidak mempunyai NaN**. Rata-rata kelengkapan train 0,7522 (median 0,7000; rentang 0,4917–1). Terhitung **6.401.365 sel kosong**, dengan **5.848.837 (91,37%)** berada pada blok hunian. Ini memberi konteks bahwa skor bukan agregat domain yang seimbang.

### 4.1 Blok hunian dan pola bersama

Blok 47 fitur terdiri atas 42 ukuran AVG/MODE/MEDI, TOTALAREA_MODE, dan empat kategori hunian sesuai [audit semantik](<HOME_CREDIT_SEMANTIC_AUDIT.md#L80-L82>). Bobot literalnya **47/120=39,17%** dari skor. Missing per fitur hunian berada sekitar **47,37–69,82%** train. Seluruh 47 kosong pada **101.963 train (47,37%)**; seluruhnya terisi pada **55.122 (25,61%)**.

Tiga pola lengkap paling sering di train adalah: semua hunian + OWN_CAR_AGE + EXT_SOURCE_1 kosong (**17.263**); semua hunian + OWN_CAR_AGE (**15.161**); semua hunian + OWN_CAR_AGE + EXT_SOURCE_1 + OCCUPATION_TYPE (**12.789**). Pola ini menjelaskan mengapa penghitungan tiap kolom sebagai satu unit dapat memperbesar pengaruh satu sumber/blok informasi.

**Batas interpretasi:** co-missing menunjukkan ketersediaan bersama, bukan bahwa nilai kolom identik, dan bukan bukti semua NaN struktural. Tidak diketahui apakah data hunian tidak berlaku, tidak dikumpulkan, atau tidak diketahui pada setiap aplikasi.

### 4.2 Relasi kondisional yang diperiksa ulang

| Relasi train | Bukti numerik | Makna yang dapat dipertahankan |
|---|---|---|
| Kepemilikan mobil–umur mobil | N: 142.086/142.086 umur kosong; Y: 5/73.171 kosong | Sangat mendukung ketidakberlakuan umur mobil bagi bukan pemilik; lima pemilik kosong berbeda sifatnya. |
| Organisasi–durasi kerja | XNA dan sentinel 365243 sama persis pada 38.756 baris; mismatch kedua arah 0 | Kode khusus bukan durasi normal. Hubungan terverifikasi, arti resmi XNA/sentinel belum terkonfirmasi. |
| Pendapatan–kode kerja | Pensioner: 38.740/38.748 berkode; Unemployed: 16/16; kategori pendapatan lain: 0 | Konsisten dengan kemungkinan tidak berlaku pada nonpekerja; ada **8 Pensioner** tanpa pasangan kode, jadi bukan aturan universal. |
| Pendapatan–occupation kosong | Pensioner 38.744/38.748; Unemployed 16/16; Working 17.458/110.984; Commercial associate 8.646/50.106 | Ketidakberlakuan pekerjaan masuk akal untuk sebagian kasus, tetapi occupation kosong juga terjadi pada kelompok aktif. Jangan menghapus seluruh NaN sebagai struktural. |
| Enam inquiry biro | 29.081 baris kosong di keenam fitur sekaligus; 186.176 terisi semuanya; tidak ada pola parsial | Ada blok pengamatan bersama. NaN bukan otomatis nol inquiry atau bukti tidak punya riwayat kredit. |
| Empat hitungan social circle | 714 baris kosong di keempat fitur sekaligus; 214.543 terisi semuanya; tidak ada pola parsial | Co-missing terverifikasi, tetapi alasan dan applicability belum diketahui. |

**Pemeriksaan yang tidak mendukung aturan applicability sederhana:** seluruh hunian kosong pada **32.255/65.845 (48,99%)** bukan pemilik realty dan **69.708/149.412 (46,65%)** pemilik realty. Jadi `FLAG_OWN_REALTY=N` tidak menjelaskan kekosongan hunian secara deterministik. Di setiap kategori NAME_HOUSING_TYPE terdapat kasus kosong dan tidak kosong: contoh House/apartment **90.585/191.159**, rented **2.133/3.357**, with parents **5.613/10.330** seluruh hunian kosong. Perbedaan frekuensi ada, tetapi bukan bukti bahwa penyewa atau penghuni bersama orang tua otomatis tidak memiliki fitur hunian yang berlaku.

Fitur nonhunian lain yang menonjol: EXT_SOURCE_1 kosong **121.373 (56,39%)**, EXT_SOURCE_3 **42.680 (19,83%)**, OCCUPATION_TYPE **67.480 (31,35%)**. Tidak ada dasar dari data ini untuk menganggap skor eksternal kosong sebagai ketidakberlakuan. Missing sangat kecil juga tetap dihitung: annuity 8, goods price 187, suite 901, family members 1, last phone change 1; semuanya tercakup profil 120 fitur.

## 5. Perbedaan E dan U

Persentase berikut selalu memakai jumlah anggota kelompok sebagai penyebut, kecuali statistik numerik yang memakai nilai teramati.

### 5.1 Kelengkapan dan pola dominan

| Deskripsi | E (n=8.636) | U (n=8.741) |
|---|---:|---:|
| Rata-rata c | 0,8754 | 0,5816 |
| Q1 / median / Q3 | 0,8000 / 0,9250 / 0,9833 | 0,5833 / 0,5917 / 0,6000 |
| Minimum–maksimum c | 0,6083–1,0000 | 0,5000–0,6000 |
| Rata-rata jumlah fitur hunian kosong | 12,52 dari 47 | 46,97 dari 47 |
| Semua hunian kosong | 777 (9,00%) | 8.633 (98,76%) |
| Semua hunian terisi | 3.866 (44,77%) | 0 |
| Kelengkapan rata-rata pada 73 fitur di luar hunian | 96,67% | 95,56% |
| EXT_SOURCE_1 kosong | 52,20% | 67,09% |
| EXT_SOURCE_3 kosong | 19,00% | 26,85% |
| OCCUPATION_TYPE kosong | 22,37% | 28,10% |
| Semua enam inquiry kosong | 14,09% | 20,95% |
| Pola missing berbeda (mask 120 fitur) | 1.416 | 89 |

Kontribusi hunian terhadap gap mean dihitung `(46,9728−12,5237)/120 ÷ (0,875352−0,581579) = 97,72%`. Ini **dekomposisi aritmetis**, bukan estimasi sebab-akibat. Kelengkapan di luar hunian adalah deskripsi, bukan skor pengganti.

Tiga pola terbanyak E: hanya OWN_CAR_AGE + EXT_SOURCE_1 kosong (**825**), hanya semua hunian kosong (**777**), hanya OWN_CAR_AGE kosong (**704**). Tiga pola terbanyak U: semua hunian + OWN_CAR_AGE + EXT_SOURCE_1 kosong (**1.970**), semua hunian + OWN_CAR_AGE (**1.436**), semua hunian + EXT_SOURCE_1 (**1.058**). “Hanya” berarti tidak ada fitur lain yang kosong pada mask tersebut.

Contoh penting: **777 E tidak punya satupun fitur hunian terisi**. Karena semua 73 fitur lainnya terisi, skornya 73/120=0,6083 dan masuk E; jika hanya satu field lain kosong, skornya tepat 0,6 dan masuk U. Jadi E bukan sinonim “punya informasi hunian”, dan batas lokal dapat ditentukan satu field, termasuk field yang tidak berlaku.

### 5.2 Karakteristik pemohon yang relevan

| Karakteristik | E | U | Mengapa dibandingkan |
|---|---:|---:|---|
| Umur median [Q1–Q3], tahun* | 38,91 [31,30–48,93] | 39,22 [31,07–49,69] | Memeriksa apakah pemisahan sekadar perbedaan usia; ringkasannya berdekatan. |
| Pendapatan median [Q1–Q3] | 157.500 [112.500–202.500] | 135.000 [99.000–180.000] | Seleksi terkait profil ekonomi; bukan hanya jumlah NaN. |
| Kredit median [Q1–Q3] | 512.064 [295.168,5–760.225,5] | 462.195 [276.277,5–675.000] | Memeriksa cakupan besaran aplikasi; distribusi tumpang tindih. |
| Bukan pemilik mobil | 64,07% | 74,79% | Relasi langsung dengan penalti umur mobil kosong. |
| Higher education | 20,63% | 11,83% | Perbedaan komposisi pendidikan pada sumber sintesis. |
| Working | 59,14% | 62,57% | Cakupan jenis pendapatan. |
| Commercial associate | 24,94% | 18,83% | Cakupan jenis pendapatan. |
| Pensioner | 10,85% | 13,19% | Konteks kode kerja dan missing occupation. |
| Rented apartment | 1,73% | 3,08% | Profil tempat tinggal, bukan alasan menetapkan semua hunian tidak berlaku. |
| EXT_SOURCE_2 median, nilai teramati | 0,4786 | 0,3978 | Informasi substantif dapat berbeda walaupun missing kecil (0,21% vs 0,24%). |

*Umur deskriptif = −DAYS_BIRTH/365,25. Satuan moneter tidak ditafsirkan sebagai rupiah; identitas/formula skor EXT_SOURCE tidak diketahui. Median EXT_SOURCE_3 teramati justru berdekatan: **0,3808 E versus 0,3825 U**, meskipun cakupan keterisiannya berbeda. Median anak keduanya 0 [0–1]. Tidak dilakukan uji signifikansi, klaim risiko relatif, atau metrik prediksi E/U.

### 5.3 Cakupan dan keragaman positif

Kedua kelompok mencakup lima jenis pendapatan positif yang sama, enam tipe tempat tinggal yang sama, serta seluruh 18 kategori occupation yang teramati. Jadi E tidak menghilangkan semua profil U secara kategorikal. Akan tetapi proporsinya berbeda, dan ada dukungan kategori langka yang tidak sama: Academic degree hanya di U (**1**); organisasi Trade:type4 dan Trade:type5 hanya di U (**masing-masing 1**), Industry:type10 hanya di E (**5**). E mencakup 56 kategori organisasi, U 57.

U mempunyai lebih sedikit pola missing berbeda, **bukan berarti lebih sedikit keragaman pemohon**: ketika hampir semua fitur hunian kosong bersama, ruang mask memang menyusut. Cakupan kategori marginal dan kuartil yang tumpang tindih juga tidak membuktikan cakupan kombinasi multivariat atau geometri tetangga yang setara. Yang terbukti adalah M4 tidak memakai **8.741 positif U** sebagai sumber sintesis, termasuk profil-profil di atas; U tetap hadir sebagai observasi asli berbobot. Tidak menganalisis tetangga atau membuat sintetis baru pada fase ini.

## 6. Penilaian validitas kriteria kelengkapan

### Fakta: penalti ketidakberlakuan dan kredit keterisian kode khusus

- Bukan pemilik mobil kehilangan **1/120=0,008333** pada skor karena umur mobil NaN, meskipun ketidakberlakuannya masuk akal. Ada **12.070 positif** terdampak (5.533 E, 6.537 U). Kelompok ini tidak boleh otomatis disebut kualitas informasinya buruk. Seluruh NaN umur mobil positif berasal dari bukan pemilik; lima pemilik dengan NaN berada di train nonpositif.
- DAYS_EMPLOYED sentinel **38.756 train**, termasuk **2.095 positif (939 E, 1.156 U)**, tetap memperoleh satu kredit keterisian pada skor raw, padahal dimask pada representasi generator/model. Seluruh pasangan ORGANIZATION_TYPE=XNA juga dihitung terisi. XNA organisasi mungkin membawa informasi status, sehingga tidak tepat otomatis menyebut kedua field tidak informatif.
- CODE_GENDER=XNA **2 train** dan NAME_FAMILY_STATUS=Unknown **1 train** terhitung hadir; **tidak ada pada positif train**, sehingga dua kode itu tidak menentukan E/U positif pada split ini. Tidak menyamakan makna XNA antarfitur.
- Hunian menanggung 39,17% skor; blok ini menyumbang **91,32% sel kosong positif**. Lima puluh tiga fitur selalu terisi memberi baseline keterisian, bukan bukti kecukupan informasi. Nol pada indikator dokumen/telepon, nol inquiry, atau nilai hari negatif tidak diperlakukan sebagai missing.

### Sensitivitas deskriptif, bukan redefinisi E/U

Semua skenario dihitung di memori, **tau tetap 0,6**; tidak menghitung threshold optimum/median baru, tidak mengubah pipeline, bobot, atau budget sampling. Tujuannya mengukur pengaruh mekanis komponen skor, bukan memilih skor alternatif.

| Stress test satu faktor | Rumus untuk deskripsi | E→sisi U | U→sisi E |
|---|---|---:|---:|
| Mask sentinel durasi saja | `(n_terisi − I[sentinel])/120` | 1 | 0 |
| Keluarkan umur mobil yang tidak berlaku | `n_terisi/(120 − I[car=N dan age NaN])` | 0 | 1.483 |
| Hilangkan blok hunian dari penghitungan | `n_terisi_nonhunian/73` | 0 | 8.741 |

Pada stress test mobil, **1.483/8.741=16,97% U**, atau **8,53% seluruh positif**, melewati batas. Ini menunjukkan isu satu field struktural dapat berpengaruh di sekitar tie; bukan hanya perubahan skor yang abstrak. Mean perubahan skor positif +0,004237. Mask sentinel mengubah mean −0,001005 dan keanggotaan satu orang: **tidak cukup** untuk menganggap sentinel sendirian menjelaskan hasil negatif.

Menghilangkan hunian adalah **uji dominasi domain yang sengaja ekstrem**, bukan usulan skor. Semua positif melewati 0,6 sesudahnya; ambang 0,6 tidak bermakna sama setelah domain diganti. Angka transisi tidak membuktikan klasifikasi baru lebih benar. Tidak ada eksperimen performa untuk membandingkan skenario. Tidak dilakukan penyesuaian occupation karena applicability individual belum terverifikasi.

**Putusan konstruk:** `notna()` **didukung sebagai ukuran operasional keterisian field yang sederhana dan konsisten**, tetapi **melemah sebagai proksi kualitas/kecukupan informasi dan kelayakan sumber sintetis**. Bukti menunjukkan pengaruh struktural/domain yang material; belum tersedia ground truth kualitas atau kelayakan sintesis untuk memvalidasi ranking E lebih baik dari U. Definisi E/U beku tetap dipertahankan sebagai definisi eksperimen yang sudah selesai, bukan diganti secara retrospektif.

## 7. Hipotesis yang belum terbukti dan interpretasi hasil negatif

**Fakta historis, bukan evaluasi ulang:** [laporan eksperimen](<CG_HIL_EXPERIMENT_REPORT.md#L25-L41>) mencatat AP M3=0,24014824719054298 dan M4=0,22336570832530905; selisih **−0,016782538865233926**. Fase ini tidak menghitung AP atau metrik model apa pun. AP tetap metrik primer; ROC-AUC, precision, recall, F1 dan confusion matrix tetap sekunder pada protokol, bukan ditambahkan sebagai statistik E/U.

**Hipotesis yang konsisten dengan deskripsi tetapi belum dibuktikan:**

1. Seleksi E memusatkan sintesis pada profil dengan blok hunian lebih tersedia dan komposisi ekonomi/pendidikan tertentu, sehingga cakupan sintetis kurang mewakili sebagian positif. Cakupan marginal yang berbeda mendukung risiko ini, bukan bukti dampak prediksinya.
2. Menghindari sintesis U tidak otomatis menghindari informasi yang buruk: sebagian missing U struktural, dan di luar hunian keterisiannya tinggi. Namun kelayakan interpolasi U juga belum terbukti.
3. Pembobotan U dan seleksi sumber mungkin mempunyai efek terpisah atau interaksi; M3–M4 mengubah keduanya. Kesamaan total bobot positif dan jumlah sintetis tidak mengidentifikasi kontribusi masing-masing.

**Belum diketahui:** mekanisme NaN individual (termasuk MCAR/MAR/MNAR), arti resmi semua kode khusus, kualitas aktual informasi E/U, keunggulan geometri/koherensi sintesis E, serta hubungan kausal komponen tersebut dengan AP. Perbedaan profil bukan bukti diskriminasi atau kausalitas. Diagnosis tidak membuktikan penurunan AP disebabkan oleh completeness, tidak menguji signifikansi delta, dan tidak menyelamatkan klaim keunggulan CG-HIL yang tidak didukung run asli.

Interpretasi yang defensibel: **hasil negatif membatasi dukungan empiris untuk kebijakan CG-HIL yang benar-benar diuji**. Validitas teknis pembagian E/U tidak sama dengan validitas asumsi bahwa pemilihan berdasarkan jumlah field terisi memberi manfaat prediktif. Ini bukan alasan mengubah protokol, skor atau threshold dengan pengetahuan test.

## 8. Rekomendasi dan batas berhenti

**Rekomendasi: A1/A2 masih layak sebagai langkah berikutnya untuk memisahkan kontribusi seleksi sumber dan pembobotan**, bukan untuk mencari konfigurasi yang mengalahkan hasil test. Karena catatan pascates tidak tersedia dan definisi rinci A1/A2 tidak ada dalam mandat ini, laporan tidak menetapkan atau mengarang pemetaan A1/A2. Mahasiswa perlu meninjau temuan ini dan mengonfirmasi definisi/protokol follow-up sebelum eksekusi. Ablation dapat menguji kontribusi komponen; ia tidak dengan sendirinya memvalidasi makna missingness atau membuktikan skor baru.

**Yang tidak dijalankan:** ablation A1/A2, error analysis, bootstrap, generator, fitting/retraining model, prediksi/evaluasi test, tuning threshold/bobot/budget/hyperparameter, penggantian E/U, revisi RQ/desain, maupun penulisan ulang bab tesis. Semua artefak eksperimen dan sumber beku dipertahankan.

**Berhenti pada laporan ini. Satu langkah berikutnya: review dan persetujuan mahasiswa atas interpretasi serta kelayakan follow-up A1/A2.**
