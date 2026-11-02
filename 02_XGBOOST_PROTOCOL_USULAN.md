# Tugas 7 — Usulan protokol eksperimen XGBoost M0–M4 CG-HIL
Tanggal: 2026-11-02
**Status: USULAN; belum persetujuan mahasiswa dan bukan hasil eksperimen.** Tidak mengubah RQ, lima konfigurasi, dataset, maupun desain CG-HIL.

## 1. Keputusan yang hendak diuji
RQ1 membuktikan mekanisme CG-HIL dapat dilaksanakan. RQ2 menilai apakah seleksi berdasarkan kelengkapan menambah manfaat: perbandingan **utama** `average_precision(M4) - average_precision(M3)` pada test yang sama. M0/M1/M2 adalah konteks perbandingan tambahan. Hasil negatif/setara adalah hasil penelitian yang sah.

## 2. Data, pembagian, input
- Dataset berlabel Home Credit `application_train.csv`, 120 fitur; identitas `SK_ID_CURR` dan `TARGET` bukan prediktor. Split train 70%, validation 15%, test 15%, stratified TARGET, seed 42 menggunakan **indeks split yang telah diaudit** (jangan melakukan split baru yang menghasilkan keanggotaan berbeda).
- Data test tetap prevalensi alami; train saja yang di-resample, di-fit preprocessing dan ditentukan tau/S/bobot. Validation untuk threshold, bukan source resampling/fit encoder. Test hanya sekali untuk evaluasi final.
- Angka yang dilaporkan dalam precheck: train 215257, validation 46127, test 46127, n1=17377, E=8636, U=8741, S=8636, tau=.6.
- Numerik model: float64, NaN asli tetap dipertahankan; DAYS_EMPLOYED=365243 disajikan sebagai NaN pada model. Tidak menambah indikator fitur.
- Kategorikal model: gunakan shared OrdinalEncoder fit hanya **kategori pada train asli** yang sudah diperiksa generator, termasuk `__MISSING__`, dengan aturan unknown yang eksplisit dan deterministik. Jangan treat code ordinal sebagai jarak bermakna; XGBoost tetap menerima numeric codes karena kontrak encoding yang sudah dipilih; risiko ordinality ini dicatat sebagai keterbatasan. Mapping fitur, urutan dan kategori harus sama kelima model. **Catat konfigurasi encoder persis dari skrip**; jangan merekayasa instance berbeda demi protokol.
- Sintetis M2/M3/M4: generator training-only dan `synthetic_model_frame` bersama dari freeze tugas 6. Asli tidak diproses oleh fungsi ini. Gunakan urutan kolom sama 120 fitur; lakukan assertion tidak ada ID/label, inf, kategori synthetic unseen, dan original prefix tak berubah.

## 3. Konfigurasi XGBoost tunggal — diusulkan sebelum train
`XGBClassifier` dengan set berikut sama untuk semua M0–M4:

```python
XGB_PARAMS = dict(
    objective="binary:logistic",
    tree_method="hist",
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    min_child_weight=5,
    subsample=1.0,
    colsample_bytree=1.0,
    reg_lambda=1.0,
    reg_alpha=0.0,
    gamma=0.0,
    scale_pos_weight=1.0,
    random_state=42,
    n_jobs=4,
    eval_metric="logloss",
)
```

Alasan: 300 pohon kedalaman 4 dengan learning rate .05 adalah baseline konservatif untuk tabular cukup besar; min_child_weight=5 membatasi fragmentasi; semua metode memegang kapasitas dan regularisasi identik. `subsample=1` dan `colsample_bytree=1` menghilangkan dua sumber variasi sampling. `n_jobs=4` membatasi resource, bukan parameter riset. **Tidak mengklaim parameter ini optimal**; tidak ada grid/random search, early stopping, perubahan jumlah pohon atau parameter per metode. Record versi `xgboost` pada environment sebelum run dan API signature yang dipakai; jangan mengarang versi. Parameter didasarkan pada rancangan sederhana, bukan tuning test.

## 4. Lima konfigurasi (fixed)
| Model | Synthetic source | #synthetic | Bobot positif asli | Bobot sintesis |
|---|---|---:|---|---:|
| M0 | — | 0 | Semua=1 | — |
| M1 | — | 0 | Semua=1+2S/n1 | — |
| M2 | Semua positif train | 2S | Semua=1 | 1 |
| M3 | Semua positif train | S | Semua=1+S/n1 | 1 |
| M4 | Positif E saja | S | E=1; U=1+S/nU | 1 |

Mayoritas selalu weight 1. M1–M4 total bobot positif efektif = `n1+2*S=34649` (dari precheck); M3 dan M4 persis sama jumlah sintetis dan effective positive weight. **Jangan memasang tambahan `class_weight`, `scale_pos_weight` non-1, atau penyeimbangan lain.** Tidak ada test-time adjustment.

## 5. Evaluasi dan threshold
- **Primer:** `sklearn.metrics.average_precision_score(y_test, p_test)` (nama laporan `AP / PR-AUC (average precision)`; jangan menyamakan persis dengan trapezoidal PR-AUC).
- Tambahan tanpa threshold: ROC-AUC. Tambahan dengan threshold: precision, recall, F1, confusion matrix (label positif=1).
- Untuk setiap model, prediksi probabilitas `p_valid=P(TARGET=1)` pada validation alami; cari threshold **dari nilai probabilitas unik validation** yang memaksimalkan F1. Untuk ties pilih threshold TERBESAR (aturan deterministik untuk menghindari kasus positif tambahan ketika F1 identik). Implementasi dapat menggunakan `precision_recall_curve`; ambang array tidak memuat titik akhir tanpa threshold. Simpan threshold dan F1_valid. Gunakan prediksi positif jika `p >= threshold` untuk validation dan test. Karena presisi F1 threshold sensitif, jangan memilih threshold lagi di test.
- Test: hitung AP/ROC-AUC dari probabilitas mentah, precision/recall/F1/confusion matrix dari threshold validation yang dibekukan. Hindari menginterpretasi output XGBoost sebagai probabilitas terkalibrasi (tidak ada kalibrasi di desain).
- Primary contrast: delta AP = AP(M4)-AP(M3), tanpa menentukan besaran signifikansi buatan. Laporkan besaran aktual, arah dan trade-off. Confidence interval bootstrap berpasangan pada test **opsional untuk memperkuat interpretasi**, bukan prasyarat untuk menjalankan M0–M4; jika dipilih, catat desainnya sebelum membuka hasil test, jangan dipakai tuning.

## 6. Format artefak dan reproducibility
Berkas output yang direkomendasikan (nama dapat diselaraskan dengan struktur repo yang sudah ada, tanpa memperumitnya):
- `run_manifest.json`: tanggal, commit SHA, source SHA256, dataset SHA256, versi Python/numpy/pandas/sklearn/imblearn/xgboost, seed, feature count, split checksums/counts, encoder/NaN policy, param dict, S/tau/E/U.
- `model_summary.csv`: baris M0–M4, n_original, n_synthetic, positive_weight_total, best_valid_threshold, F1_valid, AP_test, ROC_AUC_test, precision_test, recall_test, F1_test, TP, FP, TN, FN.
- `comparison.json`: delta AP M4-M3 dan flag interpretasi positif/nol/negatif, tanpa klaim keunggulan statistik yang tidak diuji.
- `predictions_test.csv` bila dibutuhkan untuk perbandingan paired: ID split anonim/internal row index, y_test, probabilities M0–M4. Jangan commit data/label aplikasi atau skor individu publik; simpan dalam ignored results lokal.
- `EXPERIMENT_LOG.md`: command, manifest, hasil runtime, penyimpangan jika ada. `results/` dan bobot model `.json`/`.ubj` besar sebaiknya gitignored sesuai struktur repo.

## 7. Preflight sebelum eksperimen (bukan latihan ulang)
1. Freeze tugas 6 sudah selesai dengan commit/hash valid dan semua kontrak bersama M2/M3/M4 aktif.
2. Dokumentasikan versi XGBoost aktual serta parameter efektif dari `model.get_params()` dan encoder actual; check kompatibilitas `sample_weight`, missing `NaN` dan fitur kategorikal encoded.
3. Validasi invariants train: split konsisten; E/U/S sesuai; synthetic counts; total positive weights M1–M4; seluruh asli terjaga. Jangan memasukkan test pada fitting atau menentukan threshold.
4. Protokol ini **disetujui mahasiswa** dan parameter dibekukan sebelum M0–M4 dijalankan.

## 8. Pemeriksaan lokal aktual — 2 November 2026

**Status: USULAN / ISSUES — menunggu persetujuan; kompatibilitas XGBoost belum dapat disahkan.**

- Freeze generator selesai pada commit `75bf630`; source yang diperiksa berasal dari `9c1c2c9` dan tidak berubah. Scope freeze bukan runner M0–M4: jalur generator global M2/M3 belum dijalankan, sehingga integrasi bersama tetap harus diperiksa sebelum training.
- Environment eksperimen `.venv/bin/python`: Python 3.13.5, numpy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, imbalanced-learn 0.14.2 (dependency lengkap di manifest freeze). `importlib.util.find_spec('xgboost')` mengembalikan `None`; metadata distribusi menyatakan **NOT INSTALLED**. Tidak ada versi XGBoost aktual yang boleh dilaporkan sebagai kompatibel. Tidak memasang/mengubah environment pada tugas ini.
- Akibatnya `XGBClassifier.get_params()`, signature `fit(sample_weight=...)`, penerimaan parameter usulan oleh versi lokal, dukungan runtime NaN, dan integrasi input encoded belum dapat diperiksa pada XGBoost lokal. Daftar parameter bagian 3 dipertahankan sebagai usulan, tidak diubah diam-diam. Instansiasi/get_params nantinya hanya pemeriksaan API, bukan bukti keberhasilan training.
- Encoder aktual pada `precheck_smotenc_cghil.py`: `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)`; default dtype float64, `categories='auto'`, `encoded_missing_value=np.nan`. Kategori lebih dulu menjadi string, missing menjadi `__MISSING__`; fit hanya pada asli train. Output kategori numerik tersebut bukan native categorical XGBoost. Tidak menambahkan encoder atau desain representasi baru.
- Numerik model diseragamkan float64, missing asli dipertahankan kecuali sentinel durasi→NaN. Dua masking struktural hanya untuk sintetis sesudah inverse scaling/koreksi hitungan dan sebelum encoder yang sama. Full precheck aktual memverifikasi tidak ada kategori sintetis unknown dan prefix asli tetap sama.
- Split aktual dibuat oleh dua `train_test_split` seed 42 (test_size=.30 lalu .50), pada urutan baris raw yang hash-nya terkunci; precheck belum menyimpan indeks split. Jadi rujukan “indeks split yang telah diaudit” bukan berarti file indeks sudah tersedia. Implementasi eksperimen nanti wajib mereplikasi fungsi/urutan yang sama dan menyimpan checksum keanggotaan, bukan mengganti algoritma split.
- Tidak menjalankan training/model fitting, threshold search, prediksi, evaluasi test, atau mengubah Bab I/III. Pemasangan versi XGBoost dan pemeriksaan API tanpa fit perlu dilakukan setelah mahasiswa menyetujui persiapan environment; protokol tetap memerlukan persetujuan sebelum eksperimen.

## Batas interpretasi
Dataset tunggal; split acak tidak mengukur generalisasi waktu; code missing/kelengkapan tidak otomatis menunjukkan kualitas; OrdinalEncoder punya asumsi representasi; kesetaraan total effective weight tidak berarti efek regularisasi sama. Rekomendasi akademik: tidak perlu menambah baseline, metode, dan hyperparameter search hanya untuk mengoptimalkan hasil.
