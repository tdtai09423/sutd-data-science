# Peak / decline extension

In-wave: y[t] > 52-week mean and y[t] >= 100. decl_h: y[t+h] <= (1-q)*y[t], q = {1: 0.1, 2: 0.15, 4: 0.2}. Scored on in-wave weeks only.
Rolling origin by week from 2016, refit every origin, purged by horizon.
p_better = share of 500 block-bootstrap draws (13-week blocks) beating the momentum baseline. Precision/recall at P >= 0.5.

# development

## decl_h1 (best on development: logit[peak])
```
                    model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  positives  n
            seasonal[woy]   0.472      0.247      0.706                      0.966    0.701  0.197      0.500   0.034         29 92
              logit[peak]   0.444      0.193      0.544                      0.938    0.580  0.213      0.750   0.103         29 92
     ridge_logcount[peak]   0.429      0.177      0.526                      0.950    0.527  0.221      0.556   0.172         29 92
      random_forest[peak]   0.403      0.210      0.434                      0.778    0.573  0.216      0.444   0.138         29 92
lasso_logit[peak+weather]   0.384      0.207      0.596                      0.934    0.567  0.215      0.333   0.034         29 92
    ridge_logcount[cases]   0.380      0.180      0.491                      0.992    0.495  0.226      0.286   0.069         29 92
             logit[cases]   0.346      0.175      0.455                      0.910    0.468  0.223      1.000   0.069         29 92
          momentum[trend]   0.290      0.131      0.428                      0.000    0.356  0.229      1.000   0.034         29 92
               prior[woy]   0.279      0.134      0.457                      0.476    0.420  0.218      0.000   0.000         29 92
```

## decl_h2 (best on development: logit[cases])
```
                    model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  positives  n
             logit[cases]   0.495      0.319      0.642                      1.000    0.679  0.177      0.500   0.083         24 92
              logit[peak]   0.458      0.184      0.637                      1.000    0.664  0.177      1.000   0.083         24 92
    ridge_logcount[cases]   0.451      0.263      0.612                      1.000    0.667  0.187      0.500   0.042         24 92
     ridge_logcount[peak]   0.447      0.132      0.563                      0.952    0.558  0.191      0.667   0.167         24 92
            seasonal[woy]   0.426      0.169      0.663                      0.992    0.731  0.173      0.333   0.125         24 92
lasso_logit[peak+weather]   0.386      0.181      0.499                      0.956    0.691  0.188      0.286   0.083         24 92
      random_forest[peak]   0.376      0.133      0.470                      0.816    0.618  0.199      0.417   0.417         24 92
          momentum[trend]   0.236      0.083      0.354                      0.000    0.336  0.201      0.000   0.000         24 92
               prior[woy]   0.203      0.090      0.314                      0.198    0.342  0.197      0.000   0.000         24 92
```

## decl_h4 (best on development: logit[peak])
```
                    model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  positives  n
              logit[peak]   0.558      0.328      0.775                      1.000    0.651  0.219      0.714   0.303         33 92
             logit[cases]   0.520      0.300      0.707                      0.986    0.648  0.223      0.556   0.152         33 92
      random_forest[peak]   0.517      0.196      0.835                      0.948    0.695  0.217      0.535   0.697         33 92
    ridge_logcount[cases]   0.512      0.264      0.682                      0.974    0.649  0.220      0.500   0.030         33 92
     ridge_logcount[peak]   0.496      0.181      0.646                      0.850    0.501  0.254      0.615   0.242         33 92
lasso_logit[peak+weather]   0.453      0.237      0.653                      0.976    0.636  0.220      0.476   0.303         33 92
            seasonal[woy]   0.446      0.220      0.672                      0.952    0.640  0.222      0.167   0.061         33 92
          momentum[trend]   0.282      0.141      0.416                      0.000    0.251  0.244      0.000   0.000         33 92
               prior[woy]   0.263      0.131      0.406                      0.352    0.277  0.240      0.000   0.000         33 92
```

# holdout

## decl_h1 (best on development: logit[peak])
```
                    model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  positives  n
      random_forest[peak]   0.403      0.069      0.469                      0.922    0.757  0.166      0.556   0.714          7 37
    ridge_logcount[cases]   0.394      0.067      0.627                      0.928    0.729  0.162      0.000   0.000          7 37
     ridge_logcount[peak]   0.328      0.095      0.494                      0.915    0.729  0.172      0.000   0.000          7 37
              logit[peak]   0.321      0.075      0.442                      0.751    0.676  0.163      0.000   0.000          7 37
             logit[cases]   0.236      0.055      0.420                      0.736    0.571  0.162      0.000   0.000          7 37
lasso_logit[peak+weather]   0.216      0.050      0.529                      0.620    0.486  0.176      0.000   0.000          7 37
            seasonal[woy]   0.203      0.043      0.536                      0.477    0.448  0.179      0.000   0.000          7 37
          momentum[trend]   0.167      0.055      0.415                      0.000    0.381  0.175      0.000   0.000          7 37
               prior[woy]   0.141      0.043      0.310                      0.002    0.248  0.164      0.000   0.000          7 37
```

## decl_h2 (best on development: logit[cases])
```
                    model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  positives  n
      random_forest[peak]   0.655      0.407      1.000                      1.000    0.875  0.148        0.5   0.375          8 37
              logit[peak]   0.604      0.333      0.700                      1.000    0.875  0.138        1.0   0.125          8 37
             logit[cases]   0.600      0.185      0.643                      1.000    0.866  0.142        0.0   0.000          8 37
    ridge_logcount[cases]   0.560      0.333      0.700                      1.000    0.884  0.140        0.0   0.000          8 37
     ridge_logcount[peak]   0.410      0.194      0.429                      0.987    0.802  0.156        0.0   0.000          8 37
            seasonal[woy]   0.406      0.029      0.616                      0.985    0.625  0.169        0.0   0.000          8 37
lasso_logit[peak+weather]   0.391      0.094      0.730                      1.000    0.759  0.160        0.0   0.000          8 37
               prior[woy]   0.153      0.028      0.372                      0.533    0.211  0.175        0.0   0.000          8 37
          momentum[trend]   0.148      0.028      0.323                      0.000    0.181  0.177        0.0   0.000          8 37
```

## decl_h4 (best on development: logit[peak])
```
                    model  pr_auc  pr_auc_lo  pr_auc_hi  p_better_than_persistence  roc_auc  brier  precision  recall  positives  n
              logit[peak]   0.902      0.333      0.907                      1.000    0.940  0.133      0.688   0.917         12 37
             logit[cases]   0.901      0.365      0.898                      1.000    0.943  0.143      1.000   0.500         12 37
    ridge_logcount[cases]   0.879      0.478      1.000                      1.000    0.943  0.146      0.800   0.333         12 37
      random_forest[peak]   0.867      0.167      0.850                      1.000    0.930  0.155      0.550   0.917         12 37
     ridge_logcount[peak]   0.866      0.333      0.874                      1.000    0.927  0.160      0.688   0.917         12 37
lasso_logit[peak+weather]   0.820      0.333      0.863                      1.000    0.917  0.139      0.818   0.750         12 37
            seasonal[woy]   0.732      0.034      0.813                      1.000    0.757  0.192      0.000   0.000         12 37
               prior[woy]   0.236      0.028      0.612                      0.663    0.253  0.222      0.000   0.000         12 37
          momentum[trend]   0.232      0.027      0.578                      0.000    0.233  0.222      0.000   0.000         12 37
```

## waves (y > 52-week mean, >= 8 weeks, peak >= 300)
```
     start        end       peak  peak_cases  weeks  peak_log1p  cum52_at_peak
2012-12-24 2013-07-22 2013-06-17         838     31        6.73           9.52
2013-08-12 2013-11-11 2013-10-21         495     14        6.21           9.87
2014-05-19 2014-08-18 2014-06-30         888     14        6.79           9.87
2015-07-06 2016-03-28 2016-01-18         635     39        6.46           9.42
2018-10-15 2019-09-16 2019-07-08         661     49        6.50           9.12
2020-01-27 2020-03-23 2020-02-03         400      9        5.99           9.73
2020-04-20 2020-09-14 2020-07-20        1791     22        7.49          10.23
2022-01-03 2022-09-12 2022-05-23        1563     37        7.36           9.56
```

## peak timing (first in-wave week with P >= 0.5)
```
 wave_peak  target           model first_signal  first_signal_minus_peak_wk  signals_before_peak  false_signals_before_peak  weeks_before_peak_scored
2019-07-08 decl_h1     logit[peak]   2019-02-11                       -21.0                    1                          0                        30
2019-07-08 decl_h1 momentum[trend]   2019-02-11                       -21.0                    1                          0                        30
2019-07-08 decl_h2    logit[cases]         None                         NaN                    0                          0                        30
2019-07-08 decl_h2 momentum[trend]         None                         NaN                    0                          0                        30
2019-07-08 decl_h4     logit[peak]         None                         NaN                    0                          0                        30
2019-07-08 decl_h4 momentum[trend]         None                         NaN                    0                          0                        30
2020-02-03 decl_h1     logit[peak]   2020-02-03                         0.0                    0                          0                         1
2020-02-03 decl_h1 momentum[trend]         None                         NaN                    0                          0                         1
2020-02-03 decl_h2    logit[cases]         None                         NaN                    0                          0                         1
2020-02-03 decl_h2 momentum[trend]         None                         NaN                    0                          0                         1
2020-02-03 decl_h4     logit[peak]         None                         NaN                    0                          0                         1
2020-02-03 decl_h4 momentum[trend]         None                         NaN                    0                          0                         1
2020-07-20 decl_h1     logit[peak]   2020-09-14                         8.0                    0                          0                        13
2020-07-20 decl_h1 momentum[trend]         None                         NaN                    0                          0                        13
2020-07-20 decl_h2    logit[cases]         None                         NaN                    0                          0                        13
2020-07-20 decl_h2 momentum[trend]         None                         NaN                    0                          0                        13
2020-07-20 decl_h4     logit[peak]   2020-07-13                        -1.0                    1                          0                        13
2020-07-20 decl_h4 momentum[trend]         None                         NaN                    0                          0                        13
2022-05-23 decl_h1     logit[peak]   2022-05-09                        -2.0                    1                          1                        20
2022-05-23 decl_h1 momentum[trend]         None                         NaN                    0                          0                        20
2022-05-23 decl_h2    logit[cases]         None                         NaN                    0                          0                        20
2022-05-23 decl_h2 momentum[trend]         None                         NaN                    0                          0                        20
2022-05-23 decl_h4     logit[peak]   2022-05-09                        -2.0                    1                          1                        20
2022-05-23 decl_h4 momentum[trend]         None                         NaN                    0                          0                        20
```
