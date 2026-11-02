# CG-HIL — Catatan analisis lanjutan pascahasil M0–M4

**Tanggal pencatatan:** 2 November 2026  
**Status:** **CATATAN DISKUSI / KANDIDAT ANALISIS**, belum merupakan persetujuan mahasiswa untuk menjalankan eksperimen atau merevisi metode/protokol/RQ.  
**Sumber status utama:** `THESIS_STATE.md`. Hasil primer dan protokol yang telah dibekukan tetap berlaku.

## Konteks hasil yang tidak diubah

Eksperimen M0–M4 sudah selesai; integrasi dan 15/15 unit test dilaporkan PASS. Metrik primer `average_precision_score` (AP) pada test: M0 0,247985; M1 0,247339; M2 0,222291; M3 0,240148; M4 (CG-HIL) 0,223366. Kontras utama **M4−M3 = −0,016782538865233926**; belum ada interval ketidakpastian/signifikansi. M4 tidak unggul. Pola kelemahan M4 terhadap M3 juga sudah tampak pada AP validasi. Jangan mengubah hasil ini atau menafsirkan PASS teknis sebagai keunggulan prediksi.

## 1. Ablation: sumber sintesis vs. pembobotan

**Pertanyaan:** Apakah penurunan AP CG-HIL lebih terkait pembatasan sumber SMOTENC ke kelompok E, pengalihan bobot positif asli ke U, atau interaksi keduanya?

Perbandingan utama yang sudah dijalankan (M3 vs M4) mengubah dua dimensi sekaligus. Usulan diagnostik minimal adalah desain 2 × 2:

| | Pembobotan global | Pembobotan E/U (khusus U) |
|---|---|---|
| Sumber sintesis seluruh positif | **M3** (sudah ada) | **A1** (kandidat) |
| Sumber sintesis E saja | **A2** (kandidat) | **M4** (sudah ada) |

- **M3 vs A1** atau **A2 vs M4** mengisolasi perbedaan skema bobot pada sumber sintesis yang sama.
- **M3 vs A2** atau **A1 vs M4** mengisolasi perbedaan sumber sintesis pada skema bobot yang sama.
- Pertahankan jumlah sintesis `S=8636`, total bobot positif efektif `34649`, seluruh baris asli, fitur, generator bersama, XGBoost dan parameter yang telah dibekukan, jika analisis ini nanti disetujui.
- Mencatat AP per konfigurasi saja belum membuktikan mekanisme kausal universal. Interaksi dua dimensi perlu diperhatikan.
- **Status:** kandidat analisis eksploratori setelah hasil test terlihat, **bukan** pembanding konfirmatori yang sudah dipraregistrasi. Tidak boleh men-tuning A1/A2 pada test atau mengganti hasil utama M3 vs M4.

## 2. Diagnosis kriteria kelengkapan dan pembagian E/U

**Pertanyaan:** Apakah proporsi fitur `notna()` mentah sebelum imputasi benar-benar menjadi proksi yang layak bagi kecukupan informasi untuk sintesis, atau justru mencampurkan *missingness* tidak berlaku (*not applicable*), nilai khusus, dan kekosongan informasi substantif?

Rancangan beku: `tau=0,6`, E positif latih dengan `c>tau` = 8.636; U positif latih dengan `c<=tau` = 8.741. Skor dihitung dari 120 prediktor mentah sebelum perlakuan sentinel; **bukan** ukuran kualitas semantik yang telah tervalidasi.

Pola relevan yang sudah tercatat dari audit semantik:
- `FLAG_OWN_CAR=N` berkaitan dengan `OWN_CAR_AGE` kosong: secara konsep umur mobil tidak berlaku bagi pemohon tanpa mobil.
- `ORGANIZATION_TYPE=XNA` berkaitan dengan nilai khusus `DAYS_EMPLOYED=365243`; sebelum masking sentinel, nilai numerik ini dihitung sebagai *terisi*. Arti resmi kode belum seluruhnya terverifikasi.

**Pemeriksaan yang diusulkan (hanya train; tidak melatih model):**
1. Audit pola missing/not-applicable pada 120 fitur, terutama fitur kondisional, serta dampaknya terhadap skor kelengkapan; jangan mengklaim seluruh nilai kosong bersifat struktural.
2. Deskripsikan perbedaan karakteristik pemohon positif E vs U dan cakupan karakteristik sumber sintesis. Bila ingin membandingkan prevalensi `TARGET=1` menurut kelengkapan, gunakan **seluruh data latih**, karena E dan U sendiri didefinisikan dari observasi yang semuanya `TARGET=1`.
3. Periksa *seberapa banyak* keanggotaan E/U berpotensi berubah di bawah definisi deskriptif yang sadar ketidakberlakuan; jangan menggunakan hasil ini untuk diam-diam mendefinisikan ulang M4.

**Batas kesimpulan:** masalah pada proksi kelengkapan adalah **hipotesis penyebab**, bukan fakta bahwa E/U saat ini salah atau pasti akan memberi AP lebih baik jika diganti. Perubahan definisi E/U adalah **revisi metode** yang membutuhkan keputusan mahasiswa, dokumentasi pascahoc, dan rencana evaluasi baru; tidak menjadi bagian dari M4 final yang sudah dibekukan.

## 3. Kandidat tambahan yang bersifat opsional

**A. Analisis kesalahan M3 vs M4 (tanpa fitting):** gunakan prediksi tersimpan, bila tersedia, untuk melihat kasus positif/negatif yang berbeda urutan atau berbeda keputusan di antara kedua model, dan apakah perbedaan berkaitan dengan tingkat kelengkapan. Tujuannya menemukan *di mana* M4 melemah, bukan membenarkan penyebab tanpa bukti. Analisis pada test berstatus deskriptif pascahoc, tidak untuk memilih perubahan metode.

**B. Ketidakpastian delta AP (bootstrap berpasangan):** dari pasangan label/prediksi uji yang **sudah dibekukan**, perkirakan interval ketidakpastian untuk `AP(M4)−AP(M3)`. Ini membantu menilai ketelitian estimasi, bukan penyebab perbedaan atau generalisasi lintas institusi. Tidak memerlukan melatih ulang atau menyesuaikan threshold; opsional bila memang dibutuhkan untuk penyajian akademik.

## Urutan kerja yang direkomendasikan, belum disetujui

1. **Diagnosis E/U** dari data latih terlebih dahulu, karena menguji asumsi pusat CG-HIL dan tidak memerlukan model baru.
2. Jika penjelasan masih belum cukup, **pertimbangkan ablation A1/A2** sebagai analisis eksploratori pada data validasi yang sudah tersedia, dengan batas interpretasi karena hasil validasi sebelumnya telah dilihat.
3. Analisis kesalahan dan bootstrap hanya jika membantu menjawab pertanyaan interpretasi yang tersisa; tidak otomatis wajib.

**Aturan tetap:** Tidak ada eksekusi eksperimen, tuning, penggantian threshold, penambahan dataset/model, perubahan RQ, revisi protokol beku, atau penggantian kesimpulan hasil test tanpa keputusan eksplisit mahasiswa. Data test yang sudah dibuka tidak boleh dipakai sebagai sarana pencarian konfigurasi yang menang. Persetujuan pembimbing untuk konteks/judul/RQ final tetap persoalan terpisah.
