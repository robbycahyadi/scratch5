import unittest
import numpy as np
import pandas as pd
from cghil_semantics import derive_semantic_columns, semantic_numeric, model_frame, round_counts, validate_semantics

class SemanticTests(unittest.TestCase):
    def test_dictionary(self):
        num, cat, count = derive_semantic_columns()
        self.assertEqual((len(num),len(cat),len(count)), (69,51,12))
        self.assertIn('OBS_60_CNT_SOCIAL_CIRCLE', count)
        self.assertNotIn('ELEVATORS_AVG', count)

    def test_sentinel_and_original_missing(self):
        raw=pd.DataFrame({'DAYS_EMPLOYED':[365243,-10,np.nan], 'AMT_CREDIT':[np.nan,1,2]})
        saved=raw.copy(deep=True)
        out=semantic_numeric(raw)
        self.assertTrue(pd.isna(out.iloc[0,0]))
        self.assertEqual(out.iloc[1,0],-10)
        pd.testing.assert_frame_equal(raw,saved)
        pd.testing.assert_series_equal(out.AMT_CREDIT, raw.AMT_CREDIT)

    def test_explicit_categories(self):
        raw=pd.DataFrame({'CODE_GENDER':['XNA',None,'F'], 'NAME_FAMILY_STATUS':['Unknown',None,'Married'], 'ORGANIZATION_TYPE':['XNA',None,'Other']})
        out=model_frame(raw,list(raw),list(raw))
        self.assertEqual(out.iloc[0].tolist(), ['XNA','Unknown','XNA'])
        self.assertEqual(out.iloc[1].tolist(), ['__MISSING__']*3)
        self.assertTrue(raw.iloc[1].isna().all())

    def test_round_counts_only(self):
        raw=pd.DataFrame({'CNT_CHILDREN':[-.2,.5,1.5,2.5], 'AMT_CREDIT':[1.2]*4, 'ELEVATORS_AVG':[.123]*4})
        out=round_counts(raw,['CNT_CHILDREN'])
        self.assertEqual(out.CNT_CHILDREN.tolist(),[0,0,2,2])
        pd.testing.assert_frame_equal(out.drop(columns='CNT_CHILDREN'),raw.drop(columns='CNT_CHILDREN'))
        self.assertEqual(raw.CNT_CHILDREN.iloc[0],-.2)

    def test_hard_and_potential(self):
        f=pd.DataFrame({'CNT_CHILDREN':[1.2,-1], 'OBS_30_CNT_SOCIAL_CIRCLE':[1,2], 'DEF_30_CNT_SOCIAL_CIRCLE':[2,1], 'DAYS_EMPLOYED':[365243,-3], 'FLAG_OWN_CAR':['N','bad'], 'OWN_CAR_AGE':[2,np.inf]})
        numeric=[c for c in f if c!='FLAG_OWN_CAR']
        v=validate_semantics(f,numeric,['FLAG_OWN_CAR'],['CNT_CHILDREN'],{'FLAG_OWN_CAR':{'Y','N'}})
        for rule in ['count_fractional','count_negative','DEF30_gt_OBS30','days_employed_positive','category_domain','numeric_nonfinite']:
            self.assertEqual(v[rule]['count'],1,rule)
            self.assertEqual(v[rule]['pct'],50)
            self.assertEqual(v[rule]['severity'],'hard')
        self.assertEqual(v['car_N_age_present']['severity'],'potential')
        self.assertEqual(v['car_N_age_present']['count'],1)

    def test_floating_noise(self):
        f=pd.DataFrame({'CNT_CHILDREN':[-1e-16]})
        v=validate_semantics(f,['CNT_CHILDREN'],[],['CNT_CHILDREN'],{})
        self.assertEqual(v['count_negative']['count'],0)
        self.assertEqual(round_counts(f,['CNT_CHILDREN']).iloc[0,0],0)

    def test_structural_missingness_synthetic_only(self):
        from cghil_semantics import synthetic_model_frame, assert_synthetic_model_numeric
        raw = pd.DataFrame({'FLAG_OWN_CAR':['N','Y','Y'], 'OWN_CAR_AGE':[4.,5.,6.],
                            'ORGANIZATION_TYPE':['Other','XNA','Other'], 'DAYS_EMPLOYED':[-3.,-4.,-5.]})
        saved = raw.copy(deep=True)
        cat = ['FLAG_OWN_CAR','ORGANIZATION_TYPE']
        num = ['OWN_CAR_AGE','DAYS_EMPLOYED']
        for method in ('M2','M3','M4'):
            out = synthetic_model_frame(raw,list(raw),cat)
            assert_synthetic_model_numeric(out,num)
            self.assertTrue(pd.isna(out.OWN_CAR_AGE.iloc[0]),method)
            self.assertTrue(pd.isna(out.DAYS_EMPLOYED.iloc[1]),method)
            self.assertEqual(out.OWN_CAR_AGE.iloc[1],5.)
            self.assertEqual(out.DAYS_EMPLOYED.iloc[0],-3.)
            pd.testing.assert_frame_equal(out,synthetic_model_frame(out,list(out),cat))
        pd.testing.assert_frame_equal(raw,saved)
        pd.testing.assert_frame_equal(model_frame(raw,list(raw),cat)[num],raw[num])

    def test_unexpected_missing_and_infinity_rejected(self):
        from cghil_semantics import synthetic_model_frame, assert_synthetic_model_numeric
        raw = pd.DataFrame({'FLAG_OWN_CAR':['Y'], 'OWN_CAR_AGE':[4.],
                            'ORGANIZATION_TYPE':['Other'], 'DAYS_EMPLOYED':[-3.]})
        num = ['OWN_CAR_AGE','DAYS_EMPLOYED']
        for bad in (np.nan,np.inf):
            out = synthetic_model_frame(raw,list(raw),['FLAG_OWN_CAR','ORGANIZATION_TYPE'])
            out.loc[0,'OWN_CAR_AGE'] = bad
            with self.assertRaises(AssertionError): assert_synthetic_model_numeric(out,num)

if __name__=='__main__': unittest.main()
