# Build summary

case source: moh_dengue_dhf_2014_2018
dengue series used: ['DHF', 'Dengue']
duplicated epi weeks: 0
weeks: 261 (2013-12-30 -> 2018-12-24), epi weeks per year: {2013: 1, 2014: 52, 2015: 52, 2016: 52, 2017: 52, 2018: 52}
weeks with missing cases: 0 []

cross-check against moh_weekly_bulletin on overlapping weeks (revisions between releases):
```
      series  overlap_weeks  identical_weeks  max_abs_diff  total_main  total_other
dengue_fever            261              209           8.0     48656.0        48768
         dhf            261              259           1.0        99.0          101
```
weather source: MSS station S24 (rain, temperature) 2011-06-01 -> 2022-12-31, 4232 days; humidity: open_meteo
MSS missing days per variable: rain=0, temp_mean=0, temp_max=0, temp_min=0

weather cross-checks (corr, mean difference second - first):
```
                               check   n  corr  mean_diff
  weekly rain_sum: MSS vs Open-Meteo 603 0.482     17.627
 weekly temp_mean: MSS vs Open-Meteo 603 0.908     -1.334
  weekly temp_max: MSS vs Open-Meteo 603 0.751     -2.508
  weekly temp_min: MSS vs Open-Meteo 603 0.673     -0.709
monthly RH: Open-Meteo vs NEA Changi 139 0.562      5.825
```
weather weeks: 603 (2011-06-06 -> 2022-12-19)

weeks with |week-on-week log change| > 0.5 (possible reporting artefacts): 6
```
week_start  cases  log_change
2014-02-17  194.0       -0.64
2015-02-16   99.0       -0.55
2015-02-23  172.0        0.55
2015-03-09  110.0       -0.54
2017-11-20   24.0       -0.71
2018-02-12   28.0       -0.56
```
weather values outside plausible ranges {'rain_sum': (0, 600), 'temp_mean': (22, 32), 'temp_max': (24, 38), 'temp_min': (19, 30), 'rh_mean': (50, 100)}: {'rain_sum': 0, 'temp_mean': 0, 'temp_max': 0, 'temp_min': 0, 'rh_mean': 0}

missing values per column:
```
week_start      0
epi_week        0
dengue_fever    0
dhf             0
cases           0
rain_sum        0
rain_days       0
temp_mean       0
temp_max        0
temp_min        0
rh_mean         0
```

describe:
```
              count                 mean                  min                  25%                  50%                  75%                  max         std
week_start      261  2016-06-27 00:00:00  2013-12-30 00:00:00  2015-03-30 00:00:00  2016-06-27 00:00:00  2017-09-25 00:00:00  2018-12-24 00:00:00         NaN
dengue_fever  261.0           186.421456                 24.0                 60.0                157.0                250.0                888.0  158.706595
dhf           261.0              0.37931                  0.0                  0.0                  0.0                  1.0                  4.0    0.654712
cases         261.0           186.800766                 24.0                 62.0                158.0                250.0                891.0  158.826461
rain_sum      261.0            32.571264                  0.0                  6.4                 24.0                 45.8                177.4   34.239278
rain_days     261.0              2.51341                  0.0                  1.0                  2.0                  4.0                  7.0    1.702038
temp_mean     261.0            28.032512                 24.5            27.428571            28.085714            28.657143                 29.9    0.901549
temp_max      261.0            31.634428                 26.7            31.057143            31.657143                 32.3                 33.8    1.016716
temp_min      261.0            25.488506            22.785714            24.771429            25.457143            26.171429            27.814286     0.92756
rh_mean       261.0            84.889984            72.428571            83.142857            85.428571            86.857143            91.428571    3.169891
```

yearly totals:
```
                sum    max   mean
week_start                       
2013          437.0  437.0  437.0
2014        17889.0  891.0  344.0
2015        11294.0  457.0  217.2
2016        13085.0  637.0  251.6
2017         2767.0   91.0   53.2
2018         3283.0  160.0   63.1
```
