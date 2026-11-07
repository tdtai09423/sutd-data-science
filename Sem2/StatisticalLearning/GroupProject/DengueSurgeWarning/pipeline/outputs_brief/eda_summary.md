# EDA summary

yearly total / peak week:
```
                sum    max
week_start                
2013          437.0  437.0
2014        17889.0  891.0
2015        11294.0  457.0
2016        13085.0  637.0
2017         2767.0   91.0
2018         3283.0  160.0
```

strongest lag per weather var (by |corr|):
```
rain_sum   level: lag 19 r=-0.16 | growth4: lag  8 r=-0.22
rain_days  level: lag 19 r=-0.29 | growth4: lag  9 r=-0.22
temp_mean  level: lag 12 r=+0.25 | growth4: lag 19 r=-0.25
temp_max   level: lag 12 r=+0.29 | growth4: lag 19 r=-0.29
temp_min   level: lag  1 r=+0.22 | growth4: lag 19 r=-0.18
rh_mean    level: lag 19 r=-0.42 | growth4: lag 10 r=-0.29
```
NOTE: raw correlations are confounded by seasonality; treat as a guide only.

autocorrelation of log cases, lags 1..8: 0.97, 0.95, 0.93, 0.91, 0.89, 0.88, 0.85, 0.84

figures: eda_cases_timeseries.png, eda_cases_vs_weather.png, eda_lagged_corr.png, eda_seasonality.png
