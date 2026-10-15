# Model summary

Rolling-origin CV: each test year uses all earlier weeks for training (purged by h weeks). Alarm threshold for classifiers p>=0.5.

## surge_grow_h1
```
          model features  roc_auc  pr_auc  brier  precision  recall    f1  false_alarm_rate  prevalence   n
    poisson_glm     full    0.664   0.288    NaN      0.316   0.286 0.300             0.096       0.135 312
          logit     full    0.638   0.257  0.133      0.320   0.190 0.239             0.063       0.135 312
       logit_l1     full    0.646   0.250  0.113      0.000   0.000 0.000             0.000       0.135 312
  random_forest     full    0.651   0.237  0.113      0.000   0.000 0.000             0.000       0.135 312
          logit    cases    0.681   0.234  0.117      0.250   0.071 0.111             0.033       0.135 312
hist_gb_poisson     full    0.613   0.213    NaN      0.232   0.310 0.265             0.159       0.135 312
        hist_gb     full    0.540   0.196  0.130      0.286   0.048 0.082             0.019       0.135 312
        tree_d3     full    0.607   0.175  0.127      0.118   0.048 0.068             0.056       0.135 312
          logit  weather    0.508   0.172  0.146      0.200   0.095 0.129             0.059       0.135 312
          prior    cases    0.359   0.107  0.118      0.000   0.000 0.000             0.000       0.135 312
```

## surge_grow_h2
```
          model features  roc_auc  pr_auc  brier  precision  recall    f1  false_alarm_rate  prevalence   n
  random_forest     full    0.651   0.269  0.141      0.000   0.000 0.000             0.004       0.174 311
    poisson_glm     full    0.655   0.259    NaN      0.236   0.315 0.270             0.214       0.174 311
          logit     full    0.600   0.247  0.221      0.262   0.389 0.313             0.230       0.174 311
        hist_gb     full    0.584   0.241  0.171      0.258   0.148 0.188             0.089       0.174 311
          logit  weather    0.617   0.237  0.190      0.274   0.370 0.315             0.206       0.174 311
          logit    cases    0.603   0.235  0.152      0.300   0.111 0.162             0.054       0.174 311
hist_gb_poisson     full    0.596   0.234    NaN      0.186   0.241 0.210             0.222       0.174 311
       logit_l1     full    0.604   0.221  0.143      0.000   0.000 0.000             0.004       0.174 311
        tree_d3     full    0.552   0.207  0.161      0.200   0.093 0.127             0.078       0.174 311
          prior    cases    0.437   0.153  0.144      0.000   0.000 0.000             0.000       0.174 311
```

## surge_grow_h4
```
          model features  roc_auc  pr_auc  brier  precision  recall    f1  false_alarm_rate  prevalence   n
       logit_l1     full    0.619   0.329  0.163      0.250   0.015 0.029             0.012       0.214 309
  random_forest     full    0.654   0.314  0.162      0.333   0.030 0.056             0.016       0.214 309
hist_gb_poisson     full    0.593   0.300    NaN      0.160   0.182 0.170             0.259       0.214 309
    poisson_glm     full    0.608   0.293    NaN      0.230   0.258 0.243             0.235       0.214 309
        tree_d3     full    0.557   0.293  0.184      0.455   0.227 0.303             0.074       0.214 309
        hist_gb     full    0.593   0.291  0.208      0.308   0.121 0.174             0.074       0.214 309
          logit  weather    0.573   0.287  0.216      0.329   0.364 0.345             0.202       0.214 309
          logit     full    0.536   0.277  0.276      0.279   0.364 0.316             0.255       0.214 309
          logit    cases    0.614   0.258  0.181      0.200   0.061 0.093             0.066       0.214 309
          prior    cases    0.490   0.210  0.171      0.000   0.000 0.000             0.000       0.214 309
```

## surge_thr_h1
```
          model features  roc_auc  pr_auc  brier  precision  recall    f1  false_alarm_rate  prevalence   n
    poisson_glm     full    0.983   0.944    NaN      0.862   0.862 0.862             0.031       0.186 312
          logit    cases    0.955   0.861  0.059      0.820   0.707 0.759             0.035       0.186 312
hist_gb_poisson     full    0.949   0.830    NaN      0.759   0.707 0.732             0.051       0.186 312
       logit_l1     full    0.916   0.789  0.082      0.812   0.672 0.736             0.035       0.186 312
          logit     full    0.927   0.752  0.095      0.657   0.759 0.704             0.091       0.186 312
        hist_gb     full    0.874   0.720  0.100      0.707   0.500 0.586             0.047       0.186 312
  random_forest     full    0.821   0.673  0.107      0.923   0.414 0.571             0.008       0.186 312
        tree_d3     full    0.772   0.574  0.128      0.562   0.466 0.509             0.083       0.186 312
          logit  weather    0.523   0.193  0.279      0.212   0.293 0.246             0.248       0.186 312
          prior    cases    0.336   0.155  0.155      0.000   0.000 0.000             0.000       0.186 312
```

## surge_thr_h2
```
          model features  roc_auc  pr_auc  brier  precision  recall    f1  false_alarm_rate  prevalence   n
    poisson_glm     full    0.963   0.863    NaN      0.662   0.879 0.756             0.103       0.186 311
          logit    cases    0.954   0.831  0.064      0.780   0.672 0.722             0.043       0.186 311
       logit_l1     full    0.898   0.762  0.091      0.791   0.586 0.673             0.036       0.186 311
hist_gb_poisson     full    0.926   0.750    NaN      0.750   0.672 0.709             0.051       0.186 311
          logit     full    0.888   0.700  0.111      0.635   0.690 0.661             0.091       0.186 311
  random_forest     full    0.809   0.688  0.111      0.923   0.414 0.571             0.008       0.186 311
        hist_gb     full    0.840   0.649  0.116      0.636   0.483 0.549             0.063       0.186 311
        tree_d3     full    0.839   0.602  0.117      0.592   0.500 0.542             0.079       0.186 311
          logit  weather    0.518   0.192  0.277      0.235   0.328 0.273             0.245       0.186 311
          prior    cases    0.332   0.154  0.155      0.000   0.000 0.000             0.000       0.186 311
```

## surge_thr_h4
```
          model features  roc_auc  pr_auc  brier  precision  recall    f1  false_alarm_rate  prevalence   n
          logit    cases    0.927   0.815  0.077      0.816   0.635 0.714             0.037       0.204 309
       logit_l1     full    0.865   0.691  0.108      0.737   0.444 0.554             0.041       0.204 309
        hist_gb     full    0.864   0.687  0.114      0.711   0.508 0.593             0.053       0.204 309
          logit     full    0.854   0.657  0.110      0.672   0.619 0.645             0.077       0.204 309
  random_forest     full    0.775   0.624  0.127      0.833   0.317 0.460             0.016       0.204 309
    poisson_glm     full    0.891   0.554    NaN      0.639   0.841 0.726             0.122       0.204 309
hist_gb_poisson     full    0.847   0.538    NaN      0.660   0.556 0.603             0.073       0.204 309
        tree_d3     full    0.829   0.485  0.132      0.571   0.444 0.500             0.085       0.204 309
          logit  weather    0.488   0.197  0.289      0.222   0.286 0.250             0.256       0.204 309
          prior    cases    0.299   0.162  0.167      0.000   0.000 0.000             0.000       0.204 309
```

## count regression error (mean over folds)
```
                                 mae   rmse
target        model                        
surge_grow_h1 hist_gb_poisson   76.9  117.6
              poisson_glm       41.5   59.7
surge_grow_h2 hist_gb_poisson   92.6  135.7
              poisson_glm       60.8   86.5
surge_grow_h4 hist_gb_poisson  120.9  167.7
              poisson_glm      103.8  137.3
surge_thr_h1  hist_gb_poisson   76.9  117.6
              poisson_glm       41.5   59.7
surge_thr_h2  hist_gb_poisson   92.6  135.7
              poisson_glm       60.8   86.5
surge_thr_h4  hist_gb_poisson  120.9  167.7
              poisson_glm      103.8  137.3
```

see tables/feature_importance.csv, tables/tree_rules.txt, figures/model_best_*.png
