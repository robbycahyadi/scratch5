"""Train-only Phase 1 descriptions. No models, synthesis or prediction access.
Run: .venv/bin/python diagnose_cghil_eu.py --out results/eu_phase1
Output directory must not exist. Raw source and frozen source hashes are checked.
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, default=Path('application_train.csv'))
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    manifest = json.loads(Path('CG_HIL_EXPERIMENT_MANIFEST.json').read_text())
    raw_hash = sha(args.input)
    assert raw_hash == manifest['dataset_sha256']
    for name, digest in manifest['source_sha256'].items():
        assert sha(name) == digest, name
    # Only labels are read for the original stratified assignment. No holdout
    # predictors are loaded: a second chunked pass retains train rows only.
    y = pd.read_csv(args.input, usecols=['TARGET']).TARGET
    tr, _ = train_test_split(np.arange(len(y)), test_size=.30,
                             random_state=42, stratify=y)
    index_hash = hashlib.sha256(np.asarray(tr, dtype='<i8').tobytes()).hexdigest()
    assert index_hash == manifest['split']['train']['ordered_index_sha256']
    pieces = []
    offset = 0
    for chunk in pd.read_csv(args.input, chunksize=25000, low_memory=False):
        chunk.index = np.arange(offset, offset + len(chunk))
        offset += len(chunk)
        pieces.append(chunk.loc[chunk.index.isin(tr)])
    train = pd.concat(pieces).loc[tr]
    del pieces, y
    features = [c for c in train if c not in ('TARGET', 'SK_ID_CURR')]
    removed = [c for c in features if train[c].nunique(dropna=False) <= 1]
    features = [c for c in features if c not in removed]
    assert features == manifest['features'] and len(features) == 120
    miss = train[features].isna()
    c = (~miss).mean(axis=1)
    pos = train.TARGET.eq(1)
    tau = float(c[pos].median())
    E, U = pos & c.gt(tau), pos & c.le(tau)
    assert (len(train), int(pos.sum()), tau, int(E.sum()), int(U.sum())) == (215257, 17377, .6, 8636, 8741)
    housing = [f for f in features if f.endswith(('_AVG', '_MEDI', '_MODE'))]
    assert len(housing) == 47
    bureau = [f for f in features if f.startswith('AMT_REQ_CREDIT_BUREAU_')]
    social = [f for f in features if f.endswith('_CNT_SOCIAL_CIRCLE')]
    groups = {'train': pd.Series(True, index=train.index), 'positive': pos, 'E': E, 'U': U}
    out = {'provenance': {'raw_sha256': raw_hash, 'ordered_train_index_sha256': index_hash,
                         'python': platform.python_version(), 'numpy': np.__version__,
                         'pandas': pd.__version__, 'sklearn': sklearn.__version__,
                         'removed_features': removed, 'tau': tau}, 'groups': {}}
    profile = pd.DataFrame({'feature': features})
    for name, mask in groups.items():
        profile[name + '_missing_n'] = miss.loc[mask].sum().to_numpy()
        profile[name + '_missing_pct'] = 100 * miss.loc[mask].mean().to_numpy()
        t, m, s = train.loc[mask], miss.loc[mask], c.loc[mask]
        h = m[housing].sum(axis=1)
        patterns = m.apply(lambda row: '|'.join(row.index[row]), axis=1).value_counts()
        out['groups'][name] = {
            'n': len(t), 'completeness': s.describe(percentiles=[.25, .5, .75]).to_dict(),
            'at_tau': int(s.eq(tau).sum()), 'housing_missing_mean': float(h.mean()),
            'housing_all_missing': int(h.eq(47).sum()), 'housing_all_present': int(h.eq(0).sum()),
            'missing_cells': int(m.sum().sum()), 'housing_missing_cells': int(m[housing].sum().sum()),
            'unique_missing_patterns': len(patterns),
            'top_patterns': [{'missing_features': k.split('|') if k else [], 'n': int(v)} for k,v in patterns.head(3).items()],
            'numeric': {}, 'categorical': {}}
        for col in ['DAYS_BIRTH', 'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'CNT_CHILDREN', 'EXT_SOURCE_2', 'EXT_SOURCE_3']:
            values = -t[col]/365.25 if col == 'DAYS_BIRTH' else t[col]
            out['groups'][name]['numeric'][col] = values.describe().to_dict()
        for col in ['FLAG_OWN_CAR', 'NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE', 'NAME_HOUSING_TYPE', 'CODE_GENDER', 'ORGANIZATION_TYPE']:
            out['groups'][name]['categorical'][col] = {str(k): int(v) for k,v in t[col].value_counts(dropna=False).items()}
    out['conditional'] = {}
    for col in ['FLAG_OWN_CAR', 'NAME_INCOME_TYPE', 'ORGANIZATION_TYPE', 'FLAG_OWN_REALTY', 'NAME_HOUSING_TYPE']:
        rows = []
        for value, t in train.groupby(col, dropna=False):
            rows.append({'value': str(value), 'n': len(t), 'car_age_missing': int(t.OWN_CAR_AGE.isna().sum()),
                         'occupation_missing': int(t.OCCUPATION_TYPE.isna().sum()),
                         'employment_sentinel': int(t.DAYS_EMPLOYED.eq(365243).sum()),
                         'organization_XNA': int(t.ORGANIZATION_TYPE.eq('XNA').sum()),
                         'housing_all_missing': int(t[housing].isna().all(axis=1).sum())})
        out['conditional'][col] = rows
    out['blocks'] = {}
    for name, cols in [('bureau', bureau), ('social', social)]:
        out['blocks'][name] = {'features': cols, 'missing_count_distribution': {str(k): int(v) for k,v in miss[cols].sum(axis=1).value_counts().sort_index().items()}}
    out['employment_mask_mismatch'] = int((train.DAYS_EMPLOYED.eq(365243) != train.ORGANIZATION_TYPE.eq('XNA')).sum())
    out['special_counts'] = {}
    for name, mask in groups.items():
        t = train.loc[mask]
        out['special_counts'][name] = {'sentinel': int(t.DAYS_EMPLOYED.eq(365243).sum()), 'gender_XNA': int(t.CODE_GENDER.eq('XNA').sum()), 'family_Unknown': int(t.NAME_FAMILY_STATUS.eq('Unknown').sum()), 'car_N': int(t.FLAG_OWN_CAR.eq('N').sum())}
    # Fixed tau, one-factor accounting stress tests, NOT replacement scores.
    observed = (~miss).sum(axis=1)
    car_na = train.FLAG_OWN_CAR.eq('N') & train.OWN_CAR_AGE.isna()
    scenarios = {'mask_employment_sentinel': (observed-train.DAYS_EMPLOYED.eq(365243).astype(int))/120,
                 'exclude_inapplicable_car_age': observed/(120-car_na.astype(int)),
                 'omit_housing_block': (~miss.drop(columns=housing)).mean(axis=1)}
    out['sensitivity_fixed_tau'] = {}
    for name, score in scenarios.items():
        new_e = pos & score.gt(tau)
        out['sensitivity_fixed_tau'][name] = {'E_to_U': int((E & ~new_e).sum()), 'U_to_E': int((U & new_e).sum()),
                                              'positive_score_mean_change': float((score-c)[pos].mean())}
    out['coverage'] = {}
    for col in ['NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE', 'NAME_HOUSING_TYPE', 'ORGANIZATION_TYPE', 'OCCUPATION_TYPE']:
        a = set(train.loc[E, col].dropna()); b = set(train.loc[U, col].dropna())
        out['coverage'][col] = {'E_levels': len(a), 'U_levels': len(b), 'U_only': sorted(b-a), 'E_only': sorted(a-b)}
    assert sha(args.input) == raw_hash
    args.out.mkdir(parents=True, exist_ok=False)
    profile.to_csv(args.out/'feature_missingness.csv', index=False)
    (args.out/'diagnostics.json').write_text(json.dumps(out, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
    print(json.dumps({'status': 'PASS', 'train': len(train), 'positive': int(pos.sum()), 'tau': tau, 'E': int(E.sum()), 'U': int(U.sum()), 'output': str(args.out)}))


if __name__ == '__main__':
    main()
