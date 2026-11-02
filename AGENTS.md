# AGENTS.md — Eksperimen Tesis CG-HIL

## Peran dan prioritas

Repositori ini digunakan untuk **implementasi dan evaluasi tesis Magister LTI STEI ITB**, bukan produk software umum. Bantu mahasiswa menyelesaikan tesis yang valid secara akademik, sederhana, dapat direproduksi, dan dipahami sendiri. Keputusan strategis milik mahasiswa; keputusan formal akademik mengikuti pembimbing/program.

**WAJIB pada awal sesi Codex:**
1. Baca file `AI_THESIS_WORKING_CONSTITUTION.md` di root (jika nama/ekstensinya berbeda, temukan file asli `AI_THESIS_WORKING_CONSTITUTION*`; jangan membuat isinya dari ingatan). Dokumen tersebut adalah konstitusi kerja, bukan file yang boleh diganti diam-diam.
2. Baca `THESIS_STATE.md`, kemudian dokumen Bab I/Bab III, laporan generator, dan skrip yang relevan dengan tugas saat ini **jika tersedia**.
3. Baca `EXPERIMENT_LOG.md`, cek `git status --short`, `git log -5 --oneline` (jika ada Git), dan identifikasi berkas yang benar-benar ada sebelum merencanakan perubahan.
4. Jika sumber penting hilang/bertentangan, laporkan keterbatasan dan selesaikan hanya bagian yang aman. Jangan mengarang fakta, keputusan, atau hasil.

Urutan rujukan: ketentuan/keputusan eksplisit terbaru mahasiswa atau pembimbing > konstitusi kerja > `THESIS_STATE.md` > dokumen metode yang berlaku > laporan eksperimen dan kode. Bila bertentangan, **jelaskan konflik** dan jangan diam-diam memilih perubahan substantif.

## Posisi penelitian yang tidak boleh bergeser sepihak

- Topik kerja: *Completeness-Guided Hybrid Imbalance Learning* (CG-HIL) untuk prediksi risiko kesulitan pembayaran kredit konsumen pada Home Credit Default Risk.
- Masalah: kelas positif jarang dan sebagian fitur aplikasi tidak terisi.
- Unit: aplikasi kredit. Target: `TARGET=1` sesuai definisi operasional dataset, bukan semua jenis gagal bayar.
- Artefak: metode seleksi oversampling/pembobotan berbasis kelengkapan; model prediksi XGBoost **satu keluarga algoritma**; tidak memakai Federated Learning.
- E = minoritas dengan skor kelengkapan di atas median train positif; U = sisanya. U tetap masuk pelatihan dan diberi bobot. Semua baris asli dipertahankan.
- Pengujian direncanakan M0 (standar), M1 (bobot), M2 (SMOTENC), M3 (hibrida global), M4 (CG-HIL). **M3 vs M4** perbandingan utama; PR-AUC/average precision metrik primer.
- Tidak menambah dataset, model, algoritma, dashboard, framework, eksperimen, atau perubahan RQ/novelty tanpa alasan material serta persetujuan mahasiswa.
- Bab III v0.1 adalah draf/usulan teknis. Keberhasilan precheck generator bukan bukti peningkatan PR-AUC.

## Invarian data dan eksperimen

- Baca data mentah secara read-only. Simpan hash sumber; jangan mengubah file Home Credit yang didownload.
- Split awal yang sudah dipakai untuk precheck: 70/15/15 stratified, seed 42; set tetap sama untuk metode yang dibandingkan.
- `SK_ID_CURR` dan `TARGET` tidak boleh masuk prediktor; jangan memakai label validasi/uji untuk membuat fitur, imputasi, sampling, atau encoder.
- Fitting preprocessing, skor/median E-U, scaling, encoding dan SMOTENC dilakukan train-only. Validasi boleh dipakai sesuai protokol untuk threshold/keputusan yang diizinkan. **Test set jangan disentuh untuk pemilihan metode atau tuning**; hanya untuk evaluasi final setelah protokol dikunci.
- Definisi kerja kelengkapan yang telah diuji: proporsi 120 fitur prediktor yang `notna()` pada data mentah **sebelum** imputasi/masking sentinel. Ukuran ini bukan kualitas/kecukupan semantik; jangan menggantinya dengan domain-weighted/applicability-aware sepihak.
- Rancangan yang diuji: `tau=0.6`, `E=8636`, `U=8741`, `S=min(E,U)=8636`, `w_U=1+S/U ≈ 1.9879876444`; total bobot efektif kelas positif M1–M4 `34649` pada split tersebut. Angka tersebut adalah **hasil audit/precheck**, bukan skor model.
- Kontrak generator yang diuji: `SMOTENC(k_neighbors=5)`; median numerik train dan `StandardScaler` hanya untuk generator; kategori dibedakan dari `__MISSING__`; `DAYS_EMPLOYED=365243` **jangan diinterpolasi sebagai durasi**; numerik asli tetap mempertahankan missingness; 12 fitur hitungan sintetis dibulatkan deterministik/nonnegatif; `DEF<=OBS` diperiksa. Pada sintetis untuk model: `FLAG_OWN_CAR=N -> OWN_CAR_AGE=NaN`; `ORGANIZATION_TYPE=XNA -> DAYS_EMPLOYED=NaN`. Terapkan pascapemrosesan sintetis bersama untuk M2/M3/M4.
- Nilai khusus `XNA` atau `Unknown` tidak boleh disamakan satu sama lain atau otomatis dibuang; hindari aturan semantik yang tidak punya dasar bukti.
- Kode/data yang sudah diuji tidak boleh diubah saat langkah freeze kecuali kegagalan validasi baru memaksa revisi terdokumentasi.
- M1–M4 diusahakan memakai total bobot efektif positif yang setara. M3 dan M4 harus memiliki jumlah sintetis sama. Parameter XGBoost harus tetap sama antarmodel kecuali perlakuan ketimpangan yang diuji.

## Disiplin tugas

- Kerja **decision-first** dan anti-overengineering. Untuk tugas nomor 6: bekukan versi implementasi generator yang benar-benar diuji, jangan menjalankan eksperimen baru. Untuk nomor 7: ajukan **satu** konfigurasi XGBoost/protokol yang sederhana, dengan alasan, pemeriksaan kompatibilitas, dan bukti; jangan train/evaluasi M0–M4 dulu.
- Jika detail metode masih usulan, tulis `USULAN / MENUNGGU PERSETUJUAN`, bukan `FINAL`.
- Jalankan tes yang paling sempit namun memadai; hindari verifikasi berulang yang tidak menambah keputusan.
- Jika pengujian gagal, laporkan akar masalah dan perbaikan minimum; jangan mengubah desain penelitian agar tes terlihat hijau.
- Jangan menyatakan hasil yang tidak dijalankan. Catat command, versi library, seed, file input, hasil pass/fail, dan keterbatasan secara ringkas.
- Output laporan dalam Bahasa Indonesia, bedakan fakta teruji, asumsi, rekomendasi, dan keputusan mahasiswa/pembimbing.

## Git, commit, dan log — WAJIB

- Sebelum perubahan, cek status Git, branch, commit terakhir, dan lokasi root. Jangan reset/checkout/clean/amend/rebase/force-push, menghapus pekerjaan orang lain, atau memodifikasi remote tanpa persetujuan.
- Jika Git belum ada, inisialisasi **hanya setelah memastikan folder ini memang root proyek**, bukan subfolder repo lain. Jangan membuat remote otomatis.
- Pelihara `.gitignore`: minimal melindungi data Kaggle mentah, data privat/credential, `.env*`, `.venv/`, cache, hasil besar dan model biner. **Jangan** mengabaikan semua `.csv` karena kamus audit dan tabel ringkas mungkin perlu dilacak. Verifikasi `git status` agar data mentah tidak terlacak/ter-stage.
- **Sebelum commit**, selesaikan verifikasi relevan, periksa `git diff --check`, tinjau `git diff --cached --name-only`, dan stage **hanya file yang dimiliki tugas ini** (`git add <file>` eksplisit, bukan `git add -A`). Jangan commit hasil/perbaikan yang belum lolos dengan klaim PASS.
- Satu commit kecil per perubahan logis yang selesai dan diverifikasi; contoh `chore: establish thesis experiment guardrails`, `chore: freeze validated CG-HIL generator`, `docs: propose fixed XGBoost protocol`. Jangan rewrite riwayat untuk menyamarkan proses.
- Update `EXPERIMENT_LOG.md` **sebelum commit perubahan material**: tanggal, tujuan, bukti/command, hasil, keputusan/status, keterbatasan dan langkah berikutnya. Log harus menggambarkan kejadian faktual; jangan menciptakan hash commit sebelumnya. ID commit terakhir dapat dilaporkan setelah commit selesai, atau dicatat pada entri berikutnya agar tidak perlu commit tambahan demi mengubah log.
- Setelah commit, berikan hash pendek dan `git status --short`. **Tidak boleh push** kecuali pengguna secara eksplisit meminta push; jika repo tidak punya remote, jangan mengarang/membuat remote.
- Jika working tree berisi perubahan lain, jangan sertakan dalam commit. Jika file yang hendak diubah sudah punya perubahan tak terkait, hindari menimpanya dan laporkan konflik.

## Penyelesaian tugas

Laporkan singkat: tujuan, file berubah, pemeriksaan yang benar-benar dijalankan, hasil, keputusan/hal yang masih perlu disetujui, hash commit (jika dibuat), dan **satu langkah berikutnya**. Jangan mengubah keputusan riset atau menulis klaim hasil tesis dari laporan precheck.
