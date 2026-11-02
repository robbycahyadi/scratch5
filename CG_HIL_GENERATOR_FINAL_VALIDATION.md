# CG-HIL — Final Validation Generator

## 1. Executive Summary

**PASS — rekomendasi GO.** Full precheck menghasilkan 8,636 sintetis. Tidak ada training model atau eksperimen M0–M4.

## 2. Perubahan Implementasi

- Peran fitur berasal dari kamus audit, bukan inferensi dtype. Median train dan StandardScaler khusus generator tetap dipakai.
- DAYS_EMPLOYED=365243 dimask menjadi NaN sebelum median generator; completeness dihitung lebih dahulu dari non-NaN mentah.
- Setelah inverse scaling, hanya 12 hitungan sintetis dibulatkan `np.rint` (ties-to-even), dibatasi nonnegatif. DEF sintetis diproyeksikan menjadi min(DEF,OBS) jika diperlukan.
- Representasi model terpisah mempertahankan numerik NaN asli, menambah NaN sentinel, dan menggunakan kategori __MISSING__; shared OrdinalEncoder fit hanya asli train diuji tanpa melatih model.
- Tambahan final: hanya pada sintetis model, FLAG_OWN_CAR=N memask OWN_CAR_AGE dan ORGANIZATION_TYPE=XNA memask DAYS_EMPLOYED. Nilai generator saat pencarian tetangga, skor, dan data asli tidak diubah oleh tambahan ini.

## 3. Kebijakan Semantik

- XNA organisasi, XNA gender, dan Unknown status keluarga tetap kategori eksplisit, berbeda dari __MISSING__. NAME_INCOME_TYPE tetap dipakai. Tidak ada fitur/indikator baru.
- Arti resmi sentinel tidak diasumsikan; masking merupakan keputusan representasi, bukan definisi resmi. Completeness tetap mengukur keterisian field mentah, bukan applicability/kualitas.
- Nilai moneter, skor normalisasi, dan bangunan _AVG/_MODE/_MEDI tidak dibulatkan. Tidak ada ambang outlier social count >30 atau batas usia buatan.
- Toleransi audit integral/nonnegatif 1e-8 membedakan residu floating-point inverse scaling dari nilai negatif substantif; output hitungan tetap diproyeksikan tepat nonnegatif. Unit test mencakup residu -1e-16.
- Hitungan: `CNT_CHILDREN`, `CNT_FAM_MEMBERS`, `OBS_30_CNT_SOCIAL_CIRCLE`, `DEF_30_CNT_SOCIAL_CIRCLE`, `OBS_60_CNT_SOCIAL_CIRCLE`, `DEF_60_CNT_SOCIAL_CIRCLE`, `AMT_REQ_CREDIT_BUREAU_HOUR`, `AMT_REQ_CREDIT_BUREAU_DAY`, `AMT_REQ_CREDIT_BUREAU_WEEK`, `AMT_REQ_CREDIT_BUREAU_MON`, `AMT_REQ_CREDIT_BUREAU_QRT`, `AMT_REQ_CREDIT_BUREAU_YEAR`

- Sumber keputusan: [Bab III](<BAB_III_CG_HIL_draf_v0_1.md>), [audit semantik](<HOME_CREDIT_SEMANTIC_AUDIT.md>), [kamus 120 fitur](<HOME_CREDIT_FEATURE_DICTIONARY_AUDITED.csv>), dan [catatan notebook](<HOME_CREDIT_NOTEBOOK_SUPPLEMENT.md>) semuanya tersedia dan dipelajari. Hasil precheck lama tersedia; angka semantik baru berasal dari run ini, bukan diasumsikan dari PASS lama.

## 4. Hasil Full Precheck

### Verifikasi dua relasi pada train asli

Statistik berikut dihitung ulang hanya pada train mentah; valid duration berarti nilai terisi setelah sentinel 365243 dimask. Tidak ada observasi asli dikoreksi untuk memaksakan hubungan.

```json
{
  "train_rows": 215257,
  "car_N_rows": 142086,
  "car_N_age_present": 0,
  "organization_XNA_rows": 38756,
  "organization_XNA_raw_sentinel": 38756,
  "organization_XNA_valid_duration_after_sentinel_mask": 0,
  "sentinel_organization_nonXNA": 0
}
```

### Kebijakan bersama M2/M3/M4

Fungsi bersama `synthetic_model_frame` wajib dipanggil untuk setiap keluaran sintetis M2, M3, dan M4 setelah inverse scaling/koreksi hitungan dan sebelum encoder model. Tidak dipanggil pada observasi asli. M2/M3 belum dijalankan; keseragaman ini adalah kontrak implementasi, bukan klaim hasil eksperimen pembanding.

| Besaran | Hasil |
|---|---:|
| Split train | 215,257 |
| Split validation | 46,127 |
| Split test | 46,127 |
| tau | 0.6 |
| nE | 8636 |
| nU | 8741 |
| S_full | 8636 |
| n_at_median | 2794 |
| w_U | 1.9879876444 |
| Total bobot positif M1–M4 | 34,649 |

Unit test: 8/8 lulus; termasuk structural NaN, immutabilitas asli, idempotensi dan penolakan NaN/inf tidak sah. Smoke historis sebelum structural fix: 6/6 unit test lulus (sentinel, kategori eksplisit, pembulatan terbatas, kendala, kamus dan floating-point). Smoke test: PASS, sintetis 300. Seed 42; k_neighbors=5.
Versi: python=3.13.5, pandas=3.1.0, numpy=2.5.4, sklearn=1.9.1, imblearn=0.14.2

Numerik/kategorikal: 69/51, ditentukan kamus audit; 120 prediktor tidak berubah.

## 5. Semantic Validation

Koreksi hitungan: 8,184 baris dan 25,582 sel berubah (toleransi pelaporan 1e-8). Semua hitungan sesudah koreksi diperiksa ulang.

Sebelum = sintetis aktual setelah inverse scaling, sudah memakai kebijakan sentinel; sesudah = pembulatan hitungan/proyeksi DEF dan structural missingness pada representasi sintetis model. Bukan perbandingan dengan generator lama. Denominator setiap persentase adalah seluruh sintetis S=8.636; hitungan adalah baris per aturan, sehingga antaraturan dapat tumpang tindih. Diagnostik sumber E tersedia dalam JSON.

| Aturan | Kelas | Sebelum n (%) | Sesudah n (%) |
|---|---|---:|---:|
| category_domain:NAME_CONTRACT_TYPE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:CODE_GENDER | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_OWN_CAR | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_OWN_REALTY | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:NAME_TYPE_SUITE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:NAME_INCOME_TYPE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:NAME_EDUCATION_TYPE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:NAME_FAMILY_STATUS | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:NAME_HOUSING_TYPE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_MOBIL | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_EMP_PHONE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_WORK_PHONE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_CONT_MOBILE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_PHONE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_EMAIL | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:OCCUPATION_TYPE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:REGION_RATING_CLIENT | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:REGION_RATING_CLIENT_W_CITY | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:WEEKDAY_APPR_PROCESS_START | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:HOUR_APPR_PROCESS_START | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:REG_REGION_NOT_LIVE_REGION | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:REG_REGION_NOT_WORK_REGION | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:LIVE_REGION_NOT_WORK_REGION | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:REG_CITY_NOT_LIVE_CITY | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:REG_CITY_NOT_WORK_CITY | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:LIVE_CITY_NOT_WORK_CITY | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:ORGANIZATION_TYPE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FONDKAPREMONT_MODE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:HOUSETYPE_MODE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:WALLSMATERIAL_MODE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:EMERGENCYSTATE_MODE | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_2 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_3 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_4 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_5 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_6 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_7 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_8 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_9 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_10 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_11 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_12 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_13 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_14 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_15 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_16 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_17 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_18 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_19 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_20 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain:FLAG_DOCUMENT_21 | hard | 0 (0.0000%) | 0 (0.0000%) |
| category_domain | hard | 0 (0.0000%) | 0 (0.0000%) |
| numeric_nonfinite | hard | 0 (0.0000%) | 0 (0.0000%) |
| numeric_missing | diagnostic | 0 (0.0000%) | 6780 (78.5086%) |
| count_fractional:CNT_CHILDREN | hard | 2251 (26.0653%) | 0 (0.0000%) |
| count_negative:CNT_CHILDREN | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:CNT_FAM_MEMBERS | hard | 3878 (44.9050%) | 0 (0.0000%) |
| count_negative:CNT_FAM_MEMBERS | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:OBS_30_CNT_SOCIAL_CIRCLE | hard | 4617 (53.4623%) | 0 (0.0000%) |
| count_negative:OBS_30_CNT_SOCIAL_CIRCLE | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:DEF_30_CNT_SOCIAL_CIRCLE | hard | 624 (7.2256%) | 0 (0.0000%) |
| count_negative:DEF_30_CNT_SOCIAL_CIRCLE | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:OBS_60_CNT_SOCIAL_CIRCLE | hard | 4595 (53.2075%) | 0 (0.0000%) |
| count_negative:OBS_60_CNT_SOCIAL_CIRCLE | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:DEF_60_CNT_SOCIAL_CIRCLE | hard | 339 (3.9254%) | 0 (0.0000%) |
| count_negative:DEF_60_CNT_SOCIAL_CIRCLE | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:AMT_REQ_CREDIT_BUREAU_HOUR | hard | 8 (0.0926%) | 0 (0.0000%) |
| count_negative:AMT_REQ_CREDIT_BUREAU_HOUR | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:AMT_REQ_CREDIT_BUREAU_DAY | hard | 10 (0.1158%) | 0 (0.0000%) |
| count_negative:AMT_REQ_CREDIT_BUREAU_DAY | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:AMT_REQ_CREDIT_BUREAU_WEEK | hard | 64 (0.7411%) | 0 (0.0000%) |
| count_negative:AMT_REQ_CREDIT_BUREAU_WEEK | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:AMT_REQ_CREDIT_BUREAU_MON | hard | 1755 (20.3219%) | 0 (0.0000%) |
| count_negative:AMT_REQ_CREDIT_BUREAU_MON | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:AMT_REQ_CREDIT_BUREAU_QRT | hard | 1365 (15.8059%) | 0 (0.0000%) |
| count_negative:AMT_REQ_CREDIT_BUREAU_QRT | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional:AMT_REQ_CREDIT_BUREAU_YEAR | hard | 6076 (70.3566%) | 0 (0.0000%) |
| count_negative:AMT_REQ_CREDIT_BUREAU_YEAR | hard | 0 (0.0000%) | 0 (0.0000%) |
| count_fractional | hard | 8184 (94.7661%) | 0 (0.0000%) |
| count_negative | hard | 0 (0.0000%) | 0 (0.0000%) |
| DEF30_gt_OBS30 | hard | 4 (0.0463%) | 0 (0.0000%) |
| DEF60_gt_OBS60 | hard | 15 (0.1737%) | 0 (0.0000%) |
| days_employed_positive | hard | 0 (0.0000%) | 0 (0.0000%) |
| days_birth_nonnegative | hard | 0 (0.0000%) | 0 (0.0000%) |
| car_age_negative | hard | 0 (0.0000%) | 0 (0.0000%) |
| relative_days_positive:DAYS_REGISTRATION | hard | 0 (0.0000%) | 0 (0.0000%) |
| relative_days_positive:DAYS_ID_PUBLISH | hard | 0 (0.0000%) | 0 (0.0000%) |
| relative_days_positive:DAYS_LAST_PHONE_CHANGE | hard | 0 (0.0000%) | 0 (0.0000%) |
| car_N_age_present | potential | 6737 (78.0107%) | 0 (0.0000%) |
| car_Y_age_missing | potential | 0 (0.0000%) | 0 (0.0000%) |
| organization_XNA_employed_present | potential | 1142 (13.2237%) | 0 (0.0000%) |
| pensioner_unemployed_nonXNA | potential | 26 (0.3011%) | 26 (0.3011%) |
| organization_XNA_occupation_present | potential | 88 (1.0190%) | 88 (1.0190%) |
| employment_precedes_birth | potential | 0 (0.0000%) | 0 (0.0000%) |
| car_older_than_client | potential | 136 (1.5748%) | 135 (1.5632%) |

Hard = domain/tipe/definisi yang jelas; tanda hari juga memakai dukungan nilai sumber, bukan batas usia atau hukum bisnis universal buatan. Dua relasi struktural sekarang menjadi kontrak pascapemrosesan sintetis yang diuji terpisah: FLAG_OWN_CAR=N → OWN_CAR_AGE=NaN, ORGANIZATION_TYPE=XNA → DAYS_EMPLOYED=NaN. Keputusan didukung train empiris, bukan klaim arti resmi kode. Potensi lain tidak dikoreksi otomatis. numeric_missing adalah diagnostik NaN disengaja, bukan invalid numeric; assertion menuntut mask NaN persis sesuai dua kondisi dan menolak inf/NaN lain.

## 6. Consistency Checks

- Split stratified TARGET 70/15/15, random_state=42 di kedua tahap; ketiga index split saling lepas. ID/TARGET tidak masuk 120 prediktor.
- Seluruh parameter median, scaler, SMOTENC dan encoder fit hanya train. Validation/test hanya dipakai untuk split/jumlah, tidak untuk fit atau memilih kebijakan.
- Median positif raw .60, E=8.636 (c>tau), U=8.741 (c<=tau), tetap baseline; assertion menghentikan proses bila berubah.
- Mayoritas+E dipakai dalam API SMOTENC, bukan U; hanya baris sintetis baru berlabel positif yang diambil. Seluruh 215.257 asli ada dalam gabungan model 223.893 baris; prefix diuji sama dengan representasi model asli. Numerik asli sama dengan raw kecuali sentinel→NaN; bukan hasil imputasi generator.
- Nama/urutan fitur konsisten; kategori asli/sintetis dikonversi menggunakan encoder train yang sama dan tidak ada kategori sintetis tidak dikenal.
- M1: n1(1+2S/n1); M2: n1+2S; M3: n1(1+S/n1)+S; M4: nE+nU(1+S/nU)+S. Semuanya 34.649. Mayoritas/sintetis berbobot 1.
- M3 dan M4 masing-masing S=8.636 secara spesifikasi; hanya generator M4 dijalankan. Tidak mengklaim telah menjalankan pembanding.
- Durasi sintetis diperiksa langsung tidak sama dengan 365243 dan tidak positif; numerik sebelum structural masking finite dan nilai teramati sesudah masking finite, 12 hitungan integral/nonnegatif dan kedua DEF<=OBS diuji dengan assertion terpisah dari validator.

## 7. Remaining Limitations

- Dokumen kamus bersumber salinan sekunder; makna resmi 365243/XNA dan formula normalisasi belum terverifikasi. Potensi inkonsistensi tidak disamakan dengan kemustahilan.
- Missingness sintetis tidak sepenuhnya merekonstruksi semua missing asli; hanya dua pola struktural yang telah didukung train empiris dipulihkan. Semua missing asli tetap tersedia.
- Kategori pekerjaan/income/organisasi lain dan umur mobil relatif terhadap usia klien tetap diagnostik, tidak dipaksa konsisten. Tidak ada resampling ulang atau perubahan algoritma.
- Skor raw menghitung sentinel/kode eksplisit sebagai terisi, mencakup missing struktural dan dominasi kelompok bangunan. Tidak diubah applicable-aware/domain-weighted.
- Smoke pertama gagal pada assertion dtype CNT_CHILDREN (concat int64 asli dengan float64 sintetis), bukan kehilangan nilai. Perbaikan minimum: schema numerik model sama-sama float64; smoke ulang lulus. Tidak ada nilai asli dibulatkan/diimputasi.
- Rentang per kolom dan uji terbatas tidak membuktikan seluruh kombinasi semantik mungkin. Tidak ada klaim performa/keunggulan CG-HIL.

## 8. Final Recommendation

**GO untuk membekukan implementasi generator yang diuji**, dengan review mahasiswa atas keterbatasan dan kontrak representasi ini sebelum eksperimen utama. Tidak diperlukan revisi strategi. Ini bukan persetujuan otomatis perubahan Bab III.

Bukti terverifikasi = angka JSON dan assertion/test yang dijalankan. Keputusan implementasi = masking sentinel, pembulatan ties-to-even/proyeksi DEF, dan encoder bersama. Asumsi/keterbatasan = interpretasi joint status dan sumber sekunder. Persetujuan yang masih diperlukan = pembekuan kontrak tersebut dalam protokol tesis, tanpa mengedit Bab I/III otomatis.

## Reproduksi dan artefak

```bash
.venv/bin/python -m unittest -v test_cghil_semantics
.venv/bin/python precheck_smotenc_cghil.py --input application_train.csv --out results/generator_final_smoke
.venv/bin/python precheck_smotenc_cghil.py --input application_train.csv --out results/generator_final_full --full
.venv/bin/python generate_final_validation_report.py
```

- [JSON full](<results/generator_final_full/precheck_smotenc.json>)
- [JSON smoke](<results/generator_final_smoke/precheck_smotenc.json>)
- [Sampel sintetis aktual](<results/generator_final_full/synthetic_model.csv.gz>)
- [Generator](<precheck_smotenc_cghil.py>)
- [Kebijakan dan validator](<cghil_semantics.py>)
- [Unit test](<test_cghil_semantics.py>)

SHA256 dataset mentah sebelum validasi: `52e96b895b1112e1c853f670e58372719c8441c5ed1c57ac2f7fad559d784f5f`. Dataset hanya dibaca oleh pipeline; SHA256 sesudah validasi identik (terverifikasi).
