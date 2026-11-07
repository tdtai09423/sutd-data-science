# Model summary

Rolling-origin by week: expanding window from 2016, refit every 1 week(s), training rows purged so every label is known at the origin.
Development period: 2016-2021 (model comparison); target weeks in 2022 are reported separately below and do not guide model selection.
Alarm if P(surge) >= 0.20 (cost of a missed surge = 4 x a false alarm).
CI: 95% moving-block bootstrap (26-week blocks). p_better = share of bootstrap draws where the model beats the persistence baseline on PR-AUC.

# Development period

## surge_grow_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.255      0.154      0.396                      0.978    0.689  0.108      0.221   0.528           14.383         36 312
 random_forest[full]   0.247      0.145      0.420                      0.918    0.716  0.097      0.203   0.389           11.540         36 312
   poisson_glm[full]   0.213      0.137      0.306                      0.786    0.664  0.138      0.189   0.583           18.564         36 312
   lasso_logit[full]   0.207      0.118      0.353                      0.744    0.575  0.101      0.205   0.250            7.359         36 312
       seasonal[woy]   0.176      0.111      0.268                      0.692    0.570  0.103      0.138   0.111            4.850         36 312
persistence[persist]   0.168      0.092      0.295                      0.000    0.534  0.102      0.200   0.028            0.836         36 312
        logit[cases]   0.166      0.108      0.257                      0.454    0.633  0.108      0.167   0.278           10.035         36 312
         logit[full]   0.156      0.107      0.241                      0.446    0.602  0.136      0.195   0.472           14.550         36 312
       cart_d3[full]   0.137      0.094      0.212                      0.334    0.599  0.116      0.127   0.361           17.059         36 312
      logit[weather]   0.131      0.085      0.206                      0.234    0.557  0.143      0.143   0.389           16.390         36 312
          prior[woy]   0.111      0.070      0.173                      0.042    0.470  0.102      0.000   0.000            0.000         36 312
```

## surge_grow_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       seasonal[woy]   0.246      0.157      0.405                      0.872    0.593  0.127      0.233   0.362           12.248         47 311
ridge_logcount[full]   0.222      0.153      0.358                      0.844    0.611  0.149      0.210   0.447           16.778         47 311
   poisson_glm[full]   0.203      0.157      0.303                      0.790    0.604  0.195      0.201   0.617           24.161         47 311
 random_forest[full]   0.194      0.143      0.294                      0.690    0.629  0.129      0.216   0.532           19.463         47 311
   lasso_logit[full]   0.187      0.125      0.305                      0.608    0.565  0.135      0.200   0.426           16.778         47 311
persistence[persist]   0.173      0.121      0.264                      0.000    0.469  0.131      0.211   0.170            6.376         47 311
         logit[full]   0.163      0.116      0.247                      0.332    0.536  0.185      0.165   0.298           14.261         47 311
      logit[weather]   0.155      0.102      0.238                      0.256    0.513  0.176      0.150   0.362           18.959         47 311
        logit[cases]   0.154      0.119      0.230                      0.274    0.527  0.148      0.120   0.191           12.584         47 311
       cart_d3[full]   0.146      0.107      0.214                      0.102    0.463  0.158      0.133   0.277           16.443         47 311
          prior[woy]   0.131      0.083      0.197                      0.022    0.442  0.129      0.000   0.000            0.000         47 311
```

## surge_grow_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
   lasso_logit[full]   0.286      0.180      0.456                      0.984    0.623  0.134      0.230   0.510           19.082         51 309
       seasonal[woy]   0.268      0.165      0.481                      0.978    0.684  0.130      0.319   0.569           15.367         51 309
ridge_logcount[full]   0.253      0.152      0.464                      0.930    0.668  0.157      0.188   0.314           14.354         51 309
 random_forest[full]   0.246      0.166      0.361                      0.964    0.651  0.135      0.267   0.451           14.523         51 309
         logit[full]   0.245      0.161      0.431                      0.950    0.628  0.169      0.287   0.490           14.691         51 309
      logit[weather]   0.239      0.144      0.407                      0.928    0.606  0.163      0.260   0.529           17.562         51 309
       cart_d3[full]   0.197      0.118      0.296                      0.828    0.571  0.161      0.220   0.471           18.407         51 309
   poisson_glm[full]   0.194      0.138      0.293                      0.832    0.583  0.223      0.194   0.510           22.628         51 309
        logit[cases]   0.177      0.117      0.268                      0.674    0.560  0.166      0.115   0.176           13.172         51 309
persistence[persist]   0.156      0.089      0.237                      0.000    0.411  0.140      0.500   0.020            0.338         51 309
          prior[woy]   0.137      0.079      0.224                      0.240    0.431  0.139      0.000   0.000            0.000         51 309
```

## surge_seas_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.977      0.772      1.000                      0.702    0.996  0.020      0.746   1.000            9.867         44 312
   poisson_glm[full]   0.971      0.701      1.000                      0.664    0.995  0.020      0.733   1.000           10.035         44 312
persistence[persist]   0.970      0.718      1.000                      0.000    0.994  0.025      0.672   0.977           10.704         44 312
        logit[cases]   0.964      0.688      1.000                      0.249    0.991  0.022      0.712   0.955            9.867         44 312
 random_forest[full]   0.954      0.675      1.000                      0.128    0.986  0.026      0.732   0.932            9.366         44 312
   lasso_logit[full]   0.935      0.375      0.997                      0.008    0.987  0.033      0.581   0.977           12.376         44 312
       cart_d3[full]   0.933      0.476      0.990                      0.002    0.989  0.026      0.712   0.955            9.867         44 312
         logit[full]   0.894      0.245      1.000                      0.026    0.978  0.039      0.661   0.886            9.867         44 312
       seasonal[woy]   0.170      0.026      0.316                      0.000    0.592  0.128      0.152   0.273           13.212         44 312
      logit[weather]   0.156      0.022      0.320                      0.000    0.568  0.179      0.165   0.386           17.226         44 312
          prior[woy]   0.137      0.018      0.287                      0.000    0.486  0.123      0.083   0.023            2.007         44 312
```

## surge_seas_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
        logit[cases]   0.958      0.679      1.000                      0.724    0.989  0.025      0.672   0.953           10.235         43 311
ridge_logcount[full]   0.955      0.609      0.992                      0.524    0.992  0.026      0.729   1.000            9.899         43 311
   poisson_glm[full]   0.946      0.523      1.000                      0.438    0.991  0.028      0.683   1.000           10.570         43 311
 random_forest[full]   0.945      0.680      1.000                      0.685    0.985  0.030      0.702   0.930            9.564         43 311
persistence[persist]   0.942      0.625      0.992                      0.000    0.989  0.032      0.646   0.977           10.906         43 311
         logit[full]   0.897      0.351      0.990                      0.062    0.978  0.040      0.600   0.907           10.906         43 311
       cart_d3[full]   0.886      0.358      1.000                      0.151    0.972  0.033      0.651   0.953           10.570         43 311
   lasso_logit[full]   0.879      0.301      0.972                      0.012    0.975  0.045      0.545   0.977           12.919         43 311
      logit[weather]   0.148      0.022      0.288                      0.000    0.557  0.170      0.152   0.395           18.792         43 311
       seasonal[woy]   0.132      0.023      0.273                      0.000    0.493  0.134      0.120   0.209           12.584         43 311
          prior[woy]   0.122      0.015      0.288                      0.000    0.455  0.121      0.000   0.000            1.174         43 311
```

## surge_seas_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
         logit[full]   0.887      0.416      0.967                      0.891    0.970  0.057      0.522   0.878           11.652         41 309
ridge_logcount[full]   0.880      0.338      0.974                      0.925    0.979  0.042      0.667   0.927            9.625         41 309
        logit[cases]   0.869      0.354      0.951                      0.752    0.969  0.046      0.571   0.878           10.639         41 309
 random_forest[full]   0.866      0.530      0.960                      0.768    0.970  0.044      0.571   0.878           10.639         41 309
       cart_d3[full]   0.823      0.223      0.964                      0.770    0.961  0.058      0.494   0.927           13.003         41 309
   poisson_glm[full]   0.816      0.345      0.983                      0.710    0.972  0.047      0.576   0.927           11.145         41 309
persistence[persist]   0.802      0.230      0.950                      0.000    0.958  0.055      0.562   0.878           10.808         41 309
   lasso_logit[full]   0.764      0.156      0.930                      0.276    0.952  0.062      0.507   0.927           12.665         41 309
       seasonal[woy]   0.122      0.027      0.278                      0.000    0.476  0.130      0.088   0.146           11.483         41 309
      logit[weather]   0.121      0.020      0.245                      0.000    0.474  0.179      0.109   0.317           20.095         41 309
          prior[woy]   0.105      0.017      0.274                      0.000    0.401  0.119      0.000   0.000            0.000         41 309
```

## surge_seasonset_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.891      0.700      1.000                      0.998    0.995  0.010      0.333     1.0            2.931          5 267
   poisson_glm[full]   0.386      0.333      1.000                      0.981    0.980  0.022      0.263     1.0            3.713          5 267
persistence[persist]   0.259      0.146      0.567                      0.000    0.957  0.016      0.000     0.0            0.000          5 267
 random_forest[full]   0.194      0.108      0.500                      0.106    0.911  0.017      0.000     0.0            0.195          5 267
       cart_d3[full]   0.170      0.118      0.316                      0.004    0.952  0.016      0.190     0.8            4.104          5 267
        logit[cases]   0.160      0.122      0.500                      0.085    0.935  0.018      0.000     0.0            1.368          5 267
         logit[full]   0.128      0.079      0.277                      0.042    0.917  0.024      0.000     0.0            1.368          5 267
   lasso_logit[full]   0.090      0.043      0.203                      0.002    0.869  0.027      0.000     0.0            1.563          5 267
          prior[woy]   0.017      0.006      0.060                      0.000    0.361  0.018      0.000     0.0            0.000          5 267
      logit[weather]   0.016      0.008      0.048                      0.000    0.348  0.027      0.000     0.0            2.541          5 267
       seasonal[woy]   0.014      0.005      0.042                      0.000    0.241  0.019      0.000     0.0            0.000          5 267
```

## surge_seasonset_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.604      0.221      1.000                      0.992    0.987  0.015      0.353   1.000            3.335          6 266
 random_forest[full]   0.476      0.074      1.000                      0.915    0.940  0.019      0.308   0.667            2.550          6 266
        logit[cases]   0.401      0.102      1.000                      0.800    0.940  0.020      0.200   0.667            3.923          6 266
   poisson_glm[full]   0.285      0.156      1.000                      0.899    0.967  0.034      0.273   1.000            4.316          6 266
         logit[full]   0.205      0.058      0.833                      0.447    0.917  0.027      0.167   0.333            2.354          6 266
persistence[persist]   0.205      0.155      0.517                      0.000    0.950  0.019      0.000   0.000            0.392          6 266
       cart_d3[full]   0.101      0.060      0.221                      0.000    0.833  0.023      0.152   0.833            6.473          6 266
   lasso_logit[full]   0.097      0.037      0.311                      0.033    0.872  0.029      0.000   0.000            2.354          6 266
      logit[weather]   0.032      0.008      0.109                      0.000    0.535  0.029      0.000   0.000            2.746          6 266
          prior[woy]   0.017      0.006      0.048                      0.000    0.256  0.022      0.000   0.000            0.000          6 266
       seasonal[woy]   0.016      0.006      0.044                      0.000    0.199  0.025      0.000   0.000            0.000          6 266
```

## surge_seasonset_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.678      0.373      1.000                      1.000    0.983  0.022      0.500   0.909            3.953         11 264
       cart_d3[full]   0.646      0.147      1.000                      0.878    0.920  0.033      0.256   0.909            7.708         11 264
 random_forest[full]   0.596      0.285      0.888                      0.977    0.952  0.027      0.412   0.636            3.360         11 264
         logit[full]   0.581      0.217      0.807                      0.975    0.948  0.036      0.233   0.636            5.930         11 264
        logit[cases]   0.493      0.146      0.893                      0.872    0.947  0.034      0.292   0.636            4.744         11 264
   poisson_glm[full]   0.336      0.295      0.969                      0.973    0.951  0.048      0.312   0.909            6.325         11 264
persistence[persist]   0.235      0.177      0.489                      0.000    0.923  0.034      0.227   0.455            4.348         11 264
   lasso_logit[full]   0.215      0.079      0.616                      0.408    0.901  0.045      0.241   0.636            5.732         11 264
      logit[weather]   0.058      0.019      0.162                      0.000    0.522  0.060      0.029   0.091            6.918         11 264
       seasonal[woy]   0.031      0.011      0.091                      0.000    0.284  0.047      0.000   0.000            2.569         11 264
          prior[woy]   0.030      0.011      0.097                      0.000    0.274  0.041      0.000   0.000            0.000         11 264
```

## surge_thr_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
persistence[persist]   0.933      0.834      0.972                      0.000    0.986  0.035      0.656   0.930           10.202         43 312
   poisson_glm[full]   0.932      0.783      0.978                      0.366    0.983  0.039      0.615   0.930           10.871         43 312
ridge_logcount[full]   0.929      0.745      0.980                      0.322    0.983  0.034      0.645   0.930           10.369         43 312
        logit[cases]   0.924      0.794      0.974                      0.324    0.984  0.035      0.760   0.884            8.362         43 312
         logit[full]   0.888      0.746      0.950                      0.044    0.957  0.039      0.720   0.837            8.362         43 312
   lasso_logit[full]   0.875      0.739      0.938                      0.010    0.954  0.038      0.673   0.860            9.198         43 312
 random_forest[full]   0.839      0.658      0.942                      0.014    0.954  0.056      0.594   0.884           10.704         43 312
       cart_d3[full]   0.770      0.636      0.880                      0.006    0.951  0.046      0.612   0.953           11.205         43 312
      logit[weather]   0.342      0.112      0.612                      0.000    0.798  0.122      0.330   0.744           16.223         43 312
       seasonal[woy]   0.221      0.063      0.472                      0.000    0.716  0.115      0.206   0.302           10.536         43 312
          prior[woy]   0.127      0.039      0.308                      0.000    0.481  0.121      0.000   0.000            0.000         43 312
```

## surge_thr_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
persistence[persist]   0.887      0.668      0.947                      0.000    0.976  0.043      0.609   0.929           10.738         42 311
        logit[cases]   0.844      0.565      0.950                      0.190    0.973  0.047      0.706   0.857            8.557         42 311
   lasso_logit[full]   0.843      0.572      0.959                      0.356    0.974  0.045      0.549   0.929           11.912         42 311
ridge_logcount[full]   0.832      0.437      0.980                      0.296    0.973  0.044      0.621   0.976           11.074         42 311
   poisson_glm[full]   0.824      0.521      0.978                      0.294    0.973  0.052      0.562   0.976           12.248         42 311
 random_forest[full]   0.800      0.402      0.950                      0.096    0.939  0.063      0.538   0.833           10.906         42 311
         logit[full]   0.796      0.476      0.958                      0.278    0.963  0.052      0.625   0.833            9.396         42 311
       cart_d3[full]   0.730      0.401      0.852                      0.000    0.930  0.055      0.600   0.929           10.906         42 311
      logit[weather]   0.296      0.096      0.560                      0.000    0.781  0.135      0.309   0.690           15.771         42 311
       seasonal[woy]   0.181      0.057      0.385                      0.000    0.640  0.120      0.177   0.262           10.402         42 311
          prior[woy]   0.117      0.032      0.256                      0.000    0.450  0.119      0.000   0.000            0.000         42 311
```

## surge_thr_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
persistence[persist]   0.771      0.561      0.892                      0.000    0.952  0.060      0.585   0.864           10.976         44 309
   lasso_logit[full]   0.754      0.376      0.898                      0.517    0.946  0.063      0.559   0.864           11.483         44 309
 random_forest[full]   0.680      0.185      0.918                      0.255    0.882  0.080      0.532   0.750           10.470         44 309
        logit[cases]   0.677      0.380      0.851                      0.108    0.921  0.072      0.589   0.750            9.457         44 309
         logit[full]   0.641      0.264      0.878                      0.244    0.914  0.081      0.571   0.727            9.457         44 309
ridge_logcount[full]   0.625      0.196      0.965                      0.263    0.951  0.066      0.609   0.955           11.652         44 309
   poisson_glm[full]   0.549      0.206      0.919                      0.164    0.928  0.088      0.506   0.932           13.678         44 309
       cart_d3[full]   0.460      0.235      0.653                      0.002    0.876  0.090      0.549   0.886           11.990         44 309
      logit[weather]   0.241      0.058      0.511                      0.000    0.685  0.154      0.245   0.523           15.874         44 309
       seasonal[woy]   0.165      0.041      0.389                      0.000    0.587  0.129      0.162   0.250           11.483         44 309
          prior[woy]   0.115      0.030      0.273                      0.000    0.415  0.126      0.000   0.000            0.000         44 309
```

## surge_thronset_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
   poisson_glm[full]   0.322      0.041      0.803                      0.141    0.914  0.029      0.167   0.571            4.621          7 271
persistence[persist]   0.296      0.086      0.634                      0.000    0.933  0.023      0.000   0.000            0.000          7 271
         logit[full]   0.188      0.017      0.521                      0.014    0.741  0.028      0.091   0.143            2.118          7 271
        logit[cases]   0.184      0.038      0.376                      0.135    0.910  0.025      0.222   0.286            1.733          7 271
ridge_logcount[full]   0.154      0.045      0.945                      0.190    0.909  0.030      0.167   0.429            3.466          7 271
       cart_d3[full]   0.121      0.048      0.326                      0.002    0.855  0.023      0.161   0.714            5.969          7 271
 random_forest[full]   0.098      0.025      0.263                      0.010    0.796  0.025      0.000   0.000            0.963          7 271
   lasso_logit[full]   0.068      0.021      0.176                      0.000    0.780  0.026      0.000   0.000            1.540          7 271
       seasonal[woy]   0.028      0.011      0.070                      0.000    0.476  0.026      0.000   0.000            0.000          7 271
          prior[woy]   0.024      0.007      0.046                      0.000    0.351  0.025      0.000   0.000            0.000          7 271
      logit[weather]   0.021      0.007      0.047                      0.000    0.331  0.037      0.000   0.000            3.273          7 271
```

## surge_thronset_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
 random_forest[full]   0.245      0.013      0.673                      0.539    0.814  0.028      0.333   0.250            1.160          8 270
ridge_logcount[full]   0.243      0.038      0.885                      0.622    0.926  0.033      0.292   0.875            4.638          8 270
         logit[full]   0.226      0.017      0.717                      0.610    0.865  0.033      0.267   0.500            2.899          8 270
   poisson_glm[full]   0.205      0.041      0.893                      0.710    0.928  0.051      0.212   0.875            6.378          8 270
       cart_d3[full]   0.192      0.007      0.393                      0.419    0.874  0.026      0.188   0.750            6.184          8 270
persistence[persist]   0.188      0.046      0.450                      0.000    0.918  0.026      0.000   0.000            0.580          8 270
        logit[cases]   0.172      0.047      0.437                      0.461    0.910  0.029      0.182   0.250            2.126          8 270
   lasso_logit[full]   0.157      0.030      0.472                      0.364    0.891  0.033      0.188   0.375            3.092          8 270
      logit[weather]   0.047      0.008      0.144                      0.000    0.594  0.050      0.000   0.000            4.638          8 270
       seasonal[woy]   0.036      0.016      0.120                      0.048    0.484  0.031      0.000   0.000            0.387          8 270
          prior[woy]   0.021      0.008      0.050                      0.000    0.268  0.029      0.000   0.000            0.000          8 270
```

## surge_thronset_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.273      0.071      0.961                      0.863    0.939  0.053      0.345   0.833            5.646         12 268
   lasso_logit[full]   0.205      0.072      0.547                      0.713    0.869  0.052      0.292   0.583            4.673         12 268
 random_forest[full]   0.201      0.039      0.748                      0.552    0.748  0.041      0.200   0.167            1.947         12 268
         logit[full]   0.198      0.080      0.586                      0.653    0.874  0.057      0.188   0.250            3.115         12 268
   poisson_glm[full]   0.185      0.055      0.707                      0.638    0.896  0.084      0.225   0.750            7.788         12 268
       cart_d3[full]   0.178      0.089      0.355                      0.622    0.815  0.042      0.184   0.750            9.540         12 268
persistence[persist]   0.167      0.073      0.357                      0.000    0.877  0.040      0.118   0.167            3.310         12 268
        logit[cases]   0.167      0.063      0.377                      0.483    0.855  0.046      0.118   0.167            3.310         12 268
      logit[weather]   0.062      0.020      0.187                      0.018    0.590  0.077      0.059   0.167            6.620         12 268
       seasonal[woy]   0.048      0.012      0.138                      0.000    0.476  0.048      0.000   0.000            2.921         12 268
          prior[woy]   0.029      0.009      0.078                      0.000    0.217  0.044      0.000   0.000            0.000         12 268
```

# Final-period evaluation (target weeks in 2022): baselines + best development model

## surge_grow_h1 (selected on development: ridge_logcount[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
ridge_logcount[full]   0.313      0.031      0.482                      0.779    0.514  0.136      0.333   0.250            6.021          8 52
       seasonal[woy]   0.216      0.067      0.301                      0.468    0.591  0.130      0.250   0.125            4.014          8 52
persistence[persist]   0.144      0.048      0.295                      0.000    0.335  0.136      0.000   0.000            0.000          8 52
          prior[woy]   0.121      0.020      0.173                      0.000    0.266  0.132      0.000   0.000            0.000          8 52
```

## surge_grow_h2 (selected on development: ridge_logcount[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
ridge_logcount[full]   0.506      0.322      0.556                       1.00    0.777  0.180      0.500   0.167            4.014         12 52
       seasonal[woy]   0.433      0.167      0.470                       0.99    0.579  0.176      0.308   0.333           13.045         12 52
persistence[persist]   0.169      0.074      0.378                       0.00    0.238  0.187      0.000   0.000            0.000         12 52
          prior[woy]   0.159      0.055      0.318                       0.00    0.221  0.184      0.000   0.000            0.000         12 52
```

## surge_grow_h4 (selected on development: lasso_logit[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
   lasso_logit[full]   0.525      0.252      0.570                      1.000    0.792  0.204      0.474   0.562           19.066         16 52
       seasonal[woy]   0.384      0.251      0.500                      1.000    0.530  0.236      0.444   0.500           18.062         16 52
persistence[persist]   0.200      0.042      0.431                      0.000    0.153  0.235      0.000   0.000            0.000         16 52
          prior[woy]   0.197      0.041      0.439                      0.472    0.137  0.234      0.000   0.000            0.000         16 52
```

## surge_seas_h1 (selected on development: ridge_logcount[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
persistence[persist]   0.982      0.965      0.994                      0.000    0.982  0.077      0.771   1.000           35.121         27 52
ridge_logcount[full]   0.966      0.888      0.987                      0.000    0.972  0.048      0.900   1.000           30.104         27 52
       seasonal[woy]   0.689      0.615      0.945                      0.004    0.570  0.374      0.750   0.333           12.042         27 52
          prior[woy]   0.433      0.392      0.957                      0.000    0.384  0.379      0.000   0.000            0.000         27 52
```

## surge_seas_h2 (selected on development: logit[cases])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
persistence[persist]   0.955      0.930      0.992                      0.000    0.947  0.106      0.743   0.963           35.121         27 52
        logit[cases]   0.951      0.917      0.982                      0.000    0.957  0.076      0.897   0.963           29.100         27 52
       seasonal[woy]   0.661      0.548      0.942                      0.018    0.513  0.388      0.778   0.259            9.031         27 52
          prior[woy]   0.427      0.368      0.955                      0.000    0.361  0.382      0.000   0.000            0.000         27 52
```

## surge_seas_h4 (selected on development: logit[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
         logit[full]   0.947      0.920      0.987                      0.984    0.933  0.104      0.828   0.889           29.100         27 52
persistence[persist]   0.901      0.897      0.984                      0.000    0.880  0.165      0.686   0.889           35.121         27 52
       seasonal[woy]   0.672      0.620      0.942                      0.024    0.529  0.388      0.875   0.259            8.028         27 52
          prior[woy]   0.416      0.384      0.948                      0.000    0.326  0.388      0.000   0.000            0.000         27 52
```

## surge_seasonset_h1 (selected on development: ridge_logcount[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
ridge_logcount[full]   1.000      1.000      1.000                        1.0    1.000  0.021      0.667     1.0            6.262          2 25
       seasonal[woy]   0.833      0.833      0.833                        1.0    0.978  0.072      0.000     0.0            0.000          2 25
persistence[persist]   0.583      0.583      0.583                        0.0    0.957  0.063      0.000     0.0            0.000          2 25
          prior[woy]   0.076      0.076      0.076                        0.0    0.217  0.077      0.000     0.0            0.000          2 25
```

## surge_seasonset_h2 (selected on development: ridge_logcount[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
ridge_logcount[full]   0.758      0.758      0.758                        1.0    0.879  0.058        0.5   0.667            8.349          3 25
persistence[persist]   0.456      0.456      0.456                        0.0    0.788  0.094        0.5   0.333            4.174          3 25
       seasonal[woy]   0.453      0.453      0.453                        0.0    0.652  0.109        0.0   0.000            0.000          3 25
          prior[woy]   0.093      0.093      0.093                        0.0    0.152  0.114        0.0   0.000            0.000          3 25
```

## surge_seasonset_h4 (selected on development: ridge_logcount[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
ridge_logcount[full]   0.671      0.671      0.671                        1.0     0.84  0.120       0.40     0.4           10.436          5 25
       seasonal[woy]   0.508      0.508      0.508                        1.0     0.75  0.175       0.00     0.0            0.000          5 25
persistence[persist]   0.503      0.503      0.503                        0.0     0.69  0.160       0.25     0.4           16.698          5 25
          prior[woy]   0.136      0.136      0.136                        0.0     0.10  0.182       0.00     0.0            0.000          5 25
```

## surge_thr_h1 (selected on development: poisson_glm[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
persistence[persist]   0.985      0.982      1.000                      0.000    0.989  0.046      0.769    1.00           26.090         20 52
   poisson_glm[full]   0.969      0.963      1.000                      0.046    0.977  0.052      0.769    1.00           26.090         20 52
       seasonal[woy]   0.353      0.180      0.578                      0.000    0.475  0.323      0.312    0.25           16.055         20 52
          prior[woy]   0.256      0.067      0.639                      0.000    0.158  0.299      0.000    0.00            0.000         20 52
```

## surge_thr_h2 (selected on development: logit[cases])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
persistence[persist]   0.943      0.935      1.000                      0.000    0.956  0.084      0.731    0.95           26.090         20 52
        logit[cases]   0.929      0.926      1.000                      0.125    0.959  0.071      0.833    1.00           24.083         20 52
       seasonal[woy]   0.316      0.162      0.554                      0.000    0.355  0.334      0.286    0.20           14.048         20 52
          prior[woy]   0.255      0.053      0.629                      0.000    0.136  0.300      0.000    0.00            0.000         20 52
```

## surge_thr_h4 (selected on development: lasso_logit[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
persistence[persist]   0.967      0.953      1.000                        0.0    0.977  0.072      0.808   1.000           26.090         21 52
   lasso_logit[full]   0.938      0.921      1.000                        0.0    0.952  0.102      0.773   0.810           22.076         21 52
       seasonal[woy]   0.338      0.262      0.646                        0.0    0.375  0.338      0.294   0.238           17.059         21 52
          prior[woy]   0.266      0.081      0.744                        0.0    0.118  0.311      0.000   0.000            0.000         21 52
```

## surge_thronset_h1 (selected on development: poisson_glm[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
persistence[persist]   0.417      0.375      1.000                        0.0    0.919  0.048      0.000     0.0            0.000          2 33
   poisson_glm[full]   0.226      0.111      0.278                        0.0    0.839  0.062      0.167     0.5            9.487          2 33
       seasonal[woy]   0.106      0.127      0.500                        0.0    0.548  0.059      0.000     0.0            0.000          2 33
          prior[woy]   0.047      0.030      0.096                        0.0    0.032  0.058      0.000     0.0            0.000          2 33
```

## surge_thronset_h2 (selected on development: random_forest[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
persistence[persist]   0.548      0.576      0.910                        0.0    0.879  0.092       0.25    0.25            6.325          4 33
 random_forest[full]   0.317      0.242      0.437                        0.0    0.819  0.102       0.00    0.00            4.744          4 33
       seasonal[woy]   0.134      0.147      0.298                        0.0    0.474  0.119       0.00    0.00            0.000          4 33
          prior[woy]   0.089      0.075      0.192                        0.0    0.052  0.114       0.00    0.00            0.000          4 33
```

## surge_thronset_h4 (selected on development: ridge_logcount[full])
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives  n
persistence[persist]   0.768      0.768      0.862                        0.0    0.948  0.072      0.571     1.0           11.068          4 33
ridge_logcount[full]   0.685      0.655      0.798                        0.0    0.940  0.085      0.667     0.5            4.744          4 33
       seasonal[woy]   0.092      0.143      0.193                        0.0    0.190  0.124      0.000     0.0            0.000          4 33
          prior[woy]   0.078      0.122      0.162                        0.0    0.000  0.112      0.000     0.0            0.000          4 33
```

## count regression error (out-of-sample, cases)
```
          target                 model   mae   rmse
18  surge_thr_h1     poisson_glm[full]  36.9   67.4
19  surge_thr_h1  ridge_logcount[full]  33.0   59.6
20  surge_thr_h2     poisson_glm[full]  51.3   87.9
21  surge_thr_h2  ridge_logcount[full]  45.1   81.3
22  surge_thr_h4     poisson_glm[full]  80.4  138.7
23  surge_thr_h4  ridge_logcount[full]  66.2  125.1
```

## reporting-delay sensitivity (PR-AUC; delay=1: week t counts unknown)
```
                                    delay0  delay1
target        model                               
surge_grow_h1 lasso_logit[full]      0.207   0.187
              logit[cases]           0.166   0.155
              logit[full]            0.156   0.150
              logit[weather]         0.131   0.132
              persistence[persist]   0.168   0.116
              poisson_glm[full]      0.213   0.222
              seasonal[woy]          0.176   0.177
surge_seas_h1 lasso_logit[full]      0.935   0.891
              logit[cases]           0.964   0.960
              logit[full]            0.894   0.889
              logit[weather]         0.156   0.158
              persistence[persist]   0.970   0.941
              poisson_glm[full]      0.971   0.957
              seasonal[woy]          0.170   0.171
surge_thr_h1  lasso_logit[full]      0.875   0.876
              logit[cases]           0.924   0.840
              logit[full]            0.888   0.866
              logit[weather]         0.342   0.343
              persistence[persist]   0.933   0.891
              poisson_glm[full]      0.932   0.811
              seasonal[woy]          0.221   0.221
```

see tables/*.csv, tables/tree_rules.txt, figures/model_calibration.png, figures/model_best_*.png
