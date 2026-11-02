"""Read-only dataset semantic dictionary build; no preprocessing/model changes."""
from pathlib import Path
import csv, json, hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parent
SOURCE='https://raw.githubusercontent.com/gridl/workshop_2018_dsgo/2b7b0e95828b5a95e0e783b7ea764e5962fb3fb4/00_data/HomeCredit_columns_description.csv.zip'
OFFICIAL='https://www.kaggle.com/competitions/home-credit-default-risk/data'
SECONDARY='https://harnalashok.github.io/credit_risk/application_train_test.html'
def main():
    raw=ROOT/'application_train.csv'
    df=pd.read_csv(raw)
    dictionary=ROOT/'semantic_audit_sources/HomeCredit_columns_description.csv'
    entries=list(csv.DictReader(dictionary.read_bytes().decode('cp1252').splitlines()))
    lookup={r['Row']:(i+2,r) for i,r in enumerate(entries) if r['Table']=='application_{train|test}.csv'}
    result=[]
    for col in df.columns:
        if col in ('SK_ID_CURR','TARGET'): continue
        line,d=lookup[col];s=df[col]
        notes=[];certainty='Definition reproduced verbatim from secondary mirror; official bytes not verified'
        if col.startswith('FLAG_') or '_NOT_' in col:
            kind='binary categorical';smote='categorical mask = True'
        elif col in ('REGION_RATING_CLIENT','REGION_RATING_CLIENT_W_CITY','NAME_EDUCATION_TYPE'):
            kind='ordinal categorical';smote='categorical mask = True; explicit order if ordinal encoding, no arbitrary numeric distance'
        elif col=='HOUR_APPR_PROCESS_START':
            kind='cyclic discrete hour';smote='categorical mask = True defensible for raw hour; consider cyclic encoding separately, not applied'
        elif col=='WEEKDAY_APPR_PROCESS_START':
            kind='cyclic categorical weekday';smote='categorical mask = True'
        elif not pd.api.types.is_numeric_dtype(s.dtype):
            kind='nominal categorical';smote='categorical mask = True'
        elif col.startswith('DAYS_'):
            kind='relative day offset';smote='numeric; negative values valid, not missing';notes.append('Past events encoded as negative offsets relative to application; not a calendar date. Sign interpretation consistent with raw data and dictionary, not an explicit sentinel glossary.')
        elif col.startswith('CNT_') or '_CNT_SOCIAL_CIRCLE' in col or col.startswith('AMT_REQ_CREDIT_BUREAU_'):
            kind='discrete count';smote='numeric count, not categorical solely due to integer storage';notes.append('SMOTENC numeric interpolation may yield fractional counts; validate synthetic support.')
        elif col=='OWN_CAR_AGE':
            kind='numeric age';smote='numeric'
        elif col.startswith('AMT_'):
            kind='numeric monetary amount';smote='numeric'
        else:
            kind='normalized numeric measure';smote='numeric';notes.append('Normalized values, not raw counts/areas/years; no inverse normalization documented.')
        if col.startswith('EXT_SOURCE_'):
            notes.append('Only normalized external-source score documented; provider, inputs, calibration, and probability interpretation undisclosed. Not confirmed to be a bureau score.')
        if col=='FLAG_WORK_PHONE':
            notes.append('Dictionary says home phone, same as FLAG_PHONE, whereas name suggests work phone. Preserve verbatim; unresolved source ambiguity; do not silently correct.')
            certainty+='; phone subtype ambiguous'
        specials={}
        if col=='DAYS_EMPLOYED':
            specials['365243']=int(s.eq(365243).sum());notes.append('365243 is implausible tenure offset and commonly treated as anomaly/sentinel in secondary analyses; precise official meaning not verified. Retain raw; propose separate flag and derived missingness only.')
        if col in ('ORGANIZATION_TYPE','CODE_GENDER'):
            specials['XNA']=int(s.eq('XNA').sum());notes.append('XNA observed special category. Exact official expansion/unknown vs not-applicable meaning not verified; do not assign substantive category.')
        if col=='NAME_FAMILY_STATUS':
            specials['Unknown']=int(s.eq('Unknown').sum());notes.append('Unknown literal label; treat as reported unknown status, not automatically missing in raw completeness.')
        missing=int(s.isna().sum());special_n=sum(specials.values())
        result.append({'feature':col,'dictionary_definition_verbatim':d['Description'],'dictionary_special_verbatim':d['Special'],'dictionary_csv_line':line,'actual_dtype_pandas':str(s.dtype),'semantic_type_audited':kind,'missing_count_raw':missing,'missing_pct_raw':100*missing/len(df),'observed_special_codes_counts':json.dumps(specials),'special_count_nonnull':special_n,'proposed_semantic_missing_count_if_codes_mapped':missing+special_n,'completeness_recommendation':'Keep raw null completeness separate from candidate sentinel/unknown-aware completeness; no mutation applied' if specials else 'Use raw null completeness; numeric zero/negative values are not automatically missing','smotenc_recommendation':smote,'certainty':certainty,'audit_notes':' '.join(notes),'source_url':SOURCE,'crosscheck_secondary_url':SECONDARY,'official_reference_unverified_body':OFFICIAL})
    assert len(result)==120
    out=ROOT/'HOME_CREDIT_FEATURE_DICTIONARY_AUDITED.csv'
    pd.DataFrame(result).to_csv(out,index=False)
    print(f'Wrote {out.name}: {len(result)} features, {len(df)} observations; source unchanged')
if __name__=='__main__':main()
