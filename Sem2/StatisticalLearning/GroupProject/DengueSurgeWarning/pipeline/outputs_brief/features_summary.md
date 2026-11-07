# Features summary

rows: 261
feature groups: cases=15, weather=44, full=57

target prevalence (share of weeks labelled surge) and n:
```
surge_thr_h1       prevalence=0.081  n=209  positives=17
surge_seas_h1      prevalence=0.098  n=163  positives=16
surge_grow_h1      prevalence=0.138  n=260  positives=36
surge_thronset_h1  prevalence=0.026  n=195  positives=5
surge_seasonset_h1 prevalence=0.007  n=145  positives=1
surge_thr_h2       prevalence=0.082  n=208  positives=17
surge_seas_h2      prevalence=0.098  n=163  positives=16
surge_grow_h2      prevalence=0.154  n=259  positives=40
surge_thronset_h2  prevalence=0.031  n=195  positives=6
surge_seasonset_h2 prevalence=0.007  n=143  positives=1
surge_thr_h4       prevalence=0.083  n=206  positives=17
surge_seas_h4      prevalence=0.098  n=163  positives=16
surge_grow_h4      prevalence=0.148  n=257  positives=38
surge_thronset_h4  prevalence=0.046  n=195  positives=9
surge_seasonset_h4 prevalence=0.007  n=139  positives=1
```

agreement between definitions (Jaccard of surge weeks, same horizon):
```
h=1  thr-seas=0.33  thr-grow=0.09  seas-grow=0.03
h=2  thr-seas=0.33  thr-grow=0.16  seas-grow=0.07
h=4  thr-seas=0.39  thr-grow=0.20  seas-grow=0.11
```

target series: `dengue_fever` (DHF kept separate; too rare to model on its own)
```
                 df   dhf  dhf_share_pct
week_start                              
2013          436.0   1.0           0.23
2014        17870.0  19.0           0.11
2015        11282.0  12.0           0.11
2016        13061.0  24.0           0.18
2017         2750.0  17.0           0.61
2018         3257.0  26.0           0.79
```
figure: features_targets.png
