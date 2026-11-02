#!/usr/bin/env python3
"""Read-only semantic diagnostics; exploratory completeness sensitivity, no training."""
from pathlib import Path
import hashlib
import json
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, default=Path('application_train.csv'))
    p.add_argument('--out', type=Path, default=Path('results/semantic_audit'))
    a = p.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
    before = sha(a.input)
    d = pd.read_csv(a.input, low_memory=False)
    fs = [c for c in d if c not in ['TARGET', 'SK_ID_CURR']]
    outputs = []
    def csv(name, frame):
        frame.to_csv(a.out / (name + '.csv'), index=False); outputs.append(name + '.csv')
    profile=[]; cats=[]
    for c in fs:
        s=d[c]; num=pd.api.types.is_numeric_dtype(s); v=s.dropna()
        nonint=int((v.mod(1).ne(0)).sum()) if num else None
        profile.append(dict(feature=c,dtype=str(s.dtype),nunique=int(s.nunique()),missing=int(s.isna().sum()),missing_rate=float(s.isna().mean()),min=v.min() if num and len(v) else None,max=v.max() if num and len(v) else None,noninteger_count=nonint,noninteger_rate_nonmissing=nonint/len(v) if num and len(v) else None))
        if not num:
            for val,n in s.value_counts(dropna=False).items(): cats.append(dict(feature=c,value=None if pd.isna(val) else val,is_missing=bool(pd.isna(val)),count=int(n)))
    csv('predictor_profile',pd.DataFrame(profile)); csv('categorical_counts',pd.DataFrame(cats))
    sentinel=d.DAYS_EMPLOYED.eq(365243); xna=d.ORGANIZATION_TYPE.eq('XNA')
    ct=d.assign(days_employed_sentinel=sentinel,organization_xna=xna).groupby(['days_employed_sentinel','organization_xna','NAME_INCOME_TYPE'],dropna=False).size().reset_index(name='count')
    csv('employment_exact_crosstab',ct)
    csv('employment_mismatch_ids',d.loc[sentinel.ne(xna),['SK_ID_CURR','TARGET','DAYS_EMPLOYED','ORGANIZATION_TYPE','NAME_INCOME_TYPE']])
    special=d.CODE_GENDER.eq('XNA')|d.NAME_FAMILY_STATUS.eq('Unknown')
    csv('gender_family_special_ids',d.loc[special,['SK_ID_CURR','TARGET','CODE_GENDER','NAME_FAMILY_STATUS','NAME_INCOME_TYPE','DAYS_EMPLOYED','ORGANIZATION_TYPE']])
    csv('gender_family_crosstab',d.groupby(['CODE_GENDER','NAME_FAMILY_STATUS'],dropna=False).size().reset_index(name='count'))
    structural=[]
    for col,group in [('OWN_CAR_AGE','FLAG_OWN_CAR'),('OCCUPATION_TYPE','NAME_INCOME_TYPE'),('OWN_CAR_AGE','FLAG_MOBIL')]:
        t=d.assign(is_missing=d[col].isna()).groupby([group,'is_missing'],dropna=False).size().reset_index(name='count'); t.insert(0,'feature',col); t=t.rename(columns={group:'group_value'}); t.insert(1,'group_feature',group); structural.append(t)
    csv('structural_missing_crosstabs',pd.concat(structural,ignore_index=True))
    housing=[c for c in fs if c.endswith(('_AVG','_MODE','_MEDI')) or c in ['FONDKAPREMONT_MODE','HOUSETYPE_MODE','WALLSMATERIAL_MODE','EMERGENCYSTATE_MODE']]
    hm=d[housing].isna(); pair=[]
    for i,c in enumerate(housing):
        for b in housing[i+1:]: pair.append(dict(feature_a=c,feature_b=b,both_missing=int((hm[c]&hm[b]).sum()),a_only_missing=int((hm[c]&~hm[b]).sum()),b_only_missing=int((~hm[c]&hm[b]).sum()),both_present=int((~hm[c]&~hm[b]).sum())))
    csv('housing_missing_pairs',pd.DataFrame(pair))
    csv('housing_missing_patterns',hm.astype('uint8').astype(str).agg(''.join,axis=1).value_counts().rename_axis('pattern_in_column_order').reset_index(name='count'))
    checks=[]; violations=[]
    for days in ['30','60']:
        obs=f'OBS_{days}_CNT_SOCIAL_CIRCLE'; default=f'DEF_{days}_CNT_SOCIAL_CIRCLE'; valid=d[[obs,default]].notna().all(axis=1); bad=valid & d[default].gt(d[obs])
        checks.append(dict(check=default+' <= '+obs,comparable=int(valid.sum()),violations=int(bad.sum()),missing_pair=int((~valid).sum())))
        for row in d.loc[bad,['SK_ID_CURR',obs,default]].to_dict('records'): violations.append(dict(check=default+' <= '+obs,**row))
    csv('social_violations',pd.DataFrame(violations,columns=['check','SK_ID_CURR','OBS_30_CNT_SOCIAL_CIRCLE','DEF_30_CNT_SOCIAL_CIRCLE','OBS_60_CNT_SOCIAL_CIRCLE','DEF_60_CNT_SOCIAL_CIRCLE']))
    days=[]
    for c in [c for c in fs if c.startswith('DAYS_') or c.startswith('AMT_REQ_CREDIT_BUREAU_') or 'CNT_SOCIAL_CIRCLE' in c]:
        s=d[c]; v=s.dropna(); days.append(dict(feature=c,missing=int(s.isna().sum()),negative=int(s.lt(0).sum()),zero=int(s.eq(0).sum()),positive=int(s.gt(0).sum()),sentinel_365243=int(s.eq(365243).sum()),noninteger=int(v.mod(1).ne(0).sum()),noninteger_rate_nonmissing=float(v.mod(1).ne(0).mean()),min=v.min(),max=v.max()))
    csv('days_credit_social_numeric_checks',pd.DataFrame(days))
    tr,ho=train_test_split(np.arange(len(d)),test_size=.30,random_state=42,stratify=d.TARGET)
    va,te=train_test_split(ho,test_size=.5,random_state=42,stratify=d.TARGET.iloc[ho])
    train=d.iloc[tr]; removed=[c for c in fs if train[c].nunique(dropna=False)<=1]; features=[c for c in fs if c not in removed]
    base=train[features].notna(); emp=train.DAYS_EMPLOYED.eq(365243)
    one=base.copy(); one.loc[emp,'DAYS_EMPLOYED']=False
    four=one.copy()
    for c,val in [('ORGANIZATION_TYPE','XNA'),('CODE_GENDER','XNA'),('NAME_FAMILY_STATUS','Unknown')]: four.loc[train[c].eq(val),c]=False
    # Exploratory: non-applicable employment/org removed from denominator for pensioners/unemployed;
    # outside that group all four markers remain masked. No changes to source data.
    applicable=~train.NAME_INCOME_TYPE.isin(['Pensioner','Unemployed']); aware=four.copy(); denom=pd.Series(len(features),index=train.index)
    aware.loc[~applicable,['DAYS_EMPLOYED','ORGANIZATION_TYPE']]=False; denom.loc[~applicable]-=2
    scores={'baseline_notna':base.mean(axis=1),'mask_employed_sentinel':one.mean(axis=1),'mask_four_codes':four.mean(axis=1),'applicable_aware_exploratory':aware.sum(axis=1)/denom}
    positive=train.TARGET.eq(1); summaries=[]; membership=pd.DataFrame({'SK_ID_CURR':train.SK_ID_CURR,'TARGET':train.TARGET,'NAME_INCOME_TYPE':train.NAME_INCOME_TYPE}); groups={}
    for name,score in scores.items():
        ps=score[positive]; tau=float(ps.median()); group=pd.Series(np.where(score.gt(tau),'E','U'),index=train.index); groups[name]=group
        E=int((ps>tau).sum()); U=int((ps<=tau).sum()); S=min(E,U); n=len(ps)
        summaries.append(dict(scenario=name,tau=tau,E=E,U=U,equal_tau=int(ps.eq(tau).sum()),S=S,wU=1+S/U if U else None,positive_weight_total=n+2*S,M1_original_positive_weight=1+2*S/n,M3_original_positive_weight=1+S/n,original_E_weight=1,original_U_weight_M2_M4=1+S/U if U else None))
        membership[name+'_score']=score; membership[name+'_group']=group.where(positive,'not_positive')
    csv('sensitivity_summary',pd.DataFrame(summaries)); csv('train_membership_sensitivity',membership)
    transitions=[]; incomes=[]
    for name,g in groups.items():
        t=pd.DataFrame({'income':train.NAME_INCOME_TYPE[positive],'baseline':groups['baseline_notna'][positive],'scenario_group':g[positive]})
        for (b,s),n in t.groupby(['baseline','scenario_group']).size().items(): transitions.append(dict(scenario=name,baseline=b,scenario_group=s,count=int(n)))
        for (inc,b,s),n in t.groupby(['income','baseline','scenario_group']).size().items(): incomes.append(dict(scenario=name,income=inc,baseline=b,scenario_group=s,count=int(n)))
    csv('positive_EU_transitions',pd.DataFrame(transitions)); csv('positive_income_EU_transitions',pd.DataFrame(incomes))
    after=sha(a.input)
    report=dict(source=str(a.input.resolve()),sha256_before=before,sha256_after=after,source_unchanged=before==after,rows=len(d),predictor_count=len(fs),employment_sentinel_count=int(sentinel.sum()),organization_xna_count=int(xna.sum()),employment_mismatch_count=int(sentinel.ne(xna).sum()),special_gender_count=int(d.CODE_GENDER.eq('XNA').sum()),special_family_count=int(d.NAME_FAMILY_STATUS.eq('Unknown').sum()),gender_family_overlap=int((d.CODE_GENDER.eq('XNA')&d.NAME_FAMILY_STATUS.eq('Unknown')).sum()),housing_columns=housing,housing_all_missing=int(hm.all(axis=1).sum()),housing_none_missing=int((~hm.any(axis=1)).sum()),social_checks=checks,split=dict(seed=42,stratified=True,train=len(tr),valid=len(va),test=len(te),train_positive=int(positive.sum()),features_removed_train_only=removed,score_features=len(features)),scenario_definitions=dict(baseline_notna='Literal pandas notna, no semantic masking',mask_employed_sentinel='Only DAYS_EMPLOYED=365243 marked absent',mask_four_codes='DAYS_EMPLOYED=365243, ORGANIZATION_TYPE=XNA, CODE_GENDER=XNA, NAME_FAMILY_STATUS=Unknown marked absent',applicable_aware_exploratory='Four-code mask; exclude DAYS_EMPLOYED and ORGANIZATION_TYPE from numerator AND denominator for Pensioner/Unemployed only; exploratory, not final'),sensitivity=summaries,outputs=outputs,no_training=True,no_design_change=True)
    (a.out/'diagnostics.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    assert before==after, 'Source hash changed'
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
