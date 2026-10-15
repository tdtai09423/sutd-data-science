# Model summary

Rolling-origin by week: expanding window from 2017, refit every 4 week(s), training rows purged so every label is known at the origin.
Alarm if P(surge) >= 0.20 (cost of a missed surge = 4 x a false alarm).
CI: 95% moving-block bootstrap (26-week blocks). p_better = share of bootstrap draws where the model beats the persistence baseline on PR-AUC.

## surge_grow_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.259      0.192      0.419                      0.970    0.653  0.117      0.263   0.476           12.711         42 312
   lasso_logit[full]   0.225      0.151      0.396                      0.890    0.627  0.113      0.233   0.238            7.191         42 312
         logit[full]   0.215      0.159      0.363                      0.868    0.590  0.129      0.246   0.357           10.202         42 312
 random_forest[full]   0.208      0.137      0.330                      0.758    0.603  0.115      0.176   0.286           11.373         42 312
   poisson_glm[full]   0.201      0.146      0.327                      0.774    0.623  0.147      0.183   0.524           20.069         42 312
       seasonal[woy]   0.181      0.128      0.267                      0.622    0.547  0.118      0.192   0.119            4.348         42 312
        logit[cases]   0.180      0.127      0.354                      0.622    0.631  0.124      0.191   0.214            7.860         42 312
persistence[persist]   0.166      0.101      0.337                      0.000    0.467  0.118      0.000   0.000            0.669         42 312
      logit[weather]   0.146      0.096      0.220                      0.310    0.504  0.143      0.125   0.286           16.055         42 312
       cart_d3[full]   0.145      0.095      0.204                      0.214    0.511  0.134      0.146   0.310           14.885         42 312
          prior[woy]   0.119      0.078      0.184                      0.012    0.430  0.117      0.000   0.000            0.000         42 312
```

## surge_grow_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       seasonal[woy]   0.279      0.177      0.437                      0.918    0.600  0.143      0.257   0.345           12.416         55 311
 random_forest[full]   0.274      0.203      0.406                      0.960    0.697  0.138      0.280   0.600           19.798         55 311
   lasso_logit[full]   0.253      0.182      0.379                      0.912    0.621  0.148      0.256   0.564           20.302         55 311
   poisson_glm[full]   0.241      0.185      0.402                      0.886    0.651  0.197      0.265   0.655           22.818         55 311
ridge_logcount[full]   0.237      0.174      0.404                      0.834    0.614  0.171      0.263   0.473           16.610         55 311
         logit[full]   0.235      0.181      0.361                      0.858    0.609  0.178      0.266   0.455           15.771         55 311
      logit[weather]   0.226      0.157      0.349                      0.768    0.581  0.178      0.250   0.564           20.805         55 311
       cart_d3[full]   0.218      0.140      0.351                      0.684    0.572  0.161      0.271   0.418           14.261         55 311
        logit[cases]   0.214      0.168      0.342                      0.668    0.620  0.158      0.221   0.309           12.919         55 311
persistence[persist]   0.191      0.134      0.282                      0.000    0.440  0.149      0.280   0.127            4.195         55 311
          prior[woy]   0.146      0.095      0.238                      0.022    0.415  0.147      0.000   0.000            0.000         55 311
```

## surge_grow_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
       seasonal[woy]   0.337      0.236      0.491                      0.996    0.654  0.160      0.383   0.554           15.874         65 309
   lasso_logit[full]   0.331      0.205      0.485                      0.964    0.662  0.160      0.318   0.631           21.784         65 309
      logit[weather]   0.315      0.191      0.480                      0.974    0.629  0.184      0.285   0.600           23.135         65 309
 random_forest[full]   0.298      0.208      0.423                      0.972    0.670  0.161      0.361   0.600           18.238         65 309
         logit[full]   0.292      0.211      0.466                      0.980    0.631  0.198      0.289   0.508           19.251         65 309
       cart_d3[full]   0.281      0.186      0.417                      0.982    0.617  0.185      0.252   0.400           17.393         65 309
ridge_logcount[full]   0.278      0.207      0.503                      0.946    0.637  0.195      0.275   0.431           17.224         65 309
        logit[cases]   0.257      0.180      0.450                      0.862    0.631  0.186      0.244   0.308           13.847         65 309
   poisson_glm[full]   0.250      0.196      0.397                      0.898    0.613  0.245      0.267   0.600           24.655         65 309
persistence[persist]   0.182      0.116      0.311                      0.000    0.405  0.172      0.500   0.015            0.338         65 309
          prior[woy]   0.176      0.109      0.331                      0.462    0.421  0.171      0.000   0.000            0.000         65 309
```

## surge_seas_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.976      0.913      0.996                      0.688    0.995  0.024      0.772   1.000           13.212         61 312
   poisson_glm[full]   0.973      0.862      0.997                      0.500    0.994  0.022      0.772   1.000           13.212         61 312
persistence[persist]   0.973      0.863      0.994                      0.000    0.993  0.035      0.690   0.984           14.550         61 312
        logit[cases]   0.957      0.805      0.990                      0.028    0.988  0.030      0.784   0.951           12.376         61 312
 random_forest[full]   0.941      0.795      0.984                      0.004    0.981  0.037      0.770   0.934           12.376         61 312
       cart_d3[full]   0.931      0.722      0.986                      0.000    0.987  0.030      0.738   0.967           13.379         61 312
         logit[full]   0.924      0.666      0.979                      0.000    0.977  0.044      0.737   0.918           12.711         61 312
   lasso_logit[full]   0.924      0.586      0.977                      0.000    0.981  0.045      0.634   0.967           15.554         61 312
          prior[woy]   0.258      0.053      0.625                      0.000    0.573  0.160      0.000   0.000            0.000         61 312
      logit[weather]   0.249      0.059      0.528                      0.000    0.632  0.182      0.246   0.279           11.540         61 312
       seasonal[woy]   0.205      0.054      0.455                      0.000    0.527  0.173      0.178   0.213           12.209         61 312
```

## surge_seas_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
   poisson_glm[full]   0.963      0.840      0.994                      0.862    0.990  0.034      0.732   0.984           13.758         61 311
ridge_logcount[full]   0.953      0.814      0.986                      0.562    0.988  0.034      0.741   0.984           13.590         61 311
        logit[cases]   0.949      0.815      0.990                      0.430    0.985  0.034      0.753   0.951           12.919         61 311
persistence[persist]   0.948      0.787      0.989                      0.000    0.985  0.044      0.670   0.967           14.765         61 311
       cart_d3[full]   0.897      0.621      0.973                      0.018    0.964  0.046      0.671   0.934           14.261         61 311
   lasso_logit[full]   0.878      0.512      0.972                      0.070    0.965  0.058      0.637   0.951           15.268         61 311
         logit[full]   0.877      0.569      0.957                      0.004    0.962  0.064      0.724   0.902           12.751         61 311
 random_forest[full]   0.873      0.749      0.979                      0.120    0.966  0.043      0.767   0.918           12.248         61 311
          prior[woy]   0.254      0.061      0.621                      0.000    0.568  0.161      0.000   0.000            0.000         61 311
      logit[weather]   0.222      0.067      0.481                      0.000    0.592  0.199      0.200   0.230           11.745         61 311
       seasonal[woy]   0.205      0.058      0.488                      0.000    0.516  0.173      0.186   0.213           11.745         61 311
```

## surge_seas_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
   poisson_glm[full]   0.906      0.577      0.966                      0.950    0.975  0.051      0.663   0.967           15.029         61 309
ridge_logcount[full]   0.896      0.500      0.968                      0.952    0.971  0.056      0.633   0.934           15.198         61 309
        logit[cases]   0.882      0.544      0.959                      0.726    0.961  0.059      0.662   0.869           13.509         61 309
         logit[full]   0.869      0.548      0.958                      0.682    0.954  0.067      0.647   0.902           14.354         61 309
persistence[persist]   0.850      0.347      0.955                      0.000    0.951  0.073      0.616   0.869           14.523         61 309
   lasso_logit[full]   0.838      0.318      0.953                      0.394    0.949  0.070      0.585   0.902           15.874         61 309
 random_forest[full]   0.819      0.614      0.929                      0.322    0.934  0.064      0.634   0.852           13.847         61 309
       cart_d3[full]   0.788      0.315      0.940                      0.196    0.920  0.077      0.545   0.902           17.056         61 309
          prior[woy]   0.242      0.044      0.572                      0.000    0.553  0.164      0.000   0.000            0.000         61 309
      logit[weather]   0.236      0.060      0.534                      0.000    0.611  0.203      0.260   0.311           12.327         61 309
       seasonal[woy]   0.218      0.060      0.482                      0.000    0.531  0.172      0.203   0.213           10.808         61 309
```

## surge_seasonset_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
   poisson_glm[full]   0.938      0.877      1.000                      0.920    0.998  0.012      0.318   1.000            4.574          7 251
ridge_logcount[full]   0.898      0.834      1.000                      0.918    0.996  0.012      0.318   1.000            4.574          7 251
persistence[persist]   0.513      0.225      1.000                      0.000    0.954  0.024      0.000   0.000            0.000          7 251
 random_forest[full]   0.396      0.168      1.000                      0.084    0.920  0.023      0.500   0.286            0.832          7 251
        logit[cases]   0.364      0.116      0.836                      0.002    0.943  0.021      0.250   0.286            1.663          7 251
         logit[full]   0.355      0.061      0.750                      0.031    0.899  0.025      0.300   0.429            2.079          7 251
   lasso_logit[full]   0.213      0.044      0.546                      0.000    0.872  0.026      0.250   0.286            1.663          7 251
       cart_d3[full]   0.209      0.154      0.438                      0.002    0.943  0.022      0.231   0.857            5.405          7 251
      logit[weather]   0.036      0.013      0.084                      0.000    0.516  0.037      0.000   0.000            1.455          7 251
       seasonal[woy]   0.034      0.006      0.119                      0.000    0.364  0.028      0.000   0.000            0.000          7 251
          prior[woy]   0.029      0.007      0.066                      0.000    0.436  0.027      0.000   0.000            0.000          7 251
```

## surge_seasonset_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.742      0.531      1.000                      0.937    0.974  0.022      0.308   0.889            5.427          9 250
   poisson_glm[full]   0.727      0.513      1.000                      0.927    0.974  0.024      0.296   0.889            5.635          9 250
 random_forest[full]   0.490      0.275      0.830                      0.722    0.876  0.028      0.286   0.444            2.922          9 250
        logit[cases]   0.485      0.161      0.842                      0.643    0.928  0.026      0.217   0.556            4.801          9 250
         logit[full]   0.481      0.119      0.835                      0.639    0.902  0.027      0.250   0.333            2.505          9 250
persistence[persist]   0.429      0.191      0.975                      0.000    0.941  0.029      0.000   0.000            0.000          9 250
   lasso_logit[full]   0.215      0.072      0.555                      0.193    0.901  0.034      0.143   0.222            2.922          9 250
       cart_d3[full]   0.131      0.066      0.378                      0.000    0.804  0.035      0.184   0.778            7.931          9 250
      logit[weather]   0.051      0.014      0.117                      0.000    0.550  0.042      0.000   0.000            1.252          9 250
       seasonal[woy]   0.034      0.010      0.073                      0.000    0.382  0.036      0.000   0.000            0.000          9 250
          prior[woy]   0.031      0.009      0.075                      0.000    0.358  0.035      0.000   0.000            0.000          9 250
```

## surge_seasonset_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.656      0.484      0.952                      0.992    0.955  0.040      0.333   0.750            7.575         16 248
   poisson_glm[full]   0.639      0.454      0.841                      0.968    0.954  0.044      0.368   0.875            7.995         16 248
         logit[full]   0.586      0.277      0.804                      0.897    0.910  0.041      0.370   0.625            5.681         16 248
 random_forest[full]   0.540      0.234      0.986                      0.889    0.831  0.046      0.389   0.438            3.787         16 248
        logit[cases]   0.527      0.201      0.818                      0.824    0.923  0.049      0.357   0.625            5.891         16 248
persistence[persist]   0.372      0.214      0.703                      0.000    0.900  0.050      0.296   0.500            5.681         16 248
       cart_d3[full]   0.288      0.090      0.845                      0.579    0.808  0.056      0.244   0.688            9.468         16 248
   lasso_logit[full]   0.263      0.079      0.675                      0.320    0.892  0.069      0.310   0.562            6.102         16 248
      logit[weather]   0.092      0.026      0.248                      0.004    0.604  0.074      0.067   0.062            3.156         16 248
       seasonal[woy]   0.065      0.017      0.119                      0.000    0.446  0.064      0.000   0.000            1.052         16 248
          prior[woy]   0.058      0.015      0.131                      0.000    0.392  0.061      0.000   0.000            0.000         16 248
```

## surge_thr_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
persistence[persist]   0.956      0.898      0.982                      0.000    0.988  0.038      0.709   0.966           13.212         58 312
        logit[cases]   0.938      0.862      0.980                      0.150    0.984  0.039      0.803   0.914           11.038         58 312
ridge_logcount[full]   0.932      0.845      0.969                      0.110    0.981  0.041      0.646   0.914           13.714         58 312
   poisson_glm[full]   0.925      0.848      0.964                      0.052    0.978  0.050      0.600   0.931           15.052         58 312
   lasso_logit[full]   0.889      0.806      0.954                      0.012    0.970  0.048      0.651   0.966           14.383         58 312
       cart_d3[full]   0.882      0.745      0.955                      0.002    0.969  0.045      0.691   0.966           13.547         58 312
         logit[full]   0.856      0.715      0.941                      0.004    0.961  0.064      0.681   0.845           12.042         58 312
 random_forest[full]   0.824      0.677      0.924                      0.002    0.939  0.075      0.580   0.879           14.717         58 312
      logit[weather]   0.371      0.160      0.603                      0.000    0.676  0.160      0.321   0.466           14.048         58 312
       seasonal[woy]   0.225      0.119      0.442                      0.000    0.607  0.159      0.239   0.293           11.874         58 312
          prior[woy]   0.184      0.078      0.430                      0.000    0.495  0.157      0.000   0.000            0.000         58 312
```

## surge_thr_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
persistence[persist]   0.908      0.800      0.955                      0.000    0.972  0.053      0.659   0.931           13.758         58 311
        logit[cases]   0.881      0.688      0.955                      0.138    0.972  0.056      0.754   0.897           11.577         58 311
ridge_logcount[full]   0.880      0.645      0.958                      0.192    0.965  0.057      0.643   0.931           14.094         58 311
   lasso_logit[full]   0.873      0.713      0.947                      0.174    0.961  0.060      0.622   0.879           13.758         58 311
   poisson_glm[full]   0.835      0.558      0.954                      0.162    0.963  0.067      0.602   0.966           15.604         58 311
         logit[full]   0.812      0.562      0.948                      0.144    0.950  0.066      0.731   0.845           11.241         58 311
 random_forest[full]   0.787      0.569      0.917                      0.022    0.918  0.087      0.565   0.828           14.261         58 311
       cart_d3[full]   0.758      0.525      0.852                      0.000    0.937  0.071      0.651   0.931           13.926         58 311
      logit[weather]   0.374      0.114      0.652                      0.000    0.693  0.163      0.342   0.466           13.255         58 311
       seasonal[woy]   0.220      0.082      0.440                      0.000    0.589  0.161      0.224   0.259           11.241         58 311
          prior[woy]   0.175      0.070      0.392                      0.000    0.471  0.158      0.000   0.000            0.000         58 311
```

## surge_thr_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
persistence[persist]   0.860      0.717      0.954                      0.000    0.959  0.068      0.675   0.903           14.016         62 309
ridge_logcount[full]   0.836      0.589      0.941                      0.370    0.956  0.072      0.622   0.903           15.198         62 309
        logit[cases]   0.825      0.527      0.961                      0.224    0.940  0.077      0.704   0.806           11.990         62 309
   lasso_logit[full]   0.807      0.590      0.906                      0.200    0.948  0.077      0.655   0.887           14.185         62 309
       cart_d3[full]   0.758      0.484      0.912                      0.012    0.907  0.088      0.600   0.871           15.198         62 309
 random_forest[full]   0.745      0.446      0.892                      0.042    0.897  0.100      0.542   0.726           14.016         62 309
   poisson_glm[full]   0.736      0.429      0.930                      0.130    0.941  0.095      0.581   0.984           17.731         62 309
         logit[full]   0.725      0.416      0.923                      0.200    0.937  0.087      0.691   0.758           11.483         62 309
      logit[weather]   0.304      0.091      0.577                      0.000    0.611  0.189      0.295   0.419           14.860         62 309
       seasonal[woy]   0.217      0.075      0.419                      0.000    0.562  0.173      0.216   0.258           12.496         62 309
          prior[woy]   0.178      0.064      0.384                      0.000    0.440  0.169      0.000   0.000            0.000         62 309
```

## surge_thronset_h1
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
ridge_logcount[full]   0.303      0.061      0.779                      0.524    0.908  0.032      0.174   0.500            4.652          8 258
persistence[persist]   0.302      0.108      0.592                      0.000    0.930  0.026      0.000   0.000            0.000          8 258
        logit[cases]   0.272      0.075      0.527                      0.278    0.909  0.027      0.429   0.375            1.416          8 258
   poisson_glm[full]   0.197      0.060      0.685                      0.192    0.900  0.044      0.143   0.500            5.663          8 258
       cart_d3[full]   0.175      0.063      0.341                      0.006    0.873  0.026      0.212   0.875            6.674          8 258
         logit[full]   0.146      0.042      0.522                      0.120    0.826  0.035      0.143   0.250            2.831          8 258
 random_forest[full]   0.128      0.046      0.374                      0.048    0.779  0.029      0.000   0.000            1.011          8 258
   lasso_logit[full]   0.104      0.041      0.310                      0.002    0.800  0.032      0.000   0.000            1.416          8 258
      logit[weather]   0.037      0.013      0.131                      0.000    0.381  0.034      0.000   0.000            1.820          8 258
       seasonal[woy]   0.036      0.018      0.089                      0.002    0.498  0.031      0.000   0.000            0.000          8 258
          prior[woy]   0.026      0.013      0.055                      0.000    0.335  0.030      0.000   0.000            0.000          8 258
```

## surge_thronset_h2
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
        logit[cases]   0.372      0.119      0.605                      0.856    0.927  0.037      0.385   0.417            2.639         12 257
 random_forest[full]   0.278      0.061      0.675                      0.536    0.782  0.042      0.250   0.167            1.624         12 257
         logit[full]   0.275      0.101      0.561                      0.650    0.862  0.046      0.300   0.500            4.061         12 257
       cart_d3[full]   0.266      0.138      0.387                      0.750    0.888  0.038      0.257   0.750            7.106         12 257
   poisson_glm[full]   0.260      0.086      0.760                      0.598    0.904  0.058      0.257   0.750            7.106         12 257
   lasso_logit[full]   0.257      0.084      0.566                      0.546    0.871  0.043      0.316   0.500            3.858         12 257
persistence[persist]   0.251      0.115      0.383                      0.000    0.911  0.039      0.200   0.083            1.015         12 257
ridge_logcount[full]   0.230      0.080      0.757                      0.472    0.892  0.050      0.259   0.583            5.482         12 257
      logit[weather]   0.106      0.033      0.293                      0.062    0.603  0.054      0.143   0.167            2.842         12 257
       seasonal[woy]   0.053      0.031      0.136                      0.012    0.469  0.047      0.000   0.000            0.000         12 257
          prior[woy]   0.038      0.019      0.085                      0.000    0.318  0.045      0.000   0.000            0.000         12 257
```

## surge_thronset_h4
```
               model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  alarms_per_year  positives   n
         logit[full]   0.311      0.091      0.950                      0.580    0.907  0.071      0.444   0.500            3.683         16 255
persistence[persist]   0.296      0.119      0.611                      0.000    0.896  0.050      0.286   0.375            4.297         16 255
ridge_logcount[full]   0.295      0.105      0.818                      0.622    0.921  0.062      0.344   0.688            6.548         16 255
        logit[cases]   0.282      0.102      0.638                      0.512    0.872  0.054      0.294   0.312            3.479         16 255
       cart_d3[full]   0.282      0.139      0.542                      0.452    0.840  0.052      0.234   0.688            9.617         16 255
   lasso_logit[full]   0.279      0.096      0.708                      0.532    0.893  0.055      0.304   0.438            4.706         16 255
 random_forest[full]   0.261      0.061      0.772                      0.440    0.804  0.054      0.267   0.250            3.069         16 255
   poisson_glm[full]   0.220      0.089      0.535                      0.280    0.883  0.087      0.292   0.875            9.822         16 255
      logit[weather]   0.128      0.028      0.584                      0.224    0.636  0.081      0.143   0.188            4.297         16 255
       seasonal[woy]   0.057      0.023      0.157                      0.002    0.406  0.064      0.000   0.000            1.432         16 255
          prior[woy]   0.050      0.022      0.116                      0.000    0.286  0.060      0.000   0.000            0.000         16 255
```

## count regression error (out-of-sample, cases)
```
                                     mae   rmse
target       model                             
surge_thr_h1 poisson_glm[full]      44.1   94.0
             ridge_logcount[full]   41.9   83.8
surge_thr_h2 poisson_glm[full]      63.3  124.6
             ridge_logcount[full]   56.4  104.5
surge_thr_h4 poisson_glm[full]     108.5  200.7
             ridge_logcount[full]   87.2  151.8
```

## reporting-delay sensitivity (PR-AUC; delay=1: week t counts unknown)
```
                                    delay0  delay1
target        model                               
surge_grow_h1 lasso_logit[full]      0.225   0.198
              logit[cases]           0.180   0.171
              logit[full]            0.215   0.205
              logit[weather]         0.146   0.147
              persistence[persist]   0.166   0.133
              poisson_glm[full]      0.201   0.205
              seasonal[woy]          0.181   0.185
surge_seas_h1 lasso_logit[full]      0.928   0.883
              logit[cases]           0.957   0.949
              logit[full]            0.924   0.905
              logit[weather]         0.249   0.255
              persistence[persist]   0.973   0.948
              poisson_glm[full]      0.973   0.957
              seasonal[woy]          0.205   0.209
surge_thr_h1  lasso_logit[full]      0.889   0.866
              logit[cases]           0.938   0.881
              logit[full]            0.856   0.816
              logit[weather]         0.371   0.371
              persistence[persist]   0.956   0.907
              poisson_glm[full]      0.925   0.815
              seasonal[woy]          0.225   0.225
```

see tables/*.csv, tables/tree_rules.txt, figures/model_calibration.png, figures/model_best_*.png
