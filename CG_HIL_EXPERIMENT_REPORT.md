# CG-HIL — Hasil eksperimen M0–M4, 2 November 2026

## Intinya

Seluruh gerbang integrasi PASS dan tepat lima model dilatih dengan protokol yang disetujui. Pada satu split test yang ditetapkan, **AP M4 lebih rendah daripada M3**, delta AP = **-0.016782538865233926**. Hasil ini tidak mendukung klaim bahwa seleksi kelengkapan CG-HIL meningkatkan AP pada kondisi eksperimen ini. Tidak ada tuning atau perubahan metode sesudah melihat test, dan tidak dilakukan bootstrap/signifikansi statistik.

## Provenance dan gerbang

- Freeze protokol administratif: `4802b50`; implementasi runner/tests: `959a644`; bukti integrasi dan threshold sebelum test: `6ec1396`.
- Generator M4/fungsi semantik beku tetap utuh sesuai SHA256 manifest freeze; tidak mengubah Bab I/III atau RQ.
- Raw SHA256: `52e96b895b1112e1c853f670e58372719c8441c5ed1c57ac2f7fad559d784f5f`.
- Python 3.13.5; numpy 2.5.4; pandas 3.1.0; scikit-learn 1.9.1; imbalanced-learn 0.14.2; xgboost-cpu 3.4.1.
- Split stratified dua tahap .30/.50 seed42: train 215257, validation 46127, test 46127. Indeks berurutan disimpan lokal dan checksum tercatat di manifest. Test positif 3724, negatif 42403 (prevalensi alami).
- 120 fitur, 69 numerik/51 kategorikal, ID/TARGET dikecualikan. Median/scaler/encoder fit hanya asli train. Kelengkapan raw: tau=.6, E=8636, U=8741, S=8636.
- Unit suite **15/15 PASS**: 8 semantik beku + 7 runner (split, bobot, kategori unknown/NaN, parameter dan threshold termasuk exact tie terbesar).
- Integrasi nyata generator **M2/M3/M4 PASS**; sintetis masing-masing 17272/8636/8636. Original prefix dan seluruh 215257 asli dipertahankan. Hard violations tersisa 0, kategori sintetis unknown 0. Mask NaN struktural tepat, sel NaN disengaja masing-masing 17367/8702/7879. Potensi semantik lain tetap diagnostik, tidak dikoreksi atau dipakai untuk tuning.
- Bobot positif efektif M1–M4=34649; M3 pada floating-point 34649.00000000001 (selisih pembulatan, toleransi 1e-7). Mayoritas dan sintetis berbobot 1.
- Lima model masing-masing 300 pohon sesuai satu parameter dict approved, tidak ada early stopping, pencarian hyperparameter, atau fitting pada validation/test.
- Kelima threshold dan hash model disimpan sebelum test. SHA256 pretest manifest: `0df2264193062e01cb0dca57e7de47d94b09b5ffa3c3997d207cda3316d64d50`. Marker eksklusif dibuat sebelum representasi/prediksi test; evaluate dijalankan sekali pada direktori run ini.

## Hasil aktual

AP adalah `average_precision_score`, bukan integral trapezoidal PR. Threshold per model dipilih hanya pada validation alami, dari probabilitas unik; F1 seri memilih threshold terbesar; keputusan positif `p>=threshold`.

| Metode | Sintetis | Threshold valid | F1 valid | AP test | ROC-AUC test | Precision test | Recall test | F1 test |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M0 | 0 | 0.163388 | 0.307826 | 0.247985 | 0.761140 | 0.257895 | 0.381579 | 0.307776 |
| M1 | 0 | 0.280008 | 0.307810 | 0.247339 | 0.761510 | 0.260894 | 0.381042 | 0.309724 |
| M2 | 17272 | 0.165179 | 0.294804 | 0.222291 | 0.749338 | 0.232314 | 0.391515 | 0.291600 |
| M3 | 8636 | 0.223946 | 0.304210 | 0.240148 | 0.755828 | 0.246080 | 0.400376 | 0.304814 |
| M4 | 8636 | 0.227240 | 0.287604 | 0.223366 | 0.746071 | 0.230685 | 0.393663 | 0.290902 |

| Metode | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| M0 | 38314 | 4089 | 2303 | 1421 |
| M1 | 38383 | 4020 | 2305 | 1419 |
| M2 | 37585 | 4818 | 2266 | 1458 |
| M3 | 37835 | 4568 | 2233 | 1491 |
| M4 | 37514 | 4889 | 2258 | 1466 |

Kontras utama M4−M3 = -0.016783 AP (sekitar -1.6783 poin persentase). M4 juga lebih rendah pada precision, recall dan F1 test dibanding M3 pada threshold yang dikunci. M0 memiliki AP tertinggi pada tabel ini; ini deskripsi hasil, bukan pemilihan/tuning model baru. Keberhasilan integrasi membuktikan implementasi berjalan dan invariants diuji, bukan efektivitas prediksi CG-HIL.

## Reproduksi dan artefak

Runner memisahkan gerbang dan menolak overwrite direktori/marker. **Jangan jalankan ulang test untuk memilih atau memperbaiki metode.** Command berikut adalah rekaman aktual, bukan instruksi mengulang eksperimen:

```bash
.venv/bin/python -m unittest -v test_cghil_semantics test_run_cghil_experiment
.venv/bin/python run_cghil_experiment.py prepare --input application_train.csv --out results/cghil_m0_m4_20261102
.venv/bin/python run_cghil_experiment.py train --out results/cghil_m0_m4_20261102
.venv/bin/python run_cghil_experiment.py evaluate --out results/cghil_m0_m4_20261102
```

Ringkasan presisi penuh: `CG_HIL_MODEL_SUMMARY.csv`; kontras: `CG_HIL_COMPARISON.json`; manifest aman: `CG_HIL_EXPERIMENT_MANIFEST.json`. Manifest lokal lengkap, matriks prepared, model UBJ, prediksi per baris dan log berada di ignored `results/`, tidak masuk Git. SHA256 memungkinkan pencocokan tanpa menerbitkan baris aplikasi. Sumber runner/tests dipin lewat commit dan hash.

## Batasan dan langkah berikutnya

Dataset tunggal/split acak tunggal, bukan generalisasi waktu/lembaga; tidak ada confidence interval atau klaim signifikansi. Kelengkapan raw bukan kualitas semantik, missingness sintetis hanya memulihkan dua pola struktural, kode ordinal memiliki keterbatasan, dan kesamaan bobot efektif tidak menyamakan efek regularisasi. Probabilitas tidak dikalibrasi. Pengaman test sekali berlaku per direktori, bukan larangan teknis global atas salinan run; disiplin no-rerun tetap berlaku.

**Satu langkah berikutnya:** mahasiswa meninjau hasil negatif ini untuk interpretasi Bab IV/V bersama pembimbing, tanpa mengubah metode atau menjalankan tuning test.
