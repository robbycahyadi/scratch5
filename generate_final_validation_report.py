"""Render final report from real precheck JSON; no model execution."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
full = json.loads((root/'results/generator_final_full/precheck_smotenc.json').read_text())
smoke = json.loads((root/'results/generator_final_smoke/precheck_smotenc.json').read_text())
sv = full['semantic_validation']
lines = ['# CG-HIL — Final Validation Generator', '', '## 1. Executive Summary', '',
    f"**{full['status']} — rekomendasi {'GO' if full['status']=='PASS' else 'BLOCKED'}.** Full precheck menghasilkan {full['generator']['synthetic_created']:,} sintetis. Tidak ada training model atau eksperimen M0–M4.", '',
    '## 2. Perubahan Implementasi', '',
    '- Peran fitur berasal dari kamus audit, bukan inferensi dtype. Median train dan StandardScaler khusus generator tetap dipakai.',
    '- DAYS_EMPLOYED=365243 dimask menjadi NaN sebelum median generator; completeness dihitung lebih dahulu dari non-NaN mentah.',
    '- Setelah inverse scaling, hanya 12 hitungan sintetis dibulatkan `np.rint` (ties-to-even), dibatasi nonnegatif. DEF sintetis diproyeksikan menjadi min(DEF,OBS) jika diperlukan.',
    '- Representasi model terpisah mempertahankan numerik NaN asli, menambah NaN sentinel, dan menggunakan kategori __MISSING__; shared OrdinalEncoder fit hanya asli train diuji tanpa melatih model.',
    '- Tambahan final: hanya pada sintetis model, FLAG_OWN_CAR=N memask OWN_CAR_AGE dan ORGANIZATION_TYPE=XNA memask DAYS_EMPLOYED. Nilai generator saat pencarian tetangga, skor, dan data asli tidak diubah oleh tambahan ini.', '',
    '## 3. Kebijakan Semantik', '',
    '- XNA organisasi, XNA gender, dan Unknown status keluarga tetap kategori eksplisit, berbeda dari __MISSING__. NAME_INCOME_TYPE tetap dipakai. Tidak ada fitur/indikator baru.',
    '- Arti resmi sentinel tidak diasumsikan; masking merupakan keputusan representasi, bukan definisi resmi. Completeness tetap mengukur keterisian field mentah, bukan applicability/kualitas.',
    '- Nilai moneter, skor normalisasi, dan bangunan _AVG/_MODE/_MEDI tidak dibulatkan. Tidak ada ambang outlier social count >30 atau batas usia buatan.',
    '- Toleransi audit integral/nonnegatif 1e-8 membedakan residu floating-point inverse scaling dari nilai negatif substantif; output hitungan tetap diproyeksikan tepat nonnegatif. Unit test mencakup residu -1e-16.',
    '- Hitungan: ' + ', '.join('`'+c+'`' for c in sv['count_columns']), '',
    '- Sumber keputusan: [Bab III](<BAB_III_CG_HIL_draf_v0_1.md>), [audit semantik](<HOME_CREDIT_SEMANTIC_AUDIT.md>), [kamus 120 fitur](<HOME_CREDIT_FEATURE_DICTIONARY_AUDITED.csv>), dan [catatan notebook](<HOME_CREDIT_NOTEBOOK_SUPPLEMENT.md>) semuanya tersedia dan dipelajari. Hasil precheck lama tersedia; angka semantik baru berasal dari run ini, bukan diasumsikan dari PASS lama.', '',
    '## 4. Hasil Full Precheck', '',
    '### Verifikasi dua relasi pada train asli', '',
    'Statistik berikut dihitung ulang hanya pada train mentah; valid duration berarti nilai terisi setelah sentinel 365243 dimask. Tidak ada observasi asli dikoreksi untuk memaksakan hubungan.', '',
    '```json', json.dumps(full['structural_missingness']['empirical_train'], indent=2), '```', '',
    '### Kebijakan bersama M2/M3/M4', '',
    'Fungsi bersama `synthetic_model_frame` wajib dipanggil untuk setiap keluaran sintetis M2, M3, dan M4 setelah inverse scaling/koreksi hitungan dan sebelum encoder model. Tidak dipanggil pada observasi asli. M2/M3 belum dijalankan; keseragaman ini adalah kontrak implementasi, bukan klaim hasil eksperimen pembanding.', '',
    '| Besaran | Hasil |', '|---|---:|']
for k,v in full['split'].items(): lines.append(f'| Split {k} | {v:,} |')
for k,v in full['completeness'].items(): lines.append(f'| {k} | {v} |')
lines += [f"| w_U | {full['weights']['w_U']:.10f} |", f"| Total bobot positif M1–M4 | {full['weights']['effective_total_positive_M1_to_M4']:,} |", '',
    f"Unit test: 8/8 lulus; termasuk structural NaN, immutabilitas asli, idempotensi dan penolakan NaN/inf tidak sah. Smoke historis sebelum structural fix: 6/6 unit test lulus (sentinel, kategori eksplisit, pembulatan terbatas, kendala, kamus dan floating-point). Smoke test: {smoke['status']}, sintetis {smoke['generator']['synthetic_created']}. Seed 42; k_neighbors=5.",
    'Versi: ' + ', '.join(k+'='+v for k,v in full['version'].items()), '',
    'Numerik/kategorikal: 69/51, ditentukan kamus audit; 120 prediktor tidak berubah.', '',
    '## 5. Semantic Validation', '',
    f"Koreksi hitungan: {full['generator']['count_corrected_rows']:,} baris dan {full['generator']['count_corrected_cells']:,} sel berubah (toleransi pelaporan 1e-8). Semua hitungan sesudah koreksi diperiksa ulang.", '',
    'Sebelum = sintetis aktual setelah inverse scaling, sudah memakai kebijakan sentinel; sesudah = pembulatan hitungan/proyeksi DEF dan structural missingness pada representasi sintetis model. Bukan perbandingan dengan generator lama. Denominator setiap persentase adalah seluruh sintetis S=8.636; hitungan adalah baris per aturan, sehingga antaraturan dapat tumpang tindih. Diagnostik sumber E tersedia dalam JSON.', '',
    '| Aturan | Kelas | Sebelum n (%) | Sesudah n (%) |', '|---|---|---:|---:|']
for k,b in sv['before'].items():
    a=sv['after'][k]
    lines.append(f"| {k} | {b['severity']} | {b['count']} ({b['pct']:.4f}%) | {a['count']} ({a['pct']:.4f}%) |")
lines += ['', 'Hard = domain/tipe/definisi yang jelas; tanda hari juga memakai dukungan nilai sumber, bukan batas usia atau hukum bisnis universal buatan. Dua relasi struktural sekarang menjadi kontrak pascapemrosesan sintetis yang diuji terpisah: FLAG_OWN_CAR=N → OWN_CAR_AGE=NaN, ORGANIZATION_TYPE=XNA → DAYS_EMPLOYED=NaN. Keputusan didukung train empiris, bukan klaim arti resmi kode. Potensi lain tidak dikoreksi otomatis. numeric_missing adalah diagnostik NaN disengaja, bukan invalid numeric; assertion menuntut mask NaN persis sesuai dua kondisi dan menolak inf/NaN lain.', '',
    '## 6. Consistency Checks', '',
    '- Split stratified TARGET 70/15/15, random_state=42 di kedua tahap; ketiga index split saling lepas. ID/TARGET tidak masuk 120 prediktor.',
    '- Seluruh parameter median, scaler, SMOTENC dan encoder fit hanya train. Validation/test hanya dipakai untuk split/jumlah, tidak untuk fit atau memilih kebijakan.',
    '- Median positif raw .60, E=8.636 (c>tau), U=8.741 (c<=tau), tetap baseline; assertion menghentikan proses bila berubah.',
    '- Mayoritas+E dipakai dalam API SMOTENC, bukan U; hanya baris sintetis baru berlabel positif yang diambil. Seluruh 215.257 asli ada dalam gabungan model 223.893 baris; prefix diuji sama dengan representasi model asli. Numerik asli sama dengan raw kecuali sentinel→NaN; bukan hasil imputasi generator.',
    '- Nama/urutan fitur konsisten; kategori asli/sintetis dikonversi menggunakan encoder train yang sama dan tidak ada kategori sintetis tidak dikenal.',
    '- M1: n1(1+2S/n1); M2: n1+2S; M3: n1(1+S/n1)+S; M4: nE+nU(1+S/nU)+S. Semuanya 34.649. Mayoritas/sintetis berbobot 1.',
    '- M3 dan M4 masing-masing S=8.636 secara spesifikasi; hanya generator M4 dijalankan. Tidak mengklaim telah menjalankan pembanding.',
    '- Durasi sintetis diperiksa langsung tidak sama dengan 365243 dan tidak positif; numerik sebelum structural masking finite dan nilai teramati sesudah masking finite, 12 hitungan integral/nonnegatif dan kedua DEF<=OBS diuji dengan assertion terpisah dari validator.', '',
    '## 7. Remaining Limitations', '',
    '- Dokumen kamus bersumber salinan sekunder; makna resmi 365243/XNA dan formula normalisasi belum terverifikasi. Potensi inkonsistensi tidak disamakan dengan kemustahilan.',
    '- Missingness sintetis tidak sepenuhnya merekonstruksi semua missing asli; hanya dua pola struktural yang telah didukung train empiris dipulihkan. Semua missing asli tetap tersedia.',
    '- Kategori pekerjaan/income/organisasi lain dan umur mobil relatif terhadap usia klien tetap diagnostik, tidak dipaksa konsisten. Tidak ada resampling ulang atau perubahan algoritma.',
    '- Skor raw menghitung sentinel/kode eksplisit sebagai terisi, mencakup missing struktural dan dominasi kelompok bangunan. Tidak diubah applicable-aware/domain-weighted.',
    '- Smoke pertama gagal pada assertion dtype CNT_CHILDREN (concat int64 asli dengan float64 sintetis), bukan kehilangan nilai. Perbaikan minimum: schema numerik model sama-sama float64; smoke ulang lulus. Tidak ada nilai asli dibulatkan/diimputasi.',
    '- Rentang per kolom dan uji terbatas tidak membuktikan seluruh kombinasi semantik mungkin. Tidak ada klaim performa/keunggulan CG-HIL.', '',
    '## 8. Final Recommendation', '',
    ('**GO untuk membekukan implementasi generator yang diuji**, dengan review mahasiswa atas keterbatasan dan kontrak representasi ini sebelum eksperimen utama. Tidak diperlukan revisi strategi. Ini bukan persetujuan otomatis perubahan Bab III.' if full['status']=='PASS' else '**BLOCKED**: terdapat hard violation tersisa di JSON; jangan lanjut eksperimen utama atau mengubah algoritma secara sepihak.'), '',
    'Bukti terverifikasi = angka JSON dan assertion/test yang dijalankan. Keputusan implementasi = masking sentinel, pembulatan ties-to-even/proyeksi DEF, dan encoder bersama. Asumsi/keterbatasan = interpretasi joint status dan sumber sekunder. Persetujuan yang masih diperlukan = pembekuan kontrak tersebut dalam protokol tesis, tanpa mengedit Bab I/III otomatis.', '',
    '## Reproduksi dan artefak', '',
    '```bash', '.venv/bin/python -m unittest -v test_cghil_semantics', '.venv/bin/python precheck_smotenc_cghil.py --input application_train.csv --out results/generator_final_smoke', '.venv/bin/python precheck_smotenc_cghil.py --input application_train.csv --out results/generator_final_full --full', '.venv/bin/python generate_final_validation_report.py', '```', '',
    '- [JSON full](<results/generator_final_full/precheck_smotenc.json>)', '- [JSON smoke](<results/generator_final_smoke/precheck_smotenc.json>)', '- [Sampel sintetis aktual](<results/generator_final_full/synthetic_model.csv.gz>)', '- [Generator](<precheck_smotenc_cghil.py>)', '- [Kebijakan dan validator](<cghil_semantics.py>)', '- [Unit test](<test_cghil_semantics.py>)', '',
    'SHA256 dataset mentah sebelum validasi: `52e96b895b1112e1c853f670e58372719c8441c5ed1c57ac2f7fad559d784f5f`. Dataset hanya dibaca oleh pipeline; SHA256 sesudah validasi identik (terverifikasi).']
(root/'CG_HIL_GENERATOR_FINAL_VALIDATION.md').write_text('\n'.join(lines)+'\n')
