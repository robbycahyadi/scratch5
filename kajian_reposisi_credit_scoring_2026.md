# Kajian Terarah Reposisi Tesis: Risiko Gagal Bayar Kredit Konsumen
Tanggal: 28 Oktober 2026

## Ringkasan keputusan
**Status: BELUM LAYAK MENGUNCI KLAIM NOVELTY.** Berdasarkan penelusuran terarah, bukan SLR formal, fokus pada penanganan ketimpangan kelas dan kualitas probabilitas risiko adalah kandidat yang paling jelas masalah dan evaluasinya, tetapi literatur 2025–2026 sudah membahas komponen utama pendekatan ini. Kontribusi yang mungkin dipertahankan bersifat studi empiris kontekstual yang ketat, bukan metode baru. Kesediaan pembimbing menerima bentuk kontribusi tersebut perlu dibicarakan; tidak dapat dipastikan hanya dari literatur.

## Keputusan pengguna yang dipertahankan
- Bidang: risiko gagal bayar kredit konsumen.
- Data: Home Credit Default Risk (kelayakan izin sudah dikonfirmasi pengguna).
- Metode: ML mapan, XGBoost sebagai kandidat; tidak menggunakan federated learning.
- Konteks koperasi Indonesia tidak lagi menjadi konteks penelitian.
- Kontribusi dan judul akhir belum diputuskan.

## Metode kajian dan keterbatasan
Pencarian web akademik terarah pada karya 2022–2026 dan sumber data resmi, bertolak dari SLR dan diikuti pemeriksaan artikel primer. Ini **bukan SLR formal**, belum merupakan pencarian lengkap/PRISMA, dan tidak mengklaim membuktikan ketiadaan publikasi identik. Penilaian 'padat' adalah sintesis kualitatif atas karya terdekat yang ditemukan.

## Landasan SOTA
1. Ayari, Guetari & Kraïem (2025/vol 2026), *Machine learning powered financial credit scoring: a systematic literature review*, Artificial Intelligence Review, DOI: 10.1007/s10462-025-11416-2. https://link.springer.com/article/10.1007/s10462-025-11416-2
2. Bahlool, Hewahi & Elmedany (2026), *Performance, Fairness, and Explainability in AI-Based Credit Scoring*, JRFM 19(2), 104. DOI: 10.3390/jrfm19020104. https://www.mdpi.com/1911-8074/19/2/104
3. Zhang dkk. (2026), *Machine Learning for Individual Credit Risk Assessment: A Systematic Literature Review*, JRFM 19(8), 607. DOI: 10.3390/jrfm19080607. https://www.mdpi.com/1911-8074/19/8/607
4. Bahadori & Hassanzadeh (2026), *A comprehensive literature review on AI-based credit assessment in digital lending*, ESWA, DOI: 10.1016/j.eswa.2026.131872. https://www.sciencedirect.com/science/article/pii/S0957417426007852

## Peta karya primer dan arti untuk seleksi
| Masalah/arah | Karya yang dekat | Kesimpulan yang dapat dipertahankan |
|---|---|---|
| Menambah sumber informasi kredit | Hlongwane dkk. (2024), *Enhancing credit scoring accuracy with a comprehensive evaluation of alternative data*. https://pmc.ncbi.nlm.nih.gov/articles/PMC11108212/ | Perbandingan tambahan informasi pada Home Credit sudah ada; tidak layak mengklaim baru hanya karena memanfaatkan tabel riwayat. |
| Missingness | Han dkk. (2025), *SMART*, Scientific Reports. https://www.nature.com/articles/s41598-025-99997-4 | Penanganan kehilangan data punya karya primer kuat; menghapus fitur secara acak bukan kontribusi otomatis. |
| Reject inference / selection bias | Kozodoi dkk. (2025), *Fighting sampling bias*, EJOR. https://www.sciencedirect.com/science/article/pii/S0377221725000839 | Pertanyaan penting, tetapi observasi hasil untuk pemohon yang ditolak tidak tersedia secara langsung dalam Home Credit Default Risk; klaim dampak nyata sulit diverifikasi. |
| Resampling untuk credit scoring | Han dkk. (2024), *NOTE: non-parametric oversampling technique for explainable credit scoring*, Scientific Reports. https://www.nature.com/articles/s41598-024-78055-5 | Penanganan ketimpangan kelas sudah luas diteliti; tidak cukup membandingkan SMOTE vs baseline. |
| Resampling dan kalibrasi | Liu (2026), *The Hidden Cost of Resampling*, preprint arXiv 2606.29720. https://arxiv.org/abs/2606.29720 | Telah menguji distorsi kalibrasi akibat resampling, manfaat kalibrasi ulang, dan beberapa kontrol; jangan mengklaim ini temuan baru. Preprint belum otomatis setara publikasi peer-reviewed. |
| Ketimpangan, model, dan threshold | *Integrating Sequential Hybrid Oversampling with Decision-Theoretic Threshold Design for Credit Risk Assessment* (2026). https://www.mdpi.com/2227-7390/14/9/1467 | Integrasi koreksi ketimpangan dan ambang keputusan sudah diteliti. Pembeda harus lebih substansial daripada menggabungkan prosedur tersebut. |
| Kalibrasi antarsegmen | Narayan (2026), *Multicalibration for Consumer-credit Probability of Default*, SSRN. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7255020 | Sudah ada kajian langsung pada Home Credit; status preprint harus dicatat. |

## Fakta mengenai data
Home Credit `application_train` berisi label `TARGET` yang secara resmi didefinisikan sebagai kesulitan pembayaran (keterlambatan lebih dari X hari pada setidaknya satu dari Y angsuran pertama), bukan definisi umum gagal bayar hukum/perbankan. Karena itu operasionalisasi 'risiko gagal bayar' harus menyebut proxy label secara tepat. Tabel sejarah kredit berasal dari periode sebelum pengajuan menurut deskripsi penyelenggara. Dataset tidak memberi hasil faktual untuk permohonan yang ditolak atau biaya ekonomi masing-masing keputusan.
Sumber: https://www.kaggle.com/competitions/home-credit-default-risk/data dan kamus kolom: https://huggingface.co/datasets/jamirc/home_credit_default_risk/blob/main/HomeCredit_columns_description.csv

## Kandidat prioritas (bukan novelty terkunci)
**Pertanyaan kerja:** Apakah penanganan ketimpangan kelas menghasilkan peningkatan deteksi pemohon berisiko yang sepadan dengan perubahan akurasi probabilitas kesulitan pembayaran dan kualitas keputusan berbasis ambang, pada Home Credit Default Risk?

**Mengapa bermakna:** prevalensi kejadian positif rendah dan skor risiko digunakan untuk mendukung keputusan. AUC/F1 sendiri tidak menunjukkan apakah angka probabilitas bermakna atau apakah kebijakan ambang tertentu menjadi lebih baik.

**Apa yang SUDAH DIJAWAB literatur:** resampling dapat mengganggu kalibrasi, kalibrasi ulang bisa membantu, dan pemilihan threshold terkait tujuan keputusan. Dengan demikian penelitian sederhana yang hanya membuktikan fakta-fakta itu lagi **belum cukup** sebagai kontribusi baru.

**Kontribusi minimal yang mungkin:** audit evaluasi terkontrol pada satu dataset konsumen dengan estimand/kriteria keputusan yang ditetapkan sebelum eksperimen; melaporkan kondisi batas, perubahan performa, dan hasil negatif. Ini adalah kontribusi bukti empiris kontekstual yang perlu dinilai bersama pembimbing; bukan klaim metode atau fenomena baru. Jika hanya mereplikasi hasil paper 2026 tanpa perbedaan substantif, arah ini harus dinilai tidak memadai.

**Batas data:** Home Credit tidak menyediakan keuntungan/kerugian bank yang dapat diverifikasi. Evaluasi biaya keputusan memerlukan asumsi yang harus dinyatakan sebagai simulasi, bukan hasil dampak bisnis riil. Label juga merupakan proksi kesulitan pembayaran.

## Dua risiko akademik yang tidak boleh disamarkan
1. **Collision:** Paper Liu 2026 dan studi threshold 2026 sudah dekat. Klaim 'pertama meneliti resampling + kalibrasi + keputusan' tidak didukung.
2. **Nilai kontribusi:** replikasi berbasis dataset tunggal mungkin sah sebagai studi empiris tergantung ekspektasi pembimbing, tetapi tidak bisa dipastikan layak hanya dari tinjauan web.

## Keputusan yang disarankan
**Jangan kunci novelty sekarang.** Pilih kandidat di atas sebagai **posisi pengajuan yang paling terdefinisi berdasarkan penelusuran ini**, dengan catatan collision kuat. Sebelum eksperimen besar, formulasi kontribusi harus dipertajam sehingga tidak mengulang Liu (2026) dan studi threshold (2026). Bila tidak ditemukan pembeda substantif dari dua karya itu, hentikan kandidat tersebut tanpa mengganti topik/domain.

**Satu langkah konkret:** buat matriks pembeda 1 halaman terhadap dua paper tersebut: research question, data, variabel target, evaluasi, hasil, yang belum terjawab, dan batas Home Credit. Ini bukan pencarian novelty tanpa batas; ini gerbang keputusan terarah. Jika matriks tidak menemukan pembeda yang bermakna, status kandidat = belum layak, dan eksplorasi berikutnya harus bertolak dari masalah lain yang didukung SLR, bukan variasi resampling baru.

## Status
- SOTA terarah: dilakukan, dengan cakupan terbatas.
- Gap spesifik yang kuat: **belum terverifikasi**.
- Eksperimen: **belum direkomendasikan**.
- Keputusan pengguna yang sudah ada: tidak diubah.
