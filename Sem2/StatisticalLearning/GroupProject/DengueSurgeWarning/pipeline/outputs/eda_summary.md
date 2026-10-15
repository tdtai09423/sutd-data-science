# EDA summary

yearly total / peak week:
```
              sum   max
week_start             
2012         4766   151
2013        22497   842
2014        17889   891
2015        11303   458
2016        13179   636
2017         2776    91
2018         3492   207
2019        16094   663
2020        35012  1792
2021         5264   194
2022        32175  1567
```

strongest lag per weather var (by |corr|):
```
rain_sum   level: lag 19 r=-0.12 | growth4: lag 11 r=-0.21
rain_days  level: lag 19 r=-0.23 | growth4: lag 11 r=-0.25
temp_mean  level: lag  9 r=+0.15 | growth4: lag 19 r=-0.21
temp_max   level: lag 15 r=+0.22 | growth4: lag  7 r=+0.25
temp_min   level: lag  2 r=+0.19 | growth4: lag 12 r=-0.25
rh_mean    level: lag 19 r=-0.20 | growth4: lag 10 r=-0.25
```
NOTE: raw correlations are confounded by seasonality; treat as a guide only.

autocorrelation of log cases, lags 1..8: 0.98, 0.96, 0.94, 0.92, 0.90, 0.87, 0.85, 0.82

figures: eda_cases_timeseries.png, eda_cases_vs_weather.png, eda_lagged_corr.png, eda_seasonality.png
