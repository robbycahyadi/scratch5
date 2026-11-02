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
