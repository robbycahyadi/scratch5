#!/usr/bin/env python3
"""Audit awal Home Credit untuk gerbang CG-HIL v0.1.

Audit ini TIDAK melakukan imputasi, SMOTENC, pelatihan, ataupun evaluasi model.
Menggunakan application_train.csv asli; tidak mengubah file sumber.

Jalankan:
  python audit_home_credit_cghil.py --input data/application_train.csv --out results/audit_cghil
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split


SEED = 42
SPECIAL_TEXT_VALUES = ("XNA", "Unknown", "UNKNOWN", "N/A", "NA")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def score_summary(scores: pd.Series) -> dict:
    if scores.empty:
        return {"n": 0}
    return {
        "n": int(scores.size),
        "min": round(float(scores.min()), 6),
        "p10": round(float(scores.quantile(0.10)), 6),
        "p25": round(float(scores.quantile(0.25)), 6),
        "median": round(float(scores.median()), 6),
        "p75": round(float(scores.quantile(0.75)), 6),
        "p90": round(float(scores.quantile(0.90)), 6),
        "max": round(float(scores.max()), 6),
    }


def md_table(headers: list[str], rows: list[list]) -> str:
    def clean(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    return "\n".join(
        ["| " + " | ".join(map(clean, headers)) + " |",
         "| " + " | ".join(["---"] * len(headers)) + " |"]
        + ["| " + " | ".join(map(clean, row)) + " |" for row in rows]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Home Credit untuk kelayakan CG-HIL (tanpa modeling)")
    parser.add_argument("--input", required=True, type=Path, help="Path application_train.csv asli")
    parser.add_argument("--out", default=Path("results/audit_cghil"), type=Path,
                        help="Direktori keluaran audit")
    args = parser.parse_args()
    source = args.input.expanduser().resolve()
    if not source.is_file():
        parser.error(f"File tidak ditemukan: {source}. Unduh dari halaman resmi Kaggle setelah menerima aturan kompetisi.")
    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    print(f"[1/4] Membaca {source.name} ({source.stat().st_size / 1_000_000:.1f} MB)")
    df = pd.read_csv(source, low_memory=False)
    needed = {"TARGET", "SK_ID_CURR"}
    if not needed.issubset(df.columns):
        raise ValueError(f"Kolom wajib hilang: {sorted(needed - set(df.columns))}")
    if df.columns.duplicated().any():
        raise ValueError("Nama kolom duplikat; periksa file sumber.")
    if df["TARGET"].isna().any() or not df["TARGET"].isin([0, 1]).all():
        raise ValueError("TARGET mengandung missing atau nilai selain 0/1.")
    if df["SK_ID_CURR"].isna().any():
        raise ValueError("SK_ID_CURR memiliki nilai kosong.")

    print("[2/4] Melakukan split awal terstratifikasi 70/15/15 (seed 42)")
    y = df["TARGET"].astype(int)
    inds = np.arange(len(df))
    train_idx, holdout_idx = train_test_split(inds, test_size=0.30,
                                               random_state=SEED, stratify=y)
    valid_idx, test_idx = train_test_split(holdout_idx, test_size=0.50,
                                          random_state=SEED, stratify=y.iloc[holdout_idx])
    assert not (set(train_idx) & set(valid_idx) or set(train_idx) & set(test_idx)
                or set(valid_idx) & set(test_idx))
    train = df.iloc[train_idx]
    train_y = y.iloc[train_idx]
    all_features = [c for c in df.columns if c not in ("TARGET", "SK_ID_CURR")]
    # Kolom yang benar-benar konstan (termasuk pola missing) dikeluarkan berdasarkan train saja.
    removed = [c for c in all_features if train[c].nunique(dropna=False) <= 1]
    features = [c for c in all_features if c not in removed]
    if not features:
        raise ValueError("Semua fitur konstan; skor kelengkapan tidak dapat dihitung.")

    print("[3/4] Memprofilkan missing values dan skor kelengkapan")
    x = train[features]
    pos = train_y.eq(1)
    neg = train_y.eq(0)
    missing_count = x.isna().sum()
    positive_missing = x.loc[pos].isna().sum()
    negative_missing = x.loc[neg].isna().sum()
    feature_rows = []
    for col in features:
        feature_rows.append({
            "feature": col,
            "dtype": str(df[col].dtype),
            "missing_count_train": int(missing_count[col]),
            "missing_pct_train": round(100 * float(missing_count[col]) / len(train), 3),
            "missing_pct_train_target_1": round(100 * float(positive_missing[col]) / int(pos.sum()), 3),
            "missing_pct_train_target_0": round(100 * float(negative_missing[col]) / int(neg.sum()), 3),
        })
    feature_df = pd.DataFrame(feature_rows).sort_values("missing_pct_train", ascending=False)
    feature_df.to_csv(out / "fitur_missing_train.csv", index=False)

    score = x.notna().mean(axis=1)
    positive_scores = score.loc[pos]
    negative_scores = score.loc[neg]
    tau = float(positive_scores.median())
    E = positive_scores.gt(tau)
    U = positive_scores.le(tau)
    nE, nU = int(E.sum()), int(U.sum())
    S = min(nE, nU)
    feasible = nE >= 6 and nU > 0 and S > 0
    n1 = int(pos.sum())
    n0 = int(neg.sum())
    weight_u = 1 + S / nU if nU else None
    effective_positive = n1 + 2 * S

    categorical_columns = [c for c in features if not pd.api.types.is_numeric_dtype(x[c])]
    numerical_columns = [c for c in features if pd.api.types.is_numeric_dtype(x[c])]
    special_values = []
    for col in categorical_columns:
        counts = x[col].value_counts(dropna=False)
        for marker in SPECIAL_TEXT_VALUES:
            count = int(counts.get(marker, 0))
            if count:
                special_values.append({"column": col, "value": marker, "n_train": count})
    if "DAYS_EMPLOYED" in x.columns:
        count = int(x["DAYS_EMPLOYED"].eq(365243).sum())
        if count:
            special_values.append({"column": "DAYS_EMPLOYED", "value": "365243", "n_train": count})

    report = {
        "environment": {"python": platform.python_version(), "pandas": pd.__version__,
                        "numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "data": {"filename": source.name, "bytes": source.stat().st_size,
                 "sha256": sha256_file(source), "rows": int(len(df)),
                 "columns": int(len(df.columns)), "target_counts": {
                     "0": int(y.eq(0).sum()), "1": int(y.eq(1).sum())},
                 "positive_pct": round(float(y.mean()) * 100, 4),
                 "duplicate_sk_id_curr": int(df["SK_ID_CURR"].duplicated().sum())},
        "protocol_draft": {"seed": SEED, "split": "70/15/15, stratified", "split_sizes": {
            "train": len(train_idx), "valid": len(valid_idx), "test": len(test_idx)},
            "split_target_1": {"train": n1, "valid": int(y.iloc[valid_idx].sum()),
                               "test": int(y.iloc[test_idx].sum())},
            "features_candidate": len(all_features), "features_used_for_score": len(features),
            "features_removed_train_only": removed, "numeric_features": len(numerical_columns),
            "categorical_features": len(categorical_columns)},
        "missingness_train": {
            "rows_with_any_missing": int(x.isna().any(axis=1).sum()),
            "pct_rows_with_any_missing": round(float(x.isna().any(axis=1).mean() * 100), 4),
            "overall_missing_cell_pct": round(float(x.isna().to_numpy().mean() * 100), 4),
            "missing_score_positive": score_summary(positive_scores),
            "missing_score_negative": score_summary(negative_scores),
            "special_values_needing_semantic_review": special_values},
        "cg_hil_precheck": {
            "tau_train_positive_median": round(tau, 8),
            "nE_positive_above_tau": nE, "nU_positive_at_or_below_tau": nU,
            "n_positive_equal_tau": int(positive_scores.eq(tau).sum()),
            "S_min_nE_nU": S, "weight_U": round(weight_u, 8) if weight_u is not None else None,
            "positive_weight_total_M1_to_M4": effective_positive,
            "M1_original_positive_weight": round(1 + 2 * S / n1, 8),
            "M3_original_positive_weight": round(1 + S / n1, 8),
            "SMOTENC_basic_group_gate_nE_ge_6_nU_gt_0": bool(feasible),
            "caveat": "Kelayakan tipe, imputasi, tetangga dan output sintetis belum diuji"},
    }

    summary_rows = [[k, f"{v:,}"] for k, v in report["data"]["target_counts"].items()]
    feature_top = [[r.feature, r.dtype, f"{r.missing_pct_train:.2f}%",
                    f"{r.missing_pct_train_target_1:.2f}%"]
                   for r in feature_df.head(15).itertuples(index=False)]
    special_rows = [[s["column"], s["value"], s["n_train"]] for s in special_values]

    lines = [
        "# Audit Awal Home Credit — CG-HIL v0.1",
        "",
        "**Status:** audit karakteristik dan *precheck* kelayakan; BUKAN hasil eksperimen SMOTENC/XGBoost.",
        "", "## Provenance", "",
        f"- Sumber lokal: `{source.name}`; ukuran {report['data']['bytes']:,} bytes",
        f"- SHA-256: `{report['data']['sha256']}`",
        "- Dataset asli tidak diubah oleh skrip.",
        f"- Versi: Python {platform.python_version()}, pandas {pd.__version__}, NumPy {np.__version__}, scikit-learn {sklearn.__version__}",
        "", "## Data dan label", "",
        f"- Total: {len(df):,} baris × {df.shape[1]} kolom",
        f"- Duplikat `SK_ID_CURR`: {report['data']['duplicate_sk_id_curr']:,}",
        f"- Persentase TARGET=1: {report['data']['positive_pct']}%",
        "", md_table(["TARGET", "Jumlah"], summary_rows),
        "", "## Split dan ruang fitur (usulan Bab III v0.1)", "",
        f"- Train/validasi/uji: {len(train_idx):,} / {len(valid_idx):,} / {len(test_idx):,}",
        f"- Fitur awal / dipakai skor: {len(all_features)} / {len(features)}",
        f"- Fitur numerik / nonnumerik: {len(numerical_columns)} / {len(categorical_columns)}",
        f"- Fitur dikeluarkan karena konstan pada train saja: {', '.join(removed) or '(tidak ada)'}",
        "", "## Missing values di data latih", "",
        f"- Observasi dengan ≥1 nilai kosong: {report['missingness_train']['rows_with_any_missing']:,} ({report['missingness_train']['pct_rows_with_any_missing']}%)",
        f"- Proporsi sel kosong: {report['missingness_train']['overall_missing_cell_pct']}%",
        "", "15 fitur dengan missing tertinggi:", "",
        md_table(["Fitur", "Tipe", "% missing train", "% missing TARGET=1"], feature_top),
        "", "Distribusi skor kelengkapan (train, sebelum imputasi):", "",
        md_table(["Kelas", "min", "p25", "median", "p75", "max"], [
            [label, *(report['missingness_train'][key][p] for p in ["min", "p25", "median", "p75", "max"])]
            for label, key in [("TARGET=1", "missing_score_positive"), ("TARGET=0", "missing_score_negative")]
        ]),
        "", "## Precheck E/U dan bobot (BUKAN keputusan final)", "",
        f"- Median kelas positif pada train, τ: **{tau:.8f}**",
        f"- E (positif dengan c > τ): **{nE:,}**",
        f"- U (positif dengan c ≤ τ): **{nU:,}**",
        f"- Tepat di median (c = τ): **{int(positive_scores.eq(tau).sum()):,}**",
        f"- S = min(nE,nU): **{S:,}**",
        f"- w_U = 1 + S/nU: **{weight_u:.6f}**" if weight_u is not None else "- w_U: tidak terdefinisi (nU=0)",
        f"- Total bobot positif efektif M1–M4: **{effective_positive:,}**",
        f"- Gerbang dasar jumlah kelompok: **{'LULUS' if feasible else 'GAGAL'}** (syarat nE≥6 dan nU>0)",
        "", "## Nilai khusus untuk kajian semantik (jangan langsung dianggap NaN)", "",
        md_table(["Kolom", "Nilai", "Jumlah train"], special_rows) if special_rows else "Tidak terdeteksi penanda khusus yang diperiksa.",
        "", "## Batas interpretasi", "",
        "- Skor kelengkapan adalah proporsi fitur non-NaN, bukan ukuran kualitas data.",
        "- Indikator seperti `XNA` atau angka khusus belum otomatis diganti menjadi missing.",
        "- Split 70/15/15 dan aturan median adalah usulan yang sedang divalidasi.",
        "- **Lulus gerbang jumlah E/U belum membuktikan SMOTENC berhasil.** Tahap selanjutnya perlu menguji generator dan pemeriksaan fitur.",
        "- Belum ada hasil performa prediksi; jangan menarik kesimpulan CG-HIL unggul.",
        "", "## Berkas keluaran", "",
        "- `audit_ringkas.md`: laporan ini",
        "- `fitur_missing_train.csv`: data missing per fitur untuk pemeriksaan lanjut",
        "- `audit_summary.json`: ringkasan terstruktur",
        "",
    ]
    (out / "audit_ringkas.md").write_text("\n".join(lines), encoding="utf-8")
    (out / "audit_summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("[4/4] Audit selesai")
    print(f"  {out / 'audit_ringkas.md'}")
    print(f"  {out / 'fitur_missing_train.csv'}")
    print(f"  {out / 'audit_summary.json'}")
    print(f"  median={tau:.6f}; nE={nE:,}; nU={nU:,}; S={S:,}; precheck={'PASS' if feasible else 'FAIL'}")


if __name__ == "__main__":
    main()
