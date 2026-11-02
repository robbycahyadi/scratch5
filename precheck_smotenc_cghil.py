#!/usr/bin/env python3
"""Uji kelayakan generator SMOTENC untuk rancangan CG-HIL v0.1.

Tidak mengubah dataset sumber, tidak melatih XGBoost, dan tidak menggunakan
validasi/uji untuk imputasi, kelengkapan, atau pembangkitan sintetis.

Mode default PILOT: menguji mekanisme pada subset latih; tidak dapat
menyatakan bahwa uji SMOTENC full-size berhasil.

Contoh:
  python precheck_smotenc_cghil.py --input application_train.csv --out results/smotenc_pilot
  python precheck_smotenc_cghil.py --input application_train.csv --out results/smotenc_full --full

Catatan rancangan: standardisasi numerik khusus generator ditambahkan sebagai
keputusan teknis pengujian ini, tanpa mengubah Bab III. Sentinel durasi
DAYS_EMPLOYED=365243 dimask sebelum imputasi; XNA tetap kategori eksplisit.
"""
from __future__ import annotations

import argparse
import json
import platform

from cghil_semantics import (derive_semantic_columns, semantic_numeric, model_frame,
                              round_counts, validate_semantics, synthetic_model_frame,
                              assert_synthetic_model_numeric)
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
import imblearn
from imblearn.over_sampling import SMOTENC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder

SEED = 42


def split_train(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    y = df['TARGET'].astype(int)
    idx = np.arange(len(df))
    train_idx, holdout_idx = train_test_split(idx, test_size=0.30, random_state=SEED, stratify=y)
    val_idx, test_idx = train_test_split(holdout_idx, test_size=0.50,
                                        random_state=SEED, stratify=y.iloc[holdout_idx])
    assert len(set(train_idx) & set(val_idx)) == 0
    assert len(set(train_idx) & set(test_idx)) == 0
    assert len(set(val_idx) & set(test_idx)) == 0
    return df.iloc[train_idx].copy(), len(val_idx), len(test_idx)


def prepare_generator(train: pd.DataFrame, features: list[str], num_cols: list[str],
                      cat_cols: list[str]) -> tuple[pd.DataFrame, StandardScaler | None]:
    """Fit generator-only preprocessing pada train, tanpa mengubah fitur asli."""
    generator = pd.DataFrame(index=train.index)
    scaler = None
    if num_cols:
        xnum = semantic_numeric(train)[num_cols].apply(pd.to_numeric, errors='raise').astype('float64')
        medians = xnum.median(axis=0)
        if medians.isna().any():
            raise ValueError('Fitur numerik tanpa nilai teramati: ' + str(medians[medians.isna()].index.tolist()))
        xnum_filled = xnum.fillna(medians)
        scaler = StandardScaler()
        generator[num_cols] = scaler.fit_transform(xnum_filled).astype('float64')
    for col in cat_cols:
        generator[col] = train[col].astype('string').fillna('__MISSING__').astype(str)
    generator = generator[features]
    if generator.isna().any().any():
        raise AssertionError('Generator masih mempunyai NaN')
    return generator, scaler


def main() -> None:
    ap = argparse.ArgumentParser(description='Precheck SMOTENC pada train Home Credit untuk CG-HIL')
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--out', type=Path, default=Path('results/smotenc_pilot'))
    ap.add_argument('--full', action='store_true', help='Gunakan seluruh mayoritas dan E; bangkitkan S penuh')
    ap.add_argument('--pilot-positive', type=int, default=300, help='Jumlah E untuk pilot')
    ap.add_argument('--pilot-majority', type=int, default=3000, help='Jumlah mayoritas untuk pilot')
    args = ap.parse_args()
    if args.pilot_positive < 6 or args.pilot_majority < args.pilot_positive:
        ap.error('Pilot perlu setidaknya 6 E dan mayoritas >= jumlah E')
    if not args.input.is_file():
        ap.error(f'File tidak ditemukan: {args.input}')
    args.out.mkdir(parents=True, exist_ok=True)

    print('[1/5] Membaca dataset, mereplikasi split audit awal... ', flush=True)
    df = pd.read_csv(args.input, low_memory=False)
    if not {'SK_ID_CURR', 'TARGET'}.issubset(df.columns):
        raise ValueError('Dataset harus memiliki TARGET dan SK_ID_CURR')
    if df['TARGET'].isna().any() or not df['TARGET'].isin([0, 1]).all():
        raise ValueError('TARGET harus biner 0/1 tanpa missing')
    if df['SK_ID_CURR'].duplicated().any():
        raise ValueError('SK_ID_CURR duplikat')
    train, n_val, n_test = split_train(df)
    features = [c for c in df.columns if c not in ('TARGET', 'SK_ID_CURR')]
    removed = [c for c in features if train[c].nunique(dropna=False) <= 1]
    features = [c for c in features if c not in removed]
    # Audited semantic roles override storage dtype below.
    numeric, categoric, count_cols = derive_semantic_columns(features)
    cat_numeric = [c for c in categoric if pd.api.types.is_numeric_dtype(train[c])]
    if not numeric or not categoric:
        raise ValueError('SMOTENC memerlukan campuran fitur numerik dan kategorikal')

    y = train['TARGET'].astype(int)
    c = train[features].notna().mean(axis=1)
    tau = float(c[y.eq(1)].median())
    idxE = c.index[y.eq(1) & c.gt(tau)]
    idxU = c.index[y.eq(1) & c.le(tau)]
    idx0 = y.index[y.eq(0)]
    nE, nU, n0 = len(idxE), len(idxU), len(idx0)
    n1 = nE + nU
    S = min(nE, nU)
    if nE < 6 or nU <= 0:
        raise ValueError('Gerbang kelayakan E/U gagal')
    assert len(idxE.intersection(idxU)) == 0
    assert 'SK_ID_CURR' not in features and 'TARGET' not in features
    print(f'      train={len(train)}; tau={tau:.6f}; E={nE}; U={nU}; S={S}', flush=True)

    # Verifikasi aritmetika lima metode tanpa melatih model.
    wU = 1 + S / nU
    weight_totals = {
        'M1': float(n1 * (1 + 2*S/n1)),
        'M2': float(n1 + 2*S),
        'M3': float(n1 * (1 + S/n1) + S),
        'M4': float(nE + nU*wU + S),
    }
    assert all(np.isclose(v, n1 + 2*S, atol=1e-7) for v in weight_totals.values())

    print('[2/5] Menyiapkan fitur generator (imputasi + scaling dari train saja)...', flush=True)
    generator, scaler = prepare_generator(train, features, numeric, categoric)
    if args.full:
        chosenE, chosen0, requested = idxE, idx0, S
    else:
        if len(idxE) < args.pilot_positive or len(idx0) < args.pilot_majority:
            raise ValueError('Ukuran subset pilot melebihi ukuran E/mayoritas')
        rng = np.random.default_rng(SEED)
        chosenE = pd.Index(rng.choice(idxE.to_numpy(), size=args.pilot_positive, replace=False))
        chosen0 = pd.Index(rng.choice(idx0.to_numpy(), size=args.pilot_majority, replace=False))
        requested = min(S, len(chosenE))
    pool_idx = chosen0.append(chosenE)
    X_pool = generator.loc[pool_idx].reset_index(drop=True)
    y_pool = np.concatenate([np.zeros(len(chosen0), dtype=np.int8), np.ones(len(chosenE), dtype=np.int8)])
    print(f'[3/5] SMOTENC: pool={len(pool_idx)} (E={len(chosenE)}, mayoritas={len(chosen0)})'
          f'; sintesis={requested}...', flush=True)
    sm = SMOTENC(categorical_features=categoric, sampling_strategy={1: len(chosenE)+requested},
                 k_neighbors=5, random_state=SEED)
    X_res, y_res = sm.fit_resample(X_pool, y_pool)
    if not isinstance(X_res, pd.DataFrame):
        raise AssertionError(f'SMOTENC tidak mengembalikan DataFrame: {type(X_res)}')
    synthetic = X_res.iloc[len(X_pool):].reset_index(drop=True)
    y_syn = np.asarray(y_res)[len(y_pool):]
    if len(synthetic) != requested or not np.all(y_syn == 1):
        raise AssertionError('Jumlah/label sampel sintetis salah')

    print('[4/5] Memeriksa tipe, domain kategori, dan keterbatasan sintetis...', flush=True)
    cat_invalid = {}
    for col in categoric:
        allowed = set(generator.loc[chosenE, col].astype(str).unique())
        unexpected = sorted(set(synthetic[col].astype(str).unique()) - allowed)
        if unexpected:
            cat_invalid[col] = unexpected
    if cat_invalid:
        raise AssertionError('Kategori sintetis di luar domain training: ' + str(cat_invalid))
    if synthetic.isna().any().any():
        raise AssertionError('Sampel sintetis mengandung NaN setelah imputasi generator')
    # Kategori numerik harus dapat dikonversi balik ke nilai numerik sah.
    for col in cat_numeric:
        recovered = pd.to_numeric(synthetic[col], errors='raise')
        valid = set(pd.to_numeric(train[col], errors='raise').dropna().unique())
        if not set(recovered.unique()).issubset(valid):
            raise AssertionError(f'Kategori numerik {col} tidak sah')
    syn_num_scaled = synthetic[numeric].astype('float64').to_numpy()
    if not np.isfinite(syn_num_scaled).all():
        raise AssertionError('Nilai numerik sintetis tidak finite')
    assert scaler is not None
    syn_num_original_scale = scaler.inverse_transform(syn_num_scaled)
    if not np.isfinite(syn_num_original_scale).all():
        raise AssertionError('Nilai sintetis setelah inverse scaling tidak finite')
    # SMOTE melakukan interpolasi sehingga tidak seharusnya melewati min/max input E numerik.
    E_num = generator.loc[chosenE, numeric].to_numpy(dtype='float64')
    eps = 1e-6
    if np.any(syn_num_scaled < E_num.min(axis=0) - eps) or np.any(syn_num_scaled > E_num.max(axis=0) + eps):
        raise AssertionError('Sintetis numerik di luar rentang sumber E')

    # Operate in original units; never substitute imputed generator rows for originals.
    before = synthetic.copy()
    before[numeric] = syn_num_original_scale
    allowed = {col: set(generator.loc[chosenE, col].astype(str)) for col in categoric}
    semantic_before = validate_semantics(before, numeric, categoric, count_cols, allowed)
    required_rules = {'category_domain', 'numeric_nonfinite', 'count_fractional', 'count_negative',
                      'DEF30_gt_OBS30', 'DEF60_gt_OBS60', 'days_employed_positive',
                      'days_birth_nonnegative', 'car_age_negative'}
    assert required_rules.issubset(semantic_before)
    corrected = round_counts(before, count_cols)
    # DEF is a subset of OBS; minimal projection affects synthetic DEF only.
    for days in (30, 60):
        obs, deff = f'OBS_{days}_CNT_SOCIAL_CIRCLE', f'DEF_{days}_CNT_SOCIAL_CIRCLE'
        corrected[deff] = np.minimum(corrected[deff], corrected[obs])
    semantic_after = validate_semantics(corrected, numeric, categoric, count_cols, allowed)
    assert len(count_cols) == 12 and semantic_after and len(semantic_after) >= 20
    assert not corrected.DAYS_EMPLOYED.eq(365243).any()
    assert corrected.DAYS_EMPLOYED.le(1e-8).all()
    assert np.isfinite(corrected[numeric].to_numpy(dtype=float)).all()
    assert np.allclose(corrected[count_cols], np.rint(corrected[count_cols]), atol=1e-8, rtol=0)
    assert corrected[count_cols].ge(0).all().all()
    for days in (30, 60):
        assert corrected[f'DEF_{days}_CNT_SOCIAL_CIRCLE'].le(corrected[f'OBS_{days}_CNT_SOCIAL_CIRCLE']).all()
    originals_model = model_frame(train, features, categoric)
    structural_before = validate_semantics(corrected, numeric, categoric, count_cols, allowed)
    synthetic_model = synthetic_model_frame(corrected, features, categoric)
    assert_synthetic_model_numeric(synthetic_model, numeric)
    semantic_after = validate_semantics(synthetic_model, numeric, categoric, count_cols, allowed)
    assert semantic_after['car_N_age_present']['count'] == 0
    assert semantic_after['organization_XNA_employed_present']['count'] == 0
    car_mask = train.FLAG_OWN_CAR.eq('N')
    org_mask = train.ORGANIZATION_TYPE.eq('XNA')
    empirical_train = {
        'train_rows': len(train),
        'car_N_rows': int(car_mask.sum()),
        'car_N_age_present': int((car_mask & train.OWN_CAR_AGE.notna()).sum()),
        'organization_XNA_rows': int(org_mask.sum()),
        'organization_XNA_raw_sentinel': int((org_mask & train.DAYS_EMPLOYED.eq(365243)).sum()),
        'organization_XNA_valid_duration_after_sentinel_mask': int((org_mask & semantic_numeric(train).DAYS_EMPLOYED.notna()).sum()),
        'sentinel_organization_nonXNA': int((~org_mask & train.DAYS_EMPLOYED.eq(365243)).sum()),
    }
    assert empirical_train['car_N_age_present'] == 0
    assert empirical_train['organization_XNA_valid_duration_after_sentinel_mask'] == 0
    assert empirical_train['sentinel_organization_nonXNA'] == 0
    # Shared numeric schema; integer raw values stay exactly equal as float64.
    originals_model[numeric] = originals_model[numeric].astype('float64')
    synthetic_model[numeric] = synthetic_model[numeric].astype('float64')
    combined = pd.concat([originals_model, synthetic_model], ignore_index=True)
    encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    encoder.fit(originals_model[categoric])
    encoded_original = encoder.transform(originals_model[categoric])
    encoded_synthetic = encoder.transform(synthetic_model[categoric])
    assert np.isfinite(encoded_original).all() and np.isfinite(encoded_synthetic).all()
    assert not (encoded_synthetic == -1).any()
    pd.testing.assert_frame_equal(combined.iloc[:len(train)].reset_index(drop=True),
                                  originals_model.reset_index(drop=True))
    expected_originals = train[features].copy()
    expected_originals.loc[expected_originals.DAYS_EMPLOYED.eq(365243), 'DAYS_EMPLOYED'] = np.nan
    pd.testing.assert_frame_equal(originals_model[numeric], expected_originals[numeric], check_dtype=False)
    assert len(combined) == len(train) + requested
    assert (len(features), len(train), n_val, n_test, nE, nU, S) == (120, 215257, 46127, 46127, 8636, 8741, 8636)
    assert np.isclose(tau, 0.6)
    reference_c = train[[r for r in train.columns if r not in ('SK_ID_CURR', 'TARGET')]].notna().mean(axis=1)
    reference_tau = reference_c[y.eq(1)].median()
    assert idxE.equals(reference_c.index[y.eq(1) & reference_c.gt(reference_tau)])
    assert idxU.equals(reference_c.index[y.eq(1) & reference_c.le(reference_tau)])
    assert not semantic_numeric(train).DAYS_EMPLOYED.eq(365243).any()
    hard_remaining = {k:v for k,v in semantic_after.items() if v['severity'] == 'hard' and v['count']}
    synthetic_model.to_csv(args.out/'synthetic_model.csv.gz', index=False)
    print('[5/5] Menulis laporan uji generator...', flush=True)
    results = {
        'status': 'BLOCKED' if hard_remaining else 'PASS',
        'seed': SEED,
        'structural_missingness': {'empirical_train': empirical_train,
            'before': {k: structural_before[k] for k in ('car_N_age_present', 'organization_XNA_employed_present')},
            'after': {k: semantic_after[k] for k in ('car_N_age_present', 'organization_XNA_employed_present')},
            'postprocessing_applies_to': ['M2', 'M3', 'M4'],
            'intentional_nan_cells': int(synthetic_model[numeric].isna().sum().sum()),
            'exact_expected_nan_mask_verified': True, 'unexpected_nan_cells': 0,
            'originals_structurally_modified': False},
        'semantic_validation': {'before': semantic_before, 'after': semantic_after,
                                'hard_remaining': hard_remaining, 'count_columns': count_cols,
                                'source_E_model': validate_semantics(model_frame(train.loc[chosenE], features, categoric), numeric, categoric, count_cols, allowed)},
        'consistency_checks': {'baseline_E_U_unchanged': True, 'original_numeric_missing_preserved': True,
            'original_rows_retained_and_equal_in_combined_model_frame': True,
            'combined_model_rows': len(combined), 'fit_scope': 'train only',
            'shared_ordinal_encoder_fitted_original_train_only': True,
            'synthetic_unknown_categories': int((encoded_synthetic == -1).sum()),
            'M3_M4_specified_synthetic_count': {'M3': S, 'M4': S},
            'M3_generator_executed': False, 'model_trained': False},
        'scope': 'full' if args.full else 'pilot',
        'limitations': [
            'Bukan evaluasi prediksi/PR-AUC dan bukan bukti keunggulan CG-HIL',
            'XNA/Unknown explicit; DAYS_EMPLOYED sentinel masked before train-median imputation; raw completeness unchanged',
            'StandardScaler adalah usulan prapemrosesan generator, belum spesifikasi final Bab III',
        ],
        'version': {'python': platform.python_version(), 'pandas': pd.__version__,
                    'numpy': np.__version__, 'sklearn': sklearn.__version__, 'imblearn': imblearn.__version__},
        'split': {'train': len(train), 'validation': n_val, 'test': n_test},
        'data': {'features': len(features), 'numeric': len(numeric), 'categorical': len(categoric),
                 'removed_constant_train': removed, 'numeric_encoded_categories': cat_numeric},
        'completeness': {'tau': tau, 'nE': nE, 'nU': nU, 'S_full': S,
                         'n_at_median': int(c.loc[idxU].eq(tau).sum())},
        'weights': {'w_U': wU, 'effective_total_positive_M1_to_M4': n1+2*S,
                    'verified_method_totals': weight_totals},
        'generator': {'input_majority': len(chosen0), 'input_E': len(chosenE),
                      'count_corrected_cells': int((~np.isclose(before[count_cols], corrected[count_cols], atol=1e-8, rtol=0)).sum()),
                      'count_corrected_rows': int((~np.isclose(before[count_cols], corrected[count_cols], atol=1e-8, rtol=0)).any(axis=1).sum()),
                      'synthetic_requested': requested, 'synthetic_created': len(synthetic),
                      'valid_category_domain': True, 'finite_numeric_after_inverse_scaling': True,
                      'original_observations_retained_for_model': 'Model not trained; no original row removed by this generator',
                      'preprocessing': 'Numeric train-median imputation + StandardScaler; categorical __MISSING__'},
    }
    (args.out/'precheck_smotenc.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    lines = [
        '# Precheck SMOTENC CG-HIL — ' + results['scope'].upper(), '',
        '**Hasil:** ' + results['status'] + ' untuk pemeriksaan yang benar-benar dijalankan (bukan hasil model).', '',
        '## Dataset dan kelompok', '',
        f'- Train/validasi/uji: {len(train):,} / {n_val:,} / {n_test:,}',
        f'- Fitur: {len(features)} ({len(numeric)} numerik; {len(categoric)} kategorikal untuk SMOTENC)',
        f'- Kategori yang disimpan numerik: {len(cat_numeric)} kolom (`FLAG_*`, rating, wilayah, jam)',
        f'- Median kelengkapan tau: {tau:.6f}',
        f'- E: {nE:,}; U: {nU:,}; S penuh: {S:,}',
        f'- Bobot U: {wU:.6f}; total positif M1-M4: {n1+2*S:,}', '',
        '## Hasil uji generator', '',
        f'- Mode: **{results["scope"]}**',
        f'- Input mayoritas/E generator: {len(chosen0):,} / {len(chosenE):,}',
        f'- Sampel sintetis diminta/dihasilkan: {requested:,} / {len(synthetic):,}',
        '- Semua kategori sintetis valid terhadap input generator: YA',
        '- Numerik sintetis finite setelah inverse standardisasi: YA',
        '- Seluruh data asli tetap tersedia untuk model: YA (generator tidak mengganti data asli)', '',
        '## Batas dan keputusan', '',
        '- **Belum menguji model XGBoost atau PR-AUC.**',
        '- StandardScaler ditambahkan secara terbuka sebagai **usulan** agar jarak numerik tidak bergantung pada satuan fitur.',
        '- XNA/Unknown tetap eksplisit; sentinel durasi dimask NaN sebelum imputasi generator.',
        '- Hitungan sintetis dibulatkan ties-to-even nonnegatif; DEF diproyeksikan ke OBS bila perlu.',
        '- Lihat JSON semantic_validation untuk jumlah hard/potential sebelum dan sesudah.',
        '- Lulus PILOT tidak sama dengan lulus FULL. Jalankan `--full` setelah PILOT berhasil.',
        '',
    ]
    (args.out/'precheck_smotenc.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'{results["status"]} {results["scope"]}: S created={len(synthetic)}; report={args.out/"precheck_smotenc.md"}', flush=True)
    if hard_remaining:
        raise SystemExit('Unresolved hard semantic violations; see JSON')


if __name__ == '__main__':
    main()
