# EXPERIMENT_LOG — CG-HIL

Tujuan: **log ringkas hasil dan keputusan yang benar-benar terjadi**, bukan todo list atau laporan akademik. Gunakan entri baru hanya pada perubahan material atau uji signifikan; bukti lengkap ada pada laporan/skrip/commit Git.

## Rekap pekerjaan sebelum pengaturan Git (historis)

**Tanggal laporan:** 2 November 2026
**Sumber:** laporan semantik, validasi generator, dan ringkasan Codex yang dibawa mahasiswa.
**Commit historis:** tidak diketahui / belum dicatat — **jangan dibuat-buat**.

- Data: Home Credit `application_train.csv`, SHA256 `52e96b895b1112e1c853f670e58372719c8441c5ed1c57ac2f7fad559d784f5f`.
- Audit: train 215.257, E=8.636, U=8.741, S=8.636, bobot U=1,9879876444, W1 M1–M4=34.649.
- Precheck sebelumnya telah menguji generator SMOTENC dan semantik fitur.
- Menurut laporan pengguna terakhir: perbaikan dua pola NaN struktural pasca-SMOTENC lulus 8/8 unit test dan full precheck; hard violation 0; M0–M4 belum dilatih.
- **Batas:** belum ada commit freeze yang terverifikasi dan hasil di atas belum boleh disebut hasil evaluasi model.

## 2026-11-02 — Setup governance repo lokal

- **Tujuan / tahap:** mengaktifkan tata kelola minimal saja; bukan freeze generator, penetapan XGBoost, atau training.
- **Preflight:** root `/home/robby/project/scratch5`; `git rev-parse --show-toplevel` di proyek dan direktori induk melaporkan bukan repo Git. Tidak ada branch/commit historis lokal untuk diperiksa. Inventaris root memuat dokumen handoff, Bab I/III, laporan generator, skrip, CSV mentah dan arsip Home Credit. `.gitignore` root belum ada.
- **Konstitusi:** berkas asli sudah berada di root, dibaca dan tidak disalin ulang/diubah. `sha256sum AI_THESIS_WORKING_CONSTITUTION.md`: `43a805a59121c4498a416f37818eefd3a0d6f6108a291efe2cab084d599f98d4` (sama setelah setup).
- **Perubahan:** menambah `.gitignore`; mempertahankan `AGENTS.md` dan konstitusi; memperbarui keterangan ketersediaan konstitusi pada `THESIS_STATE.md`; menambahkan entri ini tanpa menghapus rekap historis. Dokumen handoff sudah tersedia di root, tidak ada versi alternatif yang diberikan untuk digabungkan.
- **Git:** `git init` berhasil di root proyek, branch `main`; belum ada commit sebelumnya. Hanya lima file governance akan di-stage eksplisit. Tidak membuat remote atau push.
- **Verifikasi aktual:** `git status --short`, `git check-ignore` untuk CSV mentah, `data/raw/example.csv`, `.env`/`.env.local`, `.venv/`, arsip Home Credit, hasil/model dan CSV sintetis menunjukkan perlindungan aktif. Kamus audit CSV dan `AGENTS.md` tidak diabaikan. `git diff --check` sebelum staging tidak melaporkan masalah (file masih untracked; pemeriksaan staged menyusul sebelum commit).
- **Keputusan / status:** setup lokal dilanjutkan sesuai instruksi mahasiswa; tidak ada perubahan kode atau data, tidak ada eksperimen/test generator yang dijalankan. Seed dan versi library ML tidak berlaku untuk setup ini.
- **Batasan:** laporan `CG_HIL_GENERATOR_FINAL_VALIDATION.md` tersedia dan bagian ringkasannya dibaca hanya untuk identifikasi; klaim hasilnya tidak diuji ulang. Berkas penelitian lain tetap untracked, sengaja tidak dimasukkan ke commit governance. Folder `results/` diabaikan secara menyeluruh untuk keamanan hasil besar; ringkasan bukti kecil dapat diizinkan secara eksplisit pada tugas berikutnya.
- **Langkah berikutnya:** setelah setup selesai, mahasiswa menentukan kapan memberi mandat tugas 6; tidak dijalankan pada sesi setup ini.
- **Pemeriksaan staged:** percobaan pertama `git diff --cached --check` menemukan tiga trailing whitespace Markdown pada state/log handoff; diperbaiki hanya spasi akhir tanpa mengubah isi historis. Pemeriksaan diulang sebelum commit. Konstitusi tidak diubah.
- **Commit setup:** hash aktual dilaporkan dalam jawaban setelah commit; tidak mengarang hash di log.

## 2026-11-02 — Snapshot baseline sebelum tugas 6

- **Tujuan / persetujuan:** mahasiswa menyetujui checkpoint baseline agar working tree bersih; bukan persetujuan freeze generator atau hasil eksperimen.
- **Kondisi awal:** branch `main`, commit sebelumnya `f23efda`; 16 entri untracked pada status ringkas (termasuk direktori sumber audit), tanpa perubahan tracked.
- **Perubahan:** memasukkan 18 berkas dokumen/kode/kamus/provenance yang sudah ada sebagai snapshot; tidak mengubah isi berkas penelitian. `.gitignore` ditambah pengecualian arsip unduhan kamus sumber; CSV hasil ekstraksi dan provenance tetap dilacak.
- **Verifikasi:** pemeriksaan ukuran dengan `python3` menunjukkan seluruh kandidat <2 MB (terbesar kamus audit 92.135 byte); pemindaian pola credential terbatas tidak menemukan kecocokan. Hash CSV sumber dan arsip cocok dengan `dictionary_provenance.json`. `git check-ignore` mengonfirmasi CSV aplikasi mentah, arsip Home Credit, `.venv/`, dan arsip kamus tidak masuk snapshot.
- **Kendala pemeriksaan:** alias `python` tidak tersedia; digunakan `python3`. Pemeriksaan awal arsip menemukan tambahan metadata `__MACOSX/`; arsip tidak diubah/dihapus, tetapi dikecualikan dari Git. Pemindaian credential bukan jaminan audit keamanan menyeluruh.
- **Status / batasan:** snapshot kondisi awal saja; tidak menjalankan unit test, precheck, generator, training, atau evaluasi. Klaim pada laporan lama belum diverifikasi ulang. Seed/versi library ML tidak berlaku untuk checkpoint Git ini.
- **Pemeriksaan commit:** `git diff --check`, `git diff --cached --check`, dan daftar staged diperiksa sebelum commit; temuan format bawaan bila ada dipertahankan sebagai snapshot dan dilaporkan, bukan diperbaiki dengan mengubah kode/data.
- **Temuan whitespace:** `git diff --cached --check` melaporkan 209 temuan pada dua CSV kamus sumber (31 pada asli, 178 pada UTF-8). Byte sumber dipertahankan agar hash/provenance tetap benar; pemeriksaan ulang mengecualikan hanya dua CSV tersebut. Pemeriksaan lanjutan juga menemukan empat spasi akhir Markdown pada Bab I/III (dua per dokumen); dipertahankan sebagai format bawaan snapshot. Pengecualian pemeriksaan akhir terbatas pada dua CSV sumber dan dua dokumen Bab tersebut. Ini pengecualian format sumber terdokumentasi, bukan klaim seluruh staged bebas whitespace.
- **Langkah berikutnya:** mulai tugas 6 hanya setelah mandat terpisah. Hash commit checkpoint dilaporkan setelah commit.

## 2026-11-02 — Verifikasi dan freeze generator M4

- **Mandat:** tugas 6 dan persiapan tugas 7, tanpa training M0–M4. Branch `main`, HEAD sumber `9c1c2c98bd1f211b6a8f467fe74bb4cddf24db5a`; awal hanya dua dokumen handoff baru untracked.
- **Command / hasil:** `.venv/bin/python -m unittest -v test_cghil_semantics` PASS 8/8; `.venv/bin/python precheck_smotenc_cghil.py --input application_train.csv --out results/freeze_verification_20261102_1332/full --full` exit 0 PASS. Log runtime tersimpan lokal di folder baru, tidak menimpa baseline.
- **Bukti:** JSON rerun identik seluruh objek dengan baseline full; 95 baris aturan tabel report cocok baseline. Seed 42, E/U/S=8636/8741/8636, tau=.6, sintetis 8636, total positif efektif 34649, hard remaining kosong, NaN struktural 7879 dan tidak diharapkan 0. SHA256 raw tetap `52e96b895b1112e1c853f670e58372719c8441c5ed1c57ac2f7fad559d784f5f` sebelum/sesudah.
- **Source/config/environment:** tercatat di `CG_HIL_GENERATOR_SOURCE_MANIFEST.json`; Python 3.13.5, numpy 2.5.4, pandas 3.1.0, sklearn 1.9.1, imblearn 0.14.2. Sumber/kamus/report/JSON baseline tidak berubah. Konstitusi asli tidak berubah.
- **Audit kontrak:** structural masking hanya pada sintetis sesudah inverse scaling dan hitungan, sebelum encoder asli-train bersama. M2/M3 belum diimplementasikan/dijalankan sebagai generator global; pengujian fungsi bersama tidak membuktikan integrasi M2/M3.
- **Keterbatasan:** smoke historis tidak memiliki structural fields; tidak digunakan sebagai bukti terbaru. Renderer memuat teks unit-test tetap; tidak dijalankan/dianggap bukti. Audit awal JSON lama menemui KeyError karena skema tanpa seed; audit diulang dengan pembacaan field opsional dan selesai, bukan kegagalan generator.
- **Status:** VERIFIED untuk scope generator tersebut; commit catatan review, manifest, state/log merupakan checkpoint freeze. Tidak mengubah metode, kode generator atau Bab I/III. Raw/large outputs/sintetis/log runtime tidak di-stage; tidak push. SHA aktual dilaporkan setelah commit.

## 2026-11-02 — Audit usulan protokol XGBoost tanpa fitting

- **Status:** USULAN / ISSUES, bukan persetujuan mahasiswa. Freeze selesai pada `75bf630`.
- **Pemeriksaan aktual:** metadata/discovery modul `.venv` menggunakan `importlib.metadata` dan `importlib.util.find_spec`: XGBoost NOT INSTALLED, module None. Tidak bisa memverifikasi versi/get_params/signature fit/sample_weight/NaN pada XGBoost lokal; tidak menginstal paket dan tidak mengarang kompatibilitas PASS.
- **Encoder:** `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)`, dtype float64, categories auto, encoded_missing_value NaN, max_categories/min_frequency None; fit asli train. Kategori missing diisi string, XNA/Unknown berbeda. Unknown validasi/uji nantinya -1; bukan native categorical XGBoost. Audit read-only independen mengonfirmasi hasil ini.
- **Perubahan:** tambahkan audit aktual pada `02_XGBOOST_PROTOCOL_USULAN.md`; perbarui status tugas 7 pada state. Parameter desain tetap, Bab I/III tidak diedit. Belum ada file indeks split tersimpan dari precheck; fungsi dua tahap seed42/urutan data harus direplikasi, checksum dicatat saat implementasi kelak.
- **Larangan dipatuhi:** tidak ada fitting model, threshold search, prediksi/evaluasi test, M0–M4, atau push. Log sensitif dan artefak besar tetap ignored. Pemeriksaan diff/staged sebelum commit dokumentasi.
- **Satu aksi berikutnya:** mahasiswa meninjau usulan dan menyetujui persiapan environment XGBoost agar kompatibilitas API dapat diperiksa tanpa training. Hash commit dokumentasi dilaporkan setelah commit.

## 2026-11-02 — Dependency CPU dan kompatibilitas XGBoost tanpa fit

- **Mandat / awal:** hanya dependency dan kompatibilitas, bukan persetujuan protokol/training. HEAD `38aa18d31ce868e726b6ccd9e1ef5e51869a0fd0`, working tree bersih.
- **Instalasi:** `.venv/bin/python -m pip index versions xgboost-cpu` menampilkan stabil terbaru 3.4.1; `.venv/bin/python -m pip install --only-binary=:all: xgboost-cpu==3.4.1` berhasil. Dipilih CPU-only untuk menghindari dependency GPU yang tidak diperlukan. Pin tambahan pada `requirements-xgboost.txt`, bukan mengubah manifest historis freeze. Modul `xgboost` dan distribusi `xgboost-cpu` aktual 3.4.1; Python 3.13.5. `pip check`: No broken requirements found.
- **Pemeriksaan aktual:** command `.venv/bin/python` inline membaca dict XGB_PARAMS persis dari blok protokol melalui AST, instansiasi XGBClassifier, assert seluruh parameter get_params sama, tampilkan get_xgb_params, inspect signature fit yang memuat keyword-only sample_weight=None; default missing=NaN. Tidak memanggil fit.
- **Input tanpa training:** array buatan 2x3 float64 `[[1, NaN, -1], [2, 3, 0]]` diterima DMatrix(missing=NaN), 2 baris/3 kolom/5 nilai nonmissing. Kode -1 tetap nilai numerik, NaN diperlakukan missing. Tidak memakai data aplikasi/validation/test; model tidak memiliki `_Booster`. Ini uji penerimaan matriks/API saja, bukan bukti training atau parameter kernel efektif setelah fitting.
- **Kontrak / integritas:** OrdinalEncoder diinstansiasi tanpa fit, get_params sesuai sumber: categories auto, dtype float64, encoded_missing_value NaN, handle_unknown use_encoded_value, unknown_value -1, min_frequency/max_categories None. SHA256 semua sumber/kamus pada manifest freeze sama; semua versi dependency lama pada manifest sama sesudah instalasi. Tidak mengubah preprocessing, parameter, metode, Bab I/III, atau sumber generator.
- **Status:** PASS terbatas import/API/input; protokol tetap USULAN dan training M0–M4 belum disetujui. State diperbarui, riwayat audit sebelumnya dipertahankan. Tidak ada threshold search, prediksi atau evaluasi; tidak push. Diff/staged diperiksa sebelum commit; SHA aktual dilaporkan sesudah commit.
- **Satu langkah berikutnya:** mahasiswa meninjau dan menyetujui protokol sebelum memberi mandat implementasi/eksperimen berikutnya.

## 2026-11-02 — Freeze administratif protokol disetujui mahasiswa

- **Keputusan:** mahasiswa menyetujui eksplisit protokol `02_XGBOOST_PROTOCOL_USULAN.md`, xgboost-cpu==3.4.1 dan seluruh parameter/formula pada 2 November 2026. Bukan persetujuan formal pembimbing.
- **Preflight:** HEAD `731650b117e54405efe6a3f86fe0fa497b8e355b`; dua berkas handoff `PROTOCOL_FREEZE_APPROVAL.md` dan `CODEX_IMPLEMENT_M0_M4.md` untracked dibaca dan dipertahankan. Tidak ada perubahan tracked awal.
- **Perubahan:** status protokol DISETUJUI/FROZEN, state tugas 7 selesai; audit lama dipertahankan sebagai sejarah. Tidak mengubah parameter, sumber generator, metode, atau Bab I/III. Commit administrasi terpisah sebelum implementasi; tiga dokumen saja di-stage.
- **Mandat selanjutnya:** implementasi dan uji integrasi train-only; training/threshold validasi serta test satu kali hanya setelah gerbang PASS. Belum ada hasil training pada checkpoint ini. Tidak push sesuai instruksi terbaru.
- **Verifikasi:** git diff --check dan daftar staged diperiksa sebelum commit; hash aktual dilaporkan setelah commit.

## 2026-11-02 — Implementasi runner dan unit test sebelum training

- **Protokol:** checkpoint persetujuan administratif `4802b50`, sebelum implementasi. Berkas handoff mahasiswa dipertahankan dan akan dicatat bersama implementasi.
- **Implementasi:** `run_cghil_experiment.py` dengan tahap prepare/train/evaluate, menggunakan fungsi generator/validator beku tanpa mengubahnya. Hash sumber/dependency diverifikasi, sumber param diekstrak dari protokol approved. Manifest integrasi, checksum split/artefak, encoder train-only, prefix asli, sintetis dan bobot diperiksa. Training dan test memiliki marker eksklusif; test baru boleh setelah lima model/threshold dan pretest manifest tersimpan.
- **Unit command:** `.venv/bin/python -m unittest -v test_cghil_semantics test_run_cghil_experiment`: PASS 15/15. Uji data buatan termasuk bobot, split, unknown=-1/NaN tanpa refit, seluruh 15 parameter dan F1 exact tie terbesar. Percobaan awal test baru menemukan helper menolak all-negative labels; helper diperbaiki mendukung F1=0 dan threshold terbesar, bukan mengubah protokol. Suite akhir PASS.
- **Review statis terfokus:** tidak ada blocker material tersisa; pengaman one-shot berlaku per direktori, operator tidak boleh mengulang evaluasi lewat direktori baru. Tidak ada tuning/early stopping.
- **Integrasi aktual:** `.venv/bin/python run_cghil_experiment.py prepare --input application_train.csv --out results/cghil_m0_m4_20261102`, log `results/cghil_m0_m4_20261102_prepare.log`. Status akhir dicatat setelah command selesai; belum ada klaim training/test pada entri ini.
- **Batas / next:** semua data/model/joblib/prediksi/log lokal di ignored results, tidak push. Lanjut training hanya bila full integrasi PASS; hash commit implementasi dilaporkan setelah verifikasi.

## 2026-11-02 — Gerbang integrasi aktual PASS sebelum training

- **Runner/tests commit:** `959a644`; proses prepare dimulai ketika HEAD masih `4802b50`, kemudian kode yang sama dicommit tanpa perubahan byte; manifest menyimpan HEAD saat prepare selesai beserta SHA256 sumber.
- **Command:** `.venv/bin/python run_cghil_experiment.py prepare --input application_train.csv --out results/cghil_m0_m4_20261102`, exit 0, INTEGRATION PASS. Semua lima metode 215257 asli, fitur 120 (69/51), split 215257/46127/46127, tau=.6 E/U/S=8636/8741/8636.
- **Gerbang:** M2=17272, M3=M4=8636 sintetis. Hard remaining semua kosong; structural NaN mask tepat, unknown kategori sintetis 0, prefix asli sama, kolom dan encoder bersama sama. Total positif efektif M1–M4 34649 (M3 representasi floating 34649.00000000001, sesuai toleransi 1e-7); mayoritas/sintetis bobot1. Tidak mengganti formula.
- **Bukti:** integration_manifest.json lokal mencatat checksum ordered indeks split, sumber/konfigurasi/dependency, kategori encoder serta hash prepared artefact. Semua fit preprocessing/generator/encoder hanya train. Test belum direpresentasikan/dievaluasi; label test hanya dipakai untuk stratifikasi split sesuai kontrak.
- **Tahap berikutnya:** command `.venv/bin/python run_cghil_experiment.py train --out results/cghil_m0_m4_20261102` dimulai setelah verifikasi manifest PASS; belum mengklaim training selesai. Test tetap terkunci sampai lima model dan threshold tersimpan. Tidak push.

## 2026-11-02 — Lima model selesai, threshold dikunci sebelum test

- **Training:** command train selesai exit 0, tepat lima model M0–M4; masing-masing 300 boosting rounds, parameter identik approved, tanpa early stopping/tuning. Validation tidak dipakai fitting.
- **Pretest:** `results/cghil_m0_m4_20261102/pretest_manifest.json` tersimpan sebelum evaluasi, SHA256 `0df2264193062e01cb0dca57e7de47d94b09b5ffa3c3997d207cda3316d64d50`. Check sumber/prepared/model hash PASS; test marker belum ada.
- **Threshold / F1_valid:** M0=.16338752210140228/.30782552224266696; M1=.280007541179657/.30780960679664526; M2=.1651792675256729/.29480402912137227; M3=.2239457666873932/.3042097715866025; M4=.22724014520645142/.2876036320568496. Pemilihan kandidat unik, exact F1 tie terbesar; threshold tidak diubah berdasarkan test.
- **Status:** gerbang integrasi dan pra-test PASS. Catatan ini dibuat dan akan dicommit sebelum menjalankan evaluasi test satu kali. Tidak memilih model/metode dari skor validation dan tidak mengubah desain.

## Entri berikutnya (diisi Codex dari pekerjaan aktual)

### YYYY-MM-DD — [Nama checkpoint]

- **Tujuan / tahap:**
- **Perubahan dan file:**
- **Data & konfigurasi / versi:**
- **Verifikasi (command nyata) dan hasil:**
- **Keputusan / status:** PASS / FAIL / USULAN / BLOCKED; siapa menyetujui bila relevan.
- **Batasan / isu tersisa:**
- **Langkah berikutnya:**
- **Git:** branch; commit sebelumnya (jika ada); hash commit baru dilaporkan sesudah commit dalam jawaban Codex atau entri berikutnya.

**Aturan:** jangan mengisi angka atau hasil sebelum uji dijalankan; jangan mencatat `GO` sebagai persetujuan formal pembimbing; jangan menambahkan hasil train/test tanpa eksperimen.
