# Persetujuan dan pembekuan protokol CG-HIL — 2 November 2026

**Status keputusan mahasiswa: DISETUJUI.**
**Status berkas dalam repo GitHub ketika catatan ini dibuat: belum diubah/di-commit oleh ChatGPT.**

## Dasar keputusan dan provenance

Mahasiswa secara eksplisit menyetujui rancangan pada `02_XGBOOST_PROTOCOL_USULAN.md` di repo `robbycahyadi/scratch5`, menggunakan `xgboost-cpu==3.4.1`, tanpa mengubah RQ atau metode. Versi dokumen pada HEAD yang terakhir diperiksa: blob Git `82842c2f2d0a5e305b9b20a76f456677493019b9`; HEAD repo sebelum instruksi implementasi: `731650b117e54405efe6a3f86fe0fa497b8e355b`. Jika HEAD telah bergerak ketika Codex mulai, bandingkan perubahan, jangan menimpa keputusan yang lebih baru.

Arah, fitur dan protokol tidak dibuka ulang kecuali ada kegagalan nyata, bukti material baru, perubahan batasan, atau arahan pembimbing. Persetujuan mahasiswa bukan persetujuan akademik formal pembimbing atas perubahan konteks/judul/RQ.

## Kontrak desain yang dibekukan

- Data: `application_train.csv`, 120 fitur setelah pengecualian `SK_ID_CURR`/`TARGET` dan penyaringan fitur konstan hanya berdasarkan train; split terstratifikasi dua tahap (0,30 kemudian 0,50 atas holdout), seed 42, mempertahankan urutan dataset sumber yang hash-nya diaudit.
- Kelengkapan: proporsi nilai tidak kosong pada fitur mentah, sebelum imputasi/masking sentinel; median positif train menentukan `E` (`c>tau`) dan `U` (`c<=tau`). Hasil audit: `tau=0.6`, `E=8636`, `U=8741`, `S=8636`, positif train `n1=17377`.
- Repr. generator: median numerik train + StandardScaler khusus generator; kategori sesuai kamus audit, missing kategori `__MISSING__`, XNA/Unknown tetap eksplisit; SMOTENC `k_neighbors=5`, `random_state=42`; hasil pasca-inverse scaling dikoreksi pada 12 hitungan dan `DEF<=OBS`.
- Repr. model: numerik asli float64 dengan NaN dipertahankan kecuali `DAYS_EMPLOYED=365243` dimask sebagai NaN; kategori menggunakan `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)` fit hanya pada observasi asli train; kolom/urutan/encoder sama untuk M0–M4.
- **Hanya sintetis** M2/M3/M4 menggunakan `synthetic_model_frame` sesudah koreksi hitungan dan sebelum shared encoder: `FLAG_OWN_CAR=N -> OWN_CAR_AGE=NaN`, `ORGANIZATION_TYPE=XNA -> DAYS_EMPLOYED=NaN`. Generator M4 yang telah dibekukan pada commit `75bf630` tidak diubah diam-diam.
- M0: 0 sintetis, bobot asli 1.
- M1: 0 sintetis, bobot semua positif asli `1+2S/n1`.
- M2: `2S` sintetis dari semua minoritas asli train, bobot asli 1.
- M3: `S` sintetis dari semua minoritas asli train, bobot semua positif asli `1+S/n1`.
- M4: `S` sintetis dari kelompok E saja, bobot E 1 dan U `1+S/nU`.
- Seluruh mayoritas dan sintetis berbobot 1. Bobot positif efektif M1–M4 adalah `n1+2S=34649`; M3/M4 sama-sama memakai `S=8636` sintetis.
- `XGBClassifier`: `objective='binary:logistic'`, `tree_method='hist'`, `n_estimators=300`, `max_depth=4`, `learning_rate=0.05`, `min_child_weight=5`, `subsample=1.0`, `colsample_bytree=1.0`, `reg_lambda=1.0`, `reg_alpha=0.0`, `gamma=0.0`, `scale_pos_weight=1.0`, `random_state=42`, `n_jobs=4`, `eval_metric='logloss'`. Tidak ada tuning model, early stopping, atau kalibrasi tambahan.
- Metrik utama `average_precision_score` pada test alami, kontras utama `AP(M4)-AP(M3)`. Metrik pelengkap ROC-AUC, precision, recall, F1, confusion matrix. Threshold **per model** memaksimalkan F1 di validation dengan kandidat nilai prediksi unik; saat tie pilih threshold terbesar; rule keputusan `p>=threshold`. Threshold dibekukan sebelum test dibuka, tidak disetel lagi.
- Data test hanya dipakai **sekali** untuk evaluasi final setelah uji integrasi, training train-only dan threshold validasi lulus dan artefaknya dicatat. Hasil negatif/setara sah.

## Status pembuktian pada saat persetujuan

- Tugas 6 sudah VERIFIED untuk generator M4, bukti full rerun PASS dan manifest SHA256.
- Kompatibilitas XGBoost 3.4.1 import/API/matriks float64 + NaN PASS tanpa fitting, pada commit `731650b`.
- Generator M2/M3, integrasi lima model, training, metrik validasi/test **belum dibuktikan**.

## Apa yang wajib dilakukan Codex untuk pembekuan di repo lokal

Perbarui header/status `02_XGBOOST_PROTOCOL_USULAN.md` dari `USULAN` menjadi `DISETUJUI / FROZEN` tanpa mengganti parameter atau menghapus histori usulan. Beri catatan bertanggal bahwa bagian status lama (terutama 'XGBoost belum terpasang') adalah kondisi historis yang diselesaikan pada commit `731650b`. Catat persetujuan ini dalam `THESIS_STATE.md` dan `EXPERIMENT_LOG.md`, serta commit dokumen saja sebagai checkpoint sebelum implementasi. Jangan mengubah Bab I/III atau source generator untuk kepentingan administrasi freeze. Jangan push tanpa perintah eksplisit.
