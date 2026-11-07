# Build summary

case source: moh_weekly_bulletin
dengue series used: ['Dengue Fever', 'Dengue Haemorrhagic Fever']
duplicated epi weeks: 0
weeks: 574 (2012-01-02 -> 2022-12-26), epi weeks per year: {2012: 53, 2013: 52, 2014: 52, 2015: 52, 2016: 52, 2017: 52, 2018: 53, 2019: 52, 2020: 52, 2021: 52, 2022: 52}
weeks with missing cases: 0 []

cross-check against moh_dengue_dhf_2014_2018 on overlapping weeks (revisions between releases):
```
      series  overlap_weeks  identical_weeks  max_abs_diff  total_main  total_other
dengue_fever            261              209           8.0       48768      48656.0
         dhf            261              259           1.0         101         99.0
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

weeks with |week-on-week log change| > 0.5 (possible reporting artefacts): 7
```
week_start  cases  log_change
2014-02-17    194       -0.64
2015-02-16    100       -0.54
2015-02-23    172        0.54
2015-03-09    110       -0.54
2017-11-20     24       -0.71
2018-02-12     28       -0.56
2019-02-11    235        0.53
```
weather values outside plausible ranges {'rain_sum': (0, 600), 'temp_mean': (22, 32), 'temp_max': (24, 38), 'temp_min': (19, 30), 'rh_mean': (50, 100)}: {'rain_sum': 0, 'temp_mean': 0, 'temp_max': 0, 'temp_min': 0, 'rh_mean': 0}

missing values per column:
```
week_start      0
epi_week        0
dengue_fever    0
dhf             0
cases           0
rain_sum        1
rain_days       1
temp_mean       1
temp_max        1
temp_min        1
rh_mean         1
```

describe:
```
              count                 mean                  min                  25%                  50%                  75%                  max         std
week_start      574  2017-06-29 12:00:00  2012-01-02 00:00:00  2014-09-30 18:00:00  2017-06-29 12:00:00  2020-03-28 06:00:00  2022-12-26 00:00:00         NaN
dengue_fever  574.0           285.754355                 24.0                 81.0                208.0                372.0               1791.0  295.552225
dhf           574.0             0.738676                  0.0                  0.0                  0.0                  1.0                  8.0     1.07875
cases         574.0           286.493031                 24.0                81.25                210.0               373.75               1792.0   295.94164
rain_sum      573.0            37.849389                  0.0                  8.4                 28.4                 51.0                353.8   41.034577
rain_days     573.0             2.631763                  0.0                  1.0                  3.0                  4.0                  7.0    1.662683
temp_mean     573.0            27.968512                 24.5            27.414286            27.971429            28.528571            30.028571    0.869666
temp_max      573.0            31.628546                 26.7            31.057143            31.657143            32.285714            33.942857    1.002232
temp_min      573.0            25.383296            22.785714            24.742857            25.328571            25.928571            27.814286    0.877281
rh_mean       573.0            85.280479            72.428571            83.714286            85.714286            87.428571            91.571429    3.209816
```

yearly totals:
```
              sum   max   mean
week_start                    
2012         4766   151   89.9
2013        22497   842  432.6
2014        17889   891  344.0
2015        11303   458  217.4
2016        13179   636  253.4
2017         2776    91   53.4
2018         3492   207   65.9
2019        16094   663  309.5
2020        35012  1792  673.3
2021         5264   194  101.2
2022        32175  1567  618.8
```
