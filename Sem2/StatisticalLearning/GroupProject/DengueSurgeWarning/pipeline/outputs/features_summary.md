# Features summary

rows: 574
feature groups: cases=13, weather=44, full=55

target prevalence (share of weeks labelled surge) and n:
```
surge_thr_h1       prevalence=0.186  n=522  positives=97
surge_grow_h1      prevalence=0.120  n=573  positives=69
surge_thr_h2       prevalence=0.186  n=521  positives=97
surge_grow_h2      prevalence=0.166  n=572  positives=95
surge_thr_h4       prevalence=0.197  n=519  positives=102
surge_grow_h4      prevalence=0.182  n=570  positives=104
```

agreement between definitions (same horizon):
```
h=1  Jaccard=0.11
grow  0.0  1.0
thr           
0.0   380   45
1.0    81   16

h=2  Jaccard=0.25
grow  0.0  1.0
thr           
0.0   376   48
1.0    61   36

h=4  Jaccard=0.32
grow  0.0  1.0
thr           
0.0   370   47
1.0    54   48

```
figure: features_targets.png
