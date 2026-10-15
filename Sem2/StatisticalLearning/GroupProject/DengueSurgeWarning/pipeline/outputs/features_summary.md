# Features summary

rows: 574
feature groups: cases=15, weather=44, full=57

target prevalence (share of weeks labelled surge) and n:
```
surge_thr_h1       prevalence=0.186  n=522  positives=97
surge_seas_h1      prevalence=0.185  n=471  positives=87
surge_grow_h1      prevalence=0.120  n=573  positives=69
surge_thronset_h1  prevalence=0.032  n=431  positives=14
surge_seasonset_h1 prevalence=0.026  n=383  positives=10
surge_thr_h2       prevalence=0.186  n=521  positives=97
surge_seas_h2      prevalence=0.185  n=471  positives=87
surge_grow_h2      prevalence=0.166  n=572  positives=95
surge_thronset_h2  prevalence=0.047  n=430  positives=20
surge_seasonset_h2 prevalence=0.037  n=382  positives=14
surge_thr_h4       prevalence=0.195  n=519  positives=101
surge_seas_h4      prevalence=0.185  n=471  positives=87
surge_grow_h4      prevalence=0.179  n=570  positives=102
surge_thronset_h4  prevalence=0.063  n=428  positives=27
surge_seasonset_h4 prevalence=0.063  n=380  positives=24
```

agreement between definitions (Jaccard of surge weeks, same horizon):
```
h=1  thr-seas=0.31  thr-grow=0.11  seas-grow=0.05
h=2  thr-seas=0.31  thr-grow=0.25  seas-grow=0.11
h=4  thr-seas=0.38  thr-grow=0.32  seas-grow=0.16
```

target series: `dengue_fever` (DHF kept separate; too rare to model on its own)
```
               df  dhf  dhf_share_pct
week_start                           
2012         4734   32           0.67
2013        22405   92           0.41
2014        17870   19           0.11
2015        11291   12           0.11
2016        13153   26           0.20
2017         2759   17           0.61
2018         3464   28           0.80
2019        16007   87           0.54
2020        34959   53           0.15
2021         5251   13           0.25
2022        32130   45           0.14
```
figure: features_targets.png
