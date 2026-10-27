"""Run only when the dependencies in requirements.txt are installed."""
import numpy as np
from credit_engine import load_artifacts, numeric_medians, predict_risk

p,m=load_artifacts()
med=numeric_medians(p)
form=dict(age=27,children=0,employment_years=5,code_gender=np.nan,
          own_car=False,own_realty=True,
          ai_income=med['AMT_INCOME_TOTAL'],ai_credit=med['AMT_CREDIT'],
          ai_annuity=med['AMT_ANNUITY'],ext_source_1=np.nan,
          ext_source_2=np.nan,ext_source_3=np.nan)
risk,raw=predict_risk(p,m,form)
print('DU LIEU THO:',raw.shape)
print('DU LIEU SAU TIEN XU LY:',p.transform(raw).shape)
print('MODEL:',type(m).__name__)
print('P_risk:',f'{risk:.3%}')
print('Mô hình chạy thành công; kết quả phục vụ demo, không phục vụ tín dụng thật.')
