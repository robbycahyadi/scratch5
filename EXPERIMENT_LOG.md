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
