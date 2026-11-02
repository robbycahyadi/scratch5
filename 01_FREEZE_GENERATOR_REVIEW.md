# Tugas 6 — Review dan kontrak freeze generator CG-HIL
Tanggal: 2026-11-02
Status: VERIFIED — sumber generator siap dibekukan dalam commit catatan ini; SHA commit aktual dilaporkan setelah commit.

## Bukti yang telah tersedia (dokumen, bukan rerun independen)
Sumber: `CG_HIL_GENERATOR_FINAL_VALIDATION.md` versi unggahan 2 November dan `THESIS_STATE.md`.
- Split terstratifikasi seed 42: train 215257; validation 46127; test 46127.
- 120 prediktor (69 numerik/51 kategorikal), tidak memasukkan ID dan TARGET.
- Train positif 17377; tau=0.6; E=8636; U=8741; S=8636; w_U=1.9879876444; total bobot positif M1–M4=34649.
- M4 full precheck PASS, 8636 sintetis; smoke PASS 300 sintetis; unit test 8/8 PASS; pemeriksaan hard violations setelah koreksi = 0 menurut laporan.
- SHA-256 raw data yang *dilaporkan*: 52e96b895b1112e1c853f670e58372719c8441c5ed1c57ac2f7fad559d784f5f.
- Library generator yang *dilaporkan*: Python 3.13.5; pandas 3.1.0; numpy 2.5.4; scikit-learn 1.9.1; imbalanced-learn 0.14.2. Versi XGBoost belum dikonfirmasi.
- M2/M3 belum dieksekusi. Hasil M4 tidak boleh ditulis sebagai hasil M2/M3, apalagi hasil prediksi.

## Kontrak yang dipertahankan
1. Kelengkapan dihitung dari `notna()` fitur asli sebelum imputasi dan masking sentinel; median dan pemisahan E/U hanya di train. Skor tidak ditafsirkan sebagai mutu atau applicability.
2. Pada generator: roles dari kamus audit; numeric median fit train, StandardScaler khusus generator, kategori eksplisit termasuk XNA dan Unknown serta `__MISSING__`. DAYS_EMPLOYED=365243 menjadi NaN untuk generator, tidak mengubah skor kelengkapan asli.
3. Setelah inverse scaling, hanya 12 fitur hitungan yang dibulatkan `np.rint` (ties-to-even) dan diproyeksikan nonnegatif; DEF_30<=OBS_30 serta DEF_60<=OBS_60 dipertahankan dengan batas minimum. Jangan membulatkan variabel jumlah uang/rasio/fitur bangunan.
4. **Hanya pada sintetis model**, jalankan fungsi bersama `synthetic_model_frame` setelah inverse scaling/koreksi hitungan, sebelum encoding model: `FLAG_OWN_CAR=N -> OWN_CAR_AGE=NaN`; `ORGANIZATION_TYPE=XNA -> DAYS_EMPLOYED=NaN`. Terapkan fungsi SAMA untuk M2, M3, M4. Jangan mengubah baris asli atau tetangga SMOTENC.
5. Model XGBoost mendapat numerik asli dengan NaN dipertahankan (kecuali sentinel durasi), kategori melalui encoder yang fit di train asli dan digunakan sama untuk semua metode. Tidak melakukan imputasi numerik seluruh data model.
6. Semua observasi asli sah dipertahankan. Sintetis berbobot 1 dan mayoritas berbobot 1. Jumlah sintetis M2=2S, M3=M4=S. Sumber M2/M3 adalah seluruh minoritas train, M4 hanya E.
7. Potensi mismatch lain hanya diagnostik: pensioner/unemployed non-XNA=26, organisasi XNA dengan occupation present=88, umur mobil > usia pemohon=135 setelah koreksi. Jangan koreksi diam-diam.

## Bukti yang **belum** tersedia saat review handoff (historis)
- Kode skrip nyata yang sekarang ada di repo eksperimen lokal, keluaran tes mentah, JSON precheck penuh, `git rev-parse HEAD`, `git status --porcelain`, hash sumber/konfigurasi yang sama dengan run PASS, dan commit freeze.
- Pencarian GitHub melalui konektor tidak menemukan `precheck_smotenc_cghil.py` pada repositori yang terindeks. Ini **bukan bukti** bahwa berkas lokal tidak ada.

## Syarat pembekuan di repo (Codex)
- Baca instruksi repo (`AGENTS.md`, `AI_THESIS_WORKING_CONSTITUTION.md` asli). Jangan membuat ulang atau mengganti berkas aslinya.
- Periksa `git status` dan ignore rules; jangan menambahkan data Home Credit/CSV besar/output sintetis/model binary ke Git.
- Identifikasi path tepat: `precheck_smotenc_cghil.py`, `cghil_semantics.py`, `test_cghil_semantics.py`, `generate_final_validation_report.py` dan dependensi konfigurasi/kamus audit. Buat manifest SHA256 berkas SOURCE + environment freeze (tanpa dataset).
- Cocokkan laporan terbaru dengan JSON full precheck; rerun test yang relevan bila tersedia dan wajar, **jangan rerun training M0–M4**. Bila hasil berubah/gagal, jangan freeze; jelaskan minimal discrepancy.
- Catat hasil dan perintah di `EXPERIMENT_LOG.md`, commit dokumentasi/manifest sumber dengan aman, laporkan commit SHA serta working tree. Hindari mengubah kode generator jika seluruh verifikasi sesuai.

## Keputusan review
Keputusan handoff historis: **GO untuk freeze versi kode yang sama dengan full precheck PASS**, dengan version proof masih pending saat handoff. Verifikasi lokal berikut melengkapi bukti tersebut; tidak menyetujui protokol XGBoost secara otomatis.

## Verifikasi lokal aktual — 2 November 2026

- HEAD sumber: `9c1c2c98bd1f211b6a8f467fe74bb4cddf24db5a`, branch `main`. Awal sesi hanya dua dokumen review/usulan baru yang untracked; tidak ada modifikasi sumber tracked.
- Konstitusi asli dibaca dan hash tetap `43a805a59121c4498a416f37818eefd3a0d6f6108a291efe2cab084d599f98d4`.
- `.venv/bin/python -m unittest -v test_cghil_semantics`: **8/8 PASS**. Full precheck dijalankan ulang dengan `--input application_train.csv --out results/freeze_verification_20261102_1332/full --full`: **exit 0 / PASS**, tanpa training model.
- JSON rerun **identik seluruh objeknya** dengan JSON baseline full. Sebanyak 95 baris aturan tabel laporan historis cocok dengan JSON baseline (jumlah dan persentase). E=8636, U=8741, S=8636, tau=0.6, seed=42, positif efektif=34649, sintetis=8636; hard remaining kosong, 7879 sel NaN struktural, 0 NaN tak diharapkan. Numerik 69/kategorikal 51.
- Hash dataset sebelum/sesudah sama dengan hash yang dilaporkan. Sumber, kamus, laporan dan JSON baseline tetap utuh. Renderer laporan tidak dijalankan karena menulis ulang laporan baseline; angka unit test pada renderer merupakan teks tetap, bukan mekanisme pembuktian tes.
- Smoke baseline merupakan versi sebelum structural fix (tidak memiliki `structural_missingness`); bukan bukti versi terbaru. Ini keterbatasan provenance smoke, bukan kegagalan full rerun sumber aktif.
- Urutan kode aktual: inverse scaling → `round_counts` → proyeksi DEF<=OBS → `synthetic_model_frame` hanya pada sintetis → encoder bersama fit asli train. Baris asli menggunakan `model_frame`, tidak menggunakan fungsi structural masking sintetis. Prefix asli dan missingness numerik diuji.
- M2/M3 belum memiliki jalur generator global yang dijalankan; test fungsi bersama dengan label M2/M3/M4 bukan uji integrasi ketiga generator. Kontrak pada bagian sebelumnya tetap wajib saat implementasi pembanding, tanpa klaim M2/M3 teruji.
- Manifest aman: `CG_HIL_GENERATOR_SOURCE_MANIFEST.json` memuat SHA256 source/kamus/config, versi dependency aktual, hash bukti, command dan scope. Python 3.13.5; pandas 3.1.0; numpy 2.5.4; sklearn 1.9.1; imblearn 0.14.2. Raw data, sintetis dan log runtime tetap ignored di `results/`.
- Batas freeze: generator M4 dan fungsi semantik bersama yang benar-benar diperiksa; tidak membekukan runner training yang belum ada. Tidak mengubah Bab I/III, RQ, dataset, atau metode. Commit yang memuat catatan dan manifest ini menjadi checkpoint freeze; hash dilaporkan setelah commit. Tidak push.
