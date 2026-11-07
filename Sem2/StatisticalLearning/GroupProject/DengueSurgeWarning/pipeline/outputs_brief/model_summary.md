# Model summary

Rolling-origin by week: expanding window from 2017, refit every 1 week(s), training rows purged so every label is known at the origin.
Development period: 2017-end (model comparison).
Alarm if P(surge) >= 0.20 (cost of a missed surge = 4 x a false alarm).
CI: 95% moving-block bootstrap (26-week blocks). p_better = share of bootstrap draws where the model beats the persistence baseline on PR-AUC.

# Development period

## surge_grow_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       seasonal[woy]   0.304      0.214      0.433                      0.836    0.559  0.172      0.500   0.095            2.026         21 103
ridge_logcount[full]   0.286      0.215      0.467                      0.998    0.661  0.204      0.324   0.571           18.744         21 103
       cart_d3[full]   0.271      0.164      0.381                      0.760    0.513  0.178      0.163   0.381           24.823         21 103
   poisson_glm[full]   0.251      0.222      0.400                      0.942    0.632  0.276      0.333   0.619           19.757         21 103
 random_forest[full]   0.248      0.202      0.381                      0.822    0.532  0.166      0.250   0.333           14.185         21 103
          prior[woy]   0.224      0.164      0.317                      0.586    0.527  0.172      0.000   0.000            0.000         21 103
persistence[persist]   0.220      0.161      0.370                      0.000    0.483  0.176      0.000   0.000            1.013         21 103
      logit[weather]   0.192      0.155      0.285                      0.306    0.496  0.273      0.156   0.238           16.211         21 103
   lasso_logit[full]   0.186      0.164      0.276                      0.354    0.462  0.203      0.154   0.286           19.757         21 103
         logit[full]   0.180      0.142      0.290                      0.158    0.456  0.288      0.097   0.143           15.705         21 103
        logit[cases]   0.173      0.140      0.302                      0.012    0.405  0.200      0.133   0.190           15.198         21 103
```

## surge_grow_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       seasonal[woy]   0.266      0.122      0.400                      0.660    0.505  0.155      0.250   0.211            8.185         19 102
      logit[weather]   0.215      0.140      0.381                      0.456    0.528  0.209      0.214   0.316           14.324         19 102
persistence[persist]   0.214      0.165      0.307                      0.000    0.501  0.155      0.143   0.053            3.581         19 102
         logit[full]   0.207      0.139      0.368                      0.368    0.517  0.230      0.243   0.474           18.928         19 102
 random_forest[full]   0.205      0.155      0.286                      0.330    0.554  0.157      0.188   0.316           16.370         19 102
       cart_d3[full]   0.198      0.132      0.252                      0.198    0.505  0.173      0.174   0.421           23.532         19 102
   poisson_glm[full]   0.187      0.144      0.237                      0.032    0.512  0.289      0.162   0.316           18.928         19 102
        logit[cases]   0.184      0.131      0.273                      0.070    0.464  0.186      0.218   0.632           28.136         19 102
          prior[woy]   0.180      0.121      0.210                      0.018    0.462  0.154      0.000   0.000            0.000         19 102
ridge_logcount[full]   0.174      0.119      0.253                      0.016    0.453  0.244      0.190   0.421           21.486         19 102
   lasso_logit[full]   0.164      0.101      0.313                      0.274    0.344  0.160      0.187   0.895           46.553         19 102
```

## surge_grow_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
 random_forest[full]   0.386      0.209      0.652                      0.904    0.615  0.152      0.263   0.263            9.914         19 100
       cart_d3[full]   0.304      0.175      0.428                      0.488    0.577  0.161      0.281   0.474           16.698         19 100
persistence[persist]   0.292      0.170      0.391                      0.000    0.516  0.160      0.500   0.053            1.044         19 100
       seasonal[woy]   0.243      0.117      0.294                      0.008    0.518  0.165      0.143   0.053            3.653         19 100
      logit[weather]   0.211      0.131      0.244                      0.030    0.523  0.221      0.190   0.211           10.958         19 100
         logit[full]   0.196      0.128      0.287                      0.026    0.491  0.248      0.222   0.316           14.089         19 100
          prior[woy]   0.195      0.103      0.196                      0.000    0.486  0.161      0.000   0.000            0.000         19 100
   lasso_logit[full]   0.178      0.111      0.253                      0.036    0.413  0.170      0.179   0.263           14.610         19 100
   poisson_glm[full]   0.177      0.128      0.240                      0.042    0.475  0.379      0.146   0.316           21.394         19 100
ridge_logcount[full]   0.165      0.110      0.223                      0.004    0.433  0.277      0.111   0.211           18.785         19 100
        logit[cases]   0.162      0.112      0.195                      0.002    0.421  0.207      0.140   0.316           22.437         19 100
```

## surge_seas_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       cart_d3[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
   lasso_logit[full]     NaN        NaN        NaN                        NaN      NaN  0.005        0.0     0.0            2.026          0 103
        logit[cases]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
         logit[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
      logit[weather]     NaN        NaN        NaN                        NaN      NaN  0.043        0.0     0.0           10.132          0 103
persistence[persist]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
   poisson_glm[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
          prior[woy]     NaN        NaN        NaN                        NaN      NaN  0.025        0.0     0.0            9.625          0 103
 random_forest[full]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.000          0 103
ridge_logcount[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
       seasonal[woy]     NaN        NaN        NaN                        NaN      NaN  0.054        0.0     0.0           14.185          0 103
```

## surge_seas_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       cart_d3[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
   lasso_logit[full]     NaN        NaN        NaN                        NaN      NaN  0.010        0.0     0.0            3.069          0 102
        logit[cases]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
         logit[full]     NaN        NaN        NaN                        NaN      NaN  0.002        0.0     0.0            1.023          0 102
      logit[weather]     NaN        NaN        NaN                        NaN      NaN  0.055        0.0     0.0           10.231          0 102
persistence[persist]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
   poisson_glm[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
          prior[woy]     NaN        NaN        NaN                        NaN      NaN  0.026        0.0     0.0           10.743          0 102
 random_forest[full]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.000          0 102
ridge_logcount[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
       seasonal[woy]     NaN        NaN        NaN                        NaN      NaN  0.063        0.0     0.0           14.835          0 102
```

## surge_seas_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       cart_d3[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
   lasso_logit[full]     NaN        NaN        NaN                        NaN      NaN  0.025        0.0     0.0            6.262          0 100
        logit[cases]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
         logit[full]     NaN        NaN        NaN                        NaN      NaN  0.007        0.0     0.0            0.522          0 100
      logit[weather]     NaN        NaN        NaN                        NaN      NaN  0.096        0.0     0.0           13.567          0 100
persistence[persist]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
   poisson_glm[full]     NaN        NaN        NaN                        NaN      NaN  0.003        0.0     0.0            1.044          0 100
          prior[woy]     NaN        NaN        NaN                        NaN      NaN  0.022        0.0     0.0            7.827          0 100
 random_forest[full]     NaN        NaN        NaN                        NaN      NaN  0.003        0.0     0.0            0.000          0 100
ridge_logcount[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
       seasonal[woy]     NaN        NaN        NaN                        NaN      NaN  0.056        0.0     0.0           13.045          0 100
```

## surge_seasonset_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       cart_d3[full]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.000          0 103
   lasso_logit[full]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.000          0 103
        logit[cases]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
         logit[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
      logit[weather]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.507          0 103
persistence[persist]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
   poisson_glm[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
          prior[woy]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
 random_forest[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
ridge_logcount[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 103
       seasonal[woy]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.000          0 103
```

## surge_seasonset_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       cart_d3[full]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.000          0 102
   lasso_logit[full]     NaN        NaN        NaN                        NaN      NaN  0.002        0.0     0.0            0.512          0 102
        logit[cases]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
         logit[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
      logit[weather]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.512          0 102
persistence[persist]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
   poisson_glm[full]     NaN        NaN        NaN                        NaN      NaN  0.010        0.0     0.0            0.512          0 102
          prior[woy]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
 random_forest[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
ridge_logcount[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 102
       seasonal[woy]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.000          0 102
```

## surge_seasonset_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       cart_d3[full]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.000          0 100
   lasso_logit[full]     NaN        NaN        NaN                        NaN      NaN  0.003        0.0     0.0            0.522          0 100
        logit[cases]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
         logit[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
      logit[weather]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.522          0 100
persistence[persist]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
   poisson_glm[full]     NaN        NaN        NaN                        NaN      NaN  0.010        0.0     0.0            0.522          0 100
          prior[woy]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
 random_forest[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
ridge_logcount[full]     NaN        NaN        NaN                        NaN      NaN  0.000        0.0     0.0            0.000          0 100
       seasonal[woy]     NaN        NaN        NaN                        NaN      NaN  0.001        0.0     0.0            0.000          0 100
```

## surge_thr_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
         logit[full]   0.803      0.144      0.768                      0.919    0.918  0.027      0.833   0.714            3.040          7 103
persistence[persist]   0.786      0.067      0.786                      0.000    0.972  0.041      0.400   0.857            7.599          7 103
        logit[cases]   0.767      0.100      0.756                      0.416    0.973  0.037      0.800   0.571            2.533          7 103
 random_forest[full]   0.726      0.125      0.708                      0.774    0.917  0.048      1.000   0.429            1.520          7 103
      logit[weather]   0.572      0.109      1.000                      0.837    0.802  0.049      0.250   0.571            8.106          7 103
   poisson_glm[full]   0.552      0.017      0.555                      0.000    0.906  0.069      0.312   0.714            8.106          7 103
ridge_logcount[full]   0.510      0.017      0.508                      0.000    0.896  0.072      0.250   0.714           10.132          7 103
   lasso_logit[full]   0.432      0.071      0.500                      0.430    0.917  0.048      0.556   0.714            4.559          7 103
       cart_d3[full]   0.297      0.010      0.170                      0.000    0.804  0.060      0.273   0.857           11.145          7 103
       seasonal[woy]   0.159      0.051      0.500                      0.684    0.626  0.063      0.214   0.429            7.092          7 103
          prior[woy]   0.049      0.010      0.051                      0.000    0.245  0.066      0.000   0.000            0.000          7 103
```

## surge_thr_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
persistence[persist]   0.656      0.020      0.579                      0.000    0.914  0.049      0.308   0.571            6.650          7 102
         logit[full]   0.600      0.024      0.553                      0.416    0.898  0.043      0.667   0.571            3.069          7 102
 random_forest[full]   0.576      0.043      0.518                      0.731    0.792  0.055      1.000   0.286            1.023          7 102
        logit[cases]   0.539      0.100      0.530                      0.930    0.958  0.049      0.429   0.429            3.581          7 102
       cart_d3[full]   0.434      0.010      0.305                      0.014    0.739  0.057      0.273   0.429            5.627          7 102
   lasso_logit[full]   0.374      0.100      0.363                      0.855    0.895  0.052      0.444   0.571            4.604          7 102
      logit[weather]   0.316      0.042      0.313                      0.699    0.732  0.060      0.200   0.286            5.116          7 102
ridge_logcount[full]   0.248      0.017      0.171                      0.034    0.848  0.091      0.238   0.714           10.743          7 102
   poisson_glm[full]   0.234      0.018      0.171                      0.319    0.848  0.104      0.217   0.714           11.766          7 102
       seasonal[woy]   0.099      0.020      0.428                      0.828    0.403  0.068      0.100   0.143            5.116          7 102
          prior[woy]   0.045      0.010      0.048                      0.041    0.179  0.066      0.000   0.000            0.000          7 102
```

## surge_thr_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
persistence[persist]   0.471      0.062      0.371                      0.000    0.920  0.047      0.500   0.333            2.087          6 100
         logit[full]   0.466      0.027      0.388                      0.486    0.793  0.053      1.000   0.167            0.522          6 100
        logit[cases]   0.348      0.061      1.000                      0.624    0.926  0.054      0.333   0.167            1.565          6 100
      logit[weather]   0.231      0.023      0.368                      0.385    0.550  0.060      0.125   0.167            4.174          6 100
       cart_d3[full]   0.217      0.010      0.060                      0.000    0.504  0.070      0.053   0.167            9.914          6 100
   lasso_logit[full]   0.210      0.022      0.432                      0.211    0.801  0.060      0.286   0.333            3.653          6 100
 random_forest[full]   0.172      0.031      0.169                      0.037    0.594  0.056      0.000   0.000            0.000          6 100
ridge_logcount[full]   0.169      0.034      0.164                      0.009    0.828  0.129      0.227   0.833           11.480          6 100
   poisson_glm[full]   0.157      0.032      0.167                      0.018    0.814  0.166      0.200   0.833           13.045          6 100
          prior[woy]   0.036      0.010      0.038                      0.000    0.029  0.059      0.000   0.000            0.000          6 100
       seasonal[woy]   0.036      0.010      0.038                      0.000    0.029  0.067      0.000   0.000            4.696          6 100
```

## surge_thronset_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
        logit[cases]   0.159      0.028      0.100                      0.000    0.844  0.021        0.0     0.0            0.532          2 98
persistence[persist]   0.111      0.077      0.298                      0.000    0.849  0.020        0.0     0.0            0.000          2 98
 random_forest[full]   0.074      0.032      0.286                      0.057    0.807  0.020        0.0     0.0            0.000          2 98
   poisson_glm[full]   0.060      0.015      0.143                      0.000    0.740  0.071        0.0     0.0            7.454          2 98
ridge_logcount[full]   0.060      0.014      0.100                      0.000    0.724  0.061        0.0     0.0            6.922          2 98
       seasonal[woy]   0.056      0.077      0.250                      0.327    0.448  0.020        0.0     0.0            0.000          2 98
         logit[full]   0.047      0.042      0.133                      0.000    0.651  0.021        0.0     0.0            0.532          2 98
   lasso_logit[full]   0.041      0.036      0.111                      0.000    0.490  0.025        0.0     0.0            0.532          2 98
       cart_d3[full]   0.027      0.010      0.031                      0.000    0.602  0.024        0.0     0.0            0.000          2 98
      logit[weather]   0.025      0.022      0.087                      0.000    0.354  0.021        0.0     0.0            0.000          2 98
          prior[woy]   0.016      0.010      0.032                      0.000    0.023  0.020        0.0     0.0            0.000          2 98
```

## surge_thronset_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
        logit[cases]   0.222      0.067      0.171                      1.000    0.926  0.030      0.000   0.000            0.532          3 98
       seasonal[woy]   0.184      0.260      0.706                      0.981    0.337  0.029      0.000   0.000            0.000          3 98
ridge_logcount[full]   0.088      0.015      0.099                      0.481    0.758  0.071      0.059   0.333            9.052          3 98
   poisson_glm[full]   0.078      0.014      0.085                      0.111    0.723  0.099      0.059   0.333            9.052          3 98
 random_forest[full]   0.073      0.023      0.145                      0.908    0.709  0.030      0.000   0.000            0.000          3 98
         logit[full]   0.061      0.013      0.051                      0.040    0.649  0.033      0.000   0.000            0.532          3 98
persistence[persist]   0.060      0.017      0.087                      0.000    0.684  0.030      0.000   0.000            0.000          3 98
   lasso_logit[full]   0.052      0.022      0.077                      0.640    0.596  0.035      0.000   0.000            0.532          3 98
      logit[weather]   0.032      0.014      0.048                      0.026    0.382  0.034      0.000   0.000            1.065          3 98
       cart_d3[full]   0.032      0.023      0.111                      0.673    0.500  0.031      0.000   0.000            0.000          3 98
          prior[woy]   0.025      0.010      0.033                      0.000    0.202  0.030      0.000   0.000            0.000          3 98
```

## surge_thronset_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
         logit[full]   0.253      0.070      0.447                      1.000    0.779  0.040      0.000    0.00            0.000          4 98
        logit[cases]   0.213      0.065      1.000                      1.000    0.907  0.040      0.000    0.00            0.000          4 98
   lasso_logit[full]   0.157      0.015      0.364                      0.352    0.476  0.039      0.000    0.00            0.000          4 98
      logit[weather]   0.157      0.067      0.250                      1.000    0.598  0.040      0.000    0.00            0.000          4 98
ridge_logcount[full]   0.118      0.030      0.147                      0.944    0.803  0.114      0.118    0.50            9.052          4 98
   poisson_glm[full]   0.093      0.024      0.109                      0.907    0.750  0.180      0.111    0.75           14.376          4 98
persistence[persist]   0.071      0.020      0.080                      0.000    0.665  0.040      0.000    0.00            0.000          4 98
 random_forest[full]   0.051      0.023      0.056                      0.352    0.527  0.040      0.000    0.00            0.000          4 98
       cart_d3[full]   0.038      0.010      0.038                      0.000    0.449  0.041      0.000    0.00            0.000          4 98
          prior[woy]   0.026      0.010      0.026                      0.000    0.000  0.040      0.000    0.00            0.000          4 98
       seasonal[woy]   0.026      0.010      0.026                      0.000    0.000  0.041      0.000    0.00            0.000          4 98
```

## count regression error (out-of-sample, cases)
```
          target                 model   mae   rmse
18  surge_thr_h1     poisson_glm[full]  19.0   31.2
19  surge_thr_h1  ridge_logcount[full]  13.0   16.7
20  surge_thr_h2     poisson_glm[full]  25.3   41.3
21  surge_thr_h2  ridge_logcount[full]  17.8   22.8
22  surge_thr_h4     poisson_glm[full]  57.0  113.2
23  surge_thr_h4  ridge_logcount[full]  27.8   35.7
```

see tables/*.csv, tables/tree_rules.txt, figures/model_calibration.png, figures/model_best_*.png
