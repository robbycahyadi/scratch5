"""Fixed CG-HIL experiment; prepare -> train/validation -> one-shot test.

No tuning. Existing output directories are never overwritten. Test evaluation
requires a persisted pretest manifest and uses an exclusive start marker.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.metadata as metadata
import inspect
import json
import platform
import subprocess
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTENC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import (average_precision_score, roc_auc_score,
                             precision_score, recall_score, f1_score, confusion_matrix)
from xgboost import XGBClassifier
from precheck_smotenc_cghil import prepare_generator, split_train
from cghil_semantics import (derive_semantic_columns, model_frame, round_counts,
                            synthetic_model_frame, assert_synthetic_model_numeric,
                            validate_semantics)

ROOT = Path(__file__).resolve().parent
METHODS = ('M0', 'M1', 'M2', 'M3', 'M4')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n')


def load_params():
    text = (ROOT/'02_XGBOOST_PROTOCOL_USULAN.md').read_text()
    assert 'DISETUJUI / FROZEN' in text
    code = text.split('```python\n', 1)[1].split('```', 1)[0]
    call = ast.parse(code).body[0].value
    return {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}


def split_indices(y):
    idx = np.arange(len(y))
    tr, hold = train_test_split(idx, test_size=.30, random_state=42, stratify=y)
    va, te = train_test_split(hold, test_size=.50, random_state=42,
                              stratify=np.asarray(y)[hold])
    assert not set(tr)&set(va) and not set(tr)&set(te) and not set(va)&set(te)
    assert len(tr)+len(va)+len(te) == len(y)
    return tr, va, te


def method_weights(method, y, u_mask, S):
    assert method in METHODS
    y = np.asarray(y)
    u_mask = np.asarray(u_mask, dtype=bool)
    assert len(y) == len(u_mask) and not np.any(u_mask & (y != 1))
    w = np.ones(len(y), dtype=np.float64)
    if method == 'M1':
        w[y == 1] = 1+2*S/(y == 1).sum()
    elif method == 'M3':
        w[y == 1] = 1+S/(y == 1).sum()
    elif method == 'M4':
        w[u_mask] = 1+S/u_mask.sum()
    count = 2*S if method == 'M2' else S if method in ('M3', 'M4') else 0
    return np.concatenate([w, np.ones(count)])


def choose_threshold(y, p):
    """Exact integer-ratio F1 comparison, largest probability wins ties."""
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    assert len(y) == len(p) and len(y) and np.isfinite(p).all()
    assert set(np.unique(y)) <= {0, 1}
    order = np.argsort(-p, kind='stable')
    scores, labels = p[order], y[order]
    tp = np.cumsum(labels)
    ends = np.flatnonzero(np.r_[scores[:-1] != scores[1:], True])
    best_num, best_den, best_t = -1, 1, None
    positive_count = int(y.sum())
    for end in ends:
        num, den = 2*int(tp[end]), positive_count+int(end)+1
        if num*best_den > best_num*den:
            best_num, best_den, best_t = num, den, float(scores[end])
    return best_t, best_num/best_den


def encode_frame(frame, features, categorical, encoder):
    out = frame[features].copy()
    out[categorical] = encoder.transform(frame[categorical])
    out = out.astype('float64')
    assert not np.isinf(out.to_numpy()).any()
    return out


def verify_sources():
    manifest = json.loads((ROOT/'CG_HIL_GENERATOR_SOURCE_MANIFEST.json').read_text())
    for n, h in manifest['source_sha256'].items():
        assert sha(ROOT/n) == h, f'Frozen source changed: {n}'
    for n, v in manifest['dependencies'].items():
        assert metadata.version(n) == v, f'Dependency changed: {n}'
    assert metadata.version('xgboost-cpu') == '3.4.1'
    return manifest


def source_hashes():
    names = ['run_cghil_experiment.py', 'test_run_cghil_experiment.py',
             '02_XGBOOST_PROTOCOL_USULAN.md', 'requirements-xgboost.txt']
    names += list(verify_sources()['source_sha256'])
    return {n: sha(ROOT/n) for n in names}


def check_run(m):
    assert source_hashes() == m['source_sha256'], 'Source changed since prepare'
    assert load_params() == m['params']
    for n, h in m['artifact_sha256'].items():
        assert sha(Path(m['output'])/n) == h, f'Artifact changed: {n}'


def generate(generator, scaler, features, numeric, categorical, counts, source, majority, requested):
    pool = generator.loc[majority.append(source)].reset_index(drop=True)
    labels = np.r_[np.zeros(len(majority), dtype=np.int8), np.ones(len(source), dtype=np.int8)]
    sm = SMOTENC(categorical_features=categorical,
                 sampling_strategy={1: len(source)+requested}, k_neighbors=5, random_state=42)
    res, yr = sm.fit_resample(pool, labels)
    pd.testing.assert_frame_equal(res.iloc[:len(pool)].reset_index(drop=True), pool,
                                  check_dtype=False)
    syn = res.iloc[len(pool):].reset_index(drop=True).copy()
    assert len(syn) == requested and np.all(np.asarray(yr)[len(pool):] == 1)
    assert not syn.isna().any().any()
    allowed = {c: set(generator.loc[source, c].astype(str)) for c in categorical}
    scaled = syn[numeric].to_numpy(dtype=float)
    bounds = generator.loc[source, numeric].to_numpy(dtype=float)
    assert np.isfinite(scaled).all()
    assert np.all(scaled >= bounds.min(axis=0)-1e-6)
    assert np.all(scaled <= bounds.max(axis=0)+1e-6)
    syn[numeric] = scaler.inverse_transform(scaled)
    assert np.isfinite(syn[numeric].to_numpy(dtype=float)).all()
    syn = round_counts(syn, counts)
    for days in (30, 60):
        a, b = f'DEF_{days}_CNT_SOCIAL_CIRCLE', f'OBS_{days}_CNT_SOCIAL_CIRCLE'
        syn[a] = np.minimum(syn[a], syn[b])
    assert not syn.DAYS_EMPLOYED.eq(365243).any()
    assert syn.DAYS_EMPLOYED.le(1e-8).all()
    assert np.allclose(syn[counts], np.rint(syn[counts]), atol=1e-8, rtol=0)
    assert syn[counts].ge(0).all().all()
    syn = synthetic_model_frame(syn, features, categorical)
    assert_synthetic_model_numeric(syn, numeric)
    rules = validate_semantics(syn, numeric, categorical, counts, allowed)
    hard = {k: v for k, v in rules.items() if v['severity'] == 'hard' and v['count']}
    assert not hard, f'Hard violations: {hard}'
    assert rules['car_N_age_present']['count'] == 0
    assert rules['organization_XNA_employed_present']['count'] == 0
    return syn, {'synthetic_count': requested, 'source_positive_count': len(source),
                 'hard_remaining': hard, 'semantic_validation': rules,
                 'structural_nan_cells': int(syn[numeric].isna().sum().sum())}


def prepare(input_path, out):
    frozen = verify_sources()
    assert sha(input_path) == frozen['raw_dataset_sha256']
    out.mkdir(parents=True, exist_ok=False)
    df = pd.read_csv(input_path, low_memory=False)
    assert df.TARGET.isin([0, 1]).all() and not df.SK_ID_CURR.duplicated().any()
    tr, va, te = split_indices(df.TARGET)
    assert tuple(map(len, (tr, va, te))) == (215257, 46127, 46127)
    train = df.iloc[tr].copy()
    reference, _, _ = split_train(df)
    pd.testing.assert_frame_equal(train, reference)
    del reference
    features = [c for c in df if c not in ('TARGET', 'SK_ID_CURR')]
    removed = [c for c in features if train[c].nunique(dropna=False) <= 1]
    features = [c for c in features if c not in removed]
    numeric, categorical, counts = derive_semantic_columns(features)
    assert (len(features), len(numeric), len(categorical), len(counts)) == (120, 69, 51, 12)
    y = train.TARGET.to_numpy(dtype=int)
    comp = train[features].notna().mean(axis=1)
    tau = float(comp[y == 1].median())
    E = train.index[(y == 1) & comp.gt(tau)]
    U = train.index[(y == 1) & comp.le(tau)]
    majority = train.index[y == 0]
    S = min(len(E), len(U))
    assert (tau, len(E), len(U), S, int(y.sum())) == (.6, 8636, 8741, 8636, 17377)
    original = model_frame(train, features, categorical)
    original[numeric] = original[numeric].astype('float64')
    expected = train[features].copy()
    expected.loc[expected.DAYS_EMPLOYED.eq(365243), 'DAYS_EMPLOYED'] = np.nan
    pd.testing.assert_frame_equal(original[numeric], expected[numeric], check_dtype=False)
    encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    encoder.fit(original[categorical])
    X = encode_frame(original, features, categorical, encoder).reset_index(drop=True)
    # Only validation is represented here; test features remain untouched until evaluate.
    valid = model_frame(df.iloc[va], features, categorical)
    Xv = encode_frame(valid, features, categorical, encoder).reset_index(drop=True)
    generator, scaler = prepare_generator(train, features, numeric, categorical)
    assert int(scaler.n_samples_seen_) == len(train)
    params = load_params()
    for method in METHODS:
        model = XGBClassifier(**params)
        assert all(model.get_params()[k] == v for k, v in params.items())
        assert 'sample_weight' in inspect.signature(model.fit).parameters
    artifacts = {'X_original': X, 'y_original': y, 'X_validation': Xv,
                 'y_validation': df.iloc[va].TARGET.to_numpy(dtype=int),
                 'encoder': encoder, 'features': features, 'categorical': categorical,
                 'numeric': numeric, 'train_indices': tr, 'validation_indices': va,
                 'test_indices': te}
    joblib.dump(artifacts, out/'prepared.joblib')
    gates = {}
    u_mask = train.index.isin(U)
    for method in METHODS:
        print('PREPARE', method, flush=True)
        synX = pd.DataFrame(columns=features, dtype=float)
        details = {'synthetic_count': 0, 'hard_remaining': {}}
        if method in ('M2', 'M3', 'M4'):
            requested = 2*S if method == 'M2' else S
            syn, details = generate(generator, scaler, features, numeric, categorical,
                                    counts, E if method == 'M4' else train.index[y == 1],
                                    majority, requested)
            synX = encode_frame(syn, features, categorical, encoder)
            assert not (synX[categorical] == -1).any().any()
        combined = pd.concat([X, synX], ignore_index=True)
        pd.testing.assert_frame_equal(combined.iloc[:len(X)], X)
        yy = np.r_[y, np.ones(len(synX), dtype=int)]
        weights = method_weights(method, y, u_mask, S)
        assert len(weights) == len(combined) == len(yy)
        assert np.all(weights[yy == 0] == 1)
        assert np.all(weights[len(y):] == 1)
        total = float(weights[yy == 1].sum())
        assert np.isclose(total, 17377 if method == 'M0' else 34649, atol=1e-7, rtol=0)
        joblib.dump({'synthetic_encoded': synX, 'weights': weights}, out/f'{method}_prepared.joblib')
        gates[method] = {**details, 'original_count': len(X), 'positive_weight_total': total,
                         'original_prefix_equal': True, 'feature_schema_equal': True,
                         'synthetic_unknown_categories': 0, 'status': 'PASS'}
    names = ['prepared.joblib']+[f'{m}_prepared.joblib' for m in METHODS]
    m = {'stage': 'INTEGRATION_PASS', 'created_utc': datetime.now(timezone.utc).isoformat(),
         'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
         'output': str(out.resolve()), 'input': str(input_path.resolve()),
         'dataset_sha256': frozen['raw_dataset_sha256'], 'source_sha256': source_hashes(),
         'versions': {'python': platform.python_version(), **{n: metadata.version(n) for n in
                      ['numpy','pandas','scikit-learn','imbalanced-learn','xgboost-cpu']}},
         'params': params, 'seed': 42, 'features': features, 'numeric': numeric,
         'categorical': categorical, 'removed_constants': removed,
         'encoder_categories': [list(x) for x in encoder.categories_],
         'encoder_config': {'handle_unknown': 'use_encoded_value', 'unknown_value': -1,
                            'dtype': 'float64', 'fit_scope': 'original train only'},
         'split': {k: {'count': len(v), 'ordered_index_sha256': hashlib.sha256(
                     np.asarray(v, dtype='<i8').tobytes()).hexdigest()} for k,v in
                     [('train',tr),('validation',va),('test',te)]},
         'completeness': {'tau': tau, 'E': len(E), 'U': len(U), 'S': S},
         'gates': gates, 'test_evaluated': False,
         'artifact_sha256': {n: sha(out/n) for n in names}}
    assert sha(input_path) == m['dataset_sha256']
    save_json(out/'integration_manifest.json', m)
    print('INTEGRATION PASS; test not evaluated', flush=True)


def train_validate(out):
    m = json.loads((out/'integration_manifest.json').read_text())
    assert m['stage'] == 'INTEGRATION_PASS'
    check_run(m)
    marker = out/'training_started.json'
    with marker.open('x') as f:
        json.dump({'utc': datetime.now(timezone.utc).isoformat()}, f)
    a = joblib.load(out/'prepared.joblib')
    rows, hashes = {}, {}
    for method in METHODS:
        print('TRAIN', method, flush=True)
        b = joblib.load(out/f'{method}_prepared.joblib')
        X = pd.concat([a['X_original'], b['synthetic_encoded']], ignore_index=True)
        y = np.r_[a['y_original'], np.ones(len(b['synthetic_encoded']), dtype=int)]
        model = XGBClassifier(**m['params'])
        model.fit(X, y, sample_weight=b['weights'])
        assert model.get_booster().num_boosted_rounds() == m['params']['n_estimators']
        p = model.predict_proba(a['X_validation'])[:, 1]
        threshold, score = choose_threshold(a['y_validation'], p)
        assert np.isclose(score, f1_score(a['y_validation'], p >= threshold))
        model.save_model(out/f'{method}.ubj')
        hashes[f'{method}.ubj'] = sha(out/f'{method}.ubj')
        rows[method] = {'best_valid_threshold': threshold, 'F1_valid': score,
                        'AP_valid': float(average_precision_score(a['y_validation'], p)),
                        'n_original': len(a['y_original']),
                        'n_synthetic': len(b['synthetic_encoded']),
                        'positive_weight_total': m['gates'][method]['positive_weight_total']}
        save_json(out/'validation_progress.json', rows)
    m.update(stage='PRETEST_LOCKED', validation=rows, model_sha256=hashes,
             integration_manifest_sha256=sha(out/'integration_manifest.json'))
    save_json(out/'pretest_manifest.json', m)
    print('PRETEST LOCKED: five trained models and thresholds saved; test untouched', flush=True)


def evaluate(out):
    m = json.loads((out/'pretest_manifest.json').read_text())
    assert m['stage'] == 'PRETEST_LOCKED' and len(m['validation']) == 5
    check_run(m)
    assert sha(out/'integration_manifest.json') == m['integration_manifest_sha256']
    for n,h in m['model_sha256'].items():
        assert sha(out/n) == h
    assert sha(m['input']) == m['dataset_sha256']
    with (out/'test_evaluation_started.json').open('x') as f:
        json.dump({'utc': datetime.now(timezone.utc).isoformat(),
                   'pretest_manifest_sha256': sha(out/'pretest_manifest.json')}, f)
    a = joblib.load(out/'prepared.joblib')
    df = pd.read_csv(m['input'], low_memory=False).iloc[a['test_indices']]
    X = encode_frame(model_frame(df, a['features'], a['categorical']),
                     a['features'], a['categorical'], a['encoder'])
    y = df.TARGET.to_numpy(dtype=int)
    rows = []
    predictions = pd.DataFrame({'internal_row_index': a['test_indices'], 'TARGET': y})
    for method in METHODS:
        model = XGBClassifier(**m['params'])
        model.load_model(out/f'{method}.ubj')
        p = model.predict_proba(X)[:, 1]
        t = m['validation'][method]['best_valid_threshold']
        pred = p >= t
        tn,fp,fn,tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
        row = {'method': method, **m['validation'][method],
               'AP_test': float(average_precision_score(y,p)),
               'ROC_AUC_test': float(roc_auc_score(y,p)),
               'precision_test': float(precision_score(y,pred,zero_division=0)),
               'recall_test': float(recall_score(y,pred)), 'F1_test': float(f1_score(y,pred)),
               'TN': int(tn), 'FP': int(fp), 'FN': int(fn), 'TP': int(tp)}
        rows.append(row)
        predictions[method] = p
    summary = pd.DataFrame(rows)
    summary.to_csv(out/'model_summary.csv', index=False)
    predictions.to_csv(out/'predictions_test.csv', index=False)
    ap = summary.set_index('method').AP_test
    delta = float(ap['M4']-ap['M3'])
    comparison = {'delta_AP_M4_minus_M3': delta,
                  'direction': 'positive' if delta>0 else 'negative' if delta<0 else 'zero',
                  'statistical_significance_tested': False}
    save_json(out/'comparison.json', comparison)
    m.update(stage='TEST_EVALUATED_ONCE', test_evaluated=True,
             pretest_manifest_sha256=sha(out/'pretest_manifest.json'),
             comparison=comparison,
             result_sha256={n:sha(out/n) for n in ['model_summary.csv','comparison.json','predictions_test.csv']})
    save_json(out/'run_manifest.json', m)
    print(summary.to_string(index=False), flush=True)
    print(comparison, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=['prepare','train','evaluate'])
    p.add_argument('--input', type=Path, default=ROOT/'application_train.csv')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    if not __debug__:
        raise RuntimeError('Assertions must remain enabled; do not use python -O')
    if args.stage == 'prepare':
        prepare(args.input, args.out)
    elif args.stage == 'train':
        train_validate(args.out)
    else:
        evaluate(args.out)


if __name__ == '__main__':
    main()
