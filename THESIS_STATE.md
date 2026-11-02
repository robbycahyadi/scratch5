# THESIS_STATE — CG-HIL / Home Credit

**Snapshot handoff:** 2 November 2026
**Status dokumen:** rekonstruksi berbasis dokumen yang tersedia dan laporan pengguna terakhir. Jika ada `THESIS_STATE.md` yang lebih lengkap/baru di lokasi lain, **gabungkan perubahan material setelah membandingkan isinya; jangan timpa otomatis**.

## Arah penelitian dan keputusan yang sudah dipilih mahasiswa

- Program: Magister Layanan Teknologi Informasi, STEI ITB.
- Arah kerja: *Completeness-Guided Hybrid Imbalance Learning* (CG-HIL) untuk menangani ketidakseimbangan kelas pada prediksi risiko kesulitan pembayaran kredit konsumen.
- Data: *Home Credit Default Risk*, terutama `application_train.csv`; unit analisis satu aplikasi kredit; label `TARGET` mengikuti definisi dataset.
- Metode: oversampling SMOTENC selektif dari kelompok minoritas dengan skor kelengkapan lebih tinggi (E) dan pembobotan observasi minoritas lebih rendah kelengkapannya (U). Seluruh observasi asli dipertahankan. Model prediktif: XGBoost.
- Tidak menggunakan Federated Learning. Tidak mengubah arah ini tanpa keputusan mahasiswa atau bukti baru yang material.
- RQ1: merancang dan menjalankan CG-HIL. RQ2: menilai manfaat seleksi kelengkapan terhadap pembanding, terutama hibrida global tanpa seleksi (M3 vs M4).
- **Belum disetujui secara formal oleh pembimbing** (berdasarkan naskah Bab I): perubahan konteks dari koperasi Indonesia, judul final, dan RQ/kontribusi final. Jangan menyatakan sudah disetujui.

## Fakta sumber dan bukti yang tersedia

- Dataset hasil audit: 307.511 observasi berlabel, positif 24.825 (8,0729%); 120 prediktor setelah mengecualikan ID dan label; SHA-256 raw `application_train.csv`: `52e96b895b1112e1c853f670e58372719c8441c5ed1c57ac2f7fad559d784f5f`.
- Split precheck 70/15/15 terstratifikasi, seed 42: train 215.257, validasi 46.127, uji 46.127. Positif train 17.377.
- Skor `notna()` mentah sebelum imputasi: ambang median positif train `tau=0,6`; E=8.636, U=8.741; S=8.636, `w_U=1+S/U=1,9879876444`; total bobot positif efektif M1–M4 = 34.649.
- Audit semantik 120 fitur: `DAYS_EMPLOYED=365243` dan `ORGANIZATION_TYPE=XNA` memiliki mask sama pada 55.374 baris keseluruhan. Arti resmi kode khusus tidak terverifikasi; nilainya tidak patut dipakai sebagai durasi normal. Sebagian nilai kosong bersifat potensial struktural; skor kelengkapan **tidak sama** dengan kualitas data.
- Generator SMOTENC full precheck sebelumnya menciptakan tepat S sintetis, tipe kategori valid, 12 hitungan disesuaikan, dan pemeriksaan bobot konsisten. Laporan yang tersedia: `CG_HIL_GENERATOR_FINAL_VALIDATION.md` dan JSON precheck (periksa versinya).
- **Pembaruan terakhir menurut laporan langsung pengguna, 2 Nov 2026 (belum diperiksa melalui file/hash commit pada sesi ini):** setelah dua koreksi pascasintesis (`FLAG_OWN_CAR=N -> OWN_CAR_AGE=NaN`, `ORGANIZATION_TYPE=XNA -> DAYS_EMPLOYED=NaN`), 8/8 unit test dan full precheck PASS, 8.636 sintetis, 0 pelanggaran keras menurut validator, 7.879 sel NaN struktural yang disengaja, 0 NaN tidak diharapkan. Model M0–M4 **belum dilatih**. Kontrak pascapemrosesan harus sama untuk M2–M4.
- Tersisa inkonsistensi **potensial, bukan aturan keras** menurut pengguna: Pensioner/Unemployed dengan non-XNA 26 sintetis; XNA dengan occupation terisi 88; umur mobil lebih tua dari pemohon 135. Jangan otomatis mengoreksi tanpa dasar.

## Rancangan eksperimen (belum hasil)

| Model | Perlakuan | Sintetis | Bobot positif asli |
|---|---|---:|---|
| M0 | XGBoost standar | 0 | 1 |
| M1 | Pembobotan saja | 0 | `1 + 2S/n1` |
| M2 | SMOTENC global | `2S` | 1 |
| M3 | Hibrida global | `S` | `1 + S/n1` |
| M4 | CG-HIL | `S` dari E | E=1; U=`1+S/nU` |

Semua sintetis dan mayoritas berbobot 1. Perbandingan utama M3 vs M4; metrik primer PR-AUC/average precision; pelengkap ROC-AUC, precision, recall, F1, confusion matrix; ambang klasifikasi ditentukan dari validasi menurut satu aturan yang konsisten, bukan dari test. Data uji digunakan hanya untuk evaluasi final.

## Status pekerjaan / tahap sekarang

- [x] Audit dataset dan split
- [x] Audit semantik 120 prediktor
- [x] Precheck kelayakan E/U dan bobot
- [x] Full precheck SMOTENC dan koreksi semantik (menurut laporan terakhir)
- [x] **Tugas 6 — Verifikasi freeze generator (2 Nov 2026):** unit test aktual 8/8 PASS dan full rerun PASS, JSON identik baseline full; sumber dari `9c1c2c9` tidak berubah. Manifest `CG_HIL_GENERATOR_SOURCE_MANIFEST.json` dan review `01_FREEZE_GENERATOR_REVIEW.md` menjadi checkpoint freeze pada commit yang memuat pembaruan ini (hash dilaporkan sesudah commit). Scope hanya generator M4 dan fungsi bersama; generator global M2/M3 belum dijalankan.
- [x] **Tugas 7 — DISETUJUI / FROZEN 2 November 2026 oleh mahasiswa:** protokol dan seluruh parameter disetujui eksplisit, `xgboost-cpu==3.4.1`. Mandat kini implementasi M0–M4, integrasi, training dan evaluasi satu kali setelah gerbang PASS, tanpa push. Persetujuan ini menggantikan larangan training pada status historis berikut, bukan persetujuan formal pembimbing. **Riwayat kompatibilitas tanpa fit PASS:** setelah mandat persiapan dependency, `xgboost-cpu==3.4.1` terpasang dan dipin pada `requirements-xgboost.txt` (modul `xgboost` 3.4.1, Python 3.13.5). Import, instansiasi parameter persis usulan, get_params/get_xgb_params, signature sample_weight dan DMatrix float64+NaN lulus tanpa fit. Dependency lama dan hash sumber beku tetap sama; pip check PASS. Ini bukan bukti training/integrasi penuh dan bukan persetujuan protokol. Catatan XGBoost belum terpasang pada audit terdahulu merupakan riwayat yang kini teratasi; training M0–M4 tetap belum diizinkan.
- [x] **Eksperimen M0–M4 selesai 2 November 2026:** 15/15 unit test dan integrasi aktual seluruh metode PASS; M2/M3/M4=17272/8636/8636 sintetis, hard remaining 0. Tepat lima model 300 pohon dilatih, lima threshold validasi dikunci sebelum test, lalu evaluasi test satu kali. AP M3=0.24014824719054298, M4=0.22336570832530905; delta=-0.016782538865233926, tidak mendukung peningkatan AP oleh CG-HIL pada run ini. Tidak ada tuning test/CI/signifikansi. Lihat `CG_HIL_EXPERIMENT_REPORT.md`, manifest dan ringkasan CSV; raw/model/prediksi lokal ignored. Freeze protokol `4802b50`, runner `959a644`, checkpoint pra-test `6ec1396`.
- [ ] Lanjutkan Bab IV/V; lengkapi Bab II dan selaraskan Bab I–III sesuai bukti.

## Batasan dan aturan membuka ulang

- Hasil XGBoost kini tersedia pada run final tunggal; CG-HIL tidak unggul terhadap M3 pada AP test. PASS generator/integrasi bukan keunggulan prediksi. Pernyataan belum dilatih pada rekap historis di atas berlaku sebelum eksperimen ini, bukan status sekarang.
- Dataset tunggal; tidak ada klaim generalisasi lintas lembaga/waktu, dampak kebijakan kredit, atau koperasi Indonesia.
- Tugas 6 tidak boleh mengubah definisi metode hanya untuk mengejar hasil. Tugas 7 tidak boleh melatih M0–M4 ataupun memakai test sebagai tuning.
- Buka ulang pilihan yang sudah digunakan hanya jika ada kegagalan verifikasi aktual, bukti baru material, perubahan batasan, atau arahan pembimbing. Catat alasannya.

## Sumber rujukan

- `BAB_I_CG_HIL_credit_scoring.md` (28 Okt 2026).
- `BAB_III_CG_HIL_draf_v0_1.md` (29 Okt 2026; **belum diselaraskan dengan perubahan implementasi terakhir**).
- `HOME_CREDIT_SEMANTIC_AUDIT.md` dan `HOME_CREDIT_FEATURE_DICTIONARY_AUDITED.csv` (2 Nov 2026).
- `CG_HIL_GENERATOR_FINAL_VALIDATION.md` dan JSON full precheck terbaru; versi final setelah structural masking harus disinkronkan dari eksperimen lokal.
- `AI_THESIS_WORKING_CONSTITUTION.md` asli mahasiswa: tersedia di root dan dibaca saat setup governance 2 November 2026; dipertahankan tanpa perubahan byte. SHA-256: `43a805a59121c4498a416f37818eefd3a0d6f6108a291efe2cab084d599f98d4`. Keterangan belum tersedia pada handoff sebelumnya telah teratasi; ini bukan verifikasi freeze generator.
