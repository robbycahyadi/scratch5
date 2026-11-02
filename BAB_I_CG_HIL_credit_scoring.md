# BAB I — PENDAHULUAN

**Judul kerja:** Pengembangan Metode Hibrida Berbasis Kelengkapan Informasi untuk Penanganan Ketidakseimbangan Kelas pada Prediksi Risiko Gagal Bayar Kredit Konsumen

**Nama metode (sementara):** *Completeness-Guided Hybrid Imbalance Learning* (CG-HIL)

> **Status naskah — 28 Oktober 2026.** Ini adalah **draf Bab I untuk eksplorasi terarah dan diskusi pembimbing**, bukan proposal yang telah disetujui. Arah penelitian CG-HIL telah **dipilih dan dikunci oleh mahasiswa sebagai arah kerja**. Perubahan dari konteks koperasi Indonesia menjadi kredit konsumen masih memerlukan persetujuan formal pembimbing. Mekanisme metode, hasil, dan klaim kebaruan belum dinyatakan terbukti. Sitasi [n] mengacu pada daftar pustaka di akhir berkas. Angka penelitian terdahulu tidak boleh diperlakukan sebagai hasil eksperimen penelitian ini.

## I.1 Latar Belakang

Penilaian risiko kredit (*credit scoring*) merupakan salah satu komponen dalam proses pemberian pinjaman kepada konsumen. Penilaian ini bertujuan memperkirakan kemungkinan pemohon mengalami kesulitan memenuhi kewajiban pembayaran, sehingga lembaga pemberi pinjaman dapat menggunakan informasi risiko sebagai masukan dalam pengambilan keputusan kredit. Dalam pengembangan model berbasis data, permasalahan tersebut umumnya dirumuskan sebagai tugas klasifikasi antara pemohon yang mengalami kesulitan pembayaran dan pemohon lainnya. Bagi analis risiko maupun pengelola proses pemberian kredit, kesalahan mengenali pemohon yang berpotensi bermasalah dapat mengurangi kegunaan sistem penilaian kredit. Sebaliknya, terlalu banyak mengklasifikasikan pemohon sebagai berisiko juga dapat menimbulkan keputusan yang terlalu konservatif. Oleh karena itu, penilaian kinerja model perlu memperhatikan kemampuan mendeteksi kasus yang lebih jarang terjadi serta ketepatan hasil deteksinya [1], [3].

Penggunaan pembelajaran mesin (*machine learning*) memungkinkan pemodelan hubungan yang tidak selalu linear di antara karakteristik pemohon dan hasil pembayaran. Salah satu algoritma yang banyak digunakan untuk data tabular adalah *Extreme Gradient Boosting* (XGBoost), yaitu metode penggabungan sejumlah pohon keputusan melalui proses pembelajaran bertahap [10]. Walaupun demikian, pemilihan algoritma prediksi bukan satu-satunya persoalan. Kualitas dan distribusi data pelatihan dapat memengaruhi kemampuan model mengenali kasus risiko yang jumlahnya relatif sedikit. Zhao dkk. (2024) menunjukkan bahwa pemilihan teknik penyeimbangan kelas dalam prediksi risiko kredit bergantung pada karakteristik dataset dan tidak ada satu teknik yang selalu unggul pada seluruh keadaan [3].

Permasalahan ini terlihat pada dataset *Home Credit Default Risk* yang diterbitkan melalui kompetisi Kaggle oleh Home Credit Group pada 2018. Dataset tersebut memuat informasi aplikasi pinjaman konsumen serta sejumlah tabel riwayat terkait [1]. Bagian `application_train.csv` berisi 307.511 aplikasi berlabel; sebanyak 24.825 aplikasi atau sekitar 8,07% memiliki `TARGET = 1` [2]. Menurut dokumentasi atribut data, label ini menunjukkan adanya **kesulitan pembayaran yang didefinisikan berdasarkan keterlambatan angsuran tertentu**, bukan seluruh kemungkinan peristiwa gagal bayar secara umum [1]. Dengan demikian, istilah *risiko gagal bayar* digunakan dalam penelitian ini sebagai istilah bidang, sedangkan target empiris dibatasi pada definisi operasional `TARGET` dalam dataset.

Ketimpangan tersebut menunjukkan bahwa sebagian besar aplikasi termasuk dalam kelompok `TARGET = 0`, sementara kelompok yang perlu dideteksi lebih sedikit. Pada keadaan seperti ini, ketepatan keseluruhan (*accuracy*) dapat memberikan gambaran yang menyesatkan jika model hanya cenderung memilih kelas mayoritas. Ukuran seperti *recall*, *precision*, F1, dan luas di bawah kurva *precision–recall* (PR-AUC) membantu menilai kemampuan mengenali dan menjaga ketepatan prediksi untuk kelas minoritas. Saito dan Rehmsmeier (2015) menunjukkan pentingnya kurva *precision–recall* dalam evaluasi klasifikasi dengan distribusi kelas yang timpang [11]. ROC-AUC tetap relevan sebagai ukuran kemampuan model mengurutkan risiko, tetapi tidak digunakan sendirian untuk menilai keberhasilan penelitian.

Selain ketimpangan kelas, data aplikasi kredit dapat mengandung nilai yang tidak tersedia (*missing values*). Beberapa atribut tidak selalu terisi dengan tingkat kelengkapan yang sama antarpemohon. Nilai kosong dapat ditangani dengan menghapus observasi, mengisi nilai menggunakan statistik tertentu (*imputation*), atau melalui metode rekonstruksi yang lebih kompleks. Han, Jung, dan Yoo (2025) meneliti masalah ini dalam konteks *credit scoring* dan mengembangkan metode SMART yang menggabungkan pemrosesan data dan imputasi [4]. Penelitian tersebut menunjukkan bahwa penanganan data tidak lengkap merupakan persoalan tersendiri yang relevan terhadap mutu pemodelan kredit, tetapi tidak berarti satu metode imputasi tertentu selalu diperlukan untuk setiap penelitian.

Kedua persoalan—ketimpangan kelas dan ketidaklengkapan data—dapat muncul bersamaan. Salah satu cara menangani ketimpangan adalah *oversampling*, yakni menambah contoh kelas minoritas melalui pengulangan atau pembentukan contoh sintetis. Metode SMOTE, misalnya, membangkitkan contoh baru dengan memanfaatkan kedekatan antarsampel kelas minoritas [9]. Untuk data yang memiliki atribut numerik dan kategorikal, varian SMOTENC menyediakan mekanisme penanganan tipe data campuran [12]. Meskipun demikian, pembentukan data sintetis pada observasi yang mengandung banyak nilai kosong memerlukan keputusan tambahan mengenai atribut mana yang diimputasi dan bagaimana contoh baru dibuat. Keputusan tersebut berpotensi mengubah representasi pola ketidaklengkapan yang terdapat pada data asli. Barnard (2026) mengangkat persoalan ini dalam *preprint* OverNaN, yakni pendekatan oversampling yang mempertimbangkan pola nilai kosong [5].

Penelitian Ben Ammar dan Rubaidi (2026) merupakan acuan langsung bagi rancangan penelitian ini. Mereka mengembangkan *Sequential Hybrid Data Oversampling* (SHDO), yang menyusun lima teknik oversampling, lalu mengintegrasikannya dengan pemodelan kredit dan perancangan ambang keputusan [2]. Pada tahap prapemrosesan Home Credit, mereka melaporkan penyaringan observasi dengan **40 atau lebih nilai kosong**, sehingga jumlah data berkurang dari 307.511 menjadi 155.367 aplikasi atau sekitar 50,5% dari data awal [2]. Strategi tersebut memiliki dasar metodologis untuk membatasi profil data yang terlalu jarang terisi; penyaringan itu **tidak dapat langsung disebut keliru**. Namun, dari sudut pandang perancangan metode, praktik tersebut menimbulkan pertanyaan: **dapatkah ketimpangan kelas ditangani tanpa terlebih dahulu menghilangkan banyak observasi asli yang memiliki informasi tidak lengkap?**

Penelitian lain telah mengembangkan solusi yang berdekatan. Dou dkk. (2023) mengusulkan metode *Switching Triple-Weight-SMOTE* untuk data yang tidak seimbang sekaligus tidak lengkap [6]. Zhu dkk. (2026) menggabungkan *undersampling* berbasis pohon keputusan dan *oversampling* adaptif dengan mempertimbangkan tumpang tindih antarkelas [7]. Ying, Shi, dan Li (2025) juga menggabungkan pembangkitan data sintetis dan pembelajaran yang mempertimbangkan bobot kelas dalam kerangka prediksi risiko kredit [8]. Karya-karya tersebut menegaskan bahwa **SMOTE, pembobotan kelas, dan penggunaan pendekatan hibrida bukan hal baru**. Persoalan penelitian yang masih akan ditelaah bukan bagaimana menggabungkan dua teknik secara umum, melainkan **bagaimana memilih perlakuan penyeimbangan yang berbeda berdasarkan tingkat kelengkapan informasi setiap observasi**.

Berdasarkan sintesis tersebut, penelitian ini **mengusulkan** metode hibrida bernama sementara *Completeness-Guided Hybrid Imbalance Learning* (CG-HIL). Dalam rancangan ini, setiap observasi pelatihan dinilai terlebih dahulu berdasarkan proporsi atribut yang tersedia sebelum imputasi. Pada kelompok kelas minoritas dengan informasi relatif lebih lengkap, metode dapat membangkitkan contoh sintetis secara terbatas. Pada kelompok minoritas dengan informasi relatif kurang lengkap, observasi asli dipertahankan dan pengaruhnya dalam pelatihan diatur melalui pembobotan, tanpa menjadikannya sumber pembangkitan contoh sintetis. Kedua kelompok kemudian digunakan untuk melatih satu model XGBoost. Cara ini **diharapkan** memanfaatkan informasi yang telah tersedia, tanpa harus menerapkan oversampling yang sama pada seluruh sampel minoritas.

Mekanisme pemilihan tersebut masih merupakan **hipotesis desain**, bukan prinsip yang telah terbukti unggul. Sampel yang lebih lengkap belum tentu lebih representatif; pembobotan sampel yang kurang lengkap juga belum tentu meningkatkan kinerja. Karena itu, kontribusi penelitian harus diuji terhadap pendekatan yang tidak memakai penyeimbangan, yang hanya menggunakan pembobotan, yang hanya menggunakan oversampling, serta yang menggabungkan keduanya secara global tanpa pemilihan berdasarkan kelengkapan. Perbandingan terakhir sangat penting untuk mengetahui apakah manfaat—jika ada—berasal dari **aturan pemilihannya**, bukan hanya dari penggunaan dua teknik secara bersamaan.

Secara akademik, penelitian ini ditempatkan sebagai **pengembangan metode hibrida untuk penanganan ketimpangan kelas pada data aplikasi kredit yang tidak lengkap**, bukan pengembangan algoritma klasifikasi baru, dan bukan studi tentang koperasi Indonesia. Dataset Home Credit digunakan sebagai lingkungan pengembangan dan pengujian yang dapat direproduksi; penelitian ini belum memiliki dasar untuk mengklaim peningkatan keputusan kredit pada suatu lembaga nyata atau keberlakuan hasil pada seluruh populasi kredit konsumen.

## I.2 Rumusan Masalah

Data aplikasi kredit konsumen dapat memperlihatkan dua karakteristik sekaligus: jumlah kasus kesulitan pembayaran lebih sedikit daripada kasus lainnya dan tidak semua pemohon memiliki atribut yang terisi lengkap. Pendekatan oversampling umum menghasilkan contoh sintetis dari kelas minoritas, sedangkan penanganan nilai kosong sering membutuhkan penghapusan observasi atau imputasi. Penerapan pembobotan kelas dapat menjadi alternatif yang tidak menambah contoh sintetis, tetapi tidak dengan sendirinya menentukan observasi mana yang sebaiknya digunakan sebagai sumber oversampling [2]–[6].

Penelitian terdahulu telah membahas metode hibrida untuk ketimpangan kelas dan data tidak lengkap. Namun, dalam **pemeriksaan literatur terarah yang menjadi dasar draf ini**, belum ditemukan pembahasan yang persis sama mengenai kebijakan **memilih oversampling untuk observasi minoritas yang relatif lengkap dan pembobotan untuk observasi minoritas yang relatif tidak lengkap**, dengan seluruh observasi asli tetap dipertahankan, pada prediksi risiko kredit konsumen. Pernyataan tersebut merupakan **batas hasil penelusuran yang telah dilakukan**, bukan klaim bahwa tidak ada karya sejenis di seluruh literatur.

Dengan demikian, persoalan penelitian dirumuskan sebagai kebutuhan untuk merancang dan menguji metode penyeimbangan yang mempertimbangkan kelengkapan data pada tingkat observasi, serta memastikan bahwa mekanisme pemilihan perlakuan benar-benar memberi manfaat dibanding gabungan teknik yang diterapkan tanpa mekanisme tersebut.

**Pertanyaan penelitian (RQ)** yang diajukan adalah:

**RQ1.** Bagaimana merancang metode hibrida yang memilih antara oversampling selektif dan pembobotan sampel berdasarkan kelengkapan informasi untuk menangani ketimpangan kelas pada prediksi risiko gagal bayar kredit konsumen?

**RQ2.** Sejauh mana metode hibrida yang diusulkan meningkatkan kemampuan mengenali kasus kesulitan pembayaran dibanding XGBoost tanpa penyeimbangan, pembobotan saja, oversampling saja, dan gabungan keduanya tanpa pemilihan berdasarkan kelengkapan, jika dievaluasi dengan data dan prosedur pengujian yang setara?

Pertanyaan pertama dijawab melalui spesifikasi serta implementasi metode CG-HIL. Pertanyaan kedua dijawab melalui pengujian komparatif yang secara khusus mengisolasi manfaat aturan pemilihan berdasarkan kelengkapan. Penelitian tidak berasumsi bahwa metode usulan pasti unggul; keunggulannya merupakan hipotesis yang akan diperiksa melalui eksperimen.

## I.3 Tujuan Penelitian

Tujuan umum penelitian ini adalah **mengembangkan dan mengevaluasi metode hibrida berbasis kelengkapan informasi untuk menangani ketimpangan kelas pada pemodelan risiko gagal bayar kredit konsumen**.

Untuk mencapai tujuan tersebut, penelitian diarahkan pada dua tujuan khusus yang selaras dengan pertanyaan penelitian:

1. **Merancang dan mengimplementasikan CG-HIL**, yaitu mekanisme yang menghitung tingkat kelengkapan observasi, memilih pembangkitan sampel sintetis secara terbatas pada kelompok minoritas relatif lengkap, dan menggunakan pembobotan untuk mempertahankan kontribusi observasi minoritas relatif tidak lengkap dalam pelatihan XGBoost (menjawab RQ1).
2. **Mengukur efektivitas dan nilai tambah aturan pemilihan CG-HIL** dibandingkan metode pembanding pada data uji yang sama, dengan penekanan pada kemampuan mendeteksi `TARGET = 1`, ketepatan prediksi kelas tersebut, serta kinerja pemeringkatan risiko (menjawab RQ2).

Tujuan penelitian ini bukan mengklaim bahwa pengembangan metode secara otomatis memperbaiki proses pemberian kredit di lapangan. Keluaran yang diharapkan adalah metode yang terdefinisi dengan baik, implementasi yang dapat diuji ulang, dan bukti empiris tentang kelebihan maupun keterbatasannya pada dataset yang digunakan.

## I.4 Batasan Masalah dan Ruang Lingkup

Agar penelitian dapat dilaksanakan dan hasilnya dapat dipertanggungjawabkan, ruang lingkup ditetapkan sebagai berikut.

1. **Konteks penelitian** adalah pemodelan risiko kesulitan pembayaran pada kredit konsumen. Penelitian tidak menggunakan koperasi Indonesia sebagai konteks empiris dan tidak mengklaim model siap diterapkan di koperasi, bank, atau lembaga pembiayaan tertentu.
2. **Sumber data** adalah *Home Credit Default Risk* dari Kaggle, dengan `application_train.csv` sebagai sumber observasi berlabel untuk pengembangan dan pengujian. Tabel riwayat tambahan bukan prasyarat untuk menguji mekanisme utama CG-HIL. Karena label `application_test.csv` tidak tersedia, pemisahan pelatihan, validasi, dan pengujian dibentuk dari data berlabel [1]. Penggunaan dataset telah dikonfirmasi mahasiswa; pengaturan penyebarluasan berkas mentah tetap mengikuti ketentuan yang berlaku.
3. **Variabel keluaran** adalah `TARGET` sebagaimana didefinisikan dalam dokumentasi Home Credit. Hasil model tidak diperlakukan sebagai pengukuran semua jenis gagal bayar atau dampak kerugian finansial yang sebenarnya.
4. **Karakteristik data yang dikaji** adalah ketimpangan kelas, nilai kosong pada fitur, dan campuran atribut numerik serta kategorikal. Kelengkapan dihitung dari fitur prediktor yang ditentukan pada data pelatihan sebelum imputasi; identitas observasi dan `TARGET` tidak digunakan dalam skor kelengkapan.
5. **Metode yang dikembangkan** dibatasi pada kebijakan pemilihan oversampling dan pembobotan berdasarkan kelengkapan data. SMOTENC dipertimbangkan sebagai komponen pembangkitan sampel pada fitur campuran [12], sedangkan XGBoost digunakan sebagai model prediksi utama [10]. Penelitian tidak merancang algoritma *deep learning* atau metode imputasi generatif baru.
6. **Pengendalian nilai kosong** dilakukan dengan prosedur sederhana dan konsisten. Jika proses oversampling membutuhkan imputasi, nilai pengganti dihitung hanya dari bagian data pelatihan yang relevan. Seluruh baris asli yang sah tetap dipertahankan; hal ini **bukan berarti** seluruh nilai kosong diabaikan atau bahwa data sintetis bebas dari imputasi.
7. **Pembagian data dan pencegahan kebocoran informasi** dilakukan sebelum oversampling, penentuan ambang kelengkapan, atau estimasi parameter prapemrosesan. Seluruh mekanisme tersebut dipelajari hanya dari data pelatihan. Validasi digunakan untuk memilih pengaturan yang diperlukan; data uji tidak diberi sampel sintetis dan tidak digunakan untuk penyetelan metode.
8. **Pembanding utama** adalah (a) XGBoost tanpa penanganan ketimpangan, (b) XGBoost dengan pembobotan, (c) XGBoost dengan oversampling, dan (d) XGBoost dengan gabungan oversampling dan pembobotan tanpa aturan kelengkapan. Pembanding menggunakan fitur, pembagian data, dan kriteria penentuan ambang klasifikasi yang setara. Perbedaan jumlah sampel dan bobot efektif dicatat agar manfaat mekanisme seleksi tidak tertukar dengan besarnya koreksi ketimpangan.
9. **Evaluasi** menggunakan PR-AUC, recall, precision, F1, ROC-AUC, dan *confusion matrix*. PR-AUC diprioritaskan untuk memperhatikan kinerja pada kelas minoritas, sedangkan recall, precision, dan F1 dihitung pada ambang klasifikasi yang ditetapkan dengan aturan yang konsisten berdasarkan data validasi [11]. Tidak diperlukan optimasi biaya kredit atau penetapan ambang berbasis parameter finansial institusi yang tidak tersedia.
10. **Generalisasi** dibatasi pada data dan skenario pengujian yang tersedia. Penelitian tidak mengukur dampak terhadap nasabah, keputusan kredit institusi, keadilan antarkelompok, maupun keberhasilan implementasi operasional tanpa bukti tersendiri. Demonstrasi artefak dilakukan secara lokal menggunakan data uji, tanpa mensyaratkan survei, wawancara, atau pengujian pengguna eksternal.

## I.5 Kebaruan dan Kontribusi

Kebaruan yang **diusulkan** dalam penelitian ini adalah **mekanisme pemilihan strategi penyeimbangan kelas pada tingkat observasi berdasarkan kelengkapan informasi**, bukan penemuan kembali teknik oversampling, pembobotan kelas, ataupun XGBoost. CG-HIL berangkat dari anggapan yang perlu diuji bahwa sampel minoritas dengan informasi lebih lengkap merupakan kandidat yang lebih masuk akal untuk pembentukan sampel sintetis, sedangkan sampel minoritas dengan informasi lebih terbatas sebaiknya tetap berkontribusi melalui pembobotan tanpa digunakan sebagai sumber sintesis.

Karya terdekat menunjukkan batas pembeda tersebut:

| Penelitian | Solusi yang telah dilaporkan | Posisi dan pembeda yang diusulkan |
|---|---|---|
| Ben Ammar & Rubaidi (2026) [2] | SHDO: lima teknik oversampling berurutan, dengan penyaringan observasi yang sangat tidak lengkap sebelum pelatihan. | CG-HIL mempertahankan observasi asli dan memilih strategi penyeimbangan per kelompok berdasarkan kelengkapan, bukan menerapkan pipeline oversampling berurutan. |
| Han dkk. (2025) [4] | SMART: rekonstruksi nilai hilang dengan komponen pemrosesan dan imputasi. | CG-HIL tidak mengembangkan imputasi lanjutan; sasaran utamanya kebijakan pemilihan oversampling versus bobot. |
| Barnard (2026) [5] | OverNaN: pembangkitan contoh sintetis yang sadar pola nilai kosong; **masih preprint**. | CG-HIL menguji kebijakan **kapan tidak membangkitkan** contoh sintetis dan memilih pembobotan sebagai perlakuan alternatif. |
| Dou dkk. (2023) [6] | Metode SMOTE dengan penanganan data yang tidak lengkap dan mekanisme pembobotan saat pembangkitan sampel. | CG-HIL menggunakan kelengkapan observasi sebagai dasar pemilihan cabang perlakuan, bukan hanya pembobotan dalam generator sintetis. |
| Zhu dkk. (2026) [7] | Penggabungan undersampling dan SMOTE adaptif berdasarkan tumpang tindih kelas. | CG-HIL tidak berfokus pada batas tumpang tindih antarkelas, melainkan kelengkapan atribut. |
| Ying dkk. (2025) [8] | Penggabungan augmentasi sintetis dan *cost-sensitive learning* pada risiko kredit. | Kombinasi kedua teknik **bukan kebaruan**; pembeda CG-HIL hanya pada aturan alokasi perlakuan berdasarkan kelengkapan. |

Berdasarkan pemeriksaan literatur terarah yang telah dilakukan sampai 28 Oktober 2026, **belum ditemukan metode identik** yang menerapkan aturan pemilihan oversampling versus pembobotan berdasarkan kelengkapan informasi observasi pada konteks yang sama. Namun, pemeriksaan tersebut bukan penelusuran sistematis seluruh publikasi; karena itu, naskah ini **tidak mengklaim CG-HIL sebagai metode pertama di dunia**. Kebaruan substantifnya harus diperiksa melalui spesifikasi mekanisme dan pengujian terhadap gabungan metode tanpa aturan kelengkapan.

Kontribusi penelitian yang diharapkan mencakup dua hal:

1. **Kontribusi rancangan metode:** aturan kerja CG-HIL yang secara eksplisit menghubungkan skor kelengkapan observasi dengan pemilihan cara penanganan ketimpangan kelas, disertai implementasi yang dapat direproduksi.
2. **Kontribusi bukti empiris:** hasil perbandingan yang menunjukkan apakah aturan kelengkapan memberi nilai tambah dalam mendeteksi kasus kesulitan pembayaran dibanding penanganan ketimpangan yang tidak menggunakan aturan tersebut, berikut kondisi dan keterbatasannya.

Jika CG-HIL menunjukkan hasil lebih baik, kontribusi yang dapat dipertahankan adalah mekanisme dan bukti manfaatnya **pada kondisi uji yang dilakukan**. Jika hasilnya setara atau lebih rendah, kontribusi rancangan tetap dapat dipaparkan, tetapi klaim peningkatan harus ditolak; penelitian perlu menjelaskan mengapa strategi yang diusulkan tidak menunjukkan manfaat seperti yang diharapkan. Dengan demikian, kontribusi tidak ditentukan oleh pemberian nama baru pada gabungan algoritma, melainkan oleh pembeda desain yang teruji.

## I.6 Metodologi Penelitian

Penelitian dirancang menggunakan kerangka *Design Science Research Methodology* (DSRM) menurut Peffers dkk. (2007), yang berorientasi pada perancangan dan evaluasi artefak untuk menjawab masalah yang teridentifikasi [13]. Artefak utama penelitian ini adalah **metode CG-HIL beserta implementasi pemodelan yang dapat diuji**, bukan sistem informasi produksi berskala besar. Enam aktivitas DSRM diterapkan secara proporsional sebagai berikut.

**1. Identifikasi masalah dan motivasi.** Mengidentifikasi ketimpangan kelas serta nilai kosong pada data kredit konsumen, menelaah penanganannya dalam penelitian terdahulu, dan merumuskan batas pendekatan yang memotivasi mekanisme pemilihan berdasarkan kelengkapan data. Karya Ben Ammar dan Rubaidi (2026) digunakan sebagai salah satu acuan langsung [2].

**2. Penentuan tujuan solusi.** Menetapkan karakteristik artefak yang diinginkan: mempertahankan observasi asli yang sah, membatasi pembentukan data sintetis pada sampel minoritas yang relatif lengkap, mempertahankan pengaruh sampel minoritas yang relatif tidak lengkap melalui pembobotan, dan memungkinkan evaluasi yang adil terhadap metode standar.

**3. Perancangan dan pengembangan artefak.** Mengimplementasikan perhitungan skor kelengkapan, pemisahan kelompok minoritas sesuai ambang yang ditentukan pada data pelatihan, oversampling terbatas menggunakan SMOTENC pada kelompok yang memenuhi syarat, pembobotan observasi minoritas yang tidak di-*oversample*, serta pelatihan XGBoost. Aturan untuk menangani nilai kosong dan kategori ditetapkan konsisten sehingga observasi sintetis tidak memuat kategori tidak valid. Ambang kelengkapan dan tingkat koreksi ketimpangan diperlakukan sebagai parameter rancangan yang ditentukan melalui data pelatihan/validasi, bukan disesuaikan terhadap hasil data uji.

**4. Demonstrasi.** Menjalankan metode menggunakan skenario prediksi risiko pada Home Credit. Demonstrasi memperlihatkan data yang masuk, keputusan perlakuan penyeimbangan pada kelompok sampel, jumlah contoh sintetis yang dihasilkan, pembobotan yang dipakai, serta keluaran prediksi model. Demonstrasi ini menunjukkan bahwa artefak dapat dioperasikan, bukan dengan sendirinya membuktikan keunggulannya.

**5. Evaluasi.** Membandingkan metode usulan dengan empat pembanding utama: XGBoost standar, pembobotan saja, SMOTENC saja, serta gabungan SMOTENC dan pembobotan tanpa aturan kelengkapan. Semua model dinilai pada data uji berlabel dengan prevalensi kelas alami. PR-AUC, recall, precision, F1, ROC-AUC, serta *confusion matrix* digunakan untuk menilai kualitas hasil. Perbandingan terhadap gabungan tanpa aturan kelengkapan berfungsi sebagai uji penghilangan komponen (*ablation*) terhadap kontribusi mekanisme seleksi, bukan sebagai penelitian terpisah. Hasil juga dibahas terkait jumlah observasi asli yang dipertahankan dan keterbatasan proses pembangkitan sampel.

**6. Komunikasi.** Mendokumentasikan alasan desain, sumber data, prosedur implementasi, hasil demonstrasi, evaluasi, serta keterbatasan dalam naskah tesis dan berkas artefak yang dapat dibagikan sesuai ketentuan penggunaan data.

Urutan tersebut menjelaskan rancangan penelitian, bukan klaim bahwa keenam aktivitas telah diselesaikan. Prosedur teknis, konfigurasi parameter, serta protokol pengujian yang lebih rinci akan ditempatkan pada Bab III setelah rancangan diperiksa bersama pembimbing.

## I.7 Sistematika Penulisan

Naskah tesis direncanakan tersusun dalam enam bab sebagai berikut.

**Bab I Pendahuluan** memaparkan latar belakang, rumusan masalah dan pertanyaan penelitian, tujuan, batasan penelitian, hipotesis kebaruan serta kontribusi, metodologi secara ringkas, dan sistematika penulisan.

**Bab II Tinjauan Pustaka** menguraikan kerangka berpikir, konsep penilaian risiko kredit konsumen, karakteristik ketimpangan kelas dan nilai kosong, pendekatan oversampling dan pembobotan, serta sintesis penelitian terdekat yang mendasari posisi CG-HIL.

**Bab III Metodologi Penelitian** menjelaskan pelaksanaan enam aktivitas DSRM beserta data, definisi operasional, mekanisme CG-HIL, pembanding, skenario demonstrasi, dan protokol evaluasi.

**Bab IV Perancangan dan Pengembangan** menguraikan spesifikasi metode, implementasi artefak, pengolahan data, serta demonstrasi yang benar-benar dilaksanakan, tanpa mengulang rincian metodologi yang tidak perlu.

**Bab V Hasil dan Pembahasan** menyajikan kualitas dan cakupan data, hasil pengujian metode usulan dan pembanding, analisis nilai tambah mekanisme pemilihan, serta pembahasan keterbatasan dan implikasi temuan terhadap pertanyaan penelitian.

**Bab VI Penutup** memuat kesimpulan yang menjawab pertanyaan penelitian berdasarkan hasil dan saran yang diturunkan dari keterbatasan atau temuan aktual.

---

# Daftar Pustaka Kerja

> Daftar ini hanya memuat sumber yang digunakan dalam draf Bab I. Judul, penulis, tahun, dan tautan diperiksa melalui halaman penerbit, lembaga penyedia, atau arsip ilmiah yang dapat diakses. Format daftar pustaka akhir disesuaikan dengan pedoman institusi. **Barnard (2026) merupakan preprint**, bukan artikel jurnal yang telah dipastikan melalui penelaahan sejawat.

[1] Home Credit Group. (2018). *Home Credit Default Risk* [Dataset dan deskripsi kompetisi]. Kaggle. https://www.kaggle.com/competitions/home-credit-default-risk/data

[2] Ben Ammar, B., & Rubaidi, Z. S. (2026). Integrating Sequential Hybrid Oversampling with Decision-Theoretic Threshold Design for Credit Risk Assessment. *Mathematics, 14*(9), 1467. https://doi.org/10.3390/math14091467

[3] Zhao, Z., Cui, T., Ding, S., Li, J., & Bellotti, A. G. (2024). Resampling Techniques Study on Class Imbalance Problem in Credit Risk Prediction. *Mathematics, 12*(5), 701. https://doi.org/10.3390/math12050701

[4] Han, S., Jung, H., & Yoo, P. D. (2025). SMART: Structured Missingness Analysis and Reconstruction Technique for credit scoring. *Scientific Reports, 15*, 15111. https://doi.org/10.1038/s41598-025-99997-4

[5] Barnard, A. S. (2026). OverNaN: NaN-Aware Oversampling for Imbalanced Learning with Meaningful Missingness [Preprint]. *arXiv*, 2605.11525. https://arxiv.org/abs/2605.11525

[6] Dou, J., Wei, G., Song, Y., dkk. (2023). Switching Triple-Weight-SMOTE in Empirical Feature Space for Imbalanced and Incomplete Data. *IEEE Transactions on Automation Science and Engineering*. https://doi.org/10.1109/TASE.2023.3240759  
**Catatan bibliografi:** daftar lengkap seluruh penulis, volume, dan halaman belum diperiksa dari halaman penerbit; lengkapi sebelum penyerahan akhir.

[7] Zhu, dkk. (2026). A Hybrid Sampling Approach Integrating Decision Tree and Subregional SMOTE for Imbalanced Credit Classification With Class Overlapping. *Expert Systems*. https://doi.org/10.1111/exsy.70276  
**Catatan bibliografi:** nama lengkap para penulis dan detail volume/nomor akhir perlu diambil dari halaman penerbit pada penyuntingan daftar pustaka akhir.

[8] Ying, C., Shi, A., & Li, X. (2025). Hybrid boosted attention-based LightGBM framework for enhanced credit risk assessment in digital finance. *Humanities and Social Sciences Communications, 12*, 1036. https://doi.org/10.1057/s41599-025-05230-y

[9] Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic Minority Over-sampling Technique. *Journal of Artificial Intelligence Research, 16*, 321–357. https://doi.org/10.1613/jair.953

[10] Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785–794. https://doi.org/10.1145/2939672.2939785

[11] Saito, T., & Rehmsmeier, M. (2015). The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets. *PLOS ONE, 10*(3), e0118432. https://doi.org/10.1371/journal.pone.0118432

[12] imbalanced-learn developers. (n.d.). *SMOTENC: Synthetic Minority Over-sampling Technique for Nominal and Continuous Features* [Dokumentasi perangkat lunak]. https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTENC.html

[13] Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A Design Science Research Methodology for Information Systems Research. *Journal of Management Information Systems, 24*(3), 45–77. https://doi.org/10.2753/MIS0742-1222240302

---

# Catatan Kendali Draf (Tidak Masuk Naskah Akhir)

**Diputuskan mahasiswa (28 Oktober 2026):** domain risiko gagal bayar kredit konsumen; dataset Home Credit Default Risk; tidak menggunakan Federated Learning; arah penelitian pengembangan metode hibrida CG-HIL berbasis kelengkapan data. Jangan mengubah arah tersebut dalam sesi AI berikutnya tanpa persetujuan mahasiswa atau bukti baru yang material.

**Belum merupakan keputusan formal pembimbing:** perubahan konteks dari koperasi Indonesia; judul final; rumusan RQ final; penerimaan klaim kontribusi.

**Masih hipotesis yang harus diuji:** bahwa menghindari sintesis dari observasi minoritas yang sangat tidak lengkap memberi manfaat, dan bahwa aturan seleksi CG-HIL lebih efektif daripada gabungan oversampling–weighting tanpa aturan seleksi. **Hasil eksperimen belum ada.**

**Satu langkah terdekat:** gunakan Bab I ini sebagai dasar pembahasan rancangan CG-HIL dengan pembimbing; setelah arah disetujui secara akademik, turunkan mekanisme dan protokol eksperimen ke Bab III. Jangan membuka pencarian topik baru atau menambahkan algoritma tanpa kebutuhan yang jelas.
