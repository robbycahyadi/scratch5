"""Audited Home Credit semantics; transformations never mutate their inputs.

Validation percentages use *all* rows, not just nonmissing observations.
Potential rules are warnings, not proof that an observation is invalid.
"""
from pathlib import Path
import csv

import numpy as np
import pandas as pd

MISSING_CATEGORY = "__MISSING__"
DICTIONARY_PATH = Path(__file__).with_name("HOME_CREDIT_FEATURE_DICTIONARY_AUDITED.csv")
RELATIVE_DAYS = ("DAYS_REGISTRATION", "DAYS_ID_PUBLISH", "DAYS_LAST_PHONE_CHANGE")


def derive_semantic_columns(features=None, dictionary_path=DICTIONARY_PATH):
    """Return (numeric, categorical, count_cols) in requested/dictionary order.

    Unknown requested features fail explicitly instead of guessing from dtype.
    """
    with open(dictionary_path, newline="", encoding="utf-8-sig") as stream:
        rows = {row["feature"]: row for row in csv.DictReader(stream)}
    features = list(rows) if features is None else list(features)
    unknown = set(features) - rows.keys()
    if unknown:
        raise ValueError(f"Features absent from audited dictionary: {sorted(unknown)}")
    categorical = [c for c in features if "categorical mask = True" in rows[c]["smotenc_recommendation"]]
    numeric = [c for c in features if c not in categorical]
    counts = [c for c in features if rows[c]["semantic_type_audited"] == "discrete count"]
    return numeric, categorical, counts


def semantic_numeric(frame):
    """Copy frame, replacing only the DAYS_EMPLOYED 365243 sentinel by NaN."""
    result = frame.copy(deep=True)
    if "DAYS_EMPLOYED" in result:
        result["DAYS_EMPLOYED"] = result["DAYS_EMPLOYED"].replace(365243, np.nan)
    return result


def model_frame(frame, features, categorical):
    """Select features, normalize employment sentinel, stringify categories only.

    Numeric missingness is intentionally retained for downstream train-only imputation.
    Explicit XNA and Unknown labels remain distinct from actual missing values.
    """
    result = semantic_numeric(frame.loc[:, list(features)])
    for col in categorical:
        if col in result:
            result[col] = result[col].astype("string").fillna(MISSING_CATEGORY).astype(object)
    return result


def round_counts(synthetic, count_cols):
    """Copy and apply only maximum(0, rint(x)) to selected counts (ties-to-even)."""
    result = synthetic.copy(deep=True)
    for col in count_cols:
        if col in result:
            result[col] = np.maximum(0, np.rint(result[col]))
    return result


def synthetic_model_frame(frame, features, categorical):
    """Shared M2/M3/M4 post-generation policy, never applied to originals.

    Empirical structural missingness, not an official interpretation of XNA.
    Call after inverse scaling/count correction and before shared model encoding.
    """
    result = model_frame(frame, features, categorical)
    result.loc[result['FLAG_OWN_CAR'].eq('N'), 'OWN_CAR_AGE'] = np.nan
    result.loc[result['ORGANIZATION_TYPE'].eq('XNA'), 'DAYS_EMPLOYED'] = np.nan
    return result


def assert_synthetic_model_numeric(frame, numeric):
    """Permit exactly the two intentional NaN masks; reject other NaN and inf."""
    expected = pd.DataFrame(False, index=frame.index, columns=numeric)
    expected['OWN_CAR_AGE'] = frame['FLAG_OWN_CAR'].eq('N')
    expected['DAYS_EMPLOYED'] = frame['ORGANIZATION_TYPE'].eq('XNA')
    assert frame[numeric].isna().equals(expected), 'Unexpected or absent structural NaN'
    values = frame[numeric].to_numpy(dtype=float)
    assert not np.isinf(values).any(), 'Infinite model numeric value'


def validate_semantics(frame, numeric, categorical, count_cols, allowed):
    """Return flat rule -> {severity, count, pct}, with row-wise union totals.

    ``allowed`` maps categorical names to domains in model string representation.
    Missing numeric values have a separate diagnostic, never nonfinite violations;
    callers evaluating generator output can promote numeric_missing to failure.
    Only rules whose prerequisite columns exist are evaluated. No age cutoff is used.
    """
    result = {}
    n = len(frame)
    false = pd.Series(False, index=frame.index)

    def add(name, mask, severity="hard"):
        count = int(pd.Series(mask, index=frame.index).fillna(False).sum())
        result[name] = {"severity": severity, "count": count,
                        "pct": 100.0 * count / n if n else 0.0}

    def num(col):
        return pd.to_numeric(frame[col], errors="raise").astype(float)

    domain = false.copy()
    for col in categorical:
        if col in frame:
            values = frame[col].astype("string").fillna(MISSING_CATEGORY)
            mask = ~values.isin({str(v) for v in allowed[col]})
            add(f"category_domain:{col}", mask)
            domain |= mask
    add("category_domain", domain)
    nonfinite, missing = false.copy(), false.copy()
    for col in numeric:
        if col in frame:
            values = num(col)
            nonfinite |= values.notna() & ~np.isfinite(values)
            missing |= values.isna()
    add("numeric_nonfinite", nonfinite)
    add("numeric_missing", missing, "diagnostic")
    fractional, negative = false.copy(), false.copy()
    for col in count_cols:
        if col in frame:
            values = num(col)
            finite = np.isfinite(values)
            with np.errstate(invalid="ignore"):
                frac = finite & ((values - np.rint(values)).abs() > 1e-8)
            neg = values < -1e-8
            add(f"count_fractional:{col}", frac)
            add(f"count_negative:{col}", neg)
            fractional |= frac
            negative |= neg
    add("count_fractional", fractional)
    add("count_negative", negative)
    for period in (30, 60):
        default, observed = f"DEF_{period}_CNT_SOCIAL_CIRCLE", f"OBS_{period}_CNT_SOCIAL_CIRCLE"
        if default in frame and observed in frame:
            add(f"DEF{period}_gt_OBS{period}", num(default) > num(observed))
    for col, name, zero_invalid in (("DAYS_EMPLOYED", "days_employed_positive", False),
                                    ("DAYS_BIRTH", "days_birth_nonnegative", True),
                                    ("OWN_CAR_AGE", "car_age_negative", False)):
        if col in frame:
            values = num(col)
            mask = values < 0 if col == "OWN_CAR_AGE" else (values >= 0 if zero_invalid else values > 0)
            add(name, mask)
    for col in RELATIVE_DAYS:
        if col in frame:
            add(f"relative_days_positive:{col}", num(col) > 0)
    if {"FLAG_OWN_CAR", "OWN_CAR_AGE"} <= set(frame):
        age = num("OWN_CAR_AGE")
        add("car_N_age_present", frame["FLAG_OWN_CAR"].eq("N") & age.notna(), "potential")
        add("car_Y_age_missing", frame["FLAG_OWN_CAR"].eq("Y") & age.isna(), "potential")
    if "ORGANIZATION_TYPE" in frame:
        xna = frame["ORGANIZATION_TYPE"].eq("XNA")
        org_present = frame["ORGANIZATION_TYPE"].notna() & ~frame["ORGANIZATION_TYPE"].eq(MISSING_CATEGORY)
        if "DAYS_EMPLOYED" in frame:
            add("organization_XNA_employed_present", xna & num("DAYS_EMPLOYED").notna(), "potential")
        if "NAME_INCOME_TYPE" in frame:
            add("pensioner_unemployed_nonXNA", frame["NAME_INCOME_TYPE"].isin(["Pensioner", "Unemployed"]) & org_present & ~xna, "potential")
        if "OCCUPATION_TYPE" in frame:
            occupation = frame["OCCUPATION_TYPE"]
            add("organization_XNA_occupation_present", xna & occupation.notna() & ~occupation.eq(MISSING_CATEGORY), "potential")
    if {"DAYS_EMPLOYED", "DAYS_BIRTH"} <= set(frame):
        add("employment_precedes_birth", num("DAYS_EMPLOYED") < num("DAYS_BIRTH"), "potential")
    if {"OWN_CAR_AGE", "DAYS_BIRTH"} <= set(frame):
        add("car_older_than_client", num("OWN_CAR_AGE") > -num("DAYS_BIRTH") / 365.25, "potential")
    return result
